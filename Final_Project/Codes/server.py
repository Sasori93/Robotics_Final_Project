#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 23:51:40 2023

@author: shihangyu
"""

import zmq
import base64
import cvzone
import numpy as np
import cv2
import time
from cvzone.HandTrackingModule import HandDetector
import csv

context = zmq.Context()

footage_socket = context.socket(zmq.PAIR)
footage_socket.bind('tcp://*:5555')


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)


detector = HandDetector(detectionCon=0.8, maxHands=1)

class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None
        
        
    def update(self, cursor, bboxs):
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)


path = '/Users/shihangyu/Desktop/data.csv'
with open(path, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]


mcqList = []
for q in dataAll:
    mcqList.append(MCQ(q))
    
qNo = 0
qTotal = len(dataAll)
lst = []

    
while True:
    source = footage_socket.recv_string()
    frame = base64.b64decode(source)
    npimg = np.frombuffer(frame, dtype=np.uint8)
    frame = cv2.imdecode(npimg, 1)
    
    
    ret, img = cap.read()    
    hands, img = detector.findHands(img)
    
    
    if qNo < qTotal:
        mcq = mcqList[qNo]
    
        img, bbox = cvzone.putTextRect(img, mcq.question, [460, 200], 2, 2, offset=50, border=5)
        img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [460, 350], 2, 2, offset=50, border=5)
        img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [800, 350], 2, 2, offset=50, border=5)
        img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [460, 500], 2, 2, offset=50, border=5)
        img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [800, 500], 2, 2, offset=50, border=5)
        
        if hands:
            lmList1 = hands[0]["lmList"]  # List of 21 Landmark points
            cursor = lmList1[8]
            
            length, info, img = detector.findDistance(lmList1[8][:2], lmList1[12][:2], img)
            
            if length < 35:
                mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                if mcq.userAns is not None:
                    time.sleep(0.3)
                    qNo += 1
                    
    else:
        score_mapping = {1: 1, 2: 2, 3: 3, 4: 4}
        score = 0
        for mcq in mcqList:
            user_choice = mcq.userAns
            if user_choice in score_mapping:
                score += score_mapping[user_choice]
                       
        totalScore = score
        
        if totalScore == 12:
            img, _ = cvzone.putTextRect(img, "Red Alert: Highest risk!", [250, 300], 2, 2, offset=50, border=5)
            img, _ = cvzone.putTextRect(img, f'Evaluate Score: {totalScore}', [250, 450], 2, 2, offset=50, border=5)
        elif totalScore == 3:
            img, _ = cvzone.putTextRect(img, "Blue Alert: Lowest risk", [250, 300], 2, 2, offset=50, border=5)
            img, _ = cvzone.putTextRect(img, f'Evaluate Score: {totalScore}', [250, 450], 2, 2, offset=50, border=5)
        elif totalScore >=6 and totalScore < 9:
            img, _ = cvzone.putTextRect(img, "Yellow Alert: Lower risk", [250, 300], 2, 2, offset=50, border=5)
            img, _ = cvzone.putTextRect(img, f'Evaluate Score: {totalScore}', [250, 450], 2, 2, offset=50, border=5)
        elif totalScore >= 9 and totalScore < 12:
            img, _ = cvzone.putTextRect(img, "Orange Alert: Higher risk", [250, 300], 2, 2, offset=50, border=5)
            img, _ = cvzone.putTextRect(img, f'Evaluate Score: {totalScore}', [250, 450], 2, 2, offset=50, border=5)
            
        
    barValue = 150 + (950 // qTotal) * qNo
    cv2.rectangle(img, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (150, 600), (1100, 650), (255, 0, 255), 5)
    img, _ = cvzone.putTextRect(img, f'{round((qNo / qTotal) * 100)}%', [1130, 635], 2, 2, offset=16)
                
    
    cv2.imshow('Stream', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
