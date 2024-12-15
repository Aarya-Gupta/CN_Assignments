# # # import threading
# # # import time
# # # import random
# # # import socket
# # # import pickle

# # # # Configuration Parameters
# # # T1 = 0.1  # Minimum packet generation interval (seconds)
# # # T2 = 0.2  # Maximum packet generation interval (seconds)
# # # T3 = 0.05  # Minimum network delay (seconds)
# # # T4 = 0.1   # Maximum network delay (seconds)
# # # P = 0.1    # Frame drop probability

# # # N = 8       # Modulo for sequence numbers
# # # WINDOW_SIZE = 7  # Transmit window size

# # # TOTAL_PACKETS = 10000  # Total packets to send (for testing purposes)

# # # # Global Variables
# # # sender_queue = []
# # # receiver_queue = []

# # # sender_base = 0
# # # next_seq_num = 0
# # # expected_seq_num = 0

# # # lock = threading.Lock()
# # # print_lock = threading.Lock()
# # # packet_available = threading.Condition()

# # # # Metrics
# # # total_delay = 0
# # # total_frames_sent = 0
# # # total_retransmissions = 0

# # # # UDP Socket Setup
# # # SENDER_ADDRESS = ('localhost', 12000)
# # # RECEIVER_ADDRESS = ('localhost', 13000)

# # # sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # # receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # # sender_socket.bind(SENDER_ADDRESS)
# # # receiver_socket.bind(RECEIVER_ADDRESS)

# # # def packet_generator():
# # #     try:
# # #         """Generates packets at random intervals and adds them to the sender queue."""
# # #         global sender_queue
# # #         for i in range(TOTAL_PACKETS):
# # #             time.sleep(random.uniform(T1, T2))
# # #             packet = f"Packet_{i}"
# # #             with packet_available:
# # #                 sender_queue.append(packet)
# # #                 packet_available.notify_all()  # Notify the sender that a new packet is available
# # #             with print_lock:
# # #                 print(f"Generated: {packet}")
# # #     except Exception as e:
# # #         print(f"Exception in packet_generator: {e}")

# # # def is_seq_num_less(a, b):
# # #     return ((b - a + N) % N) < (N // 2)

# # # def send_frames():
# # #     try:
# # #         global sender_base, next_seq_num, total_frames_sent, total_retransmissions
# # #         timers = {}
# # #         while True:
# # #             # Check if all packets have been sent and acknowledged
# # #             with lock:
# # #                 if sender_base >= TOTAL_PACKETS and not timers:
# # #                     break  # All packets sent and acknowledged

# # #             # Send frames within the window
# # #             with packet_available:
# # #                 with lock:
# # #                     while next_seq_num < sender_base + WINDOW_SIZE and next_seq_num < TOTAL_PACKETS:
# # #                         if next_seq_num >= len(sender_queue):
# # #                             packet_available.wait()  # Wait for the packet to be available
# # #                             continue
# # #                         seq_num = next_seq_num % N
# # #                         packet = sender_queue[next_seq_num]
# # #                         frame = {
# # #                             'seq_num': seq_num,
# # #                             'data': packet,
# # #                             'timestamp': time.time()
# # #                         }
# # #                         simulate_network_delay()
# # #                         if not simulate_frame_drop():
# # #                             sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
# # #                             with print_lock:
# # #                                 print(f"Sent Frame: Seq {seq_num}")
# # #                         else:
# # #                             with print_lock:
# # #                                 print(f"Frame Dropped (Sender): Seq {seq_num}")
# # #                         total_frames_sent += 1
# # #                         timers[next_seq_num] = time.time()
# # #                         next_seq_num += 1

# # #             # Check for ACKs
# # #             try:
# # #                 sender_socket.settimeout(0.1)
# # #                 ack_data, _ = sender_socket.recvfrom(1024)
# # #                 ack_frame = pickle.loads(ack_data)
# # #                 ack_num = ack_frame['ack_num']
# # #                 with print_lock:
# # #                     print(f"Received ACK: {ack_num}")
# # #                 with lock:
# # #                     # Map ack_num to absolute sequence number
# # #                     acked_seq_num = None
# # #                     for seq_num in range(sender_base, next_seq_num):
# # #                         if seq_num % N == ack_num:
# # #                             acked_seq_num = seq_num
# # #                     if acked_seq_num is not None and acked_seq_num >= sender_base:
# # #                         sender_base = acked_seq_num + 1
# # #                         # Remove timers for acknowledged frames
# # #                         for seq_num in list(timers.keys()):
# # #                             if seq_num < sender_base:
# # #                                 timers.pop(seq_num)
# # #             except socket.timeout:
# # #                 pass  # No ACK received during this interval

