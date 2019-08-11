import sys
import time
sys.path.append("../tinyrpc")

from rpclient import RpClient

def main():
    client = RpClient("localhost", 8080)
    for i in range(10):
        result = client.call("add", i, i+3)
        print("result {}".format(result))
        time.sleep(1)
    del client   

if __name__ == '__main__':
    main()