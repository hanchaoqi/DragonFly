#!/usr/bin/python3
#-*-coding:utf-8-*-
#rpclient.py

import json
import time
import socket
import struct
from utils import set_timeout
from servicecenter import ServiceCenter

RPC_TIMEOUT = 20  # second

class RpClient:
    def __init__(self, timeout=10):
        self.sc_ = ServiceCenter("rpc")
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_.settimeout(timeout)
        self.index_ = 0
        self.conn_flag = False

    def __del__(self):
        self.sock_.close()
        self.conn_flag = False      

    # 客户端只有此一个对外接口
    @set_timeout(RPC_TIMEOUT)
    def call(self, func, *args):
        print("call {} {}".format(func, args))
        try:
            self._send_command(func, args)
            result = self._recv_response()
        except socket.timeout as e:
            print("rpc call timeout")
            raise RpCallException()
        except Exception as e:
            print("rpc call failed {}".format(e))
            self.conn_flag = False
            raise RpCallException()
        else:
            return result

    def _connect(self):
        try:
            service_addr = self.sc_.get_service()
            if service_addr:
                host, port = service_addr.split(":")
                self.sock_.connect((host, int(port)))
        except Exception as e:
            print("connect {} failed {}".format(service_addr, e))
            raise e
        print("connect {} success".format(service_addr))
        return True

    def _send_command(self, func, args):
        self.index_ += 1
        req_body =json.dumps({"vkey":self.index_, "func":func, "params":args})
        if not self.conn_flag:
            self._connect()
            self.conn_flag = True
        self.sock_.sendall(req_body.encode())

    def _recv_response(self):
        rsp_body_raw = self.sock_.recv(1024)
        rsp_body = json.loads(rsp_body_raw.decode())

        if rsp_body["err_code"] != 0:
            print("rsp error")
            return -1
        return rsp_body["result"]

