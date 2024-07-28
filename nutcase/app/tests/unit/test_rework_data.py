import unittest
import flask
import logging

from app.utils.rework_data import Rework_Variables
from app.utils.app_log_config import Add_Logging_Levels

BASE_CONFIG = {
    "REWORK_VAR_LIST": [],
    "REWORK":          [],
    "SERVERS":         [],

    "SECRET_KEY": "secrets",
    "WTF_CSRF_ENABLED": False,
}

# =================================================================================================
# Base scrape data
# =================================================================================================
Base_Scrape_Data = {
    'nutcase_version': 'NUTCase 0.3.0 Beta 7',
    'server_version': 'DSM7-1-1-42930-workplus-version2-repack-42930-220712',
    'server_address': '10.0.0.1',
    'server_port': 3493,
    'mode': 'nut',
    'ups_list': [
        {
        'name': 'ups',
        'description': 'Description unavailable',
        'variables': [],
        'clients': [],
        'server_address': '10.0.0.1',
        'server_port': 3493
        }
    ],
    'debug': []
}

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = flask.Flask(__name__)
        app.config.update(BASE_CONFIG)
        self.app = app
        Add_Logging_Levels()

class Test_rework_data_basics(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    # scrape data
    def test_rework_data_none(self):
        Scrape_Data = None

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)

    def test_rework_data_empty(self):
        Scrape_Data = {}

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)

    # scrape data -> ups list
    def test_rework_data_ups_list_none(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'] = None

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)

    def test_rework_data_ups_list_empty(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'] = {}

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)

    # scrape data -> ups list -> variables
    def test_rework_data_variable_list_empty(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = []

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)

    def test_rework_data_invalid_style(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        self.app.config.update(
            {"REWORK_VAR_LIST": "ups.status"}
        )
        Rework_Config = [{
            "from": "ups.status",
            "to": "nutcase.ups.status.nothing",
            "style": "invalid",
            "control": "ups.status"
            }]
        self.app.config['REWORK'] = Rework_Config
        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 1)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.status")

class Test_rework_simple_enum(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config.update(
            {"REWORK_VAR_LIST": "ups.status"}
        )
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    # scrape data -> ups list -> variable not present
    def test_scrape_rework_simple_enum_variable_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = []

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 0)

    # scrape data -> ups list -> variable present
    # no rework instructions
    def test_scrape_rework_simple_enum_no_command(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 1)

    # with rework instruction
    def test_scrape_rework_simple_enum_with_command(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]

        Rework_Config = {
            "from": "ups.status",
            "to": "nutcase.ups.status",
            "style": "simple-enum",
            "control": {
                "from": ["OL"],
                "to": ["On-Line"],
                "default": "Other"
            }
        }

        self.app.config['REWORK'] = [Rework_Config]
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.status")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["value"], "OL")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"], "nutcase.ups.status")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "On-Line")

    # with rework to default
    def test_scrape_rework_simple_enum_to_default(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OB'}]

        Rework_Config = [{
            "from": "ups.status",
            "to": "nutcase.ups.status",
            "style": "simple-enum",
            "control": {
                "from": ["OL"],
                "to": ["On-Line"],
                "default": "Other"
            }
        }]
        self.app.config['REWORK'] = Rework_Config
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.status")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["value"], "OB")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"], "nutcase.ups.status")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Other")

class Test_rework_time(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config["REWORK_VAR_LIST"] = "battery.runtime"
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    def test_scrape_rework_battery_runtime_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = []

        self.app.config['REWORK'] = [
        {
            "from": "battery.runtime",
            "to": "nutcase.battery.runtime",
            "style": "time",
            "control": "%Hh %Mm %Ss"
        }
        ]
        Rtn = Rework_Variables(Scrape_Data)

        self.assertFalse(Rtn)

    def test_scrape_rework_battery_runtime_present(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'battery.runtime', 'value': '4970'}]

        self.app.config['REWORK'] = [
        {
            "from": "battery.runtime",
            "to": "nutcase.battery.runtime",
            "style": "time",
            "control": "%Hh %Mm %Ss"
        }
        ]
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                         "nutcase.battery.runtime")
        self.assertEqual("01h 22m 50s", Scrape_Data['ups_list'][0]['variables'][1]["value"])

