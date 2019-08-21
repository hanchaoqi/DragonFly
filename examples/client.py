import sys
import time
sys.path.append("../tinyrpc")

from rpclient import RpClient
from utils import *

def main():
    client = RpClient()
    for i in range(10):
        try:
            result = client.call("sum", i, i+3)
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        else:
            print("result {}".format(result))
            time.sleep(1)
    del client

if __name__ == '__main__':
    main()

