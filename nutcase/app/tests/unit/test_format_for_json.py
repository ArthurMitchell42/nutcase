import unittest
import flask
import copy

from app.utils.format_to_json import Format_For_JSON
from app.utils.app_log_config import Add_Logging_Levels

# =================================================================================================
# Base scrape data
# =================================================================================================
Base_Scrape_Data = {
    'nutcase_version': 'NUTCase 0.3.0 Beta 7',
    'server_version': 'DSM7-1-1-42930-workplus',
    'server_address': '10.0.0.1',
    'server_port': 3493,
    'mode': 'nut',
    'ups_list': [],
    'debug': []
}

BASE_CONFIG = {
    "WEBHOOKS": {},
    }

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = flask.Flask(__name__)
        app.config.update(BASE_CONFIG)
        self.app = app
        Add_Logging_Levels()
        # app.logger.setLevel("CRITICAL")
        # app.logger.setLevel("WARNING")
        app.logger.setLevel("INFO")
        # app.logger.setLevel("DEBUG")

class Test_format_for_json_basics(BaseTestCase):
    def setUp(self):
        super().setUp()
        # self.app.config.update(
        #     {"LDAP_USER_RDN_ATTR": "cn", "LDAP_USER_LOGIN_ATTR": "cn"}
        # )
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    # no input data
    def test_input_none_filter_none(self):
        Scrape_Dict = None
        JSON_Elements = None
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {})

    # empty input data
    def test_input_empty_filter_empty(self):
        Scrape_Dict = {}
        JSON_Elements = []
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {})

    # simple
    def test_simple_no_ups_list(self):
        Scrape_Dict = copy.deepcopy(Base_Scrape_Data)
        JSON_Elements = []
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        self.assertEqual(Output_Dict['nutcase_version'], 'NUTCase 0.3.0 Beta 7')
        self.assertEqual(Output_Dict['server_version'], 'DSM7-1-1-42930-workplus')
        self.assertEqual(Output_Dict['server_address'], '10.0.0.1')
        self.assertEqual(Output_Dict['server_port'], 3493)

    # simple
    def test_simple_one_ups(self):
        Scrape_Dict = copy.deepcopy(Base_Scrape_Data)
        JSON_Elements = []
        Data_UPS1 = {
                    'name': 'ups1',
                    'description': 'Description one',
                    'variables': [],
                    # 'clients': [],
                    'server_address': '10.0.0.1',
                    'server_port': 3493
                    }

        Scrape_Dict['ups_list'].append(Data_UPS1)
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        # print("Output_Dict: {}".format(Output_Dict))
        self.assertEqual(Output_Dict['nutcase_version'], 'NUTCase 0.3.0 Beta 7')
        self.assertEqual(Output_Dict['server_version'], 'DSM7-1-1-42930-workplus')
        self.assertEqual(Output_Dict['server_address'], '10.0.0.1')
        self.assertEqual(Output_Dict['server_port'], 3493)

        self.assertEqual(Output_Dict['ups1']['description'], Data_UPS1['description'])
        # self.assertEqual(Output_Dict['ups1']['clients'], {'count': 0, 'list': []})

    # simple
    def test_simple_one_ups_vars(self):
        Scrape_Dict = copy.deepcopy(Base_Scrape_Data)
        JSON_Elements = []
        Data_UPS1 = {
                    'name': 'ups1',
                    'description': 'Description one',
                    'variables': [
                        {'name': 'ups1.one', 'value': 'val_one'},
                        {'name': 'ups1.two', 'value': 'val_two'}
                        ],
                    # 'clients': [],
                    'server_address': '10.0.0.1',
                    'server_port': 3493
                    }

        Scrape_Dict['ups_list'].append(Data_UPS1)
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        # print("Output_Dict: {}".format(Output_Dict))
        self.assertEqual(Output_Dict['nutcase_version'], 'NUTCase 0.3.0 Beta 7')
        self.assertEqual(Output_Dict['server_version'], 'DSM7-1-1-42930-workplus')
        self.assertEqual(Output_Dict['server_address'], '10.0.0.1')
        self.assertEqual(Output_Dict['server_port'], 3493)

        self.assertEqual(Output_Dict['ups1']['description'], Data_UPS1['description'])
        # self.assertEqual(Output_Dict['ups1']['clients'], {'count': 0, 'list': []})
        self.assertEqual(Output_Dict['ups1'][Data_UPS1['variables'][0]['name']],
                                                Data_UPS1['variables'][0]['value'])
        self.assertEqual(Output_Dict['ups1'][Data_UPS1['variables'][1]['name']],
                                                Data_UPS1['variables'][1]['value'])

    def test_simple_two_ups_vars(self):
        Scrape_Dict = copy.deepcopy(Base_Scrape_Data)
        JSON_Elements = []
        Data_UPS1 = {
                    'name': 'ups1',
                    'description': 'Description one',
                    'variables': [
                        {'name': 'ups1.one', 'value': 'val_one'},
                        {'name': 'ups1.two', 'value': 'val_two'}
                        ],
                    'clients': [],
                    'server_address': '10.0.0.1',
                    'server_port': 3493
                    }
        Data_UPS2 = {
                    'name': 'ups2',
                    'description': 'Description two',
                    'variables': [
                        {'name': 'ups2.one', 'value': 'val_one'},
                        {'name': 'ups2.two', 'value': 'val_two'}
                        ],
                    'clients': [],
                    'server_address': '10.0.0.1',
                    'server_port': 3493
                    }

        Scrape_Dict['ups_list'].append(Data_UPS1)
        Scrape_Dict['ups_list'].append(Data_UPS2)
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        # print("Output_Dict: {}".format(Output_Dict))
        self.assertEqual(Output_Dict['nutcase_version'], 'NUTCase 0.3.0 Beta 7')
        self.assertEqual(Output_Dict['server_version'], 'DSM7-1-1-42930-workplus')
        self.assertEqual(Output_Dict['server_address'], '10.0.0.1')
        self.assertEqual(Output_Dict['server_port'], 3493)

        self.assertEqual(Output_Dict['ups1']['description'], Data_UPS1['description'])
        self.assertEqual(Output_Dict['ups1']['clients'], {'count': 0, 'list': []})
        self.assertEqual(Output_Dict['ups1'][Data_UPS1['variables'][0]['name']],
                                                Data_UPS1['variables'][0]['value'])
        self.assertEqual(Output_Dict['ups1'][Data_UPS1['variables'][1]['name']],
                                                Data_UPS1['variables'][1]['value'])

        self.assertEqual(Output_Dict['ups2']['description'], Data_UPS2['description'])
        self.assertEqual(Output_Dict['ups2']['clients'], {'count': 0, 'list': []})
        self.assertEqual(Output_Dict['ups2'][Data_UPS2['variables'][0]['name']],
                                                Data_UPS2['variables'][0]['value'])
        self.assertEqual(Output_Dict['ups2'][Data_UPS2['variables'][1]['name']],
                                                Data_UPS2['variables'][1]['value'])

    # simple
    def test_clients(self):
        Scrape_Dict = copy.deepcopy(Base_Scrape_Data)
        JSON_Elements = []
        Data_UPS1 = {
                    'name': 'ups1',
                    'description': 'Description one',
                    'variables': [
                        {'name': 'ups1.one', 'value': 'val_one'},
                        {'name': 'ups1.two', 'value': 'val_two'}
                        ],
                    'clients': ["10.0.0.1"],
                    'server_address': '10.0.0.1',
                    'server_port': 3493
                    }

        Scrape_Dict['ups_list'].append(Data_UPS1)
        Output_Dict = Format_For_JSON(Scrape_Dict, JSON_Elements)
        # print("Output_Dict: {}".format(Output_Dict))
        self.assertEqual(Output_Dict['nutcase_version'], 'NUTCase 0.3.0 Beta 7')
        self.assertEqual(Output_Dict['server_version'], 'DSM7-1-1-42930-workplus')
        self.assertEqual(Output_Dict['server_address'], '10.0.0.1')
        self.assertEqual(Output_Dict['server_port'], 3493)

        self.assertEqual(Output_Dict['ups1']['description'], Data_UPS1['description'])
        self.assertEqual(Output_Dict['ups1']['clients'], {'count': len(Data_UPS1['clients']),
                                                          'list': Data_UPS1['clients']})
        self.assertEqual(Output_Dict['ups1'][Data_UPS1['variables'][0]['name']],
                                             Data_UPS1['variables'][0]['value'])
        self.assertEqual(Output_Dict['ups1'][Data_UPS1['variables'][1]['name']],
                                             Data_UPS1['variables'][1]['value'])

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
