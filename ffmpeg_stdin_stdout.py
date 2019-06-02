import socket
import sys
from time import sleep, strftime
import os
import subprocess

remote_addr = '127.0.0.1'
remote_port = 27183

packet_size = 4096
buffer_size = 16777216 # 16 MB

sleeping_time = 0.001
D = 10

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address specified
server_address = (remote_addr, remote_port)
print('Starting up on %s port %s' % (remote_addr, str(remote_port)))
sock.bind(server_address)
sock.listen(1)

print('Waiting for a connection')
connection, client_address = sock.accept()

yuv420p_output_dir = 'output'  
yuv420p_file_name = strftime("%Y%m%d-%H%M%S") + '.yuv'
yuv420p_file_fullname = os.path.join(yuv420p_output_dir, yuv420p_file_name)
if not os.path.exists(yuv420p_output_dir):
    os.makedirs(yuv420p_output_dir)  
if os.path.exists(yuv420p_file_fullname):
    os.remove(yuv420p_file_fullname)
#h264_file = open(yuv420p_file_fullname, 'ab')
#print('Output File: %s' % yuv420p_file_fullname)

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

    ffmpeg_cmd = [
        'ffmpeg',
        '-c:v', 'h264',
        '-f', 'h264',
        '-i', 'pipe:0',
        '-c:v', 'rawvideo', 
        '-f', 'rawvideo', 
        '-pix_fmt', 
        'yuv420p', 
        '-s', '{}x{}'.format(int(device_screen_width*0.1), int(device_screen_height*0.1)),
        'pipe:1'
    ]
    
    ffmpeg_proc = subprocess.Popen(
        ffmpeg_cmd,
        stdout = subprocess.PIPE,
        stdin = subprocess.PIPE
    )    

    # nth Packets => H.264 stream
    for i in range(1, D+1, 1):
        try:
            sleep(sleeping_time)
            data = connection.recv(packet_size)
        
            in_data = ffmpeg_proc.stdin.write(data)
            #processed_data = ffmpeg_proc.stdout.read()                        
            #ffmpeg_proc.stdin.close()
            #ffmpeg_proc.wait()
            #print(processed_data)
            
            #h264_file.write(processed_data)           
        except Exception as e:
            print(str(e))

except Exception as e:
    print(str(e))
finally:
    connection.close()