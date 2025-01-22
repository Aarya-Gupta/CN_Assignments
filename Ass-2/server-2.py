import time
from socket import *
import sys    # In order to terminate the program
import threading

def handle_client(conn):
    try:
        time.sleep(1)
        message = conn.recv(1024).decode()
        filename = message.split()[1][1:]   # Remove leading '/'
        
        f = open(filename[1:])
        outputdata = f.read()

        # Send one HTTP header line into socket
        conn.send("HTTP/1.1 200 OK\r\n".encode())
        conn.send("Content-Type: text/html\r\n\r\n".encode())
        conn.sendall(outputdata.encode())
    except IOError:
        # Send response message for file not found
        # Send HTTP response message for file not found (404 status)
        conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        conn.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        print("Connection refused as unknown file requested")
        # Close client socket
        connectionSocket.close()
    except:
        print("Error Enconutered")
        connectionSocket.close()


serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
serverPort = 80
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
print('The server is ready to receive')

while True:
    # Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()    
    print(f"Connection from {addr}")

    client_thread = threading.Thread(target = handle_client, args = (connectionSocket,))
    print(f"Number of active client threads: {threading.active_count()}")
    client_thread.start()

serverSocket.close()
sys.exit()  #Terminate the program after sending the corresponding data
