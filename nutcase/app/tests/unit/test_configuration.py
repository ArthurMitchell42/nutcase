import os
import unittest
import unittest.mock as mock
import errno
import time
import logging

from unittest.mock import call
from unittest.mock import patch, mock_open
import flask

from .mock_types import Isfile
from pathlib import PurePosixPath

from app.utils.app_log_config import Add_Logging_Levels
from app.utils.configuration import Load_Config, Parse_Config, List_Variables, \
                                    Config_File_Modified, Get_Server, Get_Device

# =================================================================================================
# Base config
# =================================================================================================
BASE_CONFIG = {
    "CONFIG_ERROR": False,
    "CONFIG_MOD_TIME": None,
    "TESTING": True,
    "BETA_OVERRIDE": False,
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

    # ===================================================================================
    def tearDown(self):
        super().tearDown()

# =================================================================================================
# Test_config_file_selection
# =================================================================================================
@mock.patch("os.path.isfile", autospec=True)
@mock.patch('builtins.open', new_callable=mock_open, read_data='rework:')
@mock.patch("os.path.getmtime", autospec=True)
class Test_config_file_selection(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()
        Config_Path = '/art/config'
        self.app.config.update(
            CONFIG_PATH = Config_Path,
            CONFIG_FILE = "conf_filename",
            )
        self.Expected_Config = {'rework': [], 'servers': [], 'settings': {}, 'webhooks': {}}

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_configuration_filename_missing(self, mock_ospath_getmtime, mock_fileopen,
                                            mock_ospath_isfile):
        File_Path = "/art/config/conf_filename"
        Good_File = "/art/config/no_file.yml"
        rtn_obj = Isfile(Good_File)
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            Returned_Config = Load_Config()

            self.assertEqual(cm.output, [
                "WARNING:Config file ({}) not found as "
                "either .yml or .yaml".format(self.app.config['CONFIG_FILE']),
                "WARNING:Couldn't identify config file None"
                ])

        self.assertEqual(Returned_Config, None)
        calls = [call(PurePosixPath(File_Path + ".yml")),
                 call(PurePosixPath(File_Path + ".yaml"))]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)
        self.assertTrue(self.app.config['CONFIG_ERROR'])

    # =============================================================================================
    def test_configuration_filename_yml(self, mock_ospath_getmtime, mock_fileopen,
                                        mock_ospath_isfile):
        File_Path = "/art/config/conf_filename"
        Good_File = File_Path + ".yml"

        mock_ospath_getmtime.return_value = time.time()

        with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            Returned_Config = Load_Config()
            self.assertEqual(cm.output, [
                "INFO:Config file is " + Good_File,
                'INFO:Loaded YAML from ' + Good_File,
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
                ])

        self.assertEqual(Returned_Config, self.Expected_Config)
        calls = [call(PurePosixPath(File_Path + ".yml"))]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)
        self.assertFalse(self.app.config['CONFIG_ERROR'])
        self.assertTrue(isinstance(self.app.config['CONFIG_MOD_TIME'], float))

    # =============================================================================================
    def test_configuration_filename_yaml(self, mock_ospath_getmtime, mock_fileopen,
                                         mock_ospath_isfile):
        File_Path = "/art/config/conf_filename"
        Good_File = File_Path + ".yaml"
        rtn_obj = Isfile(Good_File)
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        mock_ospath_getmtime.return_value = time.time()

        with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            Returned_Config = Load_Config()
            self.assertEqual(cm.output, [
                "INFO:Config file is " + Good_File,
                "INFO:Loaded YAML from " + Good_File,
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
                ])

        self.assertEqual(Returned_Config, self.Expected_Config)
        calls = [call(PurePosixPath(File_Path + ".yml")),
                 call(PurePosixPath(File_Path + ".yaml"))]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)
        self.assertFalse(self.app.config['CONFIG_ERROR'])
        self.assertTrue(isinstance(self.app.config['CONFIG_MOD_TIME'], float))

