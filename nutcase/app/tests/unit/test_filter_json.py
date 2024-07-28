import unittest
from app.utils.format_to_json import Filter_JSON

# =================================================================================================
# Base scrape data
# =================================================================================================
Base_Data = {
    'nutcase_version': 'NUTCase 0.3.0 Beta 7',
    'server_version': 'DSM7-1',
    'server_address': '10.0.0.1',
    'server_port': 3493,
    'ups1':
        {
        'description': 'Description unavailable',
        "battery.charge": "100",
        "battery.voltage": "13.60",
        "battery.voltage.high": "13.00",
        "battery.voltage.low": "10.40",
        "battery.voltage.nominal": "12.0",
        "device.type": "ups",
        "driver.name": "blazer_usb",
        "driver.parameter.pollinterval": "15",
        "driver.parameter.port": "auto",
        "clients": {
            "count": 2,
            "list": ["10.0.0.2", "10.0.0.3"]
            },
        'server_address': '10.0.0.1',
        'server_port': 3493
        },
    'ups2':
        {
        'description': 'Description unavailable',
        "ups.beeper.status": "enabled",
        "ups.delay.shutdown": "30",
        "ups.delay.start": "180",
        "ups.load": "16",
        "ups.productid": "5161",
        "ups.status": "OL",
        "ups.temperature": "25.0",
        "ups.type": "offline / line interactive",
        "ups.vendorid": "0665",
        "clients": {
            "count": 3,
            "list": ["10.0.1.2", "10.0.1.3", "10.0.1.4"]
            },
        'server_address': '10.0.0.1',
        'server_port': 3493
        },
    }

class Test_filter_json_basics(unittest.TestCase):
    # no input data
    def test_input_none_filter_none(self):
        Input_Dict = None
        JSON_Elements = None
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {})

    # empty input data
    def test_input_empty_filter_empty(self):
        Input_Dict = {}
        JSON_Elements = []
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {})

    # get single root data
    def test_get_single_root(self):
        Input_Dict = Base_Data
        JSON_Elements = ['server_address']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {"server_address": "10.0.0.1"})

    # get multiple root data
    def test_get_multiple_root(self):
        Input_Dict = Base_Data
        JSON_Elements = ['server_address', 'server_port']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {"server_address": "10.0.0.1", "server_port": 3493})

    # get single root missing
    def test_get_single_missing(self):
        Input_Dict = Base_Data
        Missing_Key = 'server_missing'
        JSON_Elements = [Missing_Key]
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {Missing_Key: 'Key ' + Missing_Key + ' not found'})

    # get multiple root, one missing
    def test_get_multiple_one_missing(self):
        Input_Dict = Base_Data
        Missing_Key = 'server_missing'
        JSON_Elements = [Missing_Key, 'server_address']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {
                        Missing_Key: 'Key ' + Missing_Key + ' not found',
                        'server_address': "10.0.0.1"
                        })

    # get single sub
    def test_get_single_sub(self):
        Input_Dict = Base_Data
        JSON_Elements = ['ups1/battery.voltage']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {'ups1/battery.voltage': '13.60'})

    # get multiple sub, one missing
    def test_get_multiple_sub_missing(self):
        Input_Dict = Base_Data
        Missing_Key = 'ups1/server_missing'
        JSON_Elements = [Missing_Key, 'ups1/battery.voltage.nominal']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {
                        'ups1/battery.voltage.nominal': "12.0",
                        Missing_Key: 'Key ' + Missing_Key + ' not found',
                        })

    # get client count
    def test_get_client_count(self):
        Input_Dict = Base_Data
        JSON_Elements = ['ups1/clients/count', 'ups2/clients/count']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {'ups1/clients/count': 2, 'ups2/clients/count': 3})

    # get client ip
    def test_get_client_ip(self):
        Input_Dict = Base_Data
        JSON_Elements = ['ups1/clients/list/1', 'ups2/clients/list/2']
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {'ups1/clients/list/1': "10.0.0.3",
                                       'ups2/clients/list/2': "10.0.1.4"})

    # get client ip with error
    def test_get_client_ip_error1(self):
        Input_Dict = Base_Data
        Missing_Key = 'ups1/clients/listx'
        JSON_Elements = [Missing_Key]
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {Missing_Key: 'Key ' + Missing_Key + ' not found'})

    def test_get_client_ip_error2(self):
        Input_Dict = Base_Data
        Missing_Key = 'ups1/clients/list'
        JSON_Elements = [Missing_Key]
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {Missing_Key: 'Index ' + Missing_Key +
                                       ' not found list index out of range'})

    def test_get_client_ip_error3(self):
        Input_Dict = Base_Data
        Missing_Key = 'ups1/clients/list/'
        JSON_Elements = [Missing_Key]
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {Missing_Key: "Index " + Missing_Key +
                                       " not found invalid literal for int() with base 10: ''"})

    def test_get_client_ip_error4(self):
        Input_Dict = Base_Data
        Missing_Key = 'ups1/clients/list/5'
        JSON_Elements = [Missing_Key]
        Output_Dict = Filter_JSON(Input_Dict, JSON_Elements)
        self.assertEqual(Output_Dict, {Missing_Key: "Index " + Missing_Key +
                                       " not found list index out of range"})

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