# # #             # Handle timeouts and retransmissions
# # #             current_time = time.time()
# # #             with lock:
# # #                 # Check if any unacknowledged frame has timed out
# # #                 for seq_num in list(timers.keys()):
# # #                     if current_time - timers[seq_num] > 1.0:
# # #                         with print_lock:
# # #                             print("Timeout occurred, retransmitting frames.")
# # #                         # Retransmit all frames in the window starting from sender_base
# # #                         for seq_num in range(sender_base, next_seq_num):
# # #                             if seq_num in timers:
# # #                                 packet_index = seq_num
# # #                                 if packet_index >= len(sender_queue):
# # #                                     break
# # #                                 packet = sender_queue[packet_index]
# # #                                 frame = {
# # #                                     'seq_num': seq_num % N,
# # #                                     'data': packet,
# # #                                     'timestamp': time.time()
# # #                                 }
# # #                                 simulate_network_delay()
# # #                                 if not simulate_frame_drop():
# # #                                     sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
# # #                                     with print_lock:
# # #                                         print(f"Retransmitted Frame: Seq {seq_num % N}")
# # #                                 else:
# # #                                     with print_lock:
# # #                                         print(f"Frame Dropped (Retransmission): Seq {seq_num % N}")
# # #                                 total_frames_sent += 1
# # #                                 total_retransmissions += 1
# # #                                 timers[seq_num] = time.time()
# # #                         break  # Exit after handling timeout
# # #             # Sleep briefly to prevent tight loop
# # #             time.sleep(0.01)
# # #     except Exception as e:
# # #         print(f"Exception in send_frames: {e}")

# # # def receive_frames():
# # #     try:
# # #         global expected_seq_num, total_delay
# # #         received_packets = 0
# # #         while True:
# # #             if received_packets >= TOTAL_PACKETS:
# # #                 break
# # #             try:
# # #                 receiver_socket.settimeout(1)
# # #                 frame_data, _ = receiver_socket.recvfrom(1024)
# # #                 frame = pickle.loads(frame_data)
# # #                 seq_num = frame['seq_num']
# # #                 data = frame['data']
# # #                 with print_lock:
# # #                     print(f"Received Frame: Seq {seq_num}")
# # #                 # Simulate network delay
# # #                 simulate_network_delay()
# # #                 if seq_num == expected_seq_num:
# # #                     # Correct frame received
# # #                     total_delay += time.time() - frame['timestamp']
# # #                     received_packets += 1
# # #                     expected_seq_num = (expected_seq_num + 1) % N
# # #                 else:
# # #                     # Discard out-of-order frames
# # #                     with print_lock:
# # #                         print(f"Discarded Frame: Seq {seq_num} (Expected: {expected_seq_num})")
# # #                 # Send ACK for the last correctly received frame
# # #                 ack_num = (expected_seq_num - 1 + N) % N
# # #                 ack_frame = {
# # #                     'ack_num': ack_num
# # #                 }
# # #                 if not simulate_frame_drop():
# # #                     receiver_socket.sendto(pickle.dumps(ack_frame), SENDER_ADDRESS)
# # #                     with print_lock:
# # #                         print(f"Sent ACK: {ack_frame['ack_num']}")
# # #                 else:
# # #                     with print_lock:
# # #                         print(f"ACK Dropped: {ack_frame['ack_num']}")
# # #             except socket.timeout:
# # #                 continue
# # #     except Exception as e:
# # #         print(f"Exception in receive_frames: {e}")

# # # def simulate_network_delay():
# # #     """Introduces a random network delay."""
# # #     delay = random.uniform(T3, T4)
# # #     time.sleep(delay)

# # # def simulate_frame_drop():
# # #     """Simulates frame drop based on probability P."""
# # #     return random.random() < P

# # # def main():
# # #     # Start packet generator thread
# # #     packet_thread = threading.Thread(target=packet_generator)
# # #     packet_thread.start()

