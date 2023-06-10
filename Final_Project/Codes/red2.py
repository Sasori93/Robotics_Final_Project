#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import time
import numpy as np
import subprocess
from picamera2 import Picamera2
import picar_4wd as fc

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()


def turn_left_90_degrees():
    start_time = time.time()
    fc.turn_left(10)
    while time.time() - start_time < 1.2:
        pass
    fc.stop()

path = '/home/pi/Desktop/fire.mp3'

def play_audio_file(file_path):
    subprocess.run(["mplayer", file_path])


while True:
    frame = picam2.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    height, width, _ = frame.shape
    
    center_x = int(width / 2)
    center_y = int(height / 2)
    
    pixel_center = hsv[center_y, center_x]
    hue = pixel_center[0]
    
    
    color = 'undefined'
    if hue > 160:
        color = 'red' 
    elif hue < 80:
        color = 'yellow'
    else:
        color = 'other'
        
    
    center_bgr = frame[center_y, center_x]
    b,g,r = int(center_bgr[0]),int(center_bgr[1]),int(center_bgr[2])
    cv2.circle(frame, (center_x, center_y), 5, (0,255,0),3)
    cv2.putText(frame, color, (10, 60),0, 1, (b,g,r), 2)
    

    #cv2.imshow('frame', frame)
    time.sleep(5)
    
    
    if color == 'red':
        time.sleep(20)
        play_audio_file(path)
    elif color == 'yellow':
        print('Yellow detected!')
        time.sleep(5)
        fc.forward(3)
        time.sleep(2)
        turn_left_90_degrees()
        time.sleep(2)
        fc.forward(2)
        time.sleep(2)
        fc.stop()
        time.sleep(3)
    else:
        fc.stop()
        time.sleep(3)
        
        
    if cv2.waitKey(1) == ord("q"):
        break
    

cv2.destroyAllWindows()
