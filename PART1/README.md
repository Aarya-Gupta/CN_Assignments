Let's go through **Part 1** of the **UDP Pinger Lab** step-by-step, where you'll implement a **UDP Pinger Client** and run it with the provided **UDP Pinger Server** code.

---

### 1. **UDP Pinger Server (`UDPPingerServer.py`)**

This is the server code you need to run first. It listens on a specific port and randomly drops packets to simulate network packet loss. It responds by capitalizing the message it receives if the packet is not "lost."

#### Server Code:

```python
import random
from socket import *

# Create a UDP socket
# SOCK_DGRAM is for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to a specific port (12000 in this case)
serverSocket.bind(('', 12000))

print("UDP Pinger Server is running...")

while True:
    # Generate random number between 0 and 10
    rand = random.randint(0, 10)

    # Receive a message and client address
    message, address = serverSocket.recvfrom(1024)

    # Capitalize the message
    message = message.upper()

    # If random number < 4, simulate packet loss
    if rand < 4:
        print(f"Simulating packet loss for message from {address}.")
        continue

    # Otherwise, send back the capitalized message
    serverSocket.sendto(message, address)
    print(f"Responding to {address} with message: {message.decode()}")
```

#### Steps to Run the Server:
1. Save this code as `UDPPingerServer.py`.
2. Run it using Python:
   ```bash
   python UDPPingerServer.py
   ```
3. This will start a server that listens for incoming UDP messages on port `12000` and randomly drops 30% of them.

---

### 2. **UDP Pinger Client (`UDPPingerClient.py`)**

Now, you will implement the client that sends **10 pings** to the server and waits for a response. If no response is received within 1 second, it assumes the packet was lost and prints "Request timed out."

#### Client Code:

```python
import time
import socket

# Create a UDP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set a timeout of 1 second for the socket
clientSocket.settimeout(1)

# Server details
serverAddress = ('localhost', 12000)  # Ensure the server is running on localhost and port 12000

# Variables to track round-trip times and packet loss
rtt_list = []
num_pings = 10
packet_loss_count = 0

for sequence_number in range(1, num_pings + 1):
    # Record the current time (for RTT calculation)
    start_time = time.time()

    # Create the message (Ping message format: "Ping <sequence_number> <timestamp>")
    message = f"Ping {sequence_number} {start_time}"

    try:
        # Send the ping message to the server
        clientSocket.sendto(message.encode(), serverAddress)
        print(f"Sent: {message}")

        # Wait for the server's response
        response, server = clientSocket.recvfrom(1024)

        # Calculate the RTT
        rtt = time.time() - start_time
        rtt_list.append(rtt)

        # Print the server's response and the RTT
        print(f"Reply from {server}: {response.decode()} RTT: {rtt:.6f} seconds")

    except socket.timeout:
        # Handle packet loss
        print(f"Request timed out for Ping {sequence_number}")
        packet_loss_count += 1

# After sending all pings, print the statistics
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
1. Save this code as `UDPPingerClient.py`.
2. Ensure the server is already running (`UDPPingerServer.py`).
3. Run the client using Python:
   ```bash
   python UDPPingerClient.py
   ```
4. The client will send 10 pings to the server, calculate the **Round Trip Time (RTT)** for each ping, and handle packet timeouts. After all pings are sent, it will print statistics, including **min, max, and average RTTs**, as well as **packet loss**.

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

### Common Troubleshooting Tips:
- Ensure the server is running before you start the client.
- If using different machines, ensure the correct server IP is set in the client (`serverAddress = ('<server-ip>', 12000)`).
- Make sure port `12000` is not blocked by your firewall.

Let me know if you encounter any issues during the process!