# # #     # Start sender and receiver threads
# # #     sender_thread = threading.Thread(target=send_frames)
# # #     receiver_thread = threading.Thread(target=receive_frames)
# # #     sender_thread.start()
# # #     receiver_thread.start()

# # #     # Wait for all threads to finish
# # #     packet_thread.join()
# # #     sender_thread.join()
# # #     receiver_thread.join()

# # #     # Close sockets
# # #     sender_socket.close()
# # #     receiver_socket.close()

# # #     # Print Metrics
# # #     print("\nSimulation Completed.")
# # #     print(f"Total Frames Sent: {total_frames_sent}")
# # #     print(f"Total Retransmissions: {total_retransmissions}")
# # #     print(f"Average Delay per Packet: {total_delay / TOTAL_PACKETS:.4f} seconds")
# # #     print(f"Average Number of Times a Frame was Sent: {total_frames_sent / TOTAL_PACKETS:.2f}")

# # # if __name__ == "__main__":
# # #     main()


# # import threading
# # import time
# # import random
# # import socket
# # import pickle

# # # Configuration Parameters
# # T1 = 0.1  # Minimum packet generation interval (seconds)
# # T2 = 0.2  # Maximum packet generation interval (seconds)

# # N = 10000   # Large modulo for sequence numbers
# # WINDOW_SIZE = 7  # Transmit window size
# # TOTAL_PACKETS = 20  # Total packets to send (for testing purposes)

# # # Global Variables
# # sender_queue = []
# # receiver_queue = []
# # sender_base = 0
# # next_seq_num = 0
# # expected_seq_num = 0

# # lock = threading.Lock()
# # packet_available = threading.Condition()

# # # Metrics
# # total_delay = 0
# # total_frames_sent = 0
# # total_retransmissions = 0

# # # UDP Socket Setup
# # SENDER_ADDRESS = ('localhost', 12000)
# # RECEIVER_ADDRESS = ('localhost', 13000)

# # sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # sender_socket.bind(SENDER_ADDRESS)
# # receiver_socket.bind(RECEIVER_ADDRESS)

# # def packet_generator():
# #     """Generates packets at random intervals and adds them to the sender queue."""
# #     global sender_queue
# #     for i in range(TOTAL_PACKETS):
# #         time.sleep(random.uniform(T1, T2))
# #         packet = f"Packet_{i}"
# #         with packet_available:
# #             sender_queue.append(packet)
# #             packet_available.notify_all()  # Notify the sender that a new packet is available

# # def is_seq_num_less(a, b):
# #     return ((b - a + N) % N) < (N // 2)

# # def send_frames(P, T3, T4, log_file):
# #     global sender_base, next_seq_num, total_frames_sent, total_retransmissions
# #     timers = {}
# #     while True:
# #         with lock:
# #             if sender_base >= TOTAL_PACKETS and not timers:
# #                 break  # All packets sent and acknowledged

# #         with packet_available:
# #             with lock:
# #                 while next_seq_num < sender_base + WINDOW_SIZE and next_seq_num < TOTAL_PACKETS:
# #                     if next_seq_num >= len(sender_queue):
# #                         packet_available.wait()
# #                         continue
# #                     seq_num = next_seq_num % N
# #                     packet = sender_queue[next_seq_num]
# #                     frame = {'seq_num': seq_num, 'data': packet, 'timestamp': time.time()}
# #                     simulate_network_delay(T3, T4)
# #                     if not simulate_frame_drop(P):
# #                         sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
# #                         log_file.write(f"Sent Frame: Seq {seq_num}\n")
# #                     else:
# #                         log_file.write(f"Frame Dropped (Sender): Seq {seq_num}\n")
# #                     total_frames_sent += 1
# #                     timers[next_seq_num] = time.time()
# #                     next_seq_num += 1

# #         try:
# #             sender_socket.settimeout(0.1)
# #             ack_data, _ = sender_socket.recvfrom(1024)
# #             ack_frame = pickle.loads(ack_data)
# #             ack_num = ack_frame['ack_num']
# #             log_file.write(f"Received ACK: {ack_num}\n")
# #             with lock:
# #                 acked_seq_num = None
# #                 for seq_num in range(sender_base, next_seq_num):
# #                     if seq_num % N == ack_num:
# #                         acked_seq_num = seq_num
# #                 if acked_seq_num is not None and acked_seq_num >= sender_base:
# #                     sender_base = acked_seq_num + 1
# #                     for seq_num in list(timers.keys()):
# #                         if seq_num < sender_base:
# #                             timers.pop(seq_num)
# #         except socket.timeout:
# #             pass

