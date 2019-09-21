#!/usr/bin/python3
# -*-coding:utf-8-*-
# servicecenter.py
import json
import random
from kazoo.client import KazooClient
from kazoo.exceptions import *
from constants import *
from loadbalance import RandomLoadBalance


class ServiceCenter(object):
    def __init__(self, service_type):
        self.zk_client = KazooClient(hosts=":".join([ZK_HOST, str(ZK_PORT)]))
        try:
            self.zk_client.start()
        except Exception as es:
            print("start zk client timeout {}".format(e))
            raise

        self.zk_client.ensure_path(ROOT_PATH)
        self.work_node = ROOT_PATH + "/" + service_type.lower()
        self.service_type = service_type

        self.service_list = set()

        if RANDOM_LOAD_BALANCE:
            self.load_balance = RandomLoadBalance()

    def __del__(self):
        self.zk_client.stop()
        self.zk_client.close()
        self.service_list.clear()

    def register_service(self, service_host, service_port):
        node_value = self._encode_node_value(service_host, service_port)
        if not node_value:
            return

        try:
            self.zk_client.create(self.work_node, node_value, ephemeral=True, sequence=True)
        except ZookeeperError as e:
            print("register_service failed {}".format(e))

    def get_service(self):
        if not len(self.service_list):
            self.get_service_list()

        if not len(self.service_list):
            print("get service list failed")
            return None

        return self.load_balance.select([item for item in self.service_list])

    def get_all_service(self):
        if not len(self.service_list):
            self.get_service_list()

        if not len(self.service_list):
            return None
        return self.service_list

    def get_service_list(self):
        def watch_handler(*args):
            print("nodes change")
            cur_service_list = set()

            for child in self.zk_client.get_children(ROOT_PATH, watch=watch_handler):
                work_nodes = self.zk_client.get(ROOT_PATH + "/" + child)
                service_addr = self._decode_node_value(work_nodes[0])
                if not service_addr:
                    continue
                cur_service_list.add(service_addr)

            new_service_list = cur_service_list - self.service_list
            invalid_service_list = self.service_list - cur_service_list

            for s in invalid_service_list:
                self.service_list.remove(s)
            for s in new_service_list:
                self.service_list.add(s)

        for child in self.zk_client.get_children(ROOT_PATH, watch=watch_handler):
            work_nodes = self.zk_client.get(ROOT_PATH + "/" + child)
            service_addr = self._decode_node_value(work_nodes[0])
            if not service_addr:
                continue
            self.service_list.add(service_addr)

    def _encode_node_value(self, host, port):
        if self.service_type == "rpc":
            addr = ":".join([host, str(port)])
            return json.dumps({"host_addr": addr}).encode()
        print("service type [{}] not support".format(service_type))
        return None

    def _decode_node_value(self, node_value):
        if self.service_type == "rpc":
            return json.loads(node_value)["host_addr"]
        print("service type [{}] not support".format(self.service_type))
        return None

