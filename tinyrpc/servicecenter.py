#!/usr/bin/python3
#-*-coding:utf-8-*-
#servicecenter.py
import json
import random
from kazoo.client import KazooClient
from kazoo.exceptions import *

ZK_HOST_ = "127.0.0.1"
ZK_PORT_ = 2181
ROOT_PATH_ = "/sc"

class ServiceCenter:
    def __init__(self, service_type):
        self.zk_client = KazooClient(hosts=":".join([ZK_HOST_, str(ZK_PORT_)]))
        try:
            self.zk_client.start()
        except Exception as es:
            print("start zk client timeout %s", e)
            raise

        self.zk_client.ensure_path(ROOT_PATH_)
        self.work_node = ROOT_PATH_ + "/" + service_type.lower()
        self.service_type = service_type

        self.service_list = set()

    def __del__(self):
        self.zk_client.stop()
        self.zk_client.close()
        self.service_list.clear()

    def register_service(self, service_host, service_port):
        node_value = self._encode_node_value(service_host, service_port)

        try:
            self.zk_client.create(self.work_node, node_value, ephemeral=True, sequence=True)
        except ZookeeperError as e:
            print(e)

    def get_service(self):
        if not len(self.service_list):
            self.get_service_list()

        if not len(self.service_list):
            return None

        return random.choice([item for item in self.service_list])

    def get_all_service(self):
        if not len(self.service_list):
            self.get_service_list()

        if not len(self.service_list):
            return None
        return  self.service_list

    def get_service_list(self):
        def watch_handler(*args):
            print("nodes change")
            cur_service_list = set()
            
            for child in self.zk_client.get_children(ROOT_PATH_, watch = watch_handler):
                work_nodes = self.zk_client.get(ROOT_PATH_ + "/" + child)
                service_addr = self._decode_node_value(work_nodes[0])
                cur_service_list.add(service_addr)

            new_service_list = cur_service_list - self.service_list
            invalid_service_list = self.service_list - cur_service_list

            for s in invalid_service_list:
                self.service_list.remove(s)
            for s in new_service_list:
                self.service_list.add(s)
        for child in self.zk_client.get_children(ROOT_PATH_, watch = watch_handler):
            work_nodes = self.zk_client.get(ROOT_PATH_ + "/" + child)
            service_addr = self._decode_node_value(work_nodes[0])
            self.service_list.add(service_addr)

    def _encode_node_value(self, host, port):
        if self.service_type == "rpc":
            addr = ":".join([host, str(port)])
            return json.dumps({"host_addr":addr}).encode()
        print("service type [%s] not support", service_type)
        raise 

    def _decode_node_value(self, node_value):
        if self.service_type == "rpc":
            return json.loads(node_value)["host_addr"]
        print("service type [%s] not support", self.service_type)
        raise


#保存服务端注册地址：失败的时候要根据错误码考虑进行重试
#返回服务端注册地址给客户端：使用roundrobin算法
#保持本地服务列表与服务端同步：注册watcher实现
#当本地与zk断开连接时，尝试先触发一次同步，然后再返回有效数据

