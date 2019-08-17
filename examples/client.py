import sys
import time
sys.path.append("../tinyrpc")

from rpclient import RpClient

def main():
    client = RpClient()
    for i in range(100):
        result = client.call("sum", i, i+3)
        print("result {}".format(result))
        time.sleep(1)
    del client

if __name__ == '__main__':
    main()

