### README for Computer Networks Assignments Repository  

# Computer Networks Assignments  

This repository contains a collection of assignments completed for **CSE 232 Section B: Computer Networks**. Each assignment focuses on implementing and simulating key networking concepts, including UDP and TCP protocols, data link layer protocols, and network performance evaluation using NS3.  

## Repository Structure  

```
CN_Assignments/  
├── Ass-1/  
│   ├── PART1/  
│   │   ├── Part1_Explanation.md  
│   │   ├── UDPPingerClient.ipynb  
│   │   ├── UDPPingerServer.ipynb  
│   ├── PART2/  
│   │   ├── Part2_Explanation.md  
│   │   ├── UDPHeartbeatClient.ipynb  
│   │   ├── UDPHeartbeatServer.ipynb  
│   ├── Programming Exercise 1.pdf  
│   └── REPORT.md  
├── Ass-2/  
│   ├── client.py  
│   ├── server-1.py  
│   ├── server-2.py  
│   ├── webpage.html  
│   ├── Programming Exercise 2.pdf  
│   └── report.pdf  
├── Ass-3/  
│   ├── Using Single Machine/  
│   │   ├── usingSingleMachine.py  
│   │   ├── Simulation Outputs/  
│   ├── Using Two Machines/  
│   │   ├── machine1.py  
│   │   ├── machine2.py  
│   │   ├── Output Logs/  
│   ├── Programming Exercise 3.pdf  
│   └── REPORT_CN_ASS-3.pdf  
├── Ass-4/  
│   ├── main.cpp  
│   ├── CN-Ass-4-Report.pdf  
│   ├── CN-Ass-4-Slides.pdf  
│   └── Programming Exercise 4.pdf  
├── README.md  
```  

## Assignments Overview  

### **Assignment 1: UDP Pinger and Heartbeat Simulation**  
- **Objective**: Learn UDP socket programming to implement a Ping application and a Heartbeat protocol.  
- **Key Features**:  
  - Measure Round-Trip Time (RTT) and simulate packet loss.  
  - Implement server availability checks using the Heartbeat protocol.  

### **Assignment 2: TCP-based Web Application**  
- **Objective**: Develop an HTTP server and client using TCP socket programming.  
- **Key Features**:  
  - Handle HTTP requests and responses in single-threaded and multi-threaded environments.  
  - Write a custom HTTP client for server testing.  

### **Assignment 3: Go-Back-N Protocol Simulation**  
- **Objective**: Simulate the Go-Back-N protocol to understand data link layer protocols.  
- **Key Features**:  
  - Simulate frame transmission, acknowledgement, and retransmission with random delays and packet loss.  
  - Analyze protocol behaviour under different loss rates and delays.  

### **Assignment 4: NS3-based Network Simulation**  
- **Objective**: Simulate a computer network using NS3 and evaluate performance metrics.  
- **Key Features**:  
  - Create custom network topologies with routers and workstations.  
  - Analyze end-to-end delays, packet drops, and queue lengths at routers.  

## How to Use  

1. Navigate to the respective assignment folder for detailed implementation and instructions.  
2. Run the code files in the specified environment (Python, C++, or NS3).  
3. Refer to the provided reports and slides for a comprehensive understanding of each assignment.  

## Acknowledgments  

These assignments were completed in the **CSE 232: Computer Networks** course, offering practical insights into network programming and simulation.  
