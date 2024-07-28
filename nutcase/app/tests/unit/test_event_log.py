import unittest
import flask
import datetime
import logging
import unittest.mock as mock
from app.utils.app_log_config import Add_Logging_Levels
from app.poller.poller import Log_Type, Device_State_Cache
from app.poller.poller import Log_Event_Message, Log_Comms_Issue, \
                                Check_Device_Parameters, Server_Poll, Check_Device_Clients
from app.utils.db_utils import Scan_DB

from app import db
from app.models import LogEntry, Log_Level, Log_Category

import queue

from .mock_types import Threading_Condition, Mock_Queue

BASE_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///:memory:',
    "SECRET_KEY": "secret",
    "TESTING": True,
    "SERVERS": [],
    "REPORT_BAT_CHARGE_PC": 5,
    "REPORT_BAT_RUNTIME_S": 120,
    "APP_STATUS_FLAGS": {
        "info":     0,
        "warning":  0,
        "alert":    0
        }
    }

# =================================================================================================
# BaseTestCase
# =================================================================================================
class BaseTestCase(unittest.TestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()
        app = flask.Flask(__name__)
        app.config.update(BASE_CONFIG)
        self.app = app
        Add_Logging_Levels()
        # app.logger.setLevel("CRITICAL")
        # app.logger.setLevel("WARNING")
        app.logger.setLevel("DEBUG")

        self.app.app_context().push()

        db.init_app(app)
        db.create_all()

    # ===================================================================================
    def tearDown(self):
        db.session.close()
        db.drop_all()
        super().tearDown()

# =================================================================================================
# Test_log_event_message
# =================================================================================================
class Test_log_event_message(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Test Database only
    def test_event_log_lem_basic(self):
        test1 = LogEntry(title='A title1', detail='A detail', level=1)
        test2 = LogEntry(title='A title2', detail='A detail', level=1)

        db.session.add(test1)
        db.session.add(test2)
        db.session.commit()
        participants = LogEntry.query.all()
        self.assertEqual(len(participants), 2)

    # ===================================================================================
    # Discreate log
    def test_event_log_lem_disc(self):
        Log_Info = {
            "type":     Log_Type.discreate,
            "title":    "Title",
            "detail":   "Detail",
            "category": "Category",
            "server":   "1.2.3.4",
            "device":   "Device",
            "level":    Log_Level.info
        }

        Log_Event_Message(Log_Info)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 1)

        if len(db_entries) == 1:
            self.assertEqual(db_entries[0].title, Log_Info["title"])
            self.assertEqual(db_entries[0].detail, Log_Info["detail"])
            self.assertEqual(db_entries[0].server, Log_Info["server"])
            self.assertEqual(db_entries[0].device, Log_Info["device"])
            self.assertEqual(db_entries[0].category, Log_Info["category"])
            self.assertEqual(db_entries[0].level, Log_Level.info.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

    # ===================================================================================
    # Discreate log (implicit)
    def test_event_log_lem_disc_im(self):
        Log_Info = {
            "title":    "Title",
            "detail":   "Detail",
            "category": "Category",
            "server":   "1.2.3.4",
            "device":   "Device",
            "level":    Log_Level.info
        }

        Log_Event_Message(Log_Info)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 1)

        if len(db_entries) == 1:
            self.assertEqual(db_entries[0].title, Log_Info["title"])
            self.assertEqual(db_entries[0].detail, Log_Info["detail"])
            self.assertEqual(db_entries[0].server, Log_Info["server"])
            self.assertEqual(db_entries[0].device, Log_Info["device"])
            self.assertEqual(db_entries[0].category, Log_Info["category"])
            self.assertEqual(db_entries[0].level, Log_Level.info.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

    # ===================================================================================
    # Single log, no server, level warn
    def test_event_log_lem_single(self):
        Log_Info = {
            "type":     Log_Type.single,
            "title":    "Title",
            "detail":   "Detail",
            "category": "Category",
            "device":   "Device",
            "level":    Log_Level.warning
        }

        Log_Event_Message(Log_Info)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 1)
        if len(db_entries) == 1:
            self.assertEqual(db_entries[0].title, Log_Info["title"])
            self.assertEqual(db_entries[0].detail, Log_Info["detail"])
            self.assertEqual(db_entries[0].server, None)
            self.assertEqual(db_entries[0].device, Log_Info["device"])
            self.assertEqual(db_entries[0].category, Log_Info["category"])
            self.assertEqual(db_entries[0].level, Log_Level.warning.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

    # ===================================================================================
    # Single log, with substitution
    def test_event_log_lem_sub(self):
        Log_Info = {
            "type":     Log_Type.single,
            "title":    "Title {server} {category}",
            "detail":   "Detail {server} {category}",
            "server":   "1.2.3.4",
            "category": "Category",
            "device":   "Device",
            "level":    Log_Level.alert
        }

        Log_Event_Message(Log_Info)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 1)
        if len(db_entries) == 1:
            self.assertEqual(db_entries[0].title, "Title " +
                                                  Log_Info["server"] + " " +
                                                  Log_Info["category"])
            self.assertEqual(db_entries[0].detail, "Detail " +
                                                  Log_Info["server"] + " " +
                                                  Log_Info["category"])
            self.assertEqual(db_entries[0].server, "1.2.3.4")
            self.assertEqual(db_entries[0].device, Log_Info["device"])
            self.assertEqual(db_entries[0].category, Log_Info["category"])
            self.assertEqual(db_entries[0].level, Log_Level.alert.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

# =================================================================================================
# Test_log_event_rpt_message
# =================================================================================================
class Test_log_event_rpt_message(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Recuring log, level alert
    def test_event_log_lem_recuring(self):
        Log_Info = {
            "type":     Log_Type.recuring,
            "title":    "Title",
            "detail":   "Detail 1",
            "server":   "1.2.3.4",
            "category": "Category",
            "device":   "Device",
            "level":    Log_Level.alert
        }

        Log_Event_Message(Log_Info)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 1)
            if len(db_entries) == 1:
                self.assertEqual(db_entries[0].title, Log_Info["title"])
                self.assertEqual(db_entries[0].detail, Log_Info["detail"])
                self.assertEqual(db_entries[0].server, Log_Info["server"])
                self.assertEqual(db_entries[0].device, Log_Info["device"])
                self.assertEqual(db_entries[0].category, Log_Info["category"])
                self.assertEqual(db_entries[0].level, Log_Level.alert.value)
                self.assertEqual(db_entries[0].read, False)
                self.assertEqual(db_entries[0].occurrences, 1)
                self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
                self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

        Log_Event_Message(Log_Info)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 1)
            if len(db_entries) == 1:
                self.assertEqual(db_entries[0].title, Log_Info["title"])
                self.assertEqual(db_entries[0].detail, Log_Info["detail"])
                self.assertEqual(db_entries[0].server, Log_Info["server"])
                self.assertEqual(db_entries[0].device, Log_Info["device"])
                self.assertEqual(db_entries[0].category, Log_Info["category"])
                self.assertEqual(db_entries[0].level, Log_Level.alert.value)
                self.assertEqual(db_entries[0].read, False)
                self.assertEqual(db_entries[0].occurrences, 2)
                self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
                self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

# =================================================================================================
# Test_log_comms_issue
# =================================================================================================
class Test_log_comms_issue(BaseTestCase):
    # ===================================================================================
    # Server comms
    def test_log_server_comms_error(self):
        Server_Info = {
            "server":   "1.2.3.4",
            "port":     3493,
            "device":   "ups-dev",
            "name":     "A name",
            "mode":     "nut",
        }

        Log_Comms_Issue(Server_Info)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 1)

        if len(db_entries) == 1:
            self.assertEqual(db_entries[0].title, "Server connection")
            self.assertEqual(db_entries[0].detail, "Server 1.2.3.4 port 3493, "
                                                        "mode nut could not be accessed")
            self.assertEqual(db_entries[0].server, "1.2.3.4")
            self.assertEqual(db_entries[0].device, "")
            self.assertEqual(db_entries[0].category, "Comms")
            self.assertEqual(db_entries[0].level, Log_Level.warning.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

        Log_Comms_Issue(Server_Info)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 1)

        if len(db_entries) == 1:
            self.assertEqual(db_entries[0].title, "Server connection")
            self.assertEqual(db_entries[0].detail, "Server 1.2.3.4 port 3493, "
                                                    "mode nut could not be accessed")
            self.assertEqual(db_entries[0].server, "1.2.3.4")
            self.assertEqual(db_entries[0].device, "")
            self.assertEqual(db_entries[0].category, "Comms")
            self.assertEqual(db_entries[0].level, Log_Level.warning.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 2)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))
            self.assertNotEqual(db_entries[0].time_first, db_entries[0].time_latest)

