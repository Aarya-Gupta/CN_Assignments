import threading
import time
import random
import socket
import pickle
import logging
import sys

# Configuration Parameters
T1 = 0.1  # Minimum packet generation interval (seconds)
T2 = 0.2  # Maximum packet generation interval (seconds)
N = 8       # Modulo for sequence numbers
WINDOW_SIZE = 7  # Transmit window size

# Machine 1 Addresses
MACHINE1_SENDER_ADDRESS = ('localhost', 12000)
MACHINE1_RECEIVER_ADDRESS = ('localhost', 13000)

# Machine 2 Addresses
MACHINE2_SENDER_ADDRESS = ('localhost', 12001)
MACHINE2_RECEIVER_ADDRESS = ('localhost', 13001)


# Global Variables for Machine 1
sender_queue = []
receiver_queue = []
sender_base = 0
next_seq_num = 0
expected_seq_num = 0
total_delay = 0
total_frames_sent = 0
total_retransmissions = 0

lock = threading.Lock()
packet_available = threading.Condition()

def packet_generator(TOTAL_PACKETS):
    """Generates packets at random intervals and adds them to the sender queue."""
    global sender_queue
    for i in range(TOTAL_PACKETS):
        time.sleep(random.uniform(T1, T2))
        packet = f"Packet_{i}"
        with packet_available:
            sender_queue.append(packet)
            packet_available.notify_all()  # Notify the sender that a new packet is available
        logging.info(f"Generated: {packet}")

