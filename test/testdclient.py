import unittest
import mox
from dhtclient import DHTClient

class TestDHTClient(unittest.TestCase):
    mockSocket = None
    controller = None
    client = None
    NODELIST = [{"host": "localhost", "port": 234555}]

    def setUp(self):
        """
        Create mox mock controller here
        setup mockanything idiom for irregular object socket which I need to mock here
        """

        self.controller = mox.Mox()
        self.mockSocket = self.controller.CreateMockAnything(description="Only way to mock socket :(")
        self.client = DHTClient(TestDHTClient.NODELIST)
        self.controller.StubOutWithMock(self.client, 'getSuitableNode')



    def test_shouldReturnNoneWhenGetFails(self):
        self.client.storeKeyLookupInfo("blahKey","meh-host",2345)
        self.client.getSuitableNode("blahKey").AndReturn(self.mockSocket)
        self.mockSocket.getpeername().AndReturn(("meh-host",1234))
        self.mockSocket.send('{"operation": "get", "key": "blahKey"}')
        self.mockSocket.recv(DHTClient.BUFFER_SIZE).AndReturn('{"status":{"code":404,"message":"lalala cant find it"}}')
        self.controller.ReplayAll()

        result = self.client.getKey("blahKey")
        self.controller.VerifyAll()
        self.assertEqual(None, result)

    def test_getShouldReturnNoneWhenUnableToConnectToSuitableNode(self):
        self.client.storeKeyLookupInfo("blahKey","meh-host",2345)
        self.client.getSuitableNode("blahKey").AndReturn(None)
        self.controller.ReplayAll()

        result = self.client.getKey("blahKey")
        self.controller.VerifyAll()
        self.assertEqual(None, result)

    def test_putShouldReturnNoneWhenUnableToConnectToSuitableNode(self):
        self.client.getSuitableNode("blahKey").AndReturn(None)
        self.controller.ReplayAll()

        result = self.client.put("blahKey","valueObject")
        self.controller.VerifyAll()
        self.assertEqual(False, result)

    def test_shouldReturnResultWhenGetSucceeds(self):
        self.client.getSuitableNode("blahKey").AndReturn(self.mockSocket)
        self.mockSocket.getpeername().AndReturn(("meh-host",1234))
        self.mockSocket.send('{"operation": "get", "key": "blahKey"}')
        self.mockSocket.recv(DHTClient.BUFFER_SIZE).AndReturn(
            '{"status":{"code":200,"message":"lalala cant found it","data":{"x":1,"y":"xxxxx"}}}')
        self.controller.ReplayAll()

        result = self.client.getKey("blahKey")
        self.controller.VerifyAll()
        self.assertNotEqual(None, result)
        self.assertEqual("xxxxx", result["y"])
        self.assertEqual(1, result["x"])

    def test_shouldReturnResultWhenPutSucceeds(self):
        self.client.getSuitableNode("blahKey").AndReturn(self.mockSocket)
        self.mockSocket.getpeername().AndReturn(("meh-host",1234))
        self.mockSocket.send('{"operation": "put", "value": "randomString", "key": "blahKey"}')
        self.mockSocket.recv(DHTClient.BUFFER_SIZE).AndReturn(
            '{"status":{"code":200,"message":"successfully put it"}}')
        self.client.storeKeyLookupInfo("blahKey","meh-host",1234)

        self.controller.ReplayAll()

        result = self.client.put("blahKey","randomString")
        self.controller.VerifyAll()
        self.assertNotEqual(None, result)