# #         current_time = time.time()
# #         with lock:
# #             for seq_num in list(timers.keys()):
# #                 if current_time - timers[seq_num] > 1.0:
# #                     log_file.write("Timeout occurred, retransmitting frames.\n")
# #                     for seq_num in range(sender_base, next_seq_num):
# #                         if seq_num in timers:
# #                             packet_index = seq_num
# #                             if packet_index >= len(sender_queue):
# #                                 break
# #                             packet = sender_queue[packet_index]
# #                             frame = {'seq_num': seq_num % N, 'data': packet, 'timestamp': time.time()}
# #                             simulate_network_delay(T3, T4)
# #                             if not simulate_frame_drop(P):
# #                                 sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
# #                                 log_file.write(f"Retransmitted Frame: Seq {seq_num % N}\n")
# #                             else:
# #                                 log_file.write(f"Frame Dropped (Retransmission): Seq {seq_num % N}\n")
# #                             total_frames_sent += 1
# #                             total_retransmissions += 1
# #                             timers[seq_num] = time.time()
# #                     break
# #         time.sleep(0.01)

# # def receive_frames(P, T3, T4, log_file):
# #     global expected_seq_num, total_delay
# #     received_packets = 0
# #     while received_packets < TOTAL_PACKETS:
# #         try:
# #             receiver_socket.settimeout(1)
# #             frame_data, _ = receiver_socket.recvfrom(1024)
# #             frame = pickle.loads(frame_data)
# #             seq_num = frame['seq_num']
# #             log_file.write(f"Received Frame: Seq {seq_num}\n")
# #             simulate_network_delay(T3, T4)
# #             if seq_num == expected_seq_num:
# #                 total_delay += time.time() - frame['timestamp']
# #                 received_packets += 1
# #                 expected_seq_num = (expected_seq_num + 1) % N
# #             ack_num = (expected_seq_num - 1 + N) % N
# #             ack_frame = {'ack_num': ack_num}
# #             if not simulate_frame_drop(P):
# #                 receiver_socket.sendto(pickle.dumps(ack_frame), SENDER_ADDRESS)
# #                 log_file.write(f"Sent ACK: {ack_num}\n")
# #             else:
# #                 log_file.write(f"ACK Dropped: {ack_num}\n")
# #         except socket.timeout:
# #             continue

# # def simulate_network_delay(T3, T4):
# #     delay = random.uniform(T3, T4)
# #     time.sleep(delay)

# # def simulate_frame_drop(P):
# #     return random.random() < P

# # def run_simulation(P, T3, T4, file_name):
# #     with open(file_name, 'w') as log_file:
# #         packet_thread = threading.Thread(target=packet_generator)
# #         packet_thread.start()
# #         sender_thread = threading.Thread(target=send_frames, args=(P, T3, T4, log_file))
# #         receiver_thread = threading.Thread(target=receive_frames, args=(P, T3, T4, log_file))
# #         sender_thread.start()
# #         receiver_thread.start()
# #         packet_thread.join()
# #         sender_thread.join()
# #         receiver_thread.join()

# #         log_file.write("\nSimulation Completed.\n")
# #         log_file.write(f"Total Frames Sent: {total_frames_sent}\n")
# #         log_file.write(f"Total Retransmissions: {total_retransmissions}\n")
# #         log_file.write(f"Average Delay per Packet: {total_delay / TOTAL_PACKETS:.4f} seconds\n")
# #         log_file.write(f"Average Number of Times a Frame was Sent: {total_frames_sent / TOTAL_PACKETS:.2f}\n")

# #     sender_socket.close()
# #     receiver_socket.close()

# # if __name__ == "__main__":
# #     run_simulation(P=0.001, T3=0.05, T4=0.1, file_name="simulation_case_1.txt")
# #     run_simulation(P=0.01, T3=0.1, T4=0.2, file_name="simulation_case_2.txt")