DD_Sequence = [
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB LB'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL CHRG'},], 'server_address': '1.2.3.4', 'server_port': 3493},

    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL TRIM'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL BOOST'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB'},], 'server_address': '1.2.3.4', 'server_port': 3493},

    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB LB'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB SD'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB FSD'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB BYPASS'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OB'},], 'server_address': '1.2.3.4', 'server_port': 3493},

    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL'},], 'server_address': '1.2.3.4', 'server_port': 3493},
    {'name': 'ups-one', 'description': 'Desc1', 'variables': [{'name': 'ups.status', 'value': 'OL RB'},], 'server_address': '1.2.3.4', 'server_port': 3493},
]
Msg_Sequence = [
    {'title': 'UPS On battery', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.alert.value},
    {'title': 'Low battery', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Battery.name, "level": Log_Level.warning.value},
    {'title': 'Power restored', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.info.value},
    {'title': 'Charging started', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Battery.name, "level": Log_Level.info.value},
    {'title': 'Charging stopped', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Battery.name, "level": Log_Level.info.value},

    {'title': 'Triming', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.warning.value},
    {'title': 'Stopped triming', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.info.value},
    {'title': 'Boosting', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.warning.value},
    {'title': 'UPS On battery', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.alert.value},
    {'title': 'Stopped boosting', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.info.value},

    {'title': 'Low battery', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Battery.name, "level": Log_Level.warning.value},
    {'title': 'Shutdown', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.warning.value},
    {'title': 'Forced shutdown', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.alert.value},
    {'title': 'On bypass', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.warning.value},
    {'title': 'Off bypass', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.info.value},

    {'title': 'Power restored', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.info.value},
    {'title': 'Replace battery', 'detail': '', 'server': "1.2.3.4", 'device': 'ups-one', 'category': Log_Category.Power.name, "level": Log_Level.alert.value},
]

