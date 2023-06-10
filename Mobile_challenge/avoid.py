import time
import cv2
from picamera2 import Picamera2
import picar_4wd as fc
from imutils import paths
import numpy as np
import imutils
import RPi.GPIO as GPIO


picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# code from move.py start
import picar_4wd as fc
import time
import sys
import termios
import tty
import threading




def forward(duration):
    start_time = time.time()
    fc.forward(10)
    while time.time() - start_time < duration:
        pass
    fc.stop()
def turn_left_90_degrees():
    start_time = time.time()
    fc.turn_left(10)
    while time.time() - start_time < 1.2: # 根据实际情况调整这个值，以实现更精确的90度左转
        pass
    fc.stop()

def turn_right_90_degrees():
    start_time = time.time()
    fc.turn_right(10)
    while time.time() - start_time < 1.0: # 根据实际情况调整这个值，以实现更精确的90度右转
        pass
    fc.stop()


# code from move.py end


def find_marker(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 35, 125)
 
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key = cv2.contourArea)    
    
    return cv2.minAreaRect(c)

    
def distance_to_camera(knownWidth, focalLength, perWidth):
    return (knownWidth * focalLength) / perWidth
    
    
KNOWN_DISTANCE = 120

KNOWN_WIDTH = 7


image = cv2.imread("/home/pi/Desktop/test.jpg")
marker = find_marker(image)
focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH


while True:
    image = picam2.capture_array()

    marker = find_marker(image)
    cm = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
 
    box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
    box = np.int0(box)
    cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
    cv2.putText(image, "%.dcm" %(cm), (image.shape[1] - 200, 
    image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
    2.0, (0, 255, 0), 3)
    cv2.imshow("image", image)
    #cv2.waitKey(0)：
    if cv2.waitKey(1) == ord("q"):
        break


def main():
    final_distance = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
    dist = final_distance - 20
    seconds = int(round(dist / 25))
    if seconds > 0 or final_distance > 20:
        fc.forward(10)
        time.sleep(seconds)
    else:
        fc.stop()
        time.sleep(1)
    
    

if __name__ == "__main__":
    try:
        main()
        
        time.sleep(1)
        turn_right_90_degrees()
        time.sleep(1)
        forward(2)
        time.sleep(1)
        turn_left_90_degrees()
        time.sleep(1)
        forward(4)
        time.sleep(1)
        turn_left_90_degrees()
        time.sleep(1)
        forward(2)
        time.sleep(1)
        turn_right_90_degrees()
        time.sleep(1)
        forward(6)
        fc.stop()
        
    finally:
        fc.stop()
