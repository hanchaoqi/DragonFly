#!/usr/bin/python3
# -*-coding:utf-8-*-
# loadbalance.py
import abc
from exceptions import RpcException
import random


class AbstractLoadBalance(metaclass=abc.ABCMeta):
    def select(self, service_list):
        print(service_list)
        if not isinstance(service_list, list):
            raise RpcException("Invalid para, service_list must is list")

        if not len(service_list):
            return None

        if len(service_list) == 1:
            return service_list[0]

        return self.do_select(service_list)

    @abc.abstractmethod
    def do_select(self, service_list):
        pass

    # TODO:后面使用实例化的客户端作为service时，再具体实现
    def _get_weight(self, one_service):
        return random.randint(1, 10)


class RandomLoadBalance(AbstractLoadBalance):
    def do_select(self, service_list):
        all_weight_equal = True
        total_weights = 0

        weigths_list = [self._get_weight(service) for service in service_list]

        for index, weight in enumerate(weigths_list):
            total_weights += weight

            if all_weight_equal and (index > 0) and (weight != weigths_list[index - 1]):
                all_weight_equal = False

        if total_weights > 0 and not all_weight_equal:
            offset = random.randint(1, total_weights)

            for index, weight in enumerate(weigths_list):
                offset = weight - offset
                if offset < 0:
                    return service_list[index]

        return random.choice(service_list)