class Test_rework_comp_enum(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config.update(
            {"REWORK_VAR_LIST": "ups.status"}
        )
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    def test_scrape_rework_comp_enum_variable_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = []

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 0)

    # no rework instructions
    def test_scrape_rework_comp_enum_no_command(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL CHRG'}]

        Rtn = Rework_Variables(Scrape_Data)
        self.assertFalse(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 1)

    # with rework instruction
    def test_scrape_rework_comp_enum_with_command(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL CHRG'}]

        Rework_Config = \
        {
            "from": "ups.status",
            "to": "nutcase.ups.status.comp",
            "style": "comp-enum",
            "control": {
                "from": ["OL", "OB", "CHRG"],
                "to": ["On-Line", "On-Bat", "Charge"],
                "default": "Other",
                "join": "+"
            }
        }

        self.app.config['REWORK'] = [Rework_Config]
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.status")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["value"], "OL CHRG")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"], "nutcase.ups.status.comp")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "On-Line+Charge")

    # with rework to default
    def test_scrape_rework_comp_enum_to_default(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'LB'}]

        Rework_Config = [
        {
            "from": "ups.status",
            "to": "nutcase.ups.status.comp",
            "style": "comp-enum",
            "control": {
                "from": ["OL", "OB", "CHRG"],
                "to": ["On-Line", "On-Bat", "Charge"],
                "default": "Other"
            }
        }
        ]
        self.app.config['REWORK'] = Rework_Config
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.status")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][0]["value"], "LB")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"], "nutcase.ups.status.comp")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Other")

class Test_rework_ratio(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config.update(
            {"REWORK_VAR_LIST": "ups.load",
             "SERVERS": [
                {"server": "10.0.0.1", "devices": [{"device": "ups", "power": 200}]}
                ]}
        )
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    def test_scrape_rework_ratio_nom_var(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [
            {'name': 'ups.load', 'value': '50'},
            {'name': 'ups.realpower.nominal', 'value': '200'}
            ]

        Rework_Config = [{
            "from": "ups.load",
            "to": "nutcase.ups.load.watts",
            "style": "ratio",
            "control": "ups.realpower.nominal"
            }]
        self.app.config['REWORK'] = Rework_Config
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 3)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.load")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][0]["value"], "50")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][2]["name"],
                                                            "nutcase.ups.load.watts")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][2]["value"], "100.0")

    # No nominal and no server/device setting
    def test_scrape_rework_ratio_nom_var_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [
            {'name': 'ups.load', 'value': '50'}
            ]
        self.app.config.update(
            {"SERVERS": []}
        )
        Rework_Config = [
        {
            "from": "ups.load",
            "to": "nutcase.ups.load.watts",
            "style": "ratio",
            "control": "ups.realpower.nominal"
            }
        ]
        self.app.config['REWORK'] = Rework_Config
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.load")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][0]["value"], "50")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                                                            "nutcase.ups.load.watts")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["value"], "0.0")

    def test_scrape_rework_ratio_nom_from_server(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [
            {'name': 'ups.load', 'value': '50'}
            ]

        Rework_Config = [
        {
            "from": "ups.load",
            "to": "nutcase.ups.load.watts",
            "style": "ratio",
            "control": ""
            }
        ]
        self.app.config['REWORK'] = Rework_Config
        Rtn = Rework_Variables(Scrape_Data)

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.load")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][0]["value"], "50")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                                                            "nutcase.ups.load.watts")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["value"], "100.0")

    def test_scrape_rework_ratio_nom_from_server_invalid(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [
            {'name': 'ups.load', 'value': '50'}
            ]
        self.app.config.update( {
            "SERVERS": [{
                "server": "10.0.0.1",
                "devices": [{"device": "ups", "power": "x"}]}
            ]
        })

        Rework_Config = [
        {
            "from": "ups.load",
            "to": "nutcase.ups.load.watts",
            "style": "ratio",
            "control": ""
            }
        ]
        self.app.config['REWORK'] = Rework_Config

        with self.assertLogs(logging.getLogger(__name__), level="INFO") as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Rtn = Rework_Variables(Scrape_Data)
            self.assertEqual(cm.output, [
                "ERROR:Can't use power value from server config x"
                ])

        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][0]["name"], "ups.load")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][0]["value"], "50")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                                                        "nutcase.ups.load.watts")
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["value"], "0.0")