def is_seq_num_less(a, b):
    return ((b - a + N) % N) < (N // 2)

def send_frames(TOTAL_PACKETS, P, T3, T4):
    global sender_base, next_seq_num, total_frames_sent, total_retransmissions
    timers = {}
    while True:
        # Check if all packets have been sent and acknowledged
        with lock:
            if sender_base >= TOTAL_PACKETS and not timers:
                break  # All packets sent and acknowledged

        # Send frames within the window
        with packet_available:
            with lock:
                while next_seq_num < sender_base + WINDOW_SIZE and next_seq_num < TOTAL_PACKETS:
                    if next_seq_num >= len(sender_queue):
                        packet_available.wait()  # Wait for the packet to be available
                        continue
                    seq_num = next_seq_num % N
                    packet = sender_queue[next_seq_num]
                    frame = {
                        'seq_num': seq_num,
                        'data': packet,
                        'timestamp': time.time()
                    }
                    simulate_network_delay(T3, T4)
                    if not simulate_frame_drop(P):
                        sender_socket.sendto(pickle.dumps(frame), MACHINE2_RECEIVER_ADDRESS)
                        logging.info(f"Sent Frame: Seq {seq_num}")
                    else:
                        logging.info(f"Frame Dropped (Sender): Seq {seq_num}")
                    total_frames_sent += 1
                    timers[next_seq_num] = time.time()
                    next_seq_num += 1

        # Check for ACKs
        try:
            sender_socket.settimeout(0.1)
            ack_data, _ = sender_socket.recvfrom(1024)
            ack_frame = pickle.loads(ack_data)
            ack_num = ack_frame['ack_num']
            logging.info(f"Received ACK: {ack_num}")
            with lock:
                # Map ack_num to absolute sequence number
                acked_seq_num = None
                for seq_num in range(sender_base, next_seq_num):
                    if seq_num % N == ack_num:
                        acked_seq_num = seq_num
                if acked_seq_num is not None and acked_seq_num >= sender_base:
                    sender_base = acked_seq_num + 1
                    # Remove timers for acknowledged frames
                    for seq_num in list(timers.keys()):
                        if seq_num < sender_base:
                            timers.pop(seq_num)
        except socket.timeout:
            pass  # No ACK received during this interval

        # Handle timeouts and retransmissions
        current_time = time.time()
        with lock:
            # Check if any unacknowledged frame has timed out
            for seq_num in list(timers.keys()):
                if current_time - timers[seq_num] > 1.0:
                    logging.info("Timeout occurred, retransmitting frames.")
                    # Retransmit all frames in the window starting from sender_base
                    for seq_num in range(sender_base, next_seq_num):
                        if seq_num in timers:
                            packet_index = seq_num
                            if packet_index >= len(sender_queue):
                                break
                            packet = sender_queue[packet_index]
                            frame = {
                                'seq_num': seq_num % N,
                                'data': packet,
                                'timestamp': time.time()
                            }
                            simulate_network_delay(T3, T4)
                            if not simulate_frame_drop(P):
                                sender_socket.sendto(pickle.dumps(frame), MACHINE2_RECEIVER_ADDRESS)
                                logging.info(f"Retransmitted Frame: Seq {seq_num % N}")
                            else:
                                logging.info(f"Frame Dropped (Retransmission): Seq {seq_num % N}")
                            total_frames_sent += 1
                            total_retransmissions += 1
                            timers[seq_num] = time.time()
                    break  # Exit after handling timeout
        # Sleep briefly to prevent tight loop
        time.sleep(0.01)

def receive_frames(TOTAL_PACKETS, P, T3, T4):
    global expected_seq_num, total_delay
    received_packets = 0
    while True:
        if received_packets >= TOTAL_PACKETS:
            break
        try:
            receiver_socket.settimeout(1)
            frame_data, _ = receiver_socket.recvfrom(1024)
            frame = pickle.loads(frame_data)
            seq_num = frame['seq_num']
            data = frame['data']
            logging.info(f"Received Frame: Seq {seq_num}")
            # Simulate network delay
            simulate_network_delay(T3, T4)
            if seq_num == expected_seq_num:
                # Correct frame received
                total_delay += time.time() - frame['timestamp']
                received_packets += 1
                expected_seq_num = (expected_seq_num + 1) % N
            else:
                # Discard out-of-order frames
                logging.info(f"Discarded Frame: Seq {seq_num} (Expected: {expected_seq_num})")
            # Send ACK for the last correctly received frame
            ack_num = (expected_seq_num - 1 + N) % N
            ack_frame = {
                'ack_num': ack_num
            }
            if not simulate_frame_drop(P):
                receiver_socket.sendto(pickle.dumps(ack_frame), MACHINE2_SENDER_ADDRESS)
                logging.info(f"Sent ACK: {ack_frame['ack_num']}")
            else:
                logging.info(f"ACK Dropped: {ack_frame['ack_num']}")
        except socket.timeout:
            continue

def simulate_network_delay(T3, T4):
    """Introduces a random network delay."""
    delay = random.uniform(T3, T4)
    time.sleep(delay)

def simulate_frame_drop(P):
    """Simulates frame drop based on probability P."""
    return random.random() < P

def reset_globals():
    """Resets global variables for a new simulation run."""
    global sender_queue, receiver_queue
    global sender_base, next_seq_num, expected_seq_num
    global total_delay, total_frames_sent, total_retransmissions
    sender_queue = []
    receiver_queue = []
    sender_base = 0
    next_seq_num = 0
    expected_seq_num = 0
    total_delay = 0
    total_frames_sent = 0
    total_retransmissions = 0

def run_simulation(TOTAL_PACKETS, P, T3, T4, output_file):
    # Reset global variables
    reset_globals()

    # Reset logging handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up logging to write to the output file
    logging.basicConfig(filename=output_file, level=logging.INFO, format='%(message)s')

    # Bind sockets
    global sender_socket, receiver_socket
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_socket.bind(MACHINE1_SENDER_ADDRESS)
    receiver_socket.bind(MACHINE1_RECEIVER_ADDRESS)

    # Start packet generator thread
    packet_thread = threading.Thread(target=packet_generator, args=(TOTAL_PACKETS,))
    packet_thread.start()

    # Start sender and receiver threads
    sender_thread = threading.Thread(target=send_frames, args=(TOTAL_PACKETS, P, T3, T4))
    receiver_thread = threading.Thread(target=receive_frames, args=(TOTAL_PACKETS, P, T3, T4))
    sender_thread.start()
    receiver_thread.start()

    # Wait for all threads to finish
    packet_thread.join()
    sender_thread.join()
    receiver_thread.join()

    # Close sockets
    sender_socket.close()
    receiver_socket.close()

    # Log Metrics
    logging.info("\nSimulation Completed.")
    logging.info(f"Total Frames Sent: {total_frames_sent}")
    logging.info(f"Total Retransmissions: {total_retransmissions}")
    logging.info(f"Average Delay per Packet: {total_delay / TOTAL_PACKETS:.4f} seconds")
    logging.info(f"Average Number of Times a Frame was Sent: {total_frames_sent / TOTAL_PACKETS:.2f}")

def main():
    # Simulation parameters
    TOTAL_PACKETS = 10000  # Number of packets to send
    P = 0.01  # Drop probability
    T3 = 0.05  # Minimum network delay
    T4 = 0.1   # Maximum network delay
    output_file = 'machine1_output.txt'

    print(f"Starting Simulation on Machine 1")
    run_simulation(TOTAL_PACKETS, P, T3, T4, output_file)
    print(f"Simulation Completed on Machine 1. Output saved to {output_file}")

if __name__ == "__main__":
    main()


# import threading
# import time
# import random
# import socket
# import pickle
# import logging
# import sys

# # Configuration Parameters
# T1 = 0.1  # Minimum packet generation interval (seconds)
# T2 = 0.2  # Maximum packet generation interval (seconds)
# N = 8       # Modulo for sequence numbers
# WINDOW_SIZE = 7  # Transmit window size

# # Machine 1 Addresses (using localhost)
# MACHINE1_SENDER_ADDRESS = ('localhost', 12000)
# MACHINE1_RECEIVER_ADDRESS = ('localhost', 13000)

# # Machine 2 Addresses (using localhost)
# MACHINE2_SENDER_ADDRESS = ('localhost', 12001)
# MACHINE2_RECEIVER_ADDRESS = ('localhost', 13001)

# # Global Variables for Machine 1
# sender_queue = []
# receiver_queue = []
# sender_base = 0
# next_seq_num = 0
# expected_seq_num = 0
# total_delay = 0
# total_frames_sent = 0
# total_retransmissions = 0

# # Flags to indicate completion
# sender_done = False
# receiver_done = False
# remote_sender_done = False

# lock = threading.Lock()
# packet_available = threading.Condition()
# remote_sender_done_event = threading.Event()

# def packet_generator(TOTAL_PACKETS):
#     """Generates packets at random intervals and adds them to the sender queue."""
#     global sender_queue
#     for i in range(TOTAL_PACKETS):
#         time.sleep(random.uniform(T1, T2))
#         packet = f"Packet_{i}"
#         with packet_available:
#             sender_queue.append(packet)
#             packet_available.notify_all()  # Notify the sender that a new packet is available
#         logging.info(f"Generated: {packet}")
#     # Signal that packet generation is done
#     with packet_available:
#         packet_available.notify_all()

# def is_seq_num_less(a, b):
#     return ((b - a + N) % N) < (N // 2)

# def send_frames(TOTAL_PACKETS, P, T3, T4):
#     global sender_base, next_seq_num, total_frames_sent, total_retransmissions, sender_done
#     timers = {}
#     while True:
#         # Check if all packets have been sent and acknowledged
#         with lock:
#             if sender_base >= TOTAL_PACKETS and not timers:
#                 break  # All packets sent and acknowledged

#         # Send frames within the window
#         with packet_available:
#             with lock:
#                 while next_seq_num < sender_base + WINDOW_SIZE and next_seq_num < TOTAL_PACKETS:
#                     if next_seq_num >= len(sender_queue):
#                         packet_available.wait()  # Wait for the packet to be available
#                         continue
#                     seq_num = next_seq_num % N
#                     packet = sender_queue[next_seq_num]
#                     frame = {
#                         'seq_num': seq_num,
#                         'data': packet,
#                         'timestamp': time.time(),
#                         'completion': False
#                     }
#                     simulate_network_delay(T3, T4)
#                     if not simulate_frame_drop(P):
#                         sender_socket.sendto(pickle.dumps(frame), MACHINE2_RECEIVER_ADDRESS)
#                         logging.info(f"Sent Frame: Seq {seq_num}")
#                     else:
#                         logging.info(f"Frame Dropped (Sender): Seq {seq_num}")
#                     total_frames_sent += 1
#                     timers[next_seq_num] = time.time()
#                     next_seq_num += 1

#         # Check for ACKs
#         try:
#             sender_socket.settimeout(0.1)
#             ack_data, _ = sender_socket.recvfrom(1024)
#             ack_frame = pickle.loads(ack_data)
#             ack_num = ack_frame['ack_num']
#             logging.info(f"Received ACK: {ack_num}")
#             with lock:
#                 # Map ack_num to absolute sequence number
#                 acked_seq_num = None
#                 for seq_num in range(sender_base, next_seq_num):
#                     if seq_num % N == ack_num:
#                         acked_seq_num = seq_num
#                         break
#                 if acked_seq_num is not None and acked_seq_num >= sender_base:
#                     sender_base = acked_seq_num + 1
#                     # Remove timers for acknowledged frames
#                     for seq_num in list(timers.keys()):
#                         if seq_num < sender_base:
#                             timers.pop(seq_num)
#         except socket.timeout:
#             pass  # No ACK received during this interval

#         # Handle timeouts and retransmissions
#         current_time = time.time()
#         with lock:
#             # Check if any unacknowledged frame has timed out
#             for seq_num in list(timers.keys()):
#                 if current_time - timers[seq_num] > 1.0:
#                     logging.info("Timeout occurred, retransmitting frames.")
#                     # Retransmit all frames in the window starting from sender_base
#                     for seq_num in range(sender_base, next_seq_num):
#                         if seq_num in timers:
#                             packet_index = seq_num
#                             if packet_index >= len(sender_queue):
#                                 break
#                             packet = sender_queue[packet_index]
#                             frame = {
#                                 'seq_num': seq_num % N,
#                                 'data': packet,
#                                 'timestamp': time.time(),
#                                 'completion': False
#                             }
#                             simulate_network_delay(T3, T4)
#                             if not simulate_frame_drop(P):
#                                 sender_socket.sendto(pickle.dumps(frame), MACHINE2_RECEIVER_ADDRESS)
#                                 logging.info(f"Retransmitted Frame: Seq {seq_num % N}")
#                             else:
#                                 logging.info(f"Frame Dropped (Retransmission): Seq {seq_num % N}")
#                             total_frames_sent += 1
#                             total_retransmissions += 1
#                             timers[seq_num] = time.time()
#                     break  # Exit after handling timeout
#         # Sleep briefly to prevent tight loop
#         time.sleep(0.01)

#     # After sending all packets and receiving all ACKs, send a completion message
#     completion_frame = {
#         'seq_num': 0,
#         'data': None,
#         'timestamp': time.time(),
#         'completion': True
#     }
#     sender_socket.sendto(pickle.dumps(completion_frame), MACHINE2_RECEIVER_ADDRESS)
#     logging.info("Sent Completion Frame")
#     sender_done = True

# def receive_frames(TOTAL_PACKETS, P, T3, T4):
#     global expected_seq_num, total_delay, receiver_done, remote_sender_done
#     received_packets = 0
#     while True:
#         if remote_sender_done and received_packets >= TOTAL_PACKETS:
#             break
#         try:
#             receiver_socket.settimeout(1)
#             frame_data, _ = receiver_socket.recvfrom(1024)
#             frame = pickle.loads(frame_data)
#             if frame.get('completion'):
#                 logging.info("Received Completion Frame from Sender")
#                 remote_sender_done = True
#                 remote_sender_done_event.set()
#                 continue
#             seq_num = frame['seq_num']
#             data = frame['data']
#             logging.info(f"Received Frame: Seq {seq_num}")
#             # Simulate network delay
#             simulate_network_delay(T3, T4)
#             if seq_num == expected_seq_num:
#                 # Correct frame received
#                 total_delay += time.time() - frame['timestamp']
#                 received_packets += 1
#                 expected_seq_num = (expected_seq_num + 1) % N
#             else:
#                 # Discard out-of-order frames
#                 logging.info(f"Discarded Frame: Seq {seq_num} (Expected: {expected_seq_num})")
#             # Send ACK for the last correctly received frame
#             ack_num = (expected_seq_num - 1 + N) % N
#             ack_frame = {
#                 'ack_num': ack_num
#             }
#             if not simulate_frame_drop(P):
#                 receiver_socket.sendto(pickle.dumps(ack_frame), MACHINE2_SENDER_ADDRESS)
#                 logging.info(f"Sent ACK: {ack_frame['ack_num']}")
#             else:
#                 logging.info(f"ACK Dropped: {ack_frame['ack_num']}")
#         except socket.timeout:
#             continue
#     receiver_done = True

# def simulate_network_delay(T3, T4):
#     """Introduces a random network delay."""
#     delay = random.uniform(T3, T4)
#     time.sleep(delay)

# def simulate_frame_drop(P):
#     """Simulates frame drop based on probability P."""
#     return random.random() < P

# def reset_globals():
#     """Resets global variables for a new simulation run."""
#     global sender_queue, receiver_queue
#     global sender_base, next_seq_num, expected_seq_num
#     global total_delay, total_frames_sent, total_retransmissions
#     global sender_done, receiver_done, remote_sender_done
#     sender_queue = []
#     receiver_queue = []
#     sender_base = 0
#     next_seq_num = 0
#     expected_seq_num = 0
#     total_delay = 0
#     total_frames_sent = 0
#     total_retransmissions = 0
#     sender_done = False
#     receiver_done = False
#     remote_sender_done = False
#     remote_sender_done_event.clear()

# def run_simulation(TOTAL_PACKETS, P, T3, T4, output_file):
#     # Reset global variables
#     reset_globals()

#     # Reset logging handlers
#     for handler in logging.root.handlers[:]:
#         logging.root.removeHandler(handler)

#     # Set up logging to write to the output file
#     logging.basicConfig(filename=output_file, level=logging.INFO, format='%(message)s')

#     # Bind sockets
#     global sender_socket, receiver_socket
#     sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sender_socket.bind(MACHINE1_SENDER_ADDRESS)
#     receiver_socket.bind(MACHINE1_RECEIVER_ADDRESS)

#     # Start packet generator thread
#     packet_thread = threading.Thread(target=packet_generator, args=(TOTAL_PACKETS,))
#     packet_thread.start()

#     # Start sender and receiver threads
#     sender_thread = threading.Thread(target=send_frames, args=(TOTAL_PACKETS, P, T3, T4))
#     receiver_thread = threading.Thread(target=receive_frames, args=(TOTAL_PACKETS, P, T3, T4))
#     sender_thread.start()
#     receiver_thread.start()

#     # Wait for all threads to finish
#     packet_thread.join()
#     sender_thread.join()
#     receiver_thread.join()

#     # Wait for remote sender to finish
#     if not remote_sender_done:
#         logging.info("Waiting for remote sender to complete...")
#         remote_sender_done_event.wait()

#     # Close sockets
#     sender_socket.close()
#     receiver_socket.close()

#     # Log Metrics
#     logging.info("\nSimulation Completed.")
#     logging.info(f"Total Frames Sent: {total_frames_sent}")
#     logging.info(f"Total Retransmissions: {total_retransmissions}")
#     logging.info(f"Average Delay per Packet: {total_delay / TOTAL_PACKETS:.4f} seconds")
#     logging.info(f"Average Number of Times a Frame was Sent: {total_frames_sent / TOTAL_PACKETS:.2f}")

# def main():
#     # Simulation parameters
#     TOTAL_PACKETS = 20  # Number of packets to send
#     P = 0.05  # Drop probability
#     T3 = 0.05  # Minimum network delay
#     T4 = 0.1   # Maximum network delay
#     output_file = 'machine1_output.txt'

#     print(f"Starting Simulation on Machine 1")
#     run_simulation(TOTAL_PACKETS, P, T3, T4, output_file)
#     print(f"Simulation Completed on Machine 1. Output saved to {output_file}")

# if __name__ == "__main__":
#     main()
