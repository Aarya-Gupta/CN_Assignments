import time
import socket

# Create a UDP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set a timeout of 1 second
clientSocket.settimeout(1)

# Server details (Assuming the server is running on the same machine)
serverAddress = ('localhost', 12000)

# Variables to track RTTs and packet loss
rtt_list = []
num_pings = 10
packet_loss_count = 0

for sequence_number in range(1, num_pings + 1):
    # Record the time the ping was sent
    start_time = time.time()
    
    # Create the message
    message = f"Ping {sequence_number} {start_time}"
    
    try:
        # Send the ping message
        clientSocket.sendto(message.encode(), serverAddress)
        
        # Receive the server's response
        response, server = clientSocket.recvfrom(1024)
        
        # Calculate the RTT
        rtt = time.time() - start_time
        rtt_list.append(rtt)
        
        # Print the server's response and RTT
        print(f"Reply from {server}: {response.decode()} RTT: {rtt:.6f} seconds")
    
    except socket.timeout:
        # Handle packet loss
        print("Request timed out")
        packet_loss_count += 1

# Calculate and display statistics after all pings
if rtt_list:
    print("\n--- Ping Statistics ---")
    print(f"Packets: Sent = {num_pings}, Received = {num_pings - packet_loss_count}, Lost = {packet_loss_count}")
    print(f"Packet Loss = {(packet_loss_count / num_pings) * 100:.2f}%")
    print(f"Min RTT = {min(rtt_list):.6f} seconds")
    print(f"Max RTT = {max(rtt_list):.6f} seconds")
    print(f"Average RTT = {sum(rtt_list) / len(rtt_list):.6f} seconds")
else:
    print("All requests timed out.")

# Close the socket
clientSocket.close()
