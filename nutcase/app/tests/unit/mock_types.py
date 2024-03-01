import unittest.mock as mock
from http import HTTPStatus

class Urlopen(mock.MagicMock):
    def __init__(self, url, code=HTTPStatus.OK, read_data='{"ok":true}', **kwargs):
        mock.MagicMock.__init__(self)
        self._url = url
        self._code = code
        self._read_data = read_data
        pass

    def getcode(self):
        return self._code

    def geturl(self):
        return self._url

    def read(self):
        return self._read_data
