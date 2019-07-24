#!/usr/bin/python3
#-*-coding:utf-8-*-
#client.py

import json
import time
import socket
import struct
from util import set_timeout

class RpClient:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.index = 0

    def __del__(self):
        self.sock.close()

    def send_command(self, func, args):
        self.index += 1
        req_body =json.dumps({"vkey":self.index, "func":func, "params":args})

        self.sock.sendall(req_body.encode())

    def recv_response(self):
        rsp_body_raw = self.sock.recv(1024)
        rsp_body = json.loads(rsp_body_raw.decode())

        if rsp_body["err_code"] != 0:
            print("rsp error")
            return -1
        return rsp_body["result"]

    @set_timeout(5)
    def call(self, func, *args):
        print("call {} {}".format(func, args))
        self.send_command(func, args)
        return self.recv_response()

if __name__ == '__main__':
    client = RpClient("localhost", 8080)
    for i in range(10):
        result = client.call("add", i, i+3)
        print("result {}".format(result))
        time.sleep(1)
    del client