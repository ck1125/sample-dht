#!/usr/bin/env python 

""" 

Node server that serves as a kv store

Each node server is responsible for holding access to a number of key-value pairs
This implementation has a few shortcomings:
1. It doesn't currently restrict the number of key value pairs stored on each node.
The kv pairs can live forever. To make it production ready the k-v store on each node should
also implement some LRU caching mechanism to ensure that storage for kv pairs can be reclaimed after
some pre-configured time.

"""
import json

import socket
from json import *
from string import Template
import sys

import logging
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger('root')

class DHTNodeServer:
    BUFFER_SIZE = 1024
    host = 'localhost'
    s = None
    backlog = 5
    hashTable = {}

    def __init__(self, port):
        """

        Construct a nodeserver object with the desired port
        """
        self.port = port

    def start(self):
        """

        Used to start the nodeserver on the local machine so it is ready to receive requests from clients
        """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.host, self.port))
            self.s.listen(self.backlog)
            logging.debug("nodeserver started.")
        except socket.error, (value, message):
            if self.s:
                self.s.close()
            logging.debug("Could not open socket: " + message)
            sys.exit(1)
        while 1:
            client, address = self.s.accept()
            data = client.recv(DHTNodeServer.BUFFER_SIZE)
            if data:
                serverResponse = self.handle(data)
                logging.debug(serverResponse)
                client.send(serverResponse)
            client.close()


    def handleGetOperation(self, decoded):
        print "Received get"
        if 'key' in decoded:
            key = decoded['key']
            if key in self.hashTable:
                return self.buildServerResponse(200, "get received", self.hashTable[key])
            else:
                return self.buildServerResponse(404, "key not found")
        else:
            return self.buildServerResponse(400, "invalid get request received")

    def handlePutOperation(self, decoded):
        logging.debug("Received put")
        if 'key' in decoded and 'value' in decoded:
            self.hashTable[decoded['key']] = decoded['value']
            return self.buildServerResponse(200, "put received")
        else:
            return self.buildServerResponse(400, "invalid put request received")

    def handleInvalidOperation(self):
        logging.debug("Unsupported operation")
        return self.buildServerResponse(500, "Unsupported operation")

    def handle(self, data):
        logging.debug("Received: " + data)
        decoded = JSONDecoder().decode(data)

        if 'operation' in decoded:
            hashOperation = decoded['operation']
            if hashOperation == 'get':
                return self.handleGetOperation(decoded)
            elif hashOperation == 'put':
                return self.handlePutOperation(decoded)
            else:
                return self.handleInvalidOperation()
        else:
            return self.handleInvalidOperation()

    def buildServerResponse(self, code, message, data=None):
        if data == None:
            return Template('{"status": {"code": $code, "message": "$message" }}').substitute(code=code,
                                                                                              message=message)
        else:
            return Template('{"status": {"code": $code, "message": "$message", "data": $data }}').substitute(code=code,
                                                                                                             message=message
                                                                                                             ,
                                                                                                             data=json.dumps(
                                                                                                                 data))


    def stop(self):
        if self.s:
            self.s.close()


def usage():
    print "Usage: python dhtnodeserver.py <port> where port number is the local port number on which to start the DHT node server"

if __name__ == '__main__':
    if (len(sys.argv) == 2):
        try:
            port = int(sys.argv[1])
        except ValueError:
            usage()
            sys.exit(1)
        logging.debug("Starting nodeserver on port " + sys.argv[1] + " ...")
        nodeserver = DHTNodeServer(port)
        nodeserver.start()
    else:
        usage()
