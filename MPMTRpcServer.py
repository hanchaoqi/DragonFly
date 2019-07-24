#!/usr/bin/python3
#-*-coding:utf-8-*-
#MPMTRpcServer.py

import socket
import struct
import json
import os
from threading import Thread

class MPMTRpcServer:
    def __init__(self, host, port, cnt = 3):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        self.process_num = cnt

    def __del__(self):
        self.sock.close()

    def run(self):
        self.pre_forking()

    def pre_forking(self):
        for i in range(self.process_num):
            pid = os.fork()
            if pid == 0:
                continue
            elif pid > 0:
                self.loop()
                break
            else:
                print("fork error")
                return

    def loop(self):
        while True:
            conn, addr = self.sock.accept() 
            try:
                thread_handler = Thread(target=self.handle_conn, args=(conn,))
                thread_handler.start()
            except Exception as e:
                print("Exception:", e)
                raise

    def handle_conn(self, conn):
        with conn:
            while True:
                req_body_raw = conn.recv(1024)
                if len(req_body_raw) == 0:
                    print("bye")
                    return

                req_body = json.loads(req_body_raw.decode())

                result = -1
                err_code = 0
                print("recv {} {}".format(req_body["func"], req_body["params"]))
                err_code, result = self.dispatcher(req_body["func"], req_body["params"])        
                self.send_rsp(conn, req_body["vkey"], err_code, result)

    def dispatcher(self, func_name, params):
        err_code = 0
        result = -1
        if func_name == "add":
            result = self.add(params[0], params[1])
        else:
            err_code = -1
        return err_code, result

    def send_rsp(self, conn, vkey, error_code, data):
        rsp_body  = json.dumps({"vkey":vkey, "err_code":error_code, "result":data})

        conn.sendall(rsp_body.encode())

    def add(self, x, y):
        return x+y

