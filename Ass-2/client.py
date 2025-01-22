import sys
from socket import *

if len(sys.argv) != 4:
    print("Usage: client.py server_host server_port filename")
    sys.exit()

server_host = sys.argv[1]
server_port = int(sys.argv[2])
filename = sys.argv[3]
clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    clientSocket.connect((server_host, server_port))
    request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\n\r\n"
    clientSocket.send(request.encode())
    response = clientSocket.recv(4096)
    while len(response) > 0:
        print(response.decode(), end='')
        response = clientSocket.recv(4096)

except Exception as e:
    print(f"Error: {e}")

finally:
    clientSocket.close()

# To run execute the command : python client.py 127.0.0.1 80 webpage.html
