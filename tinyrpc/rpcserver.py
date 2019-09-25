#!/usr/bin/python3
# -*-coding:utf-8-*-
# rpcserver.py

import socket
import json
import select
import queue
from exceptions import *
from constants import *
from dispatcher import disp
from servicecenter import ServiceCenter


class AIORpcServer(object):

    def __init__(self, host, port, timeout=10):
        self.sc_ = ServiceCenter(RPC_NODE_NAME)
        self.sc_.register_service(host, port)

        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_.setblocking(False)
        self.sock_.bind((host, port))
        self.sock_.listen(5)

        self.epoll_ = select.epoll()
        self.epoll_.register(self.sock_.fileno(), select.EPOLLIN)

        self.msg_queue_ = {}
        self.fd_2_socket_ = {self.sock_.fileno(): self.sock_}

        self.timeout_ = timeout   # second

    def __del__(self):
        self.epoll_.unregister(self.sock_.fileno())
        self.epoll_.close()
        self.sock_.close()

    def run(self):
        self.__loop()

    def __loop(self):
        while True:
            try:
                events = self.epoll_.poll(self.timeout_)
            except Exception as e:
                print("poll failed {}".format(e))
                break
            else:
                if len(events) == 0:
                    print("no msg")
                    continue
                for fd, event in events:
                    sock = self.fd_2_socket_[fd]

                    if sock == self.sock_:
                        self.__handle_conn(sock)
                    elif event & select.EPOLLIN:
                        self.__handle_req(sock)
                    elif event & select.EPOLLOUT:
                        self.__handle_rsp(sock)
                    elif event & select.EPOLLHUP:
                        self.__handle_close(fd)
                    else:
                        print("ERROR EVENT [{}] [{}]".format(fd, event))

    def __handle_conn(self, sock):
        try:
            conn, addr = sock.accept()
        except Exception as e:
            print("accept failed {}".format(e))
        else:
            conn.setblocking(False)

            self.epoll_.register(conn, select.EPOLLIN)
            self.fd_2_socket_[conn.fileno()] = conn
            self.msg_queue_[conn] = queue.Queue()

    def __handle_req(self, sock):
        try:
            req_data = ""
            while True:
                raw_data = sock.recv(RECV_BUFF_SIZE)
                if raw_data:
                    req_data += raw_data.decode()
                if len(raw_data) < RECV_BUFF_SIZE:
                    break
        except ConnectionResetError as e:
            print("client reset connection")
            self.epoll_.modify(sock.fileno(), select.EPOLLHUP)
            return
        except BlockingIOError as e:
            print("recv no data")
            return

        if len(req_data) == 0:
            print("client broken")
            self.epoll_.modify(sock.fileno(), select.EPOLLHUP)
            return

        for data in req_data.split("\r\n"):
            req_body = json.loads(data)
            print("[{}] recv {} {}".format(req_body["vkey"], req_body["func"], req_body["params"]))

            result = 0
            try:
                result = disp[req_body["func"]](req_body["params"])
            except KeyError:
                err_code = 1
            except Exception:
                err_code = 2
            else:
                err_code = 0

            print("[{}] result {} {}".format(req_body["vkey"], err_code, result))

            rsp_data = json.dumps({"vkey": req_body["vkey"], "err_code": err_code, "result": result})
            self.msg_queue_[sock].put(rsp_data.encode())
        self.epoll_.modify(sock.fileno(), select.EPOLLOUT)

    def __handle_rsp(self, sock):
        try:
            rsp_body = self.msg_queue_[sock].get_nowait()
        except queue.Empty:
            self.epoll_.modify(sock.fileno(), select.EPOLLIN)
        else:
            sock.sendall(rsp_body)

    def __handle_close(self, fd):
        self.epoll_.unregister(fd)
        self.fd_2_socket_[fd].close()
        del self.fd_2_socket_[fd]