# import threading
# import time
# import random
# import socket
# import pickle
# import logging
# import sys

# # Configuration Parameters (T1 and T2 remain the same)
# T1 = 0.1  # Minimum packet generation interval (seconds)
# T2 = 0.2  # Maximum packet generation interval (seconds)

# N = 8       # Modulo for sequence numbers
# WINDOW_SIZE = 7  # Transmit window size

# # Global Variables (will be initialized in run_simulation)
# sender_queue = []
# receiver_queue = []
# sender_base = 0
# next_seq_num = 0
# expected_seq_num = 0
# total_delay = 0
# total_frames_sent = 0
# total_retransmissions = 0

# lock = threading.Lock()
# print_lock = threading.Lock()
# packet_available = threading.Condition()

# # UDP Socket Setup
# SENDER_ADDRESS = ('localhost', 12000)
# RECEIVER_ADDRESS = ('localhost', 13000)

# def packet_generator(TOTAL_PACKETS):
#     try:
#         """Generates packets at random intervals and adds them to the sender queue."""
#         global sender_queue
#         for i in range(TOTAL_PACKETS):
#             time.sleep(random.uniform(T1, T2))
#             packet = f"Packet_{i}"
#             with packet_available:
#                 sender_queue.append(packet)
#                 packet_available.notify_all()  # Notify the sender that a new packet is available
#             logging.info(f"Generated: {packet}")
#     except Exception as e:
#         logging.error(f"Exception in packet_generator: {e}")

# def is_seq_num_less(a, b):
#     return ((b - a + N) % N) < (N // 2)

# def send_frames(TOTAL_PACKETS, P, T3, T4):
#     try:
#         global sender_base, next_seq_num, total_frames_sent, total_retransmissions
#         timers = {}
#         while True:
#             # Check if all packets have been sent and acknowledged
#             with lock:
#                 if sender_base >= TOTAL_PACKETS and not timers:
#                     break  # All packets sent and acknowledged

#             # Send frames within the window
#             with packet_available:
#                 with lock:
#                     while next_seq_num < sender_base + WINDOW_SIZE and next_seq_num < TOTAL_PACKETS:
#                         if next_seq_num >= len(sender_queue):
#                             packet_available.wait()  # Wait for the packet to be available
#                             continue
#                         seq_num = next_seq_num % N
#                         packet = sender_queue[next_seq_num]
#                         frame = {
#                             'seq_num': seq_num,
#                             'data': packet,
#                             'timestamp': time.time()
#                         }
#                         simulate_network_delay(T3, T4)
#                         if not simulate_frame_drop(P):
#                             sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
#                             logging.info(f"Sent Frame: Seq {seq_num}")
#                         else:
#                             logging.info(f"Frame Dropped (Sender): Seq {seq_num}")
#                         total_frames_sent += 1
#                         timers[next_seq_num] = time.time()
#                         next_seq_num += 1

#             # Check for ACKs
#             try:
#                 sender_socket.settimeout(0.1)
#                 ack_data, _ = sender_socket.recvfrom(1024)
#                 ack_frame = pickle.loads(ack_data)
#                 ack_num = ack_frame['ack_num']
#                 logging.info(f"Received ACK: {ack_num}")
#                 with lock:
#                     # Map ack_num to absolute sequence number
#                     acked_seq_num = None
#                     for seq_num in range(sender_base, next_seq_num):
#                         if seq_num % N == ack_num:
#                             acked_seq_num = seq_num
#                     if acked_seq_num is not None and acked_seq_num >= sender_base:
#                         sender_base = acked_seq_num + 1
#                         # Remove timers for acknowledged frames
#                         for seq_num in list(timers.keys()):
#                             if seq_num < sender_base:
#                                 timers.pop(seq_num)
#             except socket.timeout:
#                 pass  # No ACK received during this interval

