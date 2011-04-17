import unittest
from dhtnodeserver import DHTNodeServer

class TestDHTNodeServer(unittest.TestCase):
    def setUp(self):
        self.node = DHTNodeServer(23467)

    def test_shouldReturnErrorMessage(self):
        returnCode = self.node.handle('{"operation":"gettt"}')
        self.assertEquals('{"status": {"code": 500, "message": "Unsupported operation" }}', returnCode)

    def test_shouldReturnErrorMessageForNOOP(self):
        returnCode = self.node.handle('{"operation":""}')
        self.assertEquals('{"status": {"code": 500, "message": "Unsupported operation" }}', returnCode)

    def test_shouldReturnSuccessMessageForValidGetWhenKeyFound(self):
        self.node.handle('{"operation":"put","key":"blah","value":"something"}')
        returnCode = self.node.handle('{"operation":"get","key":"blah"}')
        self.assertEquals('{"status": {"code": 200, "message": "get received", "data": "something" }}', returnCode)

    def test_shouldReturn404ForValidGetWhenKeyNotFound(self):
        returnCode = self.node.handle('{"operation":"get","key":"blah"}')
        self.assertEquals('{"status": {"code": 404, "message": "key not found" }}', returnCode)

    def test_shouldReturnErrorMessageForGetWithoutKey(self):
        returnCode = self.node.handle('{"operation":"get"}')
        self.assertEquals('{"status": {"code": 400, "message": "invalid get request received" }}', returnCode,
                          "Unexpected return code")

    def test_shouldReturnErrorMessageForInvalidPut(self):
        returnCode = self.node.handle('{"operation":"put"}')
        self.assertEquals('{"status": {"code": 400, "message": "invalid put request received" }}', returnCode,
                          "Unexpected return code")

    def test_shouldReturnSuccessMessageForValidPut(self):
        returnCode = self.node.handle('{"operation":"put","key":"blah","value":"{}"}')
        self.assertEquals('{"status": {"code": 200, "message": "put received" }}', returnCode)


if __name__ == '__main__':
    unittest.main()
