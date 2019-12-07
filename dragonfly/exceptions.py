#!/usr/bin/python3
# -*-coding:utf-8-*-
# exceptions.py


class TimeOutException(Exception):
    def __init__(self, error="Timeout"):
        Exception.__init__(self, error)


class RpcException(Exception):
    def __init__(self, error="rpc call failed"):
        Exception.__init__(self, error)

