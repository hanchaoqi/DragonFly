#!/usr/bin/python3
#-*-coding:utf-8-*-
#rpcserver.py

import socket
import json
import select
import queue
from dispatcher import disp

class AIORpcServer:
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
        try:
            conn, addr = sock.accept()
        except Exception as e:
            print(str(e))
        else:
            conn.setblocking(False)

            self.epoll.register(conn, select.EPOLLIN)
            self.fd_2_socket[conn.fileno()] = conn
            self.msg_queue[conn] = queue.Queue()

    def handle_req(self, sock):
        try:
            req_data = ""
            while True:
                raw_data = sock.recv(1024)
                if raw_data:
                    req_data += raw_data.decode()
                if len(raw_data) < 1024:
                    break
        except ConnectionResetError as e:
            print("client reset connection")
            self.epoll.modify(sock.fileno(), select.EPOLLHUP)
            return
        except BlockingIOError as e:
            print("recv no data")
            return

        if len(req_data) == 0:
            print("client broken")
            self.epoll.modify(sock.fileno(), select.EPOLLHUP)
            return

        for data in req_data.split("\r\n"):
            req_body = json.loads(data)
            print("[{}] recv {} {}".format(req_body["vkey"], req_body["func"], req_body["params"]))

            try:
                result = disp[req_body["func"]](req_body["params"])
            except KeyError:
                err_code = -1
                result = 0
            else:
                err_code = 0
 
            print("[{}] result {} {}".format(req_body["vkey"], err_code, result))

            rsp_data = json.dumps({"vkey":req_body["vkey"], "err_code":err_code, "result":result})
            self.msg_queue[sock].put(rsp_data.encode())
        self.epoll.modify(sock.fileno(), select.EPOLLOUT)
          
    def handle_rsp(self, sock):
        try:
            rsp_body = self.msg_queue[sock].get_nowait()
        except queue.Empty:
            self.epoll.modify(sock.fileno(), select.EPOLLIN)
        else:
            sock.sendall(rsp_body)

    def handle_close(self, fd):
        self.epoll.unregister(fd)
        self.fd_2_socket[fd].close()
        del self.fd_2_socket[fd]