#             # Handle timeouts and retransmissions
#             current_time = time.time()
#             with lock:
#                 # Check if any unacknowledged frame has timed out
#                 for seq_num in list(timers.keys()):
#                     if current_time - timers[seq_num] > 1.0:
#                         logging.info("Timeout occurred, retransmitting frames.")
#                         # Retransmit all frames in the window starting from sender_base
#                         for seq_num in range(sender_base, next_seq_num):
#                             if seq_num in timers:
#                                 packet_index = seq_num
#                                 if packet_index >= len(sender_queue):
#                                     break
#                                 packet = sender_queue[packet_index]
#                                 frame = {
#                                     'seq_num': seq_num % N,
#                                     'data': packet,
#                                     'timestamp': time.time()
#                                 }
#                                 simulate_network_delay(T3, T4)
#                                 if not simulate_frame_drop(P):
#                                     sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
#                                     logging.info(f"Retransmitted Frame: Seq {seq_num % N}")
#                                 else:
#                                     logging.info(f"Frame Dropped (Retransmission): Seq {seq_num % N}")
#                                 total_frames_sent += 1
#                                 total_retransmissions += 1
#                                 timers[seq_num] = time.time()
#                         break  # Exit after handling timeout
#             # Sleep briefly to prevent tight loop
#             time.sleep(0.01)
#     except Exception as e:
#         logging.error(f"Exception in send_frames: {e}")

# def receive_frames(TOTAL_PACKETS, P, T3, T4):
#     try:
#         global expected_seq_num, total_delay
#         received_packets = 0
#         while True:
#             if received_packets >= TOTAL_PACKETS:
#                 break
#             try:
#                 receiver_socket.settimeout(1)
#                 frame_data, _ = receiver_socket.recvfrom(1024)
#                 frame = pickle.loads(frame_data)
#                 seq_num = frame['seq_num']
#                 data = frame['data']
#                 logging.info(f"Received Frame: Seq {seq_num}")
#                 # Simulate network delay
#                 simulate_network_delay(T3, T4)
#                 if seq_num == expected_seq_num:
#                     # Correct frame received
#                     total_delay += time.time() - frame['timestamp']
#                     received_packets += 1
#                     expected_seq_num = (expected_seq_num + 1) % N
#                 else:
#                     # Discard out-of-order frames
#                     logging.info(f"Discarded Frame: Seq {seq_num} (Expected: {expected_seq_num})")
#                 # Send ACK for the last correctly received frame
#                 ack_num = (expected_seq_num - 1 + N) % N
#                 ack_frame = {
#                     'ack_num': ack_num
#                 }
#                 if not simulate_frame_drop(P):
#                     receiver_socket.sendto(pickle.dumps(ack_frame), SENDER_ADDRESS)
#                     logging.info(f"Sent ACK: {ack_frame['ack_num']}")
#                 else:
#                     logging.info(f"ACK Dropped: {ack_frame['ack_num']}")
#             except socket.timeout:
#                 continue
#     except Exception as e:
#         logging.error(f"Exception in receive_frames: {e}")

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
#     sender_queue = []
#     receiver_queue = []
#     sender_base = 0
#     next_seq_num = 0
#     expected_seq_num = 0
#     total_delay = 0
#     total_frames_sent = 0
#     total_retransmissions = 0

# def run_simulation(TOTAL_PACKETS, P, T3, T4, output_file):
#     # Reset global variables
#     reset_globals()

#     # Set up logging to write to the output file
#     logging.basicConfig(filename=output_file, level=logging.INFO, format='%(message)s')

#     # Re-bind sockets to avoid address in use error
#     global sender_socket, receiver_socket
#     sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sender_socket.bind(SENDER_ADDRESS)
#     receiver_socket.bind(RECEIVER_ADDRESS)

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
#     TOTAL_PACKETS = 10000  # Large number as per requirement
#     T1 = 0.1  # Minimum packet generation interval
#     T2 = 0.2  # Maximum packet generation interval

#     # Define simulation cases
#     cases = [
#         # Case 1: Lower drop probability, original delays
#         {
#             'P': 0.001,  # Lower drop probability
#             'T3': 0.05,
#             'T4': 0.1,
#             'output_file': 'C:/Users/aarya/Github_Projects/CN_Assignments/Ass-2/simulation_case1.txt'
#         },
#         # Case 2: Higher drop probability, higher delays
#         {
#             'P': 0.01,  # Higher drop probability
#             'T3': 0.1,
#             'T4': 0.2,
#             'output_file': 'C:/Users/aarya/Github_Projects/CN_Assignments/Ass-2/simulation_case2.txt'
#         }
#     ]

