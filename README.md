# Computer Networks Assignments Repository

This repository contains a series of programming assignments completed as part of the **CSE 232 Section B: Computer Networks** course. The assignments involve practical implementation and simulation of various networking concepts, including UDP and TCP protocols, data link layer protocols, and network performance evaluation using NS3.

## Repository Structure
CN_Assignments/ ├── Ass-1/ │ ├── PART1/ │ │ ├── Part1_Explanation.md │ │ ├── UDPPingerClient.ipynb │ │ ├── UDPPingerServer.ipynb │ ├── PART2/ │ │ ├── Part2_Explanation.md │ │ ├── UDPHeartbeatClient.ipynb │ │ ├── UDPHeartbeatServer.ipynb │ ├── Programming Exercise 1.pdf │ └── REPORT.md ├── Ass-2/ │ ├── client.py │ ├── server-1.py │ ├── server-2.py │ ├── webpage.html │ ├── Programming Exercise 2.pdf │ └── report-raj jain.pdf ├── Ass-3/ │ ├── Using Single Machine/ │ │ ├── usingSingleMachine.py │ │ ├── simulation outputs and logs │ ├── Using Two Machines/ │ │ ├── machine1.py │ │ ├── machine2.py │ ├── Programming Exercise 3.pdf │ └── REPORT_CN_ASS-3.pdf ├── Ass-4/ │ ├── main.cpp │ ├── CN-Ass-4-Report.pdf │ └── CN-Ass-4-Slides.pdf ├── README.md


## Assignments Overview

### **Assignment 1: UDP Pinger and Heartbeat Simulation**
- **Goal**: Learn UDP socket programming by implementing a Ping application and extending it to a Heartbeat simulation.
- **Key Features**:
  - Measure Round-Trip Time (RTT) and simulate packet loss.
  - Develop a UDP Heartbeat protocol to check server availability.
  
### **Assignment 2: TCP-based Web Application**
- **Goal**: Implement a simple HTTP server and client using TCP socket programming.
- **Key Features**:
  - Single and multi-threaded server implementations.
  - Develop an HTTP client to interact with the server.

### **Assignment 3: Go-Back-N Protocol Simulation**
- **Goal**: Simulate the Go-Back-N data link layer protocol.
- **Key Features**:
  - Use socket programming for communication.
  - Simulate frame transmission with random delays and packet loss.

### **Assignment 4: NS3-based Network Simulation**
- **Goal**: Simulate a computer network using NS3 and evaluate performance metrics.
- **Key Features**:
  - Analyze end-to-end delays, packet loss, and queue lengths.
  - Create and test custom network topologies.

## How to Use
1. Navigate to the respective assignment folder for details on the implementation.
2. Follow the instructions in the provided `REPORT.md` or PDF files.
3. Run the code files in the specified environment (e.g., Python, C++, or NS3).

## Acknowledgments
This repository reflects teamwork and extensive learning of networking concepts under the guidance of the course instructors and TAs.
