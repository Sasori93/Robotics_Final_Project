import picar_4wd as fc
from imutils import paths
import numpy as np
import imutils
import cv2
import time
 
def find_marker(image):
    # convert the image to grayscale, blur it, and detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 35, 125)
 
    # find the contours in the edged image and keep the largest one;
    # we'll assume that this is our piece of paper in the image
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key = cv2.contourArea)    
    
    # compute the bounding box of the of the paper region and return it
    return cv2.minAreaRect(c)

    
def distance_to_camera(knownWidth, focalLength, perWidth):
    # compute and return the distance from the maker to the camera
    return (knownWidth * focalLength) / perWidth
    
    
KNOWN_DISTANCE = 120
 
# initialize the known object width, which in this case, the piece of
# paper is 12 inches wide
KNOWN_WIDTH = 7
 
# load the furst image that contains an object that is KNOWN TO BE 2 feet
# from our camera, then find the paper marker in the image, and initialize
# the focal length
image = cv2.imread("/home/pi/Desktop/test.jpg")
marker = find_marker(image)
focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH
    
# loop over the images
for imagePath in sorted(paths.list_images("/home/pi/Desktop/images")):
    # load the image, find the marker in the image, then compute the
    # distance to the marker from the camera
    image = cv2.imread(imagePath)
    marker = find_marker(image)
    cm = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
    print(cm)
 
    # draw a bounding box around the image and display it
    box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
    box = np.int0(box)
    cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
    cv2.putText(image, "%.dcm" %(cm), (image.shape[1] - 200, 
    image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
    2.0, (0, 255, 0), 3)
    cv2.imwrite("/home/pi/Dist_img.jpg", image)
    cv2.imshow("image", image)
    cv2.waitKey(0)


def main():
    final_distance = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
    dist = final_distance - 10
    seconds = int(round(dist / 25))
    if seconds > 0 or final_distance > 10:
        fc.forward(10)
        time.sleep(seconds)
    else:
        fc.stop()
    

if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()

