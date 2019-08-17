import sys
sys.path.append("../tinyrpc")

from rpcserver import AIORpcServer
from dispatcher import disp

@disp.add_method
def sum(args):
    result = 0
    if not isinstance(args, list):
        raise Exception

    for i in args:
        result += i
    return result

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 server.py [host] [port]")
        return

    server = AIORpcServer(sys.argv[1], int(sys.argv[2]))
    server.run()
    del server

if __name__ == "__main__":
    main()