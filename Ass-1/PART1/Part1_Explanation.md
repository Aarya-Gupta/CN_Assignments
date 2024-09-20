**Part 1: Implementing the UDP Pinger Client**

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
