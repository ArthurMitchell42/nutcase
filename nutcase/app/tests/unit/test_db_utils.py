import unittest
import flask
from app.utils.app_log_config import Add_Logging_Levels
from app.utils.db_utils import Scan_DB, Scan_DB_For_Device, Scan_DB_For_Server, Clean_Old_Logs

from app import db
from app.models import LogEntry, Log_Level
from datetime import datetime, timezone, timedelta

BASE_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///:memory:',
    "SECRET_KEY": "secret",
    "TESTING": True,
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
# Test_scan_db
# =================================================================================================
class Test_scan_db(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()
        test_info_1 = LogEntry(title='A title i1', detail='A detail', level=Log_Level.info.value)
        test_warn_1 = LogEntry(title='A title w1', detail='A detail', level=Log_Level.warning.value)
        test_warn_2 = LogEntry(title='A title w2', detail='A detail', level=Log_Level.warning.value)
        test_alert_1 = LogEntry(title='A title a1', detail='A detail', level=Log_Level.alert.value)
        test_alert_2 = LogEntry(title='A title a2', detail='A detail', level=Log_Level.alert.value)
        test_alert_3 = LogEntry(title='A title a3', detail='A detail', level=Log_Level.alert.value)
        self.app.config["APP_STATUS_FLAGS"]['info'] = 0
        self.app.config["APP_STATUS_FLAGS"]['warning'] = 0
        self.app.config["APP_STATUS_FLAGS"]['alert'] = 0

        db.session.add(test_info_1)
        db.session.add(test_warn_1)
        db.session.add(test_warn_2)
        db.session.add(test_alert_1)
        db.session.add(test_alert_2)
        db.session.add(test_alert_3)
        db.session.commit()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Test scanning the database to count events
    def test_scan_db(self):

        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['info'], 0)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['warning'], 0)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['alert'], 0)

        Scan_DB(self.app)
        Log_Entries = LogEntry.query.all()
        self.assertEqual(len(Log_Entries), 6)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['info'], 1)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['warning'], 2)
        self.assertEqual(self.app.config["APP_STATUS_FLAGS"]['alert'], 3)

