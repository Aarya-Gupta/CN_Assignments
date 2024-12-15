import socket
import threading
import queue
import time
import random

T1 = 1
T2 = 3
T3 = 1
T4 = 3
dropProb = 0.1
N = 8 ; windowSize = 7

lock1 = threading.Lock() ; lock2 = threading.Lock()

base = 0 ; nextSeqNum = 0 ; expectedSeqNum = 0 ; sendBuffer = {} ; queue1 = queue.Queue() ; queue2 = queue.Queue() ; packetStats = {} ; ackSend = 0 ; ackRecv = 0
sentpackets = 0 ; receivedPackets = 0 ; droppedPackets = 0
timeout = 1.0

# Open the file for logging
log_file_path = r'C:/Users/aarya/Github_Projects/CN_Assignments/Ass-3/Using Two Machines/machine2_output.txt'
log_file = open(log_file_path, 'w')

def log_output(message):
    log_file.write(message + "\n")
    log_file.flush()  # Ensure the message is written immediately

def networkgenPackets():
    global sentpackets
    numpackets = 0
    while numpackets < 100:
        time.sleep(random.uniform(T1, T2))
        packet = f"Packet_{numpackets}"
        queue1.put(packet)
        numpackets += 1

def networkrecvpackets():
    global receivedPackets
    while True:
        packet = queue2.get()
        if packet:
            receivedPackets += 1

def framesender(sock , remoteAddr):
    global nextSeqNum , base , sentpackets , droppedPackets , ackSend
    while True:
        with lock1:
            if (nextSeqNum < base + windowSize) and not queue1.empty():
                data = queue1.get()
                frame = {
                    'seq_num' : nextSeqNum % N,
                    'data' : data,
                    'is_ack' : False ,
                    'ack_num' : ackSend % N
                }
                if nextSeqNum not in packetStats:
                    packetStats[nextSeqNum] = [time.time() , None ,1]
                else:
                    packetStats[nextSeqNum][2] += 1
                sendBuffer[nextSeqNum] = frame
                time.sleep(random.uniform(T3 , T4))
                if random.random() >= dropProb:
                    sock.sendto(str(frame).encode() , remoteAddr)
                    log_output(f"Sent frame with SEQNUMBER {frame['seq_num']}")
                    sentpackets += 1
                else:
                    log_output(f"Dropped frame with SEQNUMBER {frame['seq_num']}")
                    droppedPackets += 1
                nextSeqNum += 1 ; ackSend += 1
            else:
                time.sleep(0.1)

def framereciever(sock , remoteAddr):
    global base , expectedSeqNum , ackRecv
    while True:
        data , addr = sock.recvfrom(1024)
        frame = eval(data.decode())
        with lock2:
            if frame['is_ack']:
                ackNum = frame['ack_num']
                log_output(f"Received ACK {ackNum}")
                while base <= ackNum:
                    if base in packetStats and packetStats[base][1] is None:
                        packetStats[base][1] = time.time()
                    if base in sendBuffer:
                        del sendBuffer[base]
                    base += 1
            else:
                log_output(f"Received frame {frame['seq_num']}")
                if frame['seq_num'] == expectedSeqNum % N:
                    queue2.put(frame['data'])
                    expectedSeqNum += 1
                ackFrame = {
                    'is_ack' : True,
                    'ack_num' :  ackRecv % N,
                    'seq_num' : None,
                    'data' : None
                }
                ackRecv += 1
                time.sleep(random.uniform(T3 , T4))
                if random.random() >= dropProb:
                    sock.sendto(str(ackFrame).encode() , remoteAddr)
                    log_output(f"Sent ACK {ackFrame['ack_num']}")
                else:
                    log_output(f"Dropped ACK {ackFrame['ack_num']}")

def timeouthandler(sock , remoteAddr):
    global base , nextSeqNum
    while True:
        currTime = time.time()
        with lock1:
            if base < nextSeqNum:
                oldesttime = packetStats[base][0]
                if currTime - oldesttime > timeout:
                    for i in range(base , nextSeqNum):
                        frame = sendBuffer[i]
                        packetStats[i][2] += 1
                        time.sleep(random.uniform(T3 , T4))
                        if random.random() >= dropProb:
                            sock.sendto(str(frame).encode() , remoteAddr)
        time.sleep(0.1)

def statscalc():
    totDelay = 0 ; totRetransmissions = 0 ; packetsCnt = 0
    for x in packetStats.values():
        sendtime , receivetime , retransmissions = x
        if receivetime is not None:
            totDelay += (receivetime - sendtime)
            totRetransmissions += retransmissions
            packetsCnt += 1
    avgDelay = totDelay/packetsCnt if packetsCnt > 0 else 0 
    avgRetransmissions = totRetransmissions/packetsCnt if packetsCnt > 0 else 0 
    log_output(f'Average delay is: {avgDelay} , Average retransmissions are: {avgRetransmissions}')

sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
sock.bind(('localhost' , 5009))
remoteAddr = ('localhost' , 5010)
threads =[ 
    threading.Thread(target=networkgenPackets ) , 
    threading.Thread(target=networkrecvpackets) ,
    threading.Thread(target=framesender , args=(sock , remoteAddr)) ,
    threading.Thread(target=framereciever , args=(sock , remoteAddr)) ,
    threading.Thread(target=timeouthandler , args=(sock , remoteAddr))
]
for x in threads:
    x.daemon = True
    x.start()

while True:
    if sentpackets == 100 and receivedPackets == 100:
        statscalc()
        break
    time.sleep(1)

# Close the log file at the end
log_file.close()
