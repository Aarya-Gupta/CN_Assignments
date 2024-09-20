# UDP Pinger Lab

## Course: CSE 232, Section B - Computer Networks

**Team Members**: [Aarya Gupta (2022006), Adarsh Jha (2022024)]

---

## Project Overview

In this project, we implemented a basic UDP Ping application and extended it into a UDP Heartbeat application. The objective was to learn the fundamentals of socket programming using UDP, understand packet loss simulation, and calculate network statistics like round-trip time (RTT) and packet loss rate.

---

## Part 1: UDP Pinger Application

### 1. **UDP Pinger Server (`UDPPingerServer.ipynb`)**

This is the server code we need to run first. It listens on a specific port and randomly drops packets to simulate network packet loss. It responds by capitalizing the message it receives if the packet is not "lost."

#### Server Code:

```python
import random
from socket import *

serverSocket = socket(AF_INET, SOCK_DGRAM)

# Binding the socket to a 12000 port 
serverSocket.bind(('', 12000))

print("UDP Pinger Server is running...")

while True:
    rand = random.randint(0, 10)
    message, address = serverSocket.recvfrom(1024)
    message = message.upper()
    # If random number < 4, simulate packet loss
    if rand < 4:
        print(f"Simulating packet loss for message from {address}.")
        continue

    serverSocket.sendto(message, address)
    print(f"Responding to {address} with message: {message.decode()}")
```

#### Steps to Run the Server:
1. Run `UDPPingerServer.ipynb` jupyter notebook.
2. This will start a server that listens for incoming UDP messages on port `12000` and randomly drops 30% of them.

---

### 2. **UDP Pinger Client (`UDPPingerClient.ipynb`)**

Now, we will implement the client that sends **10 pings** to the server and waits for a response. If no response is received within 1 second, it assumes the packet was lost and prints "Request timed out."

#### Client Code:

```python
import time
import socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Setting a timeout of 1 second for the socket
clientSocket.settimeout(1)

# Server details
# It is important for us to ensure that the server is running and reachable.
serverAddress = ('localhost', 12000)  

# Track RTTs and packet loss
rtt_list = []
num_pings = 10
packet_loss_count = 0

for sequence_number in range(1, num_pings + 1):
    start_time = time.time() # The time whenthe ping was sent.

    # Ping message format: "Ping <sequence_number> <timestamp>"
    message = f"Ping {sequence_number} {start_time}"

    try:
        # Sending the ping message to the server
        clientSocket.sendto(message.encode(), serverAddress)
        print(f"Sent: {message}")

        # Receiving the server's response
        response, server = clientSocket.recvfrom(1024)
        rtt = time.time() - start_time
        rtt_list.append(rtt)
        print(f"Reply from {server}: {response.decode()} RTT: {rtt:.6f} seconds")

    except socket.timeout:
        # Handling packet loss by timing out after 1 second
        print(f"Request timed out for Ping {sequence_number}")
        packet_loss_count += 1

    except ConnectionResetError as e:
        # Handling server closing connection or resetting the socket
        print(f"ConnectionResetError: {e}. The server may have closed the connection unexpectedly.")

    except Exception as e:
        # Handling any other unknown errors
        print(f"An error occurred: {e}")

# Statistics after all pings
if rtt_list:
    print("\n--- Ping Statistics ---")
    print(f"Packets: Sent = {num_pings}, Received = {num_pings - packet_loss_count}, Lost = {packet_loss_count}")
    print(f"Packet Loss = {(packet_loss_count / num_pings) * 100:.2f}%")
    print(f"Min RTT = {min(rtt_list):.6f} seconds")
    print(f"Max RTT = {max(rtt_list):.6f} seconds")
    print(f"Average RTT = {sum(rtt_list) / len(rtt_list):.6f} seconds")
else:
    print("All requests timed out.")

# Close the socket when done
clientSocket.close()
```

#### Steps to Run the Client:
1. Run `UDPPingerClient.ipynb`.
2. Ensure the server is already running (`UDPPingerServer.ipynb`).
3. The client will send 10 pings to the server, calculate the **Round Trip Time (RTT)** for each ping, and handle packet timeouts. After all pings are sent, it will print statistics, including **min, max, and average RTTs**, as well as **packet loss**.

---

### Step-by-Step Breakdown:

1. **Start the Server**:
   - The server will wait for UDP packets on port `12000`.
   - For every packet received, it capitalizes the message and sends it back unless it simulates packet loss (30% of the time).

2. **Run the Client**:
   - The client sends 10 ping requests to the server and waits for a response within 1 second.
   - If the server responds, the client calculates the round-trip time (RTT) and prints it.
   - If the client does not receive a response within 1 second, it prints "Request timed out."

3. **Statistics**:
   - After all pings are completed, the client displays the **number of packets sent**, **received**, **lost**, and the **packet loss percentage**.
   - It also reports the **min, max, and average RTT** values.

---

## Part 2: UDP Heartbeat Application

In **Part 2**, we extended the UDP Pinger application to simulate a **UDP Heartbeat Check**, which is commonly used to monitor whether a server is up and running.

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

## Conclusion

Through this project, we gained hands-on experience with:
- UDP socket programming in Python.
- Simulating packet loss and handling unreliable transport mechanisms.
- Calculating network metrics such as RTT and packet loss rate.
- Implementing a heartbeat mechanism to monitor the status of a server.

---