# =================================================================================================
# Test_config_file_errors
# =================================================================================================
@mock.patch("os.path.isfile", autospec=True)
class Test_config_file_errors(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()
        Config_Path = '/art/config'
        self.app.config.update(
            CONFIG_PATH = Config_Path,
            CONFIG_FILE = "conf_filename",
            )

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_open_file_error(self, mock_ospath_isfile):
        self.maxDiff = None

        File_Path = "/art/config/conf_filename"
        Good_File = File_Path + ".yaml"
        rtn_obj = Isfile(Good_File)
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        with patch('builtins.open', new_callable=mock_open, read_data='') as m:
            m.side_effect = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), Good_File)
            with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
                formatter = logging.Formatter('%(levelname)s:%(message)s')
                logging.getLogger(__name__).handlers[0].setFormatter(formatter)
                Returned_Config = Load_Config()

                self.assertEqual(cm.output, [
                    "INFO:Config file is " + Good_File,
                    "WARNING:Could not open YAML file "
                    "/art/config/conf_filename.yaml. Error: [Errno 2] "
                    "No such file or directory: '/art/config/conf_filename.yaml'",
                    "WARNING:Couldn't load YAML " + Good_File,
                    ])

        self.assertEqual(Returned_Config, None)
        calls = [call(PurePosixPath(File_Path + ".yml")),
                 call(PurePosixPath(File_Path + ".yaml"))]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)
        self.assertTrue(self.app.config['CONFIG_ERROR'])

    # =============================================================================================
    def test_open_file_yaml_error(self, mock_ospath_isfile):
        self.maxDiff = None

        File_Path = "/art/config/conf_filename"
        Good_File = File_Path + ".yaml"
        rtn_obj = Isfile(Good_File)
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        with patch('builtins.open', new_callable=mock_open, read_data='%') as m:
            with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
                formatter = logging.Formatter('%(levelname)s:%(message)s')
                logging.getLogger(__name__).handlers[0].setFormatter(formatter)
                Returned_Config = Load_Config()
                # print("Output is: \n{}\n{}".format(cm.output[0], cm.output[1]))
                self.assertEqual(cm.output[0],
                    "INFO:Config file is " + Good_File,
                )

                self.assertIn(
                    "ERROR:Error loading YAML",
                    cm.output[1]
                    )

        self.assertEqual(Returned_Config, None)
        calls = [call(PurePosixPath(File_Path + ".yml")),
                 call(PurePosixPath(File_Path + ".yaml"))]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)
        self.assertTrue(self.app.config['CONFIG_ERROR'])
        m.assert_called_once_with(PurePosixPath('/art/config/conf_filename.yaml'), 'r')

    # =============================================================================================
    @mock.patch("os.path.getmtime", autospec=True)
    def test_open_file_config_error(self, mock_ospath_getmtime, mock_ospath_isfile):
        self.maxDiff = None

        File_Path = "/art/config/conf_filename"
        Good_File = File_Path + ".yaml"
        rtn_obj = Isfile(Good_File)
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        mock_ospath_getmtime.return_value = time.time()

        with patch('builtins.open', new_callable=mock_open,
                   read_data='servers:\n  - dev: none') as m:
            with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
                formatter = logging.Formatter('%(levelname)s:%(message)s')
                logging.getLogger(__name__).handlers[0].setFormatter(formatter)
                Returned_Config = Load_Config()
                # print("Output is: \n{}\n{}".format(cm.output[0], cm.output[1]))
                self.assertEqual(cm.output[0],
                    "INFO:Config file is " + Good_File,
                )
        self.assertEqual(Returned_Config, None)
        self.assertTrue(self.app.config['CONFIG_ERROR'])
        m.assert_called_once_with(PurePosixPath('/art/config/conf_filename.yaml'), 'r')

