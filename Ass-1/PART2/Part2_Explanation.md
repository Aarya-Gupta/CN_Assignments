**The UDP Heartbeat Check**.

In this part, the **client** sends a sequence number and timestamp to the **server**, which calculates the time difference (the time between when the client sent the packet and the time the server received it). If the client doesn't receive a response for a specified number of consecutive packets (e.g., 3), we assume the server has stopped.

Similar to the previous part, we simulate a **30% packet loss** rate on the server side.

---

### 1. **UDP Heartbeat Server (`UDPHeartbeatServer.ipynb`)**

Modifying the server to calculate the time difference (i.e., latency) and return this value to the client. The server will still simulate 30% packet loss.

#### Server Code:
```python
import random
import time
from socket import *

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('', 12000))

print("UDP Heartbeat Server is running...")

while True:
    rand = random.randint(0, 10)

    message, address = serverSocket.recvfrom(1024)
    receive_time = time.time()

    if rand < 4:
        print(f"Simulating packet loss for message from {address}")
        continue

    # Extracting sequence number and timestamp from the message
    message_parts = message.decode().split()
    sequence_number = message_parts[1]
    sent_time = float(message_parts[2])

    # Calculating the latency
    time_difference = receive_time - sent_time

    response_message = f"Seq: {sequence_number}, Time Difference: {time_difference:.6f} seconds"

    # Sending the response back to the client
    serverSocket.sendto(response_message.encode(), address)
    print(f"Responded to {address} with {response_message}")
```

#### Steps:
1. We listen for UDP packets on the server.
2. Upon receiving a packet, the server calculates the time difference between when the packet was sent and when it was received.
3. It responds with the sequence number and the time difference.
4. The server simulates 30% packet loss by not responding to certain packets.

---

### 2. **UDP Heartbeat Client (`UDPHeartbeatClient.ipynb`)**

The client sends UDP Heartbeat packets and waits for a response. If it doesn’t receive a response for 3 consecutive packets, we assume the server has stopped.

#### Client Code:
```python
import time
import socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(1)  # Set a timeout of 1 second

# Server details
serverAddress = ('localhost', 12000)

# Tracking consecutive packet losses
consecutive_losses = 0
num_heartbeats = 100        # number of heartbeats to send
max_consecutive_losses = 3  # Assuming the server is down if we miss 3 responses

for sequence_number in range(1, num_heartbeats + 1):
    start_time = time.time() # Starting time; when the heartbeat was sent.

    # format: "Heartbeat <sequence_number> <timestamp>"
    message = f"Heartbeat {sequence_number} {start_time}"

    try:
        # Sending the heartbeat message to the server
        clientSocket.sendto(message.encode(), serverAddress)
        print(f"Sent: {message}")

        # Receiving the server's response
        response, server = clientSocket.recvfrom(1024)

        # If we receive a response, then reset the consecutive_losses counter
        consecutive_losses = 0

        # Server's response
        print(f"Reply from {server}: {response.decode()}")

    except socket.timeout:
        # Increment consecutive losses if a response is not received within 1 second
        consecutive_losses += 1
        print(f"Heartbeat {sequence_number}: Request timed out")

        # If 3 consecutive losses are detected, assume the server has stopped
        if consecutive_losses >= max_consecutive_losses:
            print("Server is assumed to have stopped after 3 consecutive timeouts.")
            break

clientSocket.close()
```

#### Steps:
1. The client sends **100 heartbeat packets** to the server with a sequence number and timestamp.
2. The client waits for up to 1 second for a response.
3. If the client doesn’t receive a response for **3 consecutive heartbeats**, we assume the server has stopped and exit the loop.
4. The client prints the server's response (which includes the time difference) if received.

---

### Explanation of Part 2:

1. **Server Functionality**:
   - The server listens for incoming UDP Heartbeat packets.
   - Upon receiving a packet, it calculates the time difference (latency) between when the packet was sent and when it was received.
   - It sends the time difference back to the client.
   - The server randomly drops 30% of packets to simulate packet loss.

2. **Client Functionality**:
   - The client sends Heartbeat packets (with a sequence number and timestamp) to the server.
   - It waits for a response from the server. If no response is received within 1 second, it assumes the packet was lost.
   - If the client experiences 3 consecutive packet losses (i.e., 3 heartbeats without a response), it assumes the server has stopped and exits.

---

### Steps to Run Part 2:

1. **Run the Server 'UDPHeartbeatServer.ipynb'**:

2. **Run the Client 'UDPHeartbeatClient.ipynb'**:

The client will send heartbeats to the server and monitor for responses. If it misses 3 consecutive responses, it will stop and print that the server has stopped.

---