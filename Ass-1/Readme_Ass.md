# UDP Pinger Lab

## Course: CSE 232, Section B - Computer Networks

**Team Members**: [Your Names Here]

**Due Date**: Wednesday, September 18, 2024, midnight

---

## Project Overview

In this project, we implemented a basic UDP Ping application and extended it into a UDP Heartbeat application. The objective was to learn the fundamentals of socket programming using UDP, understand packet loss simulation, and calculate network statistics like round-trip time (RTT) and packet loss rate. The project consists of two parts, as described below.

---

## Part 1: UDP Pinger Application

In **Part 1**, we implemented a basic **UDP Pinger Client** that communicates with a provided **UDP Pinger Server**.

- **Server Functionality**: The server listens for incoming UDP packets, capitalizes the message, and responds to the client. It also simulates 30% packet loss by randomly discarding packets.
- **Client Functionality**: 
  - The client sends 10 ping requests to the server, each containing a sequence number and a timestamp.
  - The client waits for a response from the server. If no response is received within 1 second, the client assumes the packet is lost and prints "Request timed out".
  - After all pings are sent, the client calculates and displays the minimum, maximum, and average round-trip times (RTTs) as well as the packet loss percentage.

### Running the Code:
1. **Start the server** using the provided `UDPPingerServer.py`:
   ```bash
   python UDPPingerServer.py
   ```
2. **Run the client** (`UDPPingerClient.py`):
   ```bash
   python UDPPingerClient.py
   ```

### Expected Output:
- For each successful ping, the client prints the server's response along with the calculated RTT.
- If the packet is lost (simulated by the server), the client prints "Request timed out".
- After all pings, the client prints statistics:
  - **Packets Sent, Received, Lost**
  - **Packet Loss Percentage**
  - **Min, Max, and Average RTT**

---

## Part 2: UDP Heartbeat Application

In **Part 2**, we extended the UDP Pinger application to simulate a **UDP Heartbeat Check**, which is commonly used to monitor whether a server is up and running.

- **Server Functionality**: The server listens for incoming heartbeat packets. Upon receiving a packet, it calculates the time difference between when the packet was sent and when it was received and returns this time difference to the client. The server continues to simulate 30% packet loss.
  
- **Client Functionality**:
  - The client sends heartbeat packets to the server, each containing a sequence number and timestamp.
  - The client waits for a response from the server. If no response is received within 1 second, the client assumes the packet was lost.
  - If the client fails to receive responses for 3 consecutive heartbeats, it assumes the server has stopped and exits.

### Running the Code:
1. **Start the server** using `UDPHeartbeatServer.py`:
   ```bash
   python UDPHeartbeatServer.py
   ```
2. **Run the client** (`UDPHeartbeatClient.py`):
   ```bash
   python UDPHeartbeatClient.py
   ```

### Expected Output:
- For each successful heartbeat, the client prints the server's response, which includes the time difference (latency).
- If the client experiences 3 consecutive packet losses, it assumes the server has stopped and prints a message accordingly.
  
---

## Conclusion

Through this project, we gained hands-on experience with:
- UDP socket programming in Python.
- Simulating packet loss and handling unreliable transport mechanisms.
- Calculating network metrics such as RTT and packet loss rate.
- Implementing a heartbeat mechanism to monitor the status of a server.

---