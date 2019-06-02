import socket
import sys
from time import sleep, strftime
import os

remote_addr = '127.0.0.1'
remote_port = 27183

packet_size = 4096
buffer_size = 16777216 # 16 MB

sleeping_time = 0.001
D = 200

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address specified
server_address = (remote_addr, remote_port)
print('Starting up on %s port %s' % (remote_addr, str(remote_port)))
sock.bind(server_address)
sock.listen(1)

print('Waiting for a connection')
connection, client_address = sock.accept()

h264_output_dir = 'output'  
h264_file_name = strftime("%Y%m%d-%H%M%S") + '.h264'
h264_file_fullname = os.path.join(h264_output_dir, h264_file_name)
if not os.path.exists(h264_output_dir):
    os.makedirs(h264_output_dir)  
if os.path.exists(h264_file_fullname):
    os.remove(h264_file_fullname)
h264_file = open(h264_file_fullname, 'ab')
print('Output File: %s' % h264_file_fullname)

try:
    print('Client connected: %s' % client_address[0])

    # 1st Packet of 64 Bytes => Device Name 
    sleep(sleeping_time)
    data = connection.recv(64)
    device_name = data.decode("utf-8")
    print('Device Name:', device_name)

    # 2nd Packet of 2 Bytes => Device Screen Width 
    sleep(sleeping_time)
    data = connection.recv(2)
    device_screen_width = int.from_bytes(data, byteorder='big')
    print('Device Screen Width:', device_screen_width)

    # 3rd Packet of 2 Bytes => Device Screen Height 
    sleep(sleeping_time)
    data = connection.recv(2)
    device_screen_height = int.from_bytes(data, byteorder='big')
    print('Device Screen Height:', device_screen_height)

    # 4th Packet of 12 Bytes => Header 
    sleep(sleeping_time)
    data = connection.recv(12)
    pts = int.from_bytes(data[1:8], byteorder='big')
    hdr_packet_size = int.from_bytes(data[9:12], byteorder='big')
    print('PTS: %d, Header Packet Size: %d' % (pts, hdr_packet_size))

    # nth Packets => H.264 stream
    for i in range(1, D+1, 1):
        try:
            sleep(sleeping_time)
            data = connection.recv(packet_size)
            h264_file.write(data)           
        except Exception as e:
            print(str(e))

except Exception as e:
    print(str(e))
finally:
    connection.close()