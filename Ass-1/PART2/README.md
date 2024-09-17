Let's implement **Part 2** of the assignment: the **UDP Heartbeat Check**.

In this part, the **client** sends a sequence number and timestamp to the **server**, which calculates the time difference (the time difference between when the client sent the packet and the time the server received it). If the client doesn't receive a response for a specified number of consecutive packets (e.g., 3), it assumes the server has stopped.

Like the previous part, the server simulates a **30% packet loss** rate.

---

### 1. **UDP Heartbeat Server (`UDPHeartbeatServer.py`)**

We will modify the server to calculate the time difference (i.e., latency) and return this value to the client. The server will still simulate 30% packet loss.

#### Server Code:
```python
import random
import time
from socket import *

# Create a UDP socket
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to port 12000
serverSocket.bind(('', 12000))

print("UDP Heartbeat Server is running...")

while True:
    # Generate a random number between 0 and 10
    rand = random.randint(0, 10)

    # Receive the client packet and the client address
    message, address = serverSocket.recvfrom(1024)
    receive_time = time.time()

    # If rand < 4, simulate packet loss (30% packet loss)
    if rand < 4:
        print(f"Simulating packet loss for message from {address}")
        continue

    # Extract sequence number and timestamp from the message
    message_parts = message.decode().split()
    sequence_number = message_parts[1]
    sent_time = float(message_parts[2])

    # Calculate the time difference (latency)
    time_difference = receive_time - sent_time

    # Create response message with the sequence number and time difference
    response_message = f"Seq: {sequence_number}, Time Difference: {time_difference:.6f} seconds"

    # Send the response back to the client
    serverSocket.sendto(response_message.encode(), address)
    print(f"Responded to {address} with {response_message}")
```

#### Steps:
1. The server listens for UDP packets.
2. Upon receiving a packet, it calculates the time difference between the time the packet was sent and the time it was received.
3. It responds with the sequence number and the time difference.
4. The server simulates 30% packet loss by skipping responses for certain packets.

---

### 2. **UDP Heartbeat Client (`UDPHeartbeatClient.py`)**

The client sends UDP Heartbeat packets and waits for a response. If it doesn’t receive a response for 3 consecutive packets, it assumes the server has stopped.

#### Client Code:
```python
import time
import socket

# Create a UDP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(1)  # Set a timeout of 1 second

# Server details
serverAddress = ('localhost', 12000)

# Variables to track consecutive packet losses
consecutive_losses = 0
num_heartbeats = 100  # Set the number of heartbeats to send
max_consecutive_losses = 3  # Assume the server is down if we miss 3 responses

for sequence_number in range(1, num_heartbeats + 1):
    # Record the time the heartbeat was sent
    start_time = time.time()

    # Create the heartbeat message (format: "Heartbeat <sequence_number> <timestamp>")
    message = f"Heartbeat {sequence_number} {start_time}"

    try:
        # Send the heartbeat message to the server
        clientSocket.sendto(message.encode(), serverAddress)
        print(f"Sent: {message}")

        # Receive the server's response
        response, server = clientSocket.recvfrom(1024)

        # If we receive a response, reset the consecutive_losses counter
        consecutive_losses = 0

        # Print the server's response
        print(f"Reply from {server}: {response.decode()}")

    except socket.timeout:
        # Increment consecutive losses if a response is not received within 1 second
        consecutive_losses += 1
        print(f"Heartbeat {sequence_number}: Request timed out")

        # If 3 consecutive losses are detected, assume the server has stopped
        if consecutive_losses >= max_consecutive_losses:
            print("Server is assumed to have stopped after 3 consecutive timeouts.")
            break

# Close the socket after the loop finishes
clientSocket.close()
```

#### Steps:
1. The client sends **100 heartbeat packets** to the server with a sequence number and timestamp.
2. The client waits for up to 1 second for the server to respond.
3. If the client doesn’t receive a response for **3 consecutive heartbeats**, it assumes the server has stopped and exits the loop.
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

1. **Run the Server**:
   - First, start the server by running:
     ```bash
     python UDPHeartbeatServer.py
     ```

2. **Run the Client**:
   - Then, run the client:
     ```bash
     python UDPHeartbeatClient.py
     ```

The client will send heartbeats to the server and monitor for responses. If it misses 3 consecutive responses, it will stop and print that the server has stopped.

---

This approach should satisfy Part 2 of your assignment. Let me know if you need further clarification!