# =================================================================================================
# Test_check_device_status
# =================================================================================================
class Test_check_device_status(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()
        self.app.config.update(APP_STATUS_FLAGS = {'info': 0, 'warning': 0, 'alert': 0})

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Check status transitions
    def test_status_change(self):

        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['info'], 0)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['warning'], 0)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['alert'], 0)

        for dd in DD_Sequence:
            Check_Device_Parameters(dd)

        db_entries = LogEntry.query.all()

        for msg_i in range(len(Msg_Sequence)):
            self.assertEqual(db_entries[msg_i].title, Msg_Sequence[msg_i]['title'])
            self.assertEqual(db_entries[msg_i].server, Msg_Sequence[msg_i]['server'])
            self.assertEqual(db_entries[msg_i].device, Msg_Sequence[msg_i]['device'])
            self.assertEqual(db_entries[msg_i].category, Msg_Sequence[msg_i]['category'])
            self.assertEqual(db_entries[msg_i].level, Msg_Sequence[msg_i]['level'])

        Scan_DB(self.app)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['info'], 7)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['warning'], 6)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['alert'], 4)

# =================================================================================================
# Test_server_poll
# =================================================================================================
class Test_server_poll(unittest.TestCase):
    # ===================================================================================
    def setUp(self):
        app = flask.Flask(__name__)
        app.config.update(BASE_CONFIG)
        app.config.update(REPORT_SCRAPE_LIMIT=10)
        self.app = app
        Add_Logging_Levels()
