import unittest.mock as mock
from http import HTTPStatus
import time

# ==============================================================================================
class Urlopen(mock.MagicMock):
    def __init__(self, url, code=HTTPStatus.OK, read_data='{"ok":true}', **kwargs):
        mock.MagicMock.__init__(self)
        self._url = url
        self._code = code
        self._read_data = read_data

    def getcode(self):
        return self._code

    def geturl(self):
        return self._url

    def read(self):
        return self._read_data

# ==============================================================================================
class Isfile(mock.MagicMock):
    def __init__(self, Good_File, **kwargs):
        mock.MagicMock.__init__(self)
        self._good_file = Good_File

    def isfile(self, File):
        Text_Name = str(File)
        if Text_Name == self._good_file:
            return True
        else:
            return False

# ==============================================================================================
class Threading_Condition(mock.MagicMock):
    def __init__(self, **kwargs):
        mock.MagicMock.__init__(self)
        self._aquired = False
        self._released = False
        self._force_timeout = False

    def acquire(self):
        self._aquired = True

    def wait(self, timeout):
        assert self._aquired
        if self._force_timeout:
            time.sleep(timeout)
            return False
        else:
            time.sleep(timeout / 2)
            return True

    def release(self):
        self._released = True

    def force_timeout(self):
        self._force_timeout = True

    def get_aquired(self):
        return self._aquired

    def get_released(self):
        return self._released

# ==============================================================================================
class Mock_Queue(mock.MagicMock):
    def __init__(self, **kwargs):
        mock.MagicMock.__init__(self)
        self._bucket = None
        self._force_fail = False
        self._data = {}

    def put(self, Bucket):
        self._bucket = Bucket
        if self._force_fail:
            self._bucket.result = False
            self._bucket.scrape_data = {}
        else:
            self._bucket.result = True
            self._bucket.scrape_data = self._data

    def get_bucket(self):
        return self._bucket

    def force_fail(self):
        self._force_fail = True

    def set_data(self, Data):
        self._data = Data