#     for idx, case in enumerate(cases):
#         print(f"Starting Simulation Case {idx + 1}")
#         run_simulation(TOTAL_PACKETS, case['P'], case['T3'], case['T4'], case['output_file'])
#         print(f"Simulation Case {idx + 1} Completed. Output saved to {case['output_file']}")

# if __name__ == "__main__":
#     main()

import threading
import time
import random
import socket
import pickle
import logging
import sys

# Configuration Parameters (T1 and T2 remain the same)
T1 = 0.1  # Minimum packet generation interval (seconds)
T2 = 0.2  # Maximum packet generation interval (seconds)

N = 8       # Modulo for sequence numbers
WINDOW_SIZE = 7  # Transmit window size

# Global Variables (will be initialized in run_simulation)
sender_queue = []
receiver_queue = []
sender_base = 0
next_seq_num = 0
expected_seq_num = 0
total_delay = 0
total_frames_sent = 0
total_retransmissions = 0

lock = threading.Lock()
print_lock = threading.Lock()
packet_available = threading.Condition()

# UDP Socket Setup
SENDER_ADDRESS = ('localhost', 12000)
RECEIVER_ADDRESS = ('localhost', 13000)

def packet_generator(TOTAL_PACKETS):
    try:
        """Generates packets at random intervals and adds them to the sender queue."""
        global sender_queue
        for i in range(TOTAL_PACKETS):
            time.sleep(random.uniform(T1, T2))
            packet = f"Packet_{i}"
            with packet_available:
                sender_queue.append(packet)
                packet_available.notify_all()  # Notify the sender that a new packet is available
            logging.info(f"Generated: {packet}")
    except Exception as e:
        logging.error(f"Exception in packet_generator: {e}")

def is_seq_num_less(a, b):
    return ((b - a + N) % N) < (N // 2)

def send_frames(TOTAL_PACKETS, P, T3, T4):
    try:
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
                            sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
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
                                    sender_socket.sendto(pickle.dumps(frame), RECEIVER_ADDRESS)
                                    logging.info(f"Retransmitted Frame: Seq {seq_num % N}")
                                else:
                                    logging.info(f"Frame Dropped (Retransmission): Seq {seq_num % N}")
                                total_frames_sent += 1
                                total_retransmissions += 1
                                timers[seq_num] = time.time()
                        break  # Exit after handling timeout
            # Sleep briefly to prevent tight loop
            time.sleep(0.01)
    except Exception as e:
        logging.error(f"Exception in send_frames: {e}")

def receive_frames(TOTAL_PACKETS, P, T3, T4):
    try:
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
                    receiver_socket.sendto(pickle.dumps(ack_frame), SENDER_ADDRESS)
                    logging.info(f"Sent ACK: {ack_frame['ack_num']}")
                else:
                    logging.info(f"ACK Dropped: {ack_frame['ack_num']}")
            except socket.timeout:
                continue
    except Exception as e:
        logging.error(f"Exception in receive_frames: {e}")

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

    # Re-bind sockets to avoid address in use error
    global sender_socket, receiver_socket
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_socket.bind(SENDER_ADDRESS)
    receiver_socket.bind(RECEIVER_ADDRESS)

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
    TOTAL_PACKETS = 10000  # Large number as per requirement
    T1 = 0.1  # Minimum packet generation interval
    T2 = 0.2  # Maximum packet generation interval

    # Define simulation cases
    cases = [
        # Case 1: Lower drop probability, original delays
        {
            'P': 0.01,  # Lower drop probability
            'T3': 0.05,
            'T4': 0.1,
            'output_file': 'C:/Users/aarya/Github_Projects/CN_Assignments/Ass-3/Using Single Machine/dummy1.txt'
        },
        # Case 2: Higher drop probability, higher delays
        {
            'P': 0.1,  # Higher drop probability
            'T3': 0.1,
            'T4': 0.2,
            'output_file': 'C:/Users/aarya/Github_Projects/CN_Assignments/Ass-3/Using Single Machine/dummy2.txt'
        }
    ]

    for idx, case in enumerate(cases):
        print(f"Starting Simulation Case {idx + 1}")
        run_simulation(TOTAL_PACKETS, case['P'], case['T3'], case['T4'], case['output_file'])
        print(f"Simulation Case {idx + 1} Completed. Output saved to {case['output_file']}")

if __name__ == "__main__":
    main()
