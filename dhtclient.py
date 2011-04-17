#!/usr/bin/env python 

"""

Client to in-memory DHT distributed nodes. Can be constructed with a list of node details(host and port).
It currently implements a very limited key-distribution algorithm using the random.choice method.
A production-ready version would implement a more suitable algorithm to ensure that nodes
are not overloaded and to minimize traffic.
"""

import json
import random
import socket
from json import JSONDecoder
from string import Template
import logging
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger('root')

class DHTClient:
    BUFFER_SIZE = 1024
    PUT_OPERATION = "put"
    GET_OPERATION = "get"

    __nodeList = []
    __keyNodeMap = {}

    def __init__(self, *nodelist):
        for node in nodelist:
            self.__nodeList.append(node)

    def connect(self, host, port):
        """
        Makes a connection to the node defined by host and port
        Returns None in the event that it fails to make a connection
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            return s
        except socket.error, (value, message):
            if s:
                s.close()
                logging.debug("Could not open socket: " + message)
                return None

    def getSuitableNode(self, key):
        """

        Returns a socket connection to a suitable node for supplied key
        This implementation currently picks a node at random to connect to in the event that a key's node
        isn't present in the keyNodeMap.
        In future i.e. to be production ready it can be modified so that selected node is driven
        by a suitable key distribution algorithm
        Analytics is also required so that cache misses are identified and can be optimized.
        """

        logging.debug(self.__keyNodeMap)
        if key in self.__keyNodeMap:
            node = self.__keyNodeMap[key]
            logging.debug(Template("connecting to $host and $port").substitute(host=node["host"], port=node["port"]))
            return self.connect(node["host"], node["port"])
        else:
            node = random.choice(self.__nodeList)
            selected = random.choice(node)
            logging.debug(Template("connecting to random $host and $port").substitute(host=selected["host"],
                                                                                      port=selected["port"]))
            return self.connect(selected["host"], selected["port"])

    def getKey(self, key):
        """
        Retrieves a key from a suitable node. Again
        """
        socket = self.getSuitableNode(key)
        if socket != None:
            payload = self.__buildGetPayLoad(key)
            payloadString = json.dumps(payload)
            host, port = socket.getpeername()
            socket.send(payloadString)
            data = socket.recv(DHTClient.BUFFER_SIZE)
            decoded = JSONDecoder().decode(data)
            if decoded["status"]["code"] != 200:
                return None
            else:
                self.storeKeyLookupInfo(key, host, port)
                return decoded["status"]["data"]
        else:
            return None


    def storeKeyLookupInfo(self, key, host, port):
        self.__keyNodeMap[key] = {"host": host, "port": port}

    def put(self, key, value):
        """

        Saves a k-v pair to the most suitable nodeserver instance
        """
        socket = self.getSuitableNode(key)
        if socket != None:
            host, port = socket.getpeername()
            payload = self.__buildPutPayLoad(key, value)
            payloadString = json.dumps(payload)
            socket.send(payloadString)
            data = socket.recv(DHTClient.BUFFER_SIZE)
            decoded = JSONDecoder().decode(data)
            if decoded["status"]["code"] != 200:
                return False
            else:
                self.storeKeyLookupInfo(key, host, port)
                return True
        else:
            return False

    def __buildGetPayLoad(self, key):
        payload = {}
        payload["operation"] = DHTClient.GET_OPERATION
        payload["key"] = key
        return payload

    def __buildPutPayLoad(self, key, value):
        payload = {}
        payload["operation"] = DHTClient.PUT_OPERATION
        payload["key"] = key
        payload["value"] = value
        return payload


if __name__ == '__main__':
    client = DHTClient([{"host": "localhost", "port": 2345}, {"host": "localhost", "port": 2346}])

    result = client.put("blahKey","sample value 1")
    while (result == False):
        result = client.put("blahKey","sample value 1")

    result = client.put("blahKey2","sample value 2")
    while (result == False):
        result = client.put("blahKey2","sample value 2")

    result = client.put("blahKey3","sample value 3")
    while (result == False):
        result = client.put("blahKey3","sample value 3")

    logger.debug(Template("value for blahKey = $value").substitute(value=client.getKey('blahKey')))
    logger.debug(Template("value for blahKey1 = $value").substitute(value=client.getKey('blahKey1')))
    logger.debug(Template("value for blahKey2 = $value").substitute(value=client.getKey('blahKey2')))
    logger.debug(Template("value for blahKey3 = $value").substitute(value=client.getKey('blahKey3')))
