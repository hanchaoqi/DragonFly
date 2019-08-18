#!/usr/bin/python3
#-*-coding:utf-8-*-
#rpclient.py

import json
import time
import socket
import struct
from utils import set_timeout
from servicecenter import ServiceCenter

class RpClient:
    def __init__(self, timeout=5):
        self.sc_ = ServiceCenter("rpc")
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.index_ = 0
        self.timeout_ = timeout  # second

        self._connect()

    def __del__(self):
        self.sock.close()

    @set_timeout(self.timeout_)
    def call(self, func, *args):
        print("call {} {} {}".format(self.service_addr_, func, args))
        self._send_command(func, args)
        return self._recv_response()

    def _connect(self):
        try:
            self.service_addr_ = self.sc_.get_service()
            if self.service_addr_:
                host, port = self.service_addr_.split(":")
                self.sock_.connect((host, int(port)))
        except ConnectionError as e:
            print("connect {} failed {}".format(self.service_addr_, e))
            return

    def _send_command(self, func, args):
        self.index += 1
        req_body =json.dumps({"vkey":self.index, "func":func, "params":args})
        try:
            self.sock.sendall(req_body.encode())
        except Exception as e:
            print("send data failed {}".format(e))
        

    def _recv_response(self):
        rsp_body_raw = self.sock.recv(1024)
        rsp_body = json.loads(rsp_body_raw.decode())

        if rsp_body["err_code"] != 0:
            print("rsp error")
            return -1
        return rsp_body["result"]

