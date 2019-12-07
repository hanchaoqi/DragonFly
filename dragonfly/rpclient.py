#!/usr/bin/python3
# -*-coding:utf-8-*-
# rpclient.py

import json
import time
import socket
import struct
from exceptions import *
from constants import *
from utils import set_timeout
from servicecenter import ServiceCenter


class RpClient(object):

    def __init__(self, timeout=SOCK_TIMEOUT_DEFAULT):
        self.sc_ = ServiceCenter(RPC_NODE_NAME)
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_.settimeout(timeout)
        self.index_ = 0
        self.conn_flag = False

    def __del__(self):
        self.sock_.close()
        self.conn_flag = False

    # 客户端只有此一个对外接口
    @set_timeout(RPC_TIMEOUT_DEFAULT)
    def call(self, func, *args):
        print("call {} {}".format(func, args))
        try:
            self.__send_command(func, args)
            result = self.__recv_response()
        except socket.timeout as e:
            raise RpcException("rpc call timeout")
        except Exception as e:
            self.conn_flag = False
            raise RpcException("rpc call failed {}".format(e))
        else:
            return result

    def __connect(self):
        service_addr = None
        try:
            service_addr = self.sc_.get_service()

            if service_addr:
                host, port = service_addr.split(":")
                self.sock_.connect((host, int(port)))
        except Exception as e:
            raise RpcException("connect {} failed {}".format(service_addr, e))
        print("connect {} success".format(service_addr))

    def __send_command(self, func, args):
        self.index_ += 1
        req_body = json.dumps({"vkey": self.index_, "func": func, "params": args})
        if not self.conn_flag:
            self.__connect()
            self.conn_flag = True
        self.sock_.sendall(req_body.encode())

    def __recv_response(self):
        rsp_body_raw = self.sock_.recv(RECV_BUFF_SIZE)
        rsp_body = json.loads(rsp_body_raw.decode())

        if rsp_body["err_code"] != 0:
            raise RpcException("rpc resp error {}".format(rsp_body["err_code"]))
        return rsp_body["result"]


