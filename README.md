# DragonFly
一个轻量级分布式RPC框架

## 整体架构
![整体架构](documents/整体架构.png)

## 使用说明
- 代码实现
  1. 暴露远程调用函数
  ```
    from dispatcher import disp

    # 使用装饰器暴露该函数
    @disp.add_method
    def Func1(args):
        pass
  ```
  2. 启动Rpc服务端
  ```
    from rpcserver import RpcServer

    # 启动服务端，需要指定所监听的IP和Port
    server = RpcServer(HOST_IP, HOST_PORT)
    server.run()
  ```
  3. 远程调用
  ```
    from rpclient import RpClient

    client = RpClient()
    result = client.call("Func1", arg1, arg2, ...)
  ```

- 环境依赖及配置
  1. 注册中心依赖ZooKeeper
  2. constants.py中配置了注册中心需要的各个参数


## 启动示例
1. 启动zookeeper
2. constants.py中配置注册中心的zookeeper相关参数
3. 切到examples目录
4. 启动服务端示例(可启动多个)：`python3 server.py [host] [port]`
5. 启动客户端示例(可启动多个)：`python3 client.py`

## 特性支持

- [x] 函数级别同步远程调用
- [x] Josn格式数据传输
- [x] 服务端实例级别分布式，支持负载均衡与故障转移
- [ ] 异步远程调用
- [ ] 共享客户端
- [ ] 数据传输协议可配置
- [ ] 负载均衡算法：一致性hash