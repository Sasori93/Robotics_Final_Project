import cv2
from picamera2 import Picamera2
import picar_4wd as fc
import numpy as np
import time

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

def find_orange(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # adjust these values
    #lower_orange = np.array([10, 100, 20])
    #upper_orange = np.array([30, 255, 255])
    lower_orange = np.array([152, 71, 67])
    upper_orange = np.array([179, 255, 255])
    mask = cv2.inRange(hsv, lower_orange, upper_orange)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        # Set a threshold value for contour area
        if cv2.contourArea(largest_contour) > 500:
            moments = cv2.moments(largest_contour)
            if moments["m00"] != 0:
                cX = int(moments["m10"] / moments["m00"])
                cY = int(moments["m01"] / moments["m00"])
                return cX, cY, True
    return None, None, False

def calculate_speed(centroid_X, frame_width):
    mid_frame = frame_width // 2
    distance_from_mid = centroid_X - mid_frame
    speed = np.clip(abs(distance_from_mid) / mid_frame * 100, 0, 100)  # calculate the speed based on the distance
    return int(speed)

def main():
    while True:
        image = picam2.capture_array()
        orange_centroid_X, orange_centroid_Y, is_orange_found = find_orange(image)
        if is_orange_found:
            speed = calculate_speed(orange_centroid_X, image.shape[1])
            if orange_centroid_X < image.shape[1] // 2:
                fc.turn_left(speed)
                time.sleep(0.1)
            elif orange_centroid_X > image.shape[1] // 2:
                fc.turn_right(speed)
                time.sleep(0.1)
            else:
                fc.forward(50)
                time.sleep(0.1)
            fc.stop()
        else:
            fc.stop()

if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()

