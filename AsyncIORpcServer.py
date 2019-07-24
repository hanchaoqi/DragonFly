#!/usr/bin/python3
#-*-coding:utf-8-*-
#AsyncIORpcServer.py

import socket
import struct
import json
import select
import queue

class AsyncIORpcServer:
    def __init__(self, host, port):
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_.setblocking(False)
        self.sock_.bind((host, port))
        self.sock_.listen(5)

        self.epoll = select.epoll()
        self.epoll.register(self.sock_.fileno(), select.EPOLLIN)

        self.msg_queue = {}
        self.fd_2_socket = {self.sock_.fileno():self.sock_}

        self.timeout = 10

    def __del__(self):
        self.epoll.unregister(self.sock_.fileno())
        self.epoll.close()
        self.sock_.close()

    def run(self):
        self.loop()

    def loop(self):
        while True:
            events = self.epoll.poll(self.timeout)
            if len(events) == 0:
                print("no msg")
                continue
            for fd, event in events:
                sock = self.fd_2_socket[fd]

                if sock == self.sock_:
                    self.handle_conn(sock)
                elif event & select.EPOLLIN:
                    self.handle_req(sock)
                elif event & select.EPOLLOUT:
                    self.handle_rsp(sock)
                elif event & select.EPOLLHUP:
                    self.handle_close(fd)
                else:
                    print("ERROR EVENT [{}] [{}]".format(fd, event))

    def handle_conn(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)

        self.epoll.register(conn, select.EPOLLIN)
        self.fd_2_socket[conn.fileno()] = conn
        self.msg_queue[conn] = queue.Queue()

    def handle_req(self, sock):
        raw_datas = sock.recv(1024)

        if not raw_datas:
            return
        
        for data in raw_datas.decode().split("\r\n"):
            req_body = json.loads(data)
            print("[{}] recv {} {}".format(req_body["vkey"], req_body["func"], req_body["params"]))

            result = -1
            err_code = 0
            err_code, result = self.dispatcher(req_body["func"], req_body["params"])        
            print("[{}] result {} {}".format(req_body["vkey"], err_code, result))

            rsp_data = json.dumps({"vkey":req_body["vkey"], "err_code":err_code, "result":result})
            self.msg_queue[sock].put(rsp_data.encode())
        self.epoll.modify(sock.fileno(), select.EPOLLOUT)
          
    def handle_rsp(self, sock):
        try:
            rsp_body = self.msg_queue[sock].get_nowait()
        except queue.Empty:
            print("[{}] queue empty".format(sock))
            self.epoll.modify(sock.fileno(), select.EPOLLIN)
        else:
            sock.sendall(rsp_body)

    def handle_close(self, fd):
        self.epoll.unregister(fd)
        self.fd_2_socket[fd].close()
        del self.fd_2_socket[fd]

    def dispatcher(self, func_name, params):
        err_code = 0
        result = -1
        if func_name == "add":
            result = self.add(params[0], params[1])
        else:
            err_code = -1
        return err_code, result

    def add(self, x, y):
        return x+y