# =================================================================================================
# Test_scan_db_for (server and device)
# =================================================================================================
class Test_scan_db_for(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()
        self.Server = "10.0.0.1"
        self.Device = "ups-dev"

        Entry_List = [
        # Server
        {"title": 'i1', "detail": 'D', "level": 1, "server": self.Server, "device": "", "read": True},
        {"title": 'i2', "detail": 'D', "level": 1, "server": self.Server, "device": "", "read": True},
        {"title": 'i3', "detail": 'D', "level": 1, "server": self.Server, "device": "", "read": True},
        {"title": 'i4', "detail": 'D', "level": 1, "server": self.Server, "device": "", "read": False},

        {"title": 'w1', "detail": 'D', "level": 2, "server": self.Server, "device": "", "read": True},
        {"title": 'w2', "detail": 'D', "level": 2, "server": self.Server, "device": "", "read": True},
        {"title": 'w3', "detail": 'D', "level": 2, "server": self.Server, "device": "", "read": True},
        {"title": 'w4', "detail": 'D', "level": 2, "server": self.Server, "device": "", "read": False},
        {"title": 'w5', "detail": 'D', "level": 2, "server": self.Server, "device": "", "read": False},

        {"title": 'a1', "detail": 'D', "level": 3, "server": self.Server, "device": "", "read": True},
        {"title": 'a2', "detail": 'D', "level": 3, "server": self.Server, "device": "", "read": True},
        {"title": 'a3', "detail": 'D', "level": 3, "server": self.Server, "device": "", "read": True},
        {"title": 'a4', "detail": 'D', "level": 3, "server": self.Server, "device": "", "read": False},
        {"title": 'a5', "detail": 'D', "level": 3, "server": self.Server, "device": "", "read": False},
        {"title": 'a6', "detail": 'D', "level": 3, "server": self.Server, "device": "", "read": False},
        # Device
        {"title": 'i1', "detail": 'D', "level": 1, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'i2', "detail": 'D', "level": 1, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'i3', "detail": 'D', "level": 1, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'i4', "detail": 'D', "level": 1, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'i5', "detail": 'D', "level": 1, "server": self.Server, "device": self.Device, "read": False},
        {"title": 'i6', "detail": 'D', "level": 1, "server": self.Server, "device": self.Device, "read": False},

        {"title": 'w1', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'w2', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'w3', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'w4', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'w5', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": False},
        {"title": 'w6', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": False},
        {"title": 'w7', "detail": 'D', "level": 2, "server": self.Server, "device": self.Device, "read": False},

        {"title": 'a1', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'a2', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'a3', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'a4', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": True},
        {"title": 'a5', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": False},
        {"title": 'a6', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": False},
        {"title": 'a7', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": False},
        {"title": 'a8', "detail": 'D', "level": 3, "server": self.Server, "device": self.Device, "read": False},
        # Interference
        {"title": 'int1', "detail": 'D', "level": 1, "server": "10.0.0.2", "device": "", "read": False},
        {"title": 'int2', "detail": 'D', "level": 1, "server": "10.0.0.2", "device": "", "read": True},
        {"title": 'int3', "detail": 'D', "level": 1, "server": self.Server, "device": "int_dev", "read": False},
        {"title": 'int4', "detail": 'D', "level": 1, "server": self.Server, "device": "int_dev", "read": True},
        ]

        for e in Entry_List:
            db.session.add(LogEntry(**e))
        db.session.commit()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Test scanning the database to count events
    def test_scan_db_for_server(self):
        Log_Values = Scan_DB_For_Server(self.Server)
        self.assertEqual(Log_Values["info"], 4)
        self.assertEqual(Log_Values["warning"], 5)
        self.assertEqual(Log_Values["alert"], 6)
        self.assertEqual(Log_Values["info_unread"], 1)
        self.assertEqual(Log_Values["warning_unread"], 2)
        self.assertEqual(Log_Values["alert_unread"], 3)

    # ===================================================================================
    # Test scanning the database to count events
    def test_scan_db_for_device(self):
        Log_Values = Scan_DB_For_Device(self.Server, self.Device)
        self.assertEqual(Log_Values["info"], 6)
        self.assertEqual(Log_Values["warning"], 7)
        self.assertEqual(Log_Values["alert"], 8)
        self.assertEqual(Log_Values["info_unread"], 2)
        self.assertEqual(Log_Values["warning_unread"], 3)
        self.assertEqual(Log_Values["alert_unread"], 4)

# =================================================================================================
# Test_clean_old_logs
# =================================================================================================
class Test_clean_old_logs(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        super().setUp()
        Entry_List = [
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=30)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=29)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=25)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=20)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=15)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=10)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=5)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=4)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=3)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=2)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=1)},
        {"title": 'i1', "detail": 'D', "level": 1, "time_latest": datetime.now(timezone.utc) - timedelta(days=0)},
        ]

        for e in Entry_List:
            db.session.add(LogEntry(**e))
        db.session.commit()

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

    # ===================================================================================
    # Test scanning the database to count events
    def test_clean_old_logs1(self):
        Log_Entries = LogEntry.query.all()
        self.assertEqual(len(Log_Entries), 12)

        Test_Data = [
            {"Retention_Days": 31, "Logs_Count": 12},
            {"Retention_Days": 30, "Logs_Count": 12},
            {"Retention_Days": 29, "Logs_Count": 11},
            {"Retention_Days": 28, "Logs_Count": 10},
            {"Retention_Days": 26, "Logs_Count": 10},
            {"Retention_Days": 25, "Logs_Count": 10},
            {"Retention_Days": 21, "Logs_Count":  9},
            {"Retention_Days": 20, "Logs_Count":  9},
            {"Retention_Days": 15, "Logs_Count":  8},
            {"Retention_Days": 14, "Logs_Count":  7},
            {"Retention_Days": 11, "Logs_Count":  7},
            {"Retention_Days": 10, "Logs_Count":  7},
            {"Retention_Days":  9, "Logs_Count":  6},
            {"Retention_Days":  6, "Logs_Count":  6},
            {"Retention_Days":  5, "Logs_Count":  6},
            {"Retention_Days":  4, "Logs_Count":  5},
            {"Retention_Days":  3, "Logs_Count":  4},
            {"Retention_Days":  2, "Logs_Count":  3},
            {"Retention_Days":  1, "Logs_Count":  2},
            {"Retention_Days":  0, "Logs_Count":  1},
        ]
        for test in Test_Data:
            Clean_Old_Logs(test['Retention_Days'])
            Log_Entries = LogEntry.query.all()
            self.assertEqual(len(Log_Entries), test['Logs_Count'])

# =================================================================================================
# Entry point
# =================================================================================================
if __name__ == '__main__':
    unittest.main()  # pragma: no cover
