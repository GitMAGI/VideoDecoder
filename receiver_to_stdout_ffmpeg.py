import socket
import sys
from time import sleep
import os
import cv2
import subprocess as sp
import numpy
import math

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

    ffmpeg_running = False
    FFMPEG_BIN = "ffmpeg"
    w = math.ceil((device_screen_width / 4) / 2.) * 2
    h = math.ceil((device_screen_height / 4) / 2.) * 2

    # nth Packets => H.264 stream
    while True:
        try:
            sleep(sleeping_time)
            data = connection.recv(packet_size)
            sys.stdin.buffer.write(data)

            if not ffmpeg_running:
                ffmpeg_running = True               
                command = [ FFMPEG_BIN,
                        '-i', '-',           
                        '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
                        '-c:v', 'rawvideo',
                        '-an','-sn',              # we want to disable audio processing (there is no audio)
                        '-f', 'image2pipe', 
                        '-s', w + 'x' + h,
                        '-']    
                pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

            raw_image = pipe.stdout.read(w*h*3)
            image =  numpy.fromstring(raw_image, dtype='uint8')
            image = image.reshape((h,w,3))          # Notice how height is specified first and then width
            if image is not None:
                cv2.imshow(device_name, image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            pipe.stdout.flush()

        except KeyboardInterrupt:
            break          
        except Exception as e:
            sys.stderr.write(str(e))
            pass
        cv2.destroyAllWindows()

except Exception as e:
    sys.stderr.write(str(e))
    pass
finally:
    connection.close()