import socket
import sys
from time import sleep
import os

remote_addr = '127.0.0.1'
remote_port = 27183

packet_size = 4096
buffer_size = 16777216 # 16 MB

sleeping_time = 0.01

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address specified
server_address = (remote_addr, remote_port)
sys.stdout.write('Starting up on %s port %s\n' % (remote_addr, str(remote_port)))
sock.bind(server_address)
sock.listen(1)

sys.stdout.write('Waiting for a connection\n')
connection, client_address = sock.accept()

try:
    #print('Client connected: %s' % client_address[0])

    # 1st Packet of 64 Bytes => Device Name 
    sleep(sleeping_time)
    data = connection.recv(64)
    device_name = data.decode("utf-8")
    sys.stdout.write('Device Name: %s\n' % device_name)

    # 2nd Packet of 2 Bytes => Device Screen Width 
    sleep(sleeping_time)
    data = connection.recv(2)
    device_screen_width = int.from_bytes(data, byteorder='big')
    sys.stdout.write('Device Screen Width: %s\n' % device_screen_width)

    # 3rd Packet of 2 Bytes => Device Screen Height 
    sleep(sleeping_time)
    data = connection.recv(2)
    device_screen_height = int.from_bytes(data, byteorder='big')
    sys.stdout.write('Device Screen Height: %s\n' % device_screen_height)

    # 4th Packet of 12 Bytes => Header 
    sleep(sleeping_time)
    data = connection.recv(12)
    pts = int.from_bytes(data[1:8], byteorder='big')
    hdr_packet_size = int.from_bytes(data[9:12], byteorder='big')
    sys.stdout.write('PTS: %d, Header Packet Size: %d\n' % (pts, hdr_packet_size))

    # nth Packets => H.264 stream
    while True:
        try:
            sleep(sleeping_time)
            data = connection.recv(packet_size)
            sys.stdout.buffer.write(data)
        except KeyboardInterrupt:
            break          
        except Exception as e:
            sys.stderr.write(str(e))
            pass

except Exception as e:
    sys.stderr.write(str(e))
    pass
finally:
    connection.close()