class Test_rework_ups_clients(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config.update(
            {"REWORK_VAR_LIST": "ups"}
        )
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    # with rework but no commands
    def test_scrape_rework_ups_no_list(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = []

        self.app.config['REWORK'] = []
        Rtn = Rework_Variables(Scrape_Data)

        self.assertFalse(Rtn)

    # with rework but no commands
    def test_scrape_rework_ups_cl_count_all_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = []

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ["3", 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Missing 3 of 3")

    def test_scrape_rework_ups_cl_count_all_present_string(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ["3", 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Clients OK (3)")

    def test_scrape_rework_ups_cl_count_all_present_int(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": [3, 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Clients OK (3)")

    def test_scrape_rework_ups_cl_count_all_present_invalid_string(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ["INVALID", 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        with self.assertLogs(logging.getLogger(__name__), level="INFO") as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Rtn = Rework_Variables(Scrape_Data)
            self.assertEqual(cm.output, [
                "ERROR:Could not use rework control "
                "{'from': 'ups', 'to': 'nutcase.ups.client-count', 'style': 'cl-count', "
                "'control': ['INVALID', 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']}, "
                "invalid literal for int() with base 10: 'INVALID'",
                ])

        self.assertTrue(Rtn)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Error")

    def test_scrape_rework_ups_cl_count_all_present_invalid_float(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": [1.0, 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        with self.assertLogs(logging.getLogger(__name__), level="INFO") as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Rtn = Rework_Variables(Scrape_Data)
            self.assertEqual(cm.output, [
                "ERROR:Could not use count in rework control "
                "{'from': 'ups', 'to': 'nutcase.ups.client-count', 'style': 'cl-count', "
                "'control': [1.0, 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']}"
                ])

        self.assertTrue(Rtn)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Error")

    def test_scrape_rework_ups_cl_count_all_present_auto(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        self.app.config["SERVERS"] = [{
                    "server": "10.0.0.1",
                    "devices": [{
                        "device": "ups",
                        "clients": ['10.0.10.10', '10.0.10.183', '127.0.0.1']
                    }]}]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ['auto', 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Clients OK (3)")

    def test_scrape_rework_ups_cl_count_one_missing_auto(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2"]
        self.app.config["SERVERS"] = [{
                    "server": "10.0.0.1",
                    "devices": [{
                        "device": "ups",
                        "clients": ['10.0.10.10', '10.0.10.183', '127.0.0.1']
                    }]}]

        Rework_Config = [{
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ['auto', 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Missing 1 of 3")

    def test_scrape_rework_ups_cl_count_none_expected(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ["0", 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "3 Extra")

    def test_scrape_rework_ups_cl_count_one_expected(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-count",
            "style": "cl-count",
            "control": ["2", 'Missing {d} of {c}', 'Clients OK ({c})', '{d} Extra']
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-count")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "1 Extra")

    def test_scrape_rework_ups_cl_check_all_present(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-check")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "All present")

    def test_scrape_rework_ups_cl_check_all_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = []

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                         "nutcase.ups.client-check")
        self.assertIn("Missing 3", Scrape_Data['ups_list'][0]['variables'][1]["value"])

    def test_scrape_rework_ups_cl_check_one_missing(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                         "nutcase.ups.client-check")
        self.assertIn("Missing 1", Scrape_Data['ups_list'][0]['variables'][1]["value"])

    def test_scrape_rework_ups_cl_check_one_extra(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertEqual(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                         "nutcase.ups.client-check")
        self.assertIn("All present", Scrape_Data['ups_list'][0]['variables'][1]["value"])

    def test_scrape_rework_ups_cl_check_not_valid(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [
        {
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": 1.0
        }
        ]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-check")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Error")

    def test_scrape_rework_ups_cl_check_not_auto_string(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

        Rework_Config = [{
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": "not_auto"
        }]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-check")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "Error")

    def test_scrape_rework_ups_cl_check_auto(self):
        Scrape_Data = Base_Scrape_Data.copy()
        Scrape_Data['ups_list'][0]['variables'] = [{'name': 'ups.status', 'value': 'OL'}]
        Scrape_Data['ups_list'][0]['clients'] = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        self.app.config["SERVERS"] = [
                {
                    "server": "10.0.0.1",
                    "devices": [{
                        "device": "ups",
                        "clients": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
                    }
                    ]
                }
            ]

        Rework_Config = [{
            "from": "ups",
            "to": "nutcase.ups.client-check",
            "style": "cl-check",
            "control": "auto"
        }]
        self.app.config['REWORK'] = Rework_Config

        Rtn = Rework_Variables(Scrape_Data)
        self.assertTrue(Rtn)
        self.assertEqual(len(Scrape_Data['ups_list'][0]['variables']), 2)
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["name"],
                      "nutcase.ups.client-check")
        self.assertIn(Scrape_Data['ups_list'][0]['variables'][1]["value"], "All present")

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
