import re
import unittest
import flask

from app.utils.app_log_config import Add_Logging_Levels
from app.events.log_utils import Get_Events, Make_Pagination

from app import db
from app.models import LogEntry, Log_Level, Log_Category

# ===================================================================================
BASE_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///:memory:',
    "SECRET_KEY": "secret",
    'TESTING': True,
    }

Base_Logs = [
['A title1', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title2', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title3', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title4', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title5', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title6', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Comms.value],
['A title7', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Comms.value],
['A title8', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Comms.value],
['A title9', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Comms.value],
['A title10', 'A detail', Log_Level.info.value, "1.0.0.1", "ups", Log_Category.Comms.value],
['A title11', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Power.value],
['A title12', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Power.value],
['A title13', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Power.value],
['A title14', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Power.value],
['A title15', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Power.value],
['A title16', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Other.value],
['A title17', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Other.value],
['A title18', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Other.value],
['A title19', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Other.value],
['A title20', 'A detail', Log_Level.info.value, "1.0.0.2", "ups", Log_Category.Other.value],
['A title21', 'A detail', Log_Level.info.value, "1.0.0.3", "ups", Log_Category.Battery.value],
['A title22', 'A detail', Log_Level.info.value, "1.0.0.3", "ups", Log_Category.Battery.value],
['A title23', 'A detail', Log_Level.info.value, "1.0.0.3", "ups", Log_Category.Battery.value],
['A title24', 'A detail', Log_Level.info.value, "1.0.0.3", "ups", Log_Category.Battery.value],
['A title25', 'A detail', Log_Level.info.value, "1.0.0.3", "ups", Log_Category.Battery.value],

['A title1', 'A detail', Log_Level.warning.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title2', 'A detail', Log_Level.warning.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title3', 'A detail', Log_Level.warning.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title4', 'A detail', Log_Level.warning.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title5', 'A detail', Log_Level.warning.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title6', 'A detail', Log_Level.warning.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title7', 'A detail', Log_Level.warning.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title8', 'A detail', Log_Level.warning.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title9', 'A detail', Log_Level.warning.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title10', 'A detail', Log_Level.warning.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title11', 'A detail', Log_Level.warning.value, "1.0.0.3", "ups", Log_Category.Power.value],
['A title12', 'A detail', Log_Level.warning.value, "1.0.0.3", "ups", Log_Category.Power.value],
['A title13', 'A detail', Log_Level.warning.value, "1.0.0.3", "ups", Log_Category.Power.value],
['A title14', 'A detail', Log_Level.warning.value, "1.0.0.3", "ups", Log_Category.Power.value],
['A title15', 'A detail', Log_Level.warning.value, "1.0.0.3", "ups", Log_Category.Power.value],

['A title1', 'A detail', Log_Level.alert.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title2', 'A detail', Log_Level.alert.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title3', 'A detail', Log_Level.alert.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title4', 'A detail', Log_Level.alert.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title5', 'A detail', Log_Level.alert.value, "1.0.0.1", "ups", Log_Category.Battery.value],
['A title6', 'A detail', Log_Level.alert.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title7', 'A detail', Log_Level.alert.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title8', 'A detail', Log_Level.alert.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title9', 'A detail', Log_Level.alert.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title10', 'A detail', Log_Level.alert.value, "1.0.0.2", "ups", Log_Category.Comms.value],
['A title11', 'A detail', Log_Level.alert.value, "1.0.0.3", "ups", Log_Category.Power.value],
]

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
#         # app.logger.setLevel("CRITICAL")
#         # app.logger.setLevel("WARNING")
        app.logger.setLevel("DEBUG")

        self.app.app_context().push()
        db.init_app(app)
        db.create_all()

        for bl in Base_Logs:
            db.session.add(LogEntry(
                    title=bl[0], detail=bl[1], level=bl[2],
                    server=bl[3], device=bl[4], category=bl[5]))

        db.session.commit()
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        db.session.close()
        db.drop_all()
        super().tearDown()

# =================================================================================================
# Test_log_utils_get_events
# =================================================================================================
class Test_log_utils_get_events(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        pass
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        pass
        super().tearDown()

    # ===================================================================================
    # Test the DB config
    def test_db_config(self):
        Entries = LogEntry.query.all()
        self.assertEqual(len(Entries), 51)

    # Test filter on level
    def test_filter_events_level(self):
        Events = Get_Events(Log_Level.alert, None)
        self.assertEqual(len(Events), 11)
        Events = Get_Events(Log_Level.warning, None)
        self.assertEqual(len(Events), 26)
        Events = Get_Events(Log_Level.info, None)
        self.assertEqual(len(Events), 51)

    # ===================================================================================
    # Test filter on category
    def test_filter_events_category(self):
        Events = Get_Events(Log_Level.info, Log_Category.Battery)
        self.assertEqual(len(Events), 20)
        Events = Get_Events(Log_Level.info, Log_Category.Comms)
        self.assertEqual(len(Events), 15)
        Events = Get_Events(Log_Level.info, Log_Category.Power)
        self.assertEqual(len(Events), 11)
        Events = Get_Events(Log_Level.warning, Log_Category.Power)
        self.assertEqual(len(Events), 6)
        Events = Get_Events(Log_Level.alert, Log_Category.Power)
        self.assertEqual(len(Events), 1)

Left_Disabled  = ['page-item disabled', 'tabindex="-1"', '>&laquo;</a>']
Left_Enabled   = ['page-item"',                          '>&laquo;</a>', 'href="./log?page={page}"']
Right_Disabled = ['page-item disabled', 'tabindex="-1"', '>&raquo;</a>']
Right_Enabled  = ['page-item"',                          '>&raquo;</a>', 'href="./log?page={page}"']
Mid_Disabled   = ['page-item disabled', 'tabindex="-1"', '>{page}</a>']
Mid_Enabled    = ['page-item"',                          '>{page}</a>', 'href="./log?page={page}"']

Pages_Test = [
    {"ne": 10, "lpp": 10, "cp": 1, "lpp_out": 10, "cp_out": 1},  # 10 lines, one page
    {"ne":  0, "lpp": 10, "cp": 1, "lpp_out": 10, "cp_out": 1},  # 0 lines
    {"ne":  0, "lpp": 10, "cp": 2, "lpp_out": 10, "cp_out": 1},  # Try p2 with 1 page, get p1
    {"ne": 11, "lpp": 10, "cp": 1, "lpp_out": 10, "cp_out": 1},  # 2p, get p1
    {"ne": 11, "lpp": 10, "cp": 2, "lpp_out": 10, "cp_out": 2},  # 2p, get p2
    {"ne": 20, "lpp": 10, "cp": 3, "lpp_out": 10, "cp_out": 2},  # 2p, try p3, get p2
    {"ne": 21, "lpp": 10, "cp": 3, "lpp_out": 10, "cp_out": 3},  # 3p, get p3
    {"ne": 26, "lpp": 25, "cp": 1, "lpp_out": 25, "cp_out": 1},  # 25lpp, p1
    {"ne": 26, "lpp": 25, "cp": 2, "lpp_out": 25, "cp_out": 2},  # p2
    {"ne": 26, "lpp": 25, "cp": 3, "lpp_out": 25, "cp_out": 2},  # p3
    {"ne": 100, "lpp": 10, "cp": 1, "lpp_out": 10, "cp_out": 1},  # p1 < 1 2 3 4 5 >
    {"ne": 100, "lpp": 10, "cp": 2, "lpp_out": 10, "cp_out": 2},  # p2 < 1 2 3 4 5 >
    {"ne": 100, "lpp": 10, "cp": 3, "lpp_out": 10, "cp_out": 3},  # p3 < 1 2 3 4 5 >
    {"ne": 100, "lpp": 10, "cp": 4, "lpp_out": 10, "cp_out": 4},  # p4 < 2 3 4 5 6 >
    {"ne": 100, "lpp": 10, "cp": 5, "lpp_out": 10, "cp_out": 5},  # p5 < 3 4 5 6 7 >
    {"ne": 100, "lpp": 10, "cp": 6, "lpp_out": 10, "cp_out": 6},  # p6 < 4 5 6 7 8 >
    {"ne": 100, "lpp": 10, "cp": 7, "lpp_out": 10, "cp_out": 7},  # p7 < 5 6 7 8 9 >
    {"ne": 100, "lpp": 10, "cp": 8, "lpp_out": 10, "cp_out": 8},  # p8 < 6 7 8 9 10 >
    {"ne": 100, "lpp": 10, "cp": 9, "lpp_out": 10, "cp_out": 9},  # p9 < 6 7 8 9 10 >
    {"ne": 100, "lpp": 10, "cp": 10, "lpp_out": 10, "cp_out": 10},  # p10 < 6 7 8 9 10 >
    ]

Find_Sets = [
    [Left_Disabled, Mid_Disabled, Right_Disabled],
    [Left_Disabled, Mid_Disabled, Right_Disabled],
    [Left_Disabled, Mid_Disabled, Right_Disabled],
    [Left_Disabled, Mid_Disabled, Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Disabled, Right_Disabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Disabled, Right_Disabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Right_Disabled],
    [Left_Disabled, Mid_Disabled, Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Disabled, Right_Disabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Disabled, Right_Disabled],
    [Left_Disabled, Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Mid_Enabled,  Right_Enabled],
    [Left_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Enabled,  Mid_Disabled, Right_Disabled],
]

Find_Sets_Pages = [
    [None, 1, None],
    [None, 1, None],
    [None, 1, None],
    [None, 1, 2, 2],
    [   1, 1, 2, 2],
    [   1, 1, 2, 2],
    [   2, 1, 2, 3, None],
    [None, 1, 2, 2],
    [   1, 1, 2, None],
    [   1, 1, 2, None],
    [   1, 1, 2, 3, 4, 5, 2],
    [   1, 1, 2, 3, 4, 5, 3],
    [   2, 1, 2, 3, 4, 5, 4],
    [   3, 2, 3, 4, 5, 6, 5],
    [   4, 3, 4, 5, 6, 7, 6],
    [   5, 4, 5, 6, 7, 8, 7],
    [   6, 5, 6, 7, 8, 9, 8],
    [   7, 6, 7, 8, 9, 10, 9],
    [   8, 6, 7, 8, 9, 10, 10],
    [   9, 6, 7, 8, 9, 10, 10],
]

def Find_Multiple(Input, Search, Search_Page):
    Result = True
    for s in Search:
        s_page = s.format(page=Search_Page)
        if s_page not in Input:
            Result = False  # pragma: no cover
    return Result

def Search_Sets(Search_Matches, Find_Set, Find_Set_Pages):
    for fs in range(len(Find_Set)):
        if not Find_Multiple(Search_Matches[fs], Find_Set[fs], Find_Set_Pages[fs]):
            return False  # pragma: no cover
    return True

# =================================================================================================
# Test_log_utils_make_pagination
# =================================================================================================
class Test_log_utils_make_pagination(BaseTestCase):
    # ===================================================================================
    def setUp(self):
        pass
        super().setUp()

    # ===================================================================================
    def tearDown(self):
        pass
        super().tearDown()

    # ===================================================================================
    # Test the DB config
    def test_pages(self):
        HTML_Search = re.compile(r"<li .*?</li>")

        for Test_Index in range(len(Pages_Test)):
            Pagination_Block, Lines_PP, Current_Page = Make_Pagination(
                                                        Pages_Test[Test_Index]['ne'],
                                                        Pages_Test[Test_Index]['lpp'],
                                                        Pages_Test[Test_Index]['cp'])
            self.assertEqual(Lines_PP, Pages_Test[Test_Index]['lpp_out'])
            self.assertEqual(Current_Page, Pages_Test[Test_Index]['cp_out'])

            Matches = re.findall(HTML_Search, Pagination_Block)

            self.assertNotEqual(len(Matches), 0)
            Result = Search_Sets(Matches, Find_Sets[Test_Index], Find_Sets_Pages[Test_Index])
            self.assertTrue(Result)

# =================================================================================================
# Entry point
# =================================================================================================
if __name__ == '__main__':
    unittest.main()  # pragma: no cover