# =================================================================================================
# Test_config_parse_config
# =================================================================================================
class Test_config_parse_config(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_config_empty(self):
        self.maxDiff = None
        Config = {}
        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # =====================================================================================
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertFalse(self.app.config['CONFIG_ERROR'])
            self.assertEqual(Config,
                {'rework': [], 'settings': {}, 'webhooks': {}, 'servers': []},
                )
            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
                ])

    # =============================================================================================
    def test_config_odd_section(self):
        self.maxDiff = None
        Config = {'unknown': 'error'}
        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Parse_Return = Parse_Config(Config)
            self.assertEqual(cm.output, [
                "WARNING:Unknown section type unknown",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                ])
            self.assertTrue(Parse_Return)
            self.assertTrue(self.app.config['CONFIG_ERROR'])
            self.assertEqual(Config,
                {'rework': [], 'settings': {}, 'unknown': 'error', 'webhooks': {}, 'servers': []},
                )

    # =============================================================================================
    def test_config_webhook_unexpected(self):
        self.maxDiff = None
        Config = {'webhooks': {'default': 'default_hook', 'unknown': 'unknown_hook'}}
        with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            Parse_Return = Parse_Config(Config)
            self.assertEqual(cm.output, [
                "WARNING:Unknown WebHook name unknown. Expected names: ok,fail",
                ])
            self.assertTrue(Parse_Return)
            self.assertTrue(self.app.config['CONFIG_ERROR'])
            self.assertEqual(Config,
                {'rework': [], 'settings': {}, 'webhooks':
                    {'default': 'default_hook', 'unknown': 'unknown_hook'}, 'servers': []},
                )

    # =============================================================================================
    def test_config_webhook_default(self):
        self.maxDiff = None
        Config = {'webhooks': {'default': 'default_hook'}}
        with self.assertNoLogs(logging.getLogger(__name__), level='DEBUG'):
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertFalse(self.app.config['CONFIG_ERROR'])
            self.assertEqual(Config,
                {'rework': [], 'settings': {}, 'webhooks': {'default': 'default_hook'},
                 'servers': []},
                )

    # =============================================================================================
    def test_config_webhook_non_default(self):
        self.maxDiff = None
        Config = {'webhooks': {'ok': 'ok_hook', 'fail': 'fail_hook'}}
        with self.assertNoLogs(logging.getLogger(__name__), level='DEBUG'):
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertFalse(self.app.config['CONFIG_ERROR'])
            self.assertEqual(Config,
                {'rework': [], 'settings': {}, 'webhooks': {'ok': 'ok_hook', 'fail': 'fail_hook'},
                 'servers': []},
                )

    # =============================================================================================
    def test_config_servers_ok(self):
        self.maxDiff = None
        Config = {
            'webhooks': {'default': 'default_hook'},
            'servers': [
                {'server': 's', 'port': 'p', 'devices': [{"device": 'd'}]}
            ]
        }
        with self.assertNoLogs(logging.getLogger(__name__), level='DEBUG'):
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertFalse(self.app.config['CONFIG_ERROR'])
            self.assertEqual(Config,
                {'rework': [],
                 'settings': {},
                 'webhooks': {'default': 'default_hook'},
                 'servers': [
                     {'devices': [{'device': 'd'}], 'port': 'p', 'server': 's'}
                             ],
                }
            )

    # =============================================================================================
    def test_config_servers_errors(self):
        self.maxDiff = None
        Config = {
            'webhooks': {'default': 'default_hook'},
        }

        with self.assertLogs(logging.getLogger(__name__), level='DEBUG') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # =====================================================================================
            Config.update( servers = [
                {
                # 'server': 's',
                'port': 'p',
                'devices': [{"device": 'd'}]
                }
            ])
            Parse_Return = Parse_Config(Config)

            # =====================================================================================
            Config.update( servers = [
                {
                'server': 's',
                # 'port': 'p',
                'devices': [{"device": 'd'}]
                }
            ])
            Parse_Return = Parse_Config(Config)

            # =====================================================================================
            Config.update( servers = [
                {
                'server': 's',
                'port': 'p',
                # 'devices': [{"device": 'd'}]
                }
            ])
            Parse_Return = Parse_Config(Config)

            # =====================================================================================
            Config.update( servers = [
                {
                'server': 's',
                'port': 'p',
                'devices': []
                }
            ])
            Parse_Return = Parse_Config(Config)
            self.assertFalse(Parse_Return)

            # =====================================================================================
            Config.update( servers = [
                {
                'server': 's',
                'port': 'p',
                'devices': {}
                }
            ])
            Parse_Return = Parse_Config(Config)
            self.assertFalse(Parse_Return)

            # =====================================================================================
            self.assertEqual(cm.output, [
                "ERROR:Server entries must have 'server', 'port' and at least one entry "
                "in the 'devices' list",
                "ERROR:Server entries must have 'server', 'port' and at least one entry "
                "in the 'devices' list",
                "ERROR:Server entries must have 'server', 'port' and at least one entry "
                "in the 'devices' list",
                "ERROR:Server entries must have 'server', 'port' and at least one entry "
                "in the 'devices' list",
                "ERROR:Server entries must have 'server', 'port' and at least one entry "
                "in the 'devices' list",
                ])

