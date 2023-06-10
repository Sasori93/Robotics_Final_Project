from imutils import paths
import numpy as np
import imutils
import cv2
import time
from picamera2 import Picamera2
import numpy as np
import picar_4wd as fc


picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

lower_range = np.array([105,85,44])
upper_range = np.array([179,255,255])

def turn_right_15_degrees():
    start_time = time.time()
    fc.turn_right(10)
    while time.time() - start_time < 0.2:  # Adjust this value to achieve a 15-degree right turn
        pass
    fc.stop()

while True:
    frame = picam2.capture_array()
    
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_range,upper_range)
    _,mask1=cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
    cnts,_=cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    
    height, width, _ = frame.shape   
    center_x = int(width / 2)
    center_y = int(height / 2)   
    pixel_center = hsv[center_y, center_x]
    hue = pixel_center[0]
    
    center_bgr = frame[center_y, center_x]
    b,g,r = int(center_bgr[0]),int(center_bgr[1]),int(center_bgr[2])
    cv2.circle(frame, (center_x, center_y), 5, (0,255,0),2)

    object_detected = False
    
    for c in cnts:
        x=600
        if cv2.contourArea(c)>x:
            x,y,w,h=cv2.boundingRect(c)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    
            obj_x = x + int(w / 2)
            obj_y = y + int(h / 2)
            
            if obj_y > center_y:
                fc.stop()
            
            if abs(obj_x - center_x) < 50 and abs(obj_y - center_y) < 50:
                object_detected = True
                break

    if object_detected:
        fc.forward(3)
        time.sleep(3)
        fc.stop()
        break  # Exit the while loop after stopping

    else:
        time.sleep(5)
        turn_right_15_degrees()
        time.sleep(5)
        fc.stop()
          
    cv2.imshow("FRAME",frame)
    if cv2.waitKey(1) == ord("q"):
        break
        
cv2.destroyAllWindows()


            

