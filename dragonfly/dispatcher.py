#!/usr/bin/python3
# -*-coding:utf-8-*-
# dispatcher.py
import collections
import functools


class Dispatcher(collections.MutableMapping):
    def __init__(self):
        self.method_map = dict()

    def __getitem__(self, key):
        return self.method_map[key]

    def __setitem__(self, key, value):
        self.method_map[key] = value

    def __delitem__(self, key):
        del self.method_map[key]

    def __iter__(self):
        return iter(self.method_map)

    def __len__(self):
        return len(self.method_map)

    def add_method(self, func=None, name=None):
        if name and not func:
            functools.partial(self.add_method, name=name)

        self.method_map[name or func.__name__] = func
        return func

disp = Dispatcher()

