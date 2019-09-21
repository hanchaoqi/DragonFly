#!/usr/bin/python3
# -*-coding:utf-8-*-
# utils.py

import signal
import exceptions


def set_timeout(time_threshold):
    def wrapper(func):
        def handler(signum, frame):
            raise TimeOutException()

        def deco(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(time_threshold)
            ret = func(*args, **kwargs)
            signal.alarm(0)
            return ret

        return deco
    return wrapper


    