import unittest
import flask
import logging

BASE_CONFIG = {
    "SECRET_KEY": "secrets",
    "WTF_CSRF_ENABLED": False,
}

class test_all_logs(unittest.TestCase):
    def setUp(self):
        super().setUp()
        app = flask.Flask(__name__)

        app.config.update(BASE_CONFIG)
        self.app = app
        self.app.app_context().push()
        self.app.logger.setLevel("DEBUG")

    def tearDown(self):
        super().tearDown()

    def test_log_one(self):
        with self.assertLogs(logging.getLogger(__name__), level="INFO") as cm:
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            logging.getLogger(__name__).handlers[0].setFormatter(formatter)
            self.app.logger.critical("Test")

            self.assertEqual(cm.output, [
                "CRITICAL:Test"
                ])

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
