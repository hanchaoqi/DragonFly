#!/usr/bin/python3
#-*-coding:utf-8-*-
#server.py

ASYNCIO_ENABLE = True

if ASYNCIO_ENABLE:
    from AsyncIORpcServer import AsyncIORpcServer as RpcServer
else:
    from MPMTRpcServer import MPMTRpcServer as RpcServer

def run():
    server = RpcServer("localhost", 8080)
    server.run()
    del server

if __name__ == "__main__":
    run()