# =================================================================================================
# Test_config_rework
# =================================================================================================
class Test_config_rework(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_config_rework_simple(self):
        self.maxDiff = None
        # Config = {}
        Config = {'rework': [
            {
            'from': 'f',
            'to': 't',
            'style': 'time',
            'control': 'c'
            }
        ]}
        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
            ])
        self.assertEqual(Config,
            {'rework': [{'control': 'c', 'from': 'f', 'style': 'time', 'to': 't'}],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_missing_entries(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # =====================================================================================
            Config.update( rework = [{
                    # 'from': 'f',
                    'to': 't',
                    'style': 'time',
                    'control': 'c'
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # =====================================================================================
            Config.update( rework = [{
                    'from': 'f',
                    # 'to': 't',
                    'style': 'time',
                    'control': 'c'
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # =====================================================================================
            Config.update( rework = [{
                    'from': 'f',
                    'to': 't',
                    # 'style': 'time',
                    'control': 'c'
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # =====================================================================================
            Config.update( rework = [{
                    'from': 'f',
                    'to': 't',
                    'style': 'time',
                    # 'control': 'c'
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # =====================================================================================
            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:All rework's must have from to style & control",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:All rework's must have from to style & control",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:All rework's must have from to style & control",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:All rework's must have from to style & control"
                ])

    # =============================================================================================
    def test_config_rework_unknown_style(self):
        self.maxDiff = None
        Config = {'rework': [
            {
            'from': 'f',
            'to': 't',
            'style': 'unknown',
            'control': 'c'
            }
        ]}
        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:Unknown style {'from': 'f', 'to': 't', "
                "'style': 'unknown', 'control': 'c'}, styles are: time, simple-enum, ratio, "
                "comp-enum, cl-count, cl-check, nutcase_logs",
                ])

        self.assertEqual(Config,
            {'rework': [],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_enum_dict(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Config.update(rework = [{'from': 'f', 'to': 't', 'style': 'simple-enum',
                                     'control': []}])

            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:simple-enum control must be dictionary Found: []",
                ])

        self.assertEqual(Config,
            {'rework': [],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_enum_good(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    'from': ["cf"],
                    "to": ["ct"],
                    'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
            ])
        self.assertEqual(Config,
            {'rework': [
                {'control': {'default': 'cd', 'from': ['cf'], 'to': ['ct']},
               'from': 'f',
               'style': 'simple-enum',
               'to': 't'}
                ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_enum_bits_missing(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # ======================================================
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    # 'from': ["cf"],
                    "to": ["ct"],
                    'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    'from': ["cf"],
                    # "to": ["ct"],
                    'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    'from': ["cf"],
                    "to": ["ct"],
                    # 'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    'from': "cf",
                    "to": ["ct"],
                    'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    'from': ["cf"],
                    "to": "ct",
                    'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [{ 'from': 'f', 'to': 't', 'style': 'simple-enum', 'control': {
                    'from': ["cf"],
                    "to": ["ct", "ct2"],
                    'default': "cd"
                }
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            print(cm.output)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:enum control needs from to & default, from & to equal len',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:enum control needs from to & default, from & to equal len',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:enum control needs from to & default, from & to equal len',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:enum control needs from to & default, from & to equal len',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:enum control needs from to & default, from & to equal len',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:enum control needs from to & default, from & to equal len'
                ])

        self.assertEqual(Config,
            {'rework': [],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_cl_count(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    {}
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    ["xxx", "a", "b", "c"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    [1, "a", "b"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    [1, "a", "b", "c"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:cl-count control=4 el. array, elem0 must be int',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:cl-count control=4 el. array, elem0 must be int',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:cl-count control=4 el. array, elem0 must be int',
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
                ])
        self.assertEqual(Config,
            {'rework': [
            {
                'control': [1, 'a', 'b', 'c'],
                'from': 'f',
                'style': 'cl-count',
                'to': 't'
            }
            ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_cl_count_ok_text_num(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    ["1", "a", "b", "c"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)
            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                ])

        self.assertEqual(Config,
            {'rework': [
            {
                'control': ["1", 'a', 'b', 'c'],
                'from': 'f',
                'style': 'cl-count',
                'to': 't'
            }
            ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_cl_count_auto(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    ["auto", "a", "b", "c"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            print("Output is: {}".format(cm.output))

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                ])

        self.assertEqual(Config,
            {'rework': [
            {
                'control': ["auto", 'a', 'b', 'c'],
                'from': 'f',
                'style': 'cl-count',
                'to': 't'
            }
            ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_cl_count_auto_error(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            # ======================================================
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-count', 'control':
                    [1.0, "a", "b", "c"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                'ERROR:cl-count control=4 el. array, elem0 must be int'
                ])
        self.assertEqual(Config,
            {'rework': [],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_cl_check(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # ======================================================
            # Not a list
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-check', 'control':
                    {}
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            # Empty list
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-check', 'control':
                    []
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            # OK
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-check', 'control':
                    ["a", "b", "c"]
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:cl-check must have a non-zero length array for 'control'",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:cl-check must have a non-zero length array for 'control'",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
                ])

        self.assertEqual(Config,
            {'rework': [
            {
                'control': ['a', 'b', 'c'],
                'from': 'f',
                'style': 'cl-check',
                'to': 't'
            }
            ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_cl_check_auto(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            # ======================================================
            # OK
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'cl-check', 'control': "auto"}
                ])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
            ])
        self.assertEqual(Config,
            {'rework': [
            {
                'control': "auto",
                'from': 'f',
                'style': 'cl-check',
                'to': 't'
            }
            ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

    # =============================================================================================
    def test_config_rework_style_nutcase_logs(self):
        self.maxDiff = None
        Config = {}

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            # ======================================================
            # Not a list
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'nutcase_logs', 'control':
                    {}
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            # ======================================================
            # OK
            Config.update(rework = [
                { 'from': 'f', 'to': 't', 'style': 'nutcase_logs', 'control':
                    "c"
                }])
            Parse_Return = Parse_Config(Config)
            self.assertTrue(Parse_Return)

            self.assertEqual(cm.output, [
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail',
                "ERROR:nutcase_logs must have a string for 'control'",
                'WARNING:Config is missing WebHook name ok',
                'WARNING:Config is missing WebHook name fail'
                ])

        self.assertEqual(Config,
            {'rework': [
            {
                'control': 'c',
                'from': 'f',
                'style': 'nutcase_logs',
                'to': 't'
            }
            ],
             'settings': {},
             'webhooks': {},
             'servers': [],
            }
        )

# =================================================================================================
# Test_config_list_variables
# =================================================================================================
class Test_config_list_variables(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_list_variables(self):
        self.maxDiff = None
        Config = {'rework': [
            {'from': 'f1', 'to': 't', 'style': 'time', 'control': 'c'},
            {'from': 'f2', 'to': 't', 'style': 'time', 'control': 'c'},
            {'from': 'f3', 'to': 't', 'style': 'time', 'control': 'c'},
        ]}
        List_Variables(Config)
        self.assertEqual(self.app.config['REWORK_VAR_LIST'], ["f1", "f2", "f3"])

# =================================================================================================
# Test_config_list_variables
# =================================================================================================
@mock.patch("os.path.isfile", autospec=True)
@mock.patch("os.path.getmtime", autospec=True)
class Test_config_file_mod(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()
        self.app.config.update(
                    CONFIG_FULLNAME = "/config/conf_filename.yaml",
                    CONFIG_MOD_TIME = 10.0
        )

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_config_file_missing(self, mock_ospath_getmtime, mock_ospath_isfile):
        self.maxDiff = None
        rtn_obj = Isfile("missing_file")
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        mock_ospath_getmtime.return_value = self.app.config["CONFIG_MOD_TIME"]

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)

            Modified = Config_File_Modified()

            self.assertEqual(cm.output, [
                "WARNING:"
                "Config file missing {}".format(self.app.config["CONFIG_FULLNAME"]),
                ])

        self.assertFalse(Modified)
        calls = [call(self.app.config["CONFIG_FULLNAME"])]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)

    # =============================================================================================
    def test_config_file_not_mod(self, mock_ospath_getmtime, mock_ospath_isfile):
        self.maxDiff = None
        rtn_obj = Isfile(self.app.config["CONFIG_FULLNAME"])
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        mock_ospath_getmtime.return_value = self.app.config["CONFIG_MOD_TIME"]

        with self.assertNoLogs(logging.getLogger(__name__), level='INFO'):
            Modified = Config_File_Modified()

        self.assertFalse(Modified)
        calls = [call(self.app.config["CONFIG_FULLNAME"])]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)

    # =============================================================================================
    def test_config_file_is_mod(self, mock_ospath_getmtime, mock_ospath_isfile):
        self.maxDiff = None
        rtn_obj = Isfile(self.app.config["CONFIG_FULLNAME"])
        mock_ospath_isfile.side_effect = rtn_obj.isfile

        mock_ospath_getmtime.return_value = self.app.config["CONFIG_MOD_TIME"] + 1.0

        with self.assertLogs(logging.getLogger(__name__), level='INFO') as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            Modified = Config_File_Modified()

            self.assertEqual(cm.output, [
                'INFO:Config file has been updated',
                ])

        self.assertTrue(Modified)
        calls = [call(self.app.config["CONFIG_FULLNAME"])]
        mock_ospath_isfile.assert_has_calls(calls, any_order=False)

# =================================================================================================
# Test_config_get_server
# =================================================================================================
class Test_config_get_server(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()
        self.app.config.update(SERVERS = [
            {"server": "10.0.0.1"},
            {"server": "10.0.0.2"},
            {"server": "10.0.0.3"}
            ])

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_config_get_server_empty(self):
        self.maxDiff = None
        self.app.config.update(SERVERS = [])

        Server = Get_Server("10.0.0.1")
        self.assertEqual(Server, None)

    # =============================================================================================
    def test_config_get_server_missing(self):
        self.maxDiff = None

        Server = Get_Server("10.0.0.9")
        self.assertEqual(Server, None)

    # =============================================================================================
    def test_config_get_server_found(self):
        self.maxDiff = None

        Server = Get_Server("10.0.0.2")
        self.assertEqual(Server, {"server": "10.0.0.2"})

# =================================================================================================
# Test_config_get_device
# =================================================================================================
class Test_config_get_device(BaseTestCase):
    # =============================================================================================
    def setUp(self):
        super().setUp()
        self.app.config.update(SERVERS = [
            {"server": "10.0.0.1",
             "devices": [
                 {"device": "s1_d1"},
                 {"device": "s1_d2"},
             ]
            },
            {"server": "10.0.0.2",
             "devices": [
                 {"device": "s2_d1"},
                 {"device": "s2_d2"},
             ]},
            {"server": "10.0.0.3",
             "devices": [
                 {"device": "s3_d1"},
                 {"device": "s3_d2"},
             ]}
            ])

    # =============================================================================================
    def tearDown(self):
        super().tearDown()

    # =============================================================================================
    def test_config_get_device_empty(self):
        self.maxDiff = None
        self.app.config.update(SERVERS = [])

        Device = Get_Device("10.0.0.1", "s1_d2")
        self.assertEqual(Device, None)

    # =============================================================================================
    def test_config_get_device_missing(self):
        self.maxDiff = None

        Device = Get_Device("10.0.0.9", "s2_d1")
        self.assertEqual(Device, None)

    # =============================================================================================
    def test_config_get_device_missing2(self):
        self.maxDiff = None

        Device = Get_Device("10.0.0.2", "s2_d3")
        self.assertEqual(Device, None)

    # =============================================================================================
    def test_config_get_device_found(self):
        self.maxDiff = None

        Device = Get_Device("10.0.0.2", "s2_d2")
        self.assertEqual(Device, {"device": "s2_d2"})

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
