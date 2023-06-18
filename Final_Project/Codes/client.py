import socket
import cv2
import zmq
import base64
from picamera2 import Picamera2
import time

    

IP = '192.168.137.72'


picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280,720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

context = zmq.Context()

footage_socket = context.socket(zmq.PAIR)
footage_socket.connect('tcp://%s:5555'%IP)
print(IP)



while True:
	frame = picam2.capture_array()
	encode, buffer = cv2.imencode('.jpg', frame)

	jpg_as_test = base64.b64encode(buffer)
	footage_socket.send(jpg_as_test)

	
cv2.destroyAllWindows()


