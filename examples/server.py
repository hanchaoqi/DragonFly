import sys
sys.path.append("../tinyrpc")

from rpcserver import AIORpcServer

def main():
    server = AIORpcServer("localhost", 8080)
    server.run()
    del server

if __name__ == "__main__":
    main()