#         # app.logger.setLevel("CRITICAL")
#         # app.logger.setLevel("WARNING")
        app.logger.setLevel("DEBUG")

        self.app.app_context().push()

        db.init_app(app)
        db.create_all()
        self.app.config.update( SERVERS = [
        {
            "server": "1.0.0.1",
            "port": 3493,
            "device": 'ups-one',
            "mode": 'nut',
            "default": True,
            "power": 550,
            "name": 'Downstairs CyberPower',
            "monitor": False
        },
        {
            "server": "1.0.0.2",
            "port": 3493,
            "device": 'ups-one',
            "mode": 'nut',
            "default": True,
            "power": 550,
            "name": 'Downstairs CyberPower',
            "monitor": True
        },
        {
            "server": "1.0.0.2",
            "port": 3493,
            "device": 'ups-two',
            "mode": 'nut',
            "default": True,
            "power": 550,
            "name": 'Downstairs CyberPower',
            "monitor": True
        }
        ])

    # ===================================================================================
    def tearDown(self):
        db.session.close()
        db.drop_all()

    # ===================================================================================
    # Check server poll timeout
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    def test_server_poll_timeout(self, mock_Queue, mock_Threading_Condition):
        q_obj = Mock_Queue()
        mock_Queue.return_value = q_obj
        q_obj.force_fail()

        thread_obj = Threading_Condition()
        thread_obj.force_timeout()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 2)

        with self.assertNoLogs(logging.getLogger(__name__), level='INFO'):
            Server_Poll(self.app)

        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())
        self.assertFalse(q_obj.get_bucket().result)

    # ===================================================================================
    # Check server poll scrape fail
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    def test_server_poll_scrape_fail(self, mock_Queue, mock_Threading_Condition):
        q_obj = Mock_Queue()
        q_obj.force_fail()
        mock_Queue.return_value = q_obj

        thread_obj = Threading_Condition()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 1)

        with self.assertNoLogs(logging.getLogger(__name__), level='INFO'):
            Server_Poll(self.app)

        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())

        self.assertFalse(q_obj.get_bucket().result)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 1)
        self.assertEqual(db_entries[0].title, "Server connection")
        self.assertEqual(db_entries[0].detail, "Server 1.0.0.2 port 3493, mode nut could not be accessed")
        self.assertEqual(db_entries[0].server, "1.0.0.2")
        self.assertEqual(db_entries[0].device, "")
        self.assertEqual(db_entries[0].category, "Comms")
        self.assertEqual(db_entries[0].level, Log_Level.warning.value)

    # ===================================================================================
    # Check server poll scrape success
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    def test_server_poll_scrape_success(self, mock_Queue, mock_Threading_Condition):
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
            Server_Poll(self.app)

        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())

        self.assertTrue(q_obj.get_bucket().result)
        self.assertEqual(q_obj.get_bucket().scrape_data, Bucket_data)

        self.assertTrue('1.0.0.2_ups-one' in Device_State_Cache)
        Test_Data = Device_State_Cache['1.0.0.2_ups-one']
        self.assertEqual(Test_Data, {'ups.status': 'OL',
                                     'battery.charge': None,
                                     'battery.runtime': None,
                                     'server_address': '1.0.0.2',
                                     'last_rep_ch': None,
                                     'last_rep_rt': None,
                                     'device': 'ups-one',
                                     'starting': False}
                                     )

    # ===================================================================================
    # Check server poll scrape processing time exceeded
    @mock.patch("threading.Condition", autospec=True)
    @mock.patch("queue.Queue", autospec=True)
    def test_server_poll_scrape_process_time(self, mock_Queue, mock_Threading_Condition):
        q_obj = Mock_Queue()
        Bucket_data = {"ups_list": [
            {'name': 'ups-one',
             'description': 'Desc1',
             'variables': [{'name': 'ups.status', 'value': 'OL'},],
             'server_address': '1.0.0.2',
             'server_port': 3493},
        ]}
        q_obj.set_data(Bucket_data)
        mock_Queue.return_value = q_obj

        self.app.config.update(REPORT_SCRAPE_LIMIT=0)

        thread_obj = Threading_Condition()
        mock_Threading_Condition.return_value = thread_obj

        self.app.config.update(CACHE_QUEUE = queue.Queue())
        self.app.config.update(SCRAPE_TIMEOUT = 1)

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Server_Poll(self.app)
            self.assertEqual(len(cm.output), 2)
            self.assertIn("WARNING:Server 1.0.0.2 Aquire", cm.output[0])
            self.assertIn("WARNING:Server 1.0.0.2 Aquire", cm.output[1])

        self.assertTrue(thread_obj.get_aquired())
        self.assertTrue(thread_obj.get_released())

        self.assertTrue(q_obj.get_bucket().result)
        self.assertEqual(q_obj.get_bucket().scrape_data, Bucket_data)

        self.assertTrue('1.0.0.2_ups-one' in Device_State_Cache)
        Test_Data = Device_State_Cache['1.0.0.2_ups-one']
        self.assertEqual(Test_Data, {'ups.status': 'OL',
                                     'battery.charge': None,
                                     'battery.runtime': None,
                                     'server_address': '1.0.0.2',
                                     'last_rep_ch': None,
                                     'last_rep_rt': None,
                                     'device': 'ups-one',
                                     'starting': False}
                                     )

# =================================================================================================
# Test_Check_Device_Clients
# =================================================================================================
class Test_Check_Device_Clients(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config["SERVERS"] = [{"server": "1.2.3.4", "devices":
            [{"device": "ups-one", "clients": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]}]
            }]

    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Check_Device_Clients
    def test_Check_Device_Clients_all_present(self):
        Device_Data = {
            "server_address": "1.2.3.4",
            "name": "ups-dev",
            "clients": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
        }
        Expected_Clients = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Check_Device_Clients(Expected_Clients, Device_Data)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 0)

    def test_Check_Device_Clients_one_missing(self):
        Device_Data = {
            "server_address": "1.2.3.4",
            "name": "ups-dev",
            "clients": ["10.0.0.1", "10.0.0.2"],
        }
        Expected_Clients = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Check_Device_Clients(Expected_Clients, Device_Data)
        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 1)
            self.assertEqual(db_entries[0].title, "Missing client")
            self.assertEqual(db_entries[0].detail, "Device ups-dev on server 1.2.3.4 is "
                             "missing client 10.0.0.3")
            self.assertEqual(db_entries[0].server, "1.2.3.4")
            self.assertEqual(db_entries[0].device, "ups-dev")
            self.assertEqual(db_entries[0].category, "Other")
            self.assertEqual(db_entries[0].level, Log_Level.alert.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

    def test_Check_Device_Clients_two_missing(self):
        Device_Data = {
            "server_address": "1.2.3.4",
            "name": "ups-dev",
            "clients": ["10.0.0.1"],
        }
        Expected_Clients = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Check_Device_Clients(Expected_Clients, Device_Data)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 2)

            self.assertEqual(db_entries[1].title, "Missing client")
            self.assertEqual(db_entries[1].detail, "Device ups-dev on server 1.2.3.4 is "
                             "missing client 10.0.0.3")
            self.assertEqual(db_entries[1].server, "1.2.3.4")
            self.assertEqual(db_entries[1].device, "ups-dev")
            self.assertEqual(db_entries[1].category, "Other")
            self.assertEqual(db_entries[1].level, Log_Level.alert.value)
            self.assertEqual(db_entries[1].read, False)
            self.assertEqual(db_entries[1].occurrences, 1)
            self.assertTrue(isinstance(db_entries[1].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[1].time_latest, datetime.datetime))

            self.assertEqual(db_entries[0].title, "Missing client")
            self.assertEqual(db_entries[0].detail, "Device ups-dev on server 1.2.3.4 is "
                             "missing client 10.0.0.2")
            self.assertEqual(db_entries[0].server, "1.2.3.4")
            self.assertEqual(db_entries[0].device, "ups-dev")
            self.assertEqual(db_entries[0].category, "Other")
            self.assertEqual(db_entries[0].level, Log_Level.alert.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

    def test_Check_Device_Clients_all_missing(self):
        Device_Data = {
            "server_address": "1.2.3.4",
            "name": "ups-dev",
            "clients": [],
        }
        Expected_Clients = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Check_Device_Clients(Expected_Clients, Device_Data)

        with self.app.app_context():
            db_entries = LogEntry.query.all()
            self.assertEqual(len(db_entries), 3)

            self.assertEqual(db_entries[2].title, "Missing client")
            self.assertEqual(db_entries[2].detail, "Device ups-dev on server 1.2.3.4 is "
                             "missing client 10.0.0.3")
            self.assertEqual(db_entries[2].server, "1.2.3.4")
            self.assertEqual(db_entries[2].device, "ups-dev")
            self.assertEqual(db_entries[2].category, "Other")
            self.assertEqual(db_entries[2].level, Log_Level.alert.value)
            self.assertEqual(db_entries[2].read, False)
            self.assertEqual(db_entries[2].occurrences, 1)
            self.assertTrue(isinstance(db_entries[2].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[2].time_latest, datetime.datetime))

            self.assertEqual(db_entries[1].title, "Missing client")
            self.assertEqual(db_entries[1].detail, "Device ups-dev on server 1.2.3.4 is "
                             "missing client 10.0.0.2")
            self.assertEqual(db_entries[1].server, "1.2.3.4")
            self.assertEqual(db_entries[1].device, "ups-dev")
            self.assertEqual(db_entries[1].category, "Other")
            self.assertEqual(db_entries[1].level, Log_Level.alert.value)
            self.assertEqual(db_entries[1].read, False)
            self.assertEqual(db_entries[1].occurrences, 1)
            self.assertTrue(isinstance(db_entries[1].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[1].time_latest, datetime.datetime))

            self.assertEqual(db_entries[0].title, "Missing client")
            self.assertEqual(db_entries[0].detail, "Device ups-dev on server 1.2.3.4 is "
                             "missing client 10.0.0.1")
            self.assertEqual(db_entries[0].server, "1.2.3.4")
            self.assertEqual(db_entries[0].device, "ups-dev")
            self.assertEqual(db_entries[0].category, "Other")
            self.assertEqual(db_entries[0].level, Log_Level.alert.value)
            self.assertEqual(db_entries[0].read, False)
            self.assertEqual(db_entries[0].occurrences, 1)
            self.assertTrue(isinstance(db_entries[0].time_first, datetime.datetime))
            self.assertTrue(isinstance(db_entries[0].time_latest, datetime.datetime))

# =================================================================================================
# Test_Check_Charge
# =================================================================================================
class Test_Check_Charge(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Check_Charge
    def test_Check_Charge_1(self):
        Device_Data = {
            "server_address": "1.2.3.4",
            "name": "ups-dev",
            "variables": [{"name": "battery.charge", "value": "100"},
                          {"name": "battery.runtime", "value": "1310"}
                          ],
        }

        for ch in range(100, 0, -1):
            Device_Data["variables"][0]["value"] = str(ch)
            Check_Device_Parameters(Device_Data)

        for ch in range(0, 101, 1):
            Device_Data["variables"][0]["value"] = str(ch)
            Check_Device_Parameters(Device_Data)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 38)

        Check_Logs = [
            {'level': Log_Level.warning.value, 'charge': 95},
            {'level': Log_Level.warning.value, 'charge': 90},
            {'level': Log_Level.warning.value, 'charge': 85},
            {'level': Log_Level.warning.value, 'charge': 80},
            {'level': Log_Level.warning.value, 'charge': 75},
            {'level': Log_Level.warning.value, 'charge': 70},
            {'level': Log_Level.warning.value, 'charge': 65},
            {'level': Log_Level.warning.value, 'charge': 60},
            {'level': Log_Level.warning.value, 'charge': 55},
            {'level': Log_Level.warning.value, 'charge': 50},
            {'level': Log_Level.warning.value, 'charge': 45},
            {'level': Log_Level.warning.value, 'charge': 40},
            {'level': Log_Level.warning.value, 'charge': 35},
            {'level': Log_Level.warning.value, 'charge': 30},
            {'level': Log_Level.warning.value, 'charge': 25},
            {'level': Log_Level.warning.value, 'charge': 20},
            {'level': Log_Level.warning.value, 'charge': 15},
            {'level': Log_Level.warning.value, 'charge': 10},
            {'level': Log_Level.warning.value, 'charge':  5},

            {'level': Log_Level.info.value, 'charge': 10},
            {'level': Log_Level.info.value, 'charge': 15},
            {'level': Log_Level.info.value, 'charge': 20},
            {'level': Log_Level.info.value, 'charge': 25},
            {'level': Log_Level.info.value, 'charge': 30},
            {'level': Log_Level.info.value, 'charge': 35},
            {'level': Log_Level.info.value, 'charge': 40},
            {'level': Log_Level.info.value, 'charge': 45},
            {'level': Log_Level.info.value, 'charge': 50},
            {'level': Log_Level.info.value, 'charge': 55},
            {'level': Log_Level.info.value, 'charge': 60},
            {'level': Log_Level.info.value, 'charge': 65},
            {'level': Log_Level.info.value, 'charge': 70},
            {'level': Log_Level.info.value, 'charge': 75},
            {'level': Log_Level.info.value, 'charge': 80},
            {'level': Log_Level.info.value, 'charge': 85},
            {'level': Log_Level.info.value, 'charge': 90},
            {'level': Log_Level.info.value, 'charge': 95},
            {'level': Log_Level.info.value, 'charge': 100},
            ]
        for cl_index in range(len(Check_Logs)):
            self.assertEqual(db_entries[cl_index].title, "Battery charge")
            self.assertEqual(db_entries[cl_index].level, Check_Logs[cl_index]['level'])
            Ch_Check = "Server 1.2.3.4, device ups-dev charge {}%".format(
                                                Check_Logs[cl_index]['charge'])
            self.assertEqual(db_entries[cl_index].detail, Ch_Check)

# =================================================================================================
# Test_Check_Runtime
# =================================================================================================
class Test_Check_Runtime(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Check_Charge
    def test_Check_Runtime_1(self):
        Device_Data = {
            "server_address": "1.2.3.4",
            "name": "ups-dev",
            "variables": [{"name": "battery.runtime", "value": "1310"},
                          {"name": "battery.charge", "value": "98"},],
        }

        for rt in range(1310, 0, -120):
            Device_Data["variables"][0]["value"] = str(rt)
            Check_Device_Parameters(Device_Data)

        for rt in range(0, 1310, 120):
            Device_Data["variables"][0]["value"] = str(rt)
            Check_Device_Parameters(Device_Data)

        db_entries = LogEntry.query.all()
        self.assertEqual(len(db_entries), 19)

        Check_Logs = [
            {'level': Log_Level.warning.value, 'runtime': 1190},
            {'level': Log_Level.warning.value, 'runtime': 1070},
            {'level': Log_Level.warning.value, 'runtime': 950},
            {'level': Log_Level.warning.value, 'runtime': 830},
            {'level': Log_Level.warning.value, 'runtime': 710},
            {'level': Log_Level.warning.value, 'runtime': 590},
            {'level': Log_Level.warning.value, 'runtime': 470},
            {'level': Log_Level.warning.value, 'runtime': 350},
            {'level': Log_Level.warning.value, 'runtime': 230},
            {'level': Log_Level.warning.value, 'runtime': 110},
            {'level': Log_Level.info.value, 'runtime': 240},
            {'level': Log_Level.info.value, 'runtime': 360},
            {'level': Log_Level.info.value, 'runtime': 480},
            {'level': Log_Level.info.value, 'runtime': 600},
            {'level': Log_Level.info.value, 'runtime': 720},
            {'level': Log_Level.info.value, 'runtime': 840},
            {'level': Log_Level.info.value, 'runtime': 960},
            {'level': Log_Level.info.value, 'runtime': 1080},
            {'level': Log_Level.info.value, 'runtime': 1200},
            ]
        for cl_index in range(len(Check_Logs)):
            self.assertEqual(db_entries[cl_index].title, "Battery runtime")
            self.assertEqual(db_entries[cl_index].level, Check_Logs[cl_index]['level'])
            Ch_Check = "Server 1.2.3.4, device ups-dev runtime {}s".format(
                                                Check_Logs[cl_index]['runtime'])
            self.assertEqual(db_entries[cl_index].detail, Ch_Check)

# =================================================================================================
# Entry point
# =================================================================================================
if __name__ == '__main__':
    unittest.main()  # pragma: no cover
