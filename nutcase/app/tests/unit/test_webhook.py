import unittest
import flask
import unittest.mock as mock
from unittest.mock import call

from http import HTTPStatus
from urllib.error import URLError, HTTPError

from .mock_types import Urlopen

from app.utils.webhook import Call_Webhook
from app.utils.webhook import Call_URL
from app.utils.app_log_config import Add_Logging_Levels

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
        app.logger.setLevel("DEBUG")

@mock.patch("urllib.request.urlopen", autospec=True)
class Test_webhook_call_url(BaseTestCase):
    # HTTPError
    def test_webhook_http_error(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj
        mock_urlopen.side_effect = HTTPError(url=url, code=HTTPStatus.BAD_REQUEST,
                                             msg="Bad request", hdrs=None, fp=None)

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Call_URL(self.app, url)
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_webhook:Failed to call webhook. Reason: Bad request",
                "WARNING:tests.unit.test_webhook:Webhook server couldn't "
                "fulfill request Error: 400",
                ])

        self.assertFalse(Rtn)

    # URLError
    def test_webhook_url_error(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj
        mock_urlopen.side_effect = URLError(reason="The reason")

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Call_URL(self.app, url)
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_webhook:Failed to call webhook. Reason: The reason"
                ])

        self.assertFalse(Rtn)

    # Normal
    def test_webhook_normal(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj
        Rtn = Call_URL(self.app, url)
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(rtn_obj.geturl(), url)

    # Return 404
    def test_webhook_return_404(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url, code=HTTPStatus.NOT_FOUND, read_data='')
        mock_urlopen.return_value = rtn_obj

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Call_URL(self.app, url)
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_webhook:WebHook returned 404: NOT_FOUND",
                "WARNING:tests.unit.test_webhook:JSON Returned by a web hook could "
                "not be parsed Expecting value: line 1 column 1 (char 0)"
                ])

        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 1)

    # Return json not ok no msg
    def test_webhook_return_json_not_ok_no_msg(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url, read_data='{"ok":false}')
        mock_urlopen.return_value = rtn_obj

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Call_URL(self.app, url)
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_webhook:The webhook returned an 'ok' "
                "element as not True with the message 'none'"
                ])

        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 1)

    # Return json not ok with msg
    def test_webhook_return_json_not_ok_with_msg(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url, read_data='{"ok":false,"msg":"A Message"}')
        mock_urlopen.return_value = rtn_obj

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Call_URL(self.app, url)
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_webhook:The webhook returned an 'ok' "
                "element as not True with the message 'A Message'"
                ])

        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 1)

@mock.patch("urllib.request.urlopen", autospec=True)
class Test_webhook_call_webhook(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    # test with no init
    def test_webhook_not_init(self, mock_urlopen):
        Rtn = Call_Webhook(self.app, "", {})
        self.assertFalse(Rtn)
        self.assertEqual(mock_urlopen.call_count, 0)

    # test with init but no default
    def test_webhook_no_default(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "named": url
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Rtn = Call_Webhook(self.app, "", {})
        self.assertFalse(Rtn)
        self.assertEqual(mock_urlopen.call_count, 0)

    # test with default, no name given
    def test_webhook_default(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "default": url
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Rtn = Call_Webhook(self.app, "", {})
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 1)
        mock_urlopen.assert_called_once_with(url)

    def test_webhook_named(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "named": url + "named",
            "default": url + "default"
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Rtn = Call_Webhook(self.app, "named", {})
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 1)
        mock_urlopen.assert_called_once_with(url + "named")

    def test_webhook_default_multiple(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "named": [url + "named1", url + "named2"],
            "default": [url + "default1", url + "default2"]
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Rtn = Call_Webhook(self.app, "", {})
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 2)

        calls = [call(url + "default1"), call(url + "default2")]
        mock_urlopen.assert_has_calls(calls, any_order=True)

    def test_webhook_named_multiple(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "named": [url + "named1", url + "named2"],
            "default": [url + "default1", url + "default2"]
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Rtn = Call_Webhook(self.app, "named", {})
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 2)

        calls = [call(url + "named1"), call(url + "named2")]
        mock_urlopen.assert_has_calls(calls, any_order=True)

@mock.patch("urllib.request.urlopen", autospec=True)
class Test_webhook_refactor(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.app_context().push()

    def tearDown(self):
        super().tearDown()

    # test refactor change
    def test_webhook_refactor_change(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "named": [url + "named1", url + "named2"],
            "default": [url + "default1", url + "default2"]
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Refactor = {
            "msg": "changed"
        }
        Rtn = Call_Webhook(self.app, "named", Refactor)
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 2)

        for c in mock_urlopen.call_args_list:
            self.assertIn("msg=changed", c[0][0])

    # test refactor add
    def test_webhook_refactor_add(self, mock_urlopen):
        url = "http://10.0.10.180:3001/api/push/fFWFJscQXd?status=up&msg=OK&ping="
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj

        Webhook_Config = {
            "named": [url + "named1", url + "named2"],
            "default": [url + "default1", url + "default2"]
        }
        self.app.config['WEBHOOKS'] = Webhook_Config

        Refactor = {
            "other": "added"
        }
        Rtn = Call_Webhook(self.app, "named", Refactor)
        self.assertTrue(Rtn)
        self.assertEqual(mock_urlopen.call_count, 2)

        for c in mock_urlopen.call_args_list:
            self.assertIn("msg=OK", c[0][0])
            self.assertIn("other=added", c[0][0])

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
