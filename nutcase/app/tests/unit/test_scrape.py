import unittest
import unittest.mock as mock
import queue
import flask
import logging

from app import db
from app.models import LogEntry

from .mock_types import Threading_Condition, Mock_Queue, Urlopen

from app.utils.app_log_config import Add_Logging_Levels
from app.utils.scrape import Check_Mode, Resolve_Address_And_Port, Get_Scrape_Data

# =================================================================================================
# Base config
# =================================================================================================
BASE_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///:memory:',
    "SECRET_KEY": "secret",
    "TESTING": True,
    "WEBHOOKS": {
        "fail": "http://10.0.0.1:3001/api/fail",
        "ok": "http://10.0.0.1:3001/api/ok"
    },
    }

# =================================================================================================
# BaseTestCase
# =================================================================================================
class BaseTestCase(unittest.TestCase):
    # ===================================================================================
    def setUp(self):
        app = flask.Flask(__name__)
        app.config.update(BASE_CONFIG)
        self.app = app
        Add_Logging_Levels()
        # app.logger.setLevel("CRITICAL")
        # app.logger.setLevel("WARNING")
        app.logger.setLevel("DEBUG")
        self.app.app_context().push()
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

class Test_scrape_check_mode(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    def test_scrape_check_mode_all(self):
        CM_Tests = [
            None,
            {"addr": "a", "dev": "d", "mode": None},
            {"addr": "a", "dev": "d", "mode": "nut"},
            {"addr": "a", "dev": "d", "mode": "NUT"},
            {"addr": "a", "dev": "d", "mode": "apc"},
            {"addr": "a", "dev": "d", "mode": "ApC"},
            {"addr": "a", "dev": "d", "mode": "an_error"},
        ]

        CM_Checks = [
            ["nut", 3493],
            ["nut", 3493],
            ["nut", 3493],
            ["nut", 3493],
            ["apc", 3551],
            ["apc", 3551],
            ["none", 3493],
        ]

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            for Index in range(len(CM_Tests)):
                Type, Port = Check_Mode(CM_Tests[Index])
                self.assertEqual(Type, CM_Checks[Index][0])
                self.assertEqual(Port, CM_Checks[Index][1])

            self.assertEqual(len(cm.output), 1)
            self.assertEqual("ERROR:Unknown server "
                             "mode requested: an_error", cm.output[0])

class Test_scrape_resolve_address(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    def test_scrape_raap(self):
        RAAP_Tests = [
            None,                                  # None test
            {"addr": "1.2.3.4"},                   # Basic addr only
            {"addr": "1.2.3.4", "port": "1234"},   # Addr and port
            {"addr": "1.2.3.4", "port": "A1234"},  # Addr and invalid port
            {"addr": "1.2.3.", "port": "1234"},    # Invalid addr and port
            {"target": "1.2.3.4"},                 # Target
            {"target": "1.2.3.4:1234"},            # Target and port
            {"target": "1.2.3."},                  # Target invalid
            {"target": "1.2.3.4:A1234"},           # Target and invalid port
        ]

        RAAP_Checks = [
            [False, None, None],
            [True, "1.2.3.4", None],
            [True, "1.2.3.4", 1234],
            [False, "1.2.3.4", None],
            [False, None, 1234],
            [True, "1.2.3.4", None],
            [True, "1.2.3.4", 1234],
            [False, None, None],
            [False, "1.2.3.4", None],
        ]

        for Index in range(len(RAAP_Tests)):
            Rtn, Addr, Port = Resolve_Address_And_Port(RAAP_Tests[Index])
            self.assertEqual(Rtn, RAAP_Checks[Index][0])
            self.assertEqual(Addr, RAAP_Checks[Index][1])
            self.assertEqual(Port, RAAP_Checks[Index][2])

class Test_scrape_get_scrape_data(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()
        db.init_app(self.app)
        db.create_all()
        self.app.config['REWORK'] = [
            {"style": "nutcase_logs", "to": "nutcase.logs.triple.total", "control": "{info_total} {warning_total} {alert_total}"},
            {"style": "nutcase_logs", "to": "nutcase.logs.triple.unread", "control": "({info_unread} {warning_unread} {alert_unread})"},
            {"style": "nutcase_logs", "to": "nutcase.logs.triple.read", "control": "({info_read} {warning_read} {alert_read})"},
        ]

    # ===================================================================================
    def tearDown(self):
        super().tearDown()
        db.session.close()
        db.drop_all()

    # ===================================================================================
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    @mock.patch("urllib.request.urlopen", autospec=True)
    def test_scrape_timeout(self, mock_urlopen, mock_Queue, mock_Threading_Condition):
        url = self.app.config['WEBHOOKS']['fail'] + "?status=down&msg=ScrapeFail-1.2.3.4"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        q_obj = Mock_Queue()
        mock_Queue.return_value = q_obj
        q_obj.force_fail()

        thread_obj = Threading_Condition()
        thread_obj.force_timeout()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 2)

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Rtn, Scrape_Data = Get_Scrape_Data({"addr": "1.2.3.4"})
            self.assertEqual(cm.output, [
                "WARNING:GSD request timed out",
                ])

        self.assertEqual(mock_urlopen.call_count, 1)
        mock_urlopen.assert_called_with(url)

        self.assertFalse(Rtn)
        self.assertEqual(Scrape_Data, {})
        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())
        self.assertFalse(q_obj.get_bucket().result)

    # ===================================================================================
    # Check server poll scrape fail
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    @mock.patch("urllib.request.urlopen", autospec=True)
    def test_scrape_fail(self, mock_urlopen, mock_Queue, mock_Threading_Condition):
        url = self.app.config['WEBHOOKS']['fail'] + "?status=down&msg=ScrapeFail-1.2.3.4"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        q_obj = Mock_Queue()
        q_obj.force_fail()
        mock_Queue.return_value = q_obj

        thread_obj = Threading_Condition()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 1)

        with self.assertNoLogs(logging.getLogger(__name__), level='INFO'):
            Rtn, Scrape_Data = Get_Scrape_Data({"addr": "1.2.3.4"})

        self.assertEqual(mock_urlopen.call_count, 1)
        mock_urlopen.assert_called_with(url)

        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())

        self.assertFalse(q_obj.get_bucket().result)

        self.assertFalse(Rtn)
        self.assertEqual(Scrape_Data, {})

    # ===================================================================================
    # Check server poll scrape success
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    @mock.patch("urllib.request.urlopen", autospec=True)
    def test_scrape_success(self, mock_urlopen, mock_Queue, mock_Threading_Condition):
        url = self.app.config['WEBHOOKS']['ok'] + "?status=up&msg=ScrapeOK-1.2.3.4"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        q_obj = Mock_Queue()
        Bucket_data = {"ups_list": [
            {'name': 'ups-one',
             'description': 'Desc1',
             'variables': [{'name': 'ups.status', 'value': 'OL'},],
             'server_address': '1.0.0.2',
             'server_port': 3493,
             'clients': [],
            },
        ]}
        q_obj.set_data(Bucket_data)
        mock_Queue.return_value = q_obj

        thread_obj = Threading_Condition()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 1)

        with self.assertNoLogs(logging.getLogger(__name__), level='INFO'):
            Rtn, Scrape_Data = Get_Scrape_Data({"addr": "1.2.3.4"})

        self.assertEqual(mock_urlopen.call_count, 1)
        mock_urlopen.assert_called_with(url)

        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())

        self.assertTrue(q_obj.get_bucket().result)
        self.assertEqual(q_obj.get_bucket().scrape_data, Bucket_data)

    # ===================================================================================
    # Check server poll scrape sequence
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    @mock.patch("urllib.request.urlopen", autospec=True)
    def test_scrape_get_scrape_data(self, mock_urlopen, mock_Queue, mock_Threading_Condition):
        url = self.app.config['WEBHOOKS']['ok'] + "?status=up&msg=ScrapeOK-1.2.3.4"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        q_obj = Mock_Queue()
        Bucket_data = {"ups_list": [
            {'name': 'ups-one',
             'description': 'Desc1',
             'variables': [{'name': 'ups.status', 'value': 'OL'},],
             'server_address': '1.0.0.2',
             'server_port': 3493,
             'clients': [],
            },
        ]}
        q_obj.set_data(Bucket_data)
        mock_Queue.return_value = q_obj

        thread_obj = Threading_Condition()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 1)

        GSD_Tests = [
            None,                                  # None test
            {"addr": "1.2.3.", "port": "1234"},    # Invalid addr and port
            {"addr": "1.2.3.4"},                   # Basic addr only
            # {"addr": "1.2.3.4", "port": "1234"},   # Addr and port
            # {"addr": "1.2.3.4", "port": "A1234"},  # Addr and invalid port
            # {"addr": "1.2.3.", "port": "1234"},    # Invalid addr and port
            # {"target": "1.2.3.4"},                 # Target
            # {"target": "1.2.3.4:1234"},            # Target and port
            # {"target": "1.2.3."},                  # Target invalid
            # {"target": "1.2.3.4:A1234"},           # Target and invalid port
        ]

        GSD_Checks = [
            [False, {}],
            [False, {}],
            [True, Bucket_data],
        ]

        for Index in range(len(GSD_Tests)):
            Rtn, Scrape_Data = Get_Scrape_Data(GSD_Tests[Index])
            self.assertEqual(Rtn, GSD_Checks[Index][0])
            self.assertEqual(Scrape_Data, GSD_Checks[Index][1])

    # ===================================================================================
    # Check server poll scrape log entries
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    @mock.patch("urllib.request.urlopen", autospec=True)
    def test_scrape_get_scrape_log_data(self, mock_urlopen, mock_Queue, mock_Threading_Condition):
        url = self.app.config['WEBHOOKS']['ok'] + "?status=up&msg=ScrapeOK-1.2.3.4"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        q_obj = Mock_Queue()
        Bucket_data = {"ups_list": [
            {'name': 'ups-one',
             'description': 'Desc1',
             'variables': [{'name': 'ups.status', 'value': 'OL'},],
             'server_address': '1.0.0.2',
             'server_port': 3493,
             'clients': [],
            },
        ]}
        q_obj.set_data(Bucket_data)
        mock_Queue.return_value = q_obj

        thread_obj = Threading_Condition()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 1)

        Test_Logs = [
            {'title': 'A title0', 'server': '1.0.0.2', 'device': '', 'read': False, 'level': 1},
            {'title': 'A title1', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 1},
            {'title': 'A title2', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 1},
            {'title': 'A title3', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 1},

            {'title': 'A title4', 'server': '1.0.0.2', 'device': '', 'read': False, 'level': 2},
            {'title': 'A title5', 'server': '1.0.0.2', 'device': '', 'read': False, 'level': 2},
            {'title': 'A title6', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 2},
            {'title': 'A title7', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 2},
            {'title': 'A title8', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 2},

            {'title': 'A title9', 'server': '1.0.0.2', 'device': '', 'read': False,  'level': 3},
            {'title': 'A title10', 'server': '1.0.0.2', 'device': '', 'read': False, 'level': 3},
            {'title': 'A title11', 'server': '1.0.0.2', 'device': '', 'read': False, 'level': 3},
            {'title': 'A title12', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 3},
            {'title': 'A title13', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 3},
            {'title': 'A title14', 'server': '1.0.0.2', 'device': '', 'read': True,  'level': 3},

            {'title': 'A title15', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title16', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title17', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title18', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title19', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title20', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title21', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 1},
            {'title': 'A title22', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 1},
            {'title': 'A title23', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 1},
            {'title': 'A title24', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 1},

            {'title': 'A title25', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title26', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title27', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title28', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title29', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title30', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title31', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title32', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 2},
            {'title': 'A title33', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 2},
            {'title': 'A title34', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 2},
            {'title': 'A title35', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 2},

            {'title': 'A title36', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title37', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title38', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title39', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title40', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title41', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title42', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title43', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title44', 'server': '1.0.0.2', 'device': 'ups-one', 'read': False, 'level': 3},
            {'title': 'A title45', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 3},
            {'title': 'A title46', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 3},
            {'title': 'A title47', 'server': '1.0.0.2', 'device': 'ups-one', 'read': True,  'level': 3},
        ]

        for tl in Test_Logs:
            New_Log = LogEntry(**tl)
            db.session.add(New_Log)
        db.session.commit()
        Entries = LogEntry.query.all()
        self.assertEqual(len(Entries), 48)

        Server_Log_Info = {
            'total': [4, 5, 6],
            'unread': [1, 2, 3],
            'nutcase.logs.triple.total': '4 5 6',
            'nutcase.logs.triple.unread': '(1 2 3)',
            'nutcase.logs.triple.read': '(3 3 3)',
        }

        Device_Log_Info = {
            'total': [10, 11, 12],
            'unread': [7, 8, 9],
            'nutcase.logs.triple.total': '10 11 12',
            'nutcase.logs.triple.unread': '(7 8 9)',
            'nutcase.logs.triple.read': '(3 3 3)',
        }

        Rtn, Scrape_Data = Get_Scrape_Data({"addr": "1.0.0.2"})
        self.assertTrue(Rtn)
        self.assertEqual(Scrape_Data['logs'], Server_Log_Info)
        self.assertEqual(Scrape_Data['ups_list'][0]['logs'], Device_Log_Info)

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
