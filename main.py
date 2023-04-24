import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import time

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-5fd35-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-5fd35.appspot.com",
})

bucket = storage.bucket()

cap = cv2.VideoCapture(1)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Resources/background3.png')
#Importing the mode images into a list
folderModePath = 'Resources/Modes'
#modePathList = os.listdir(folderModePath)
modePathList = ['1.png', '2.png', '3.png', '4.png']
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
#print(len(imgModeList))


# Load the encoding file
print("Loading Encode File ... ")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print("STUDENT IDS: ", studentIds)
print("Encode File Loaded ... ")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)          #INVERTS IMAGE ALONG THE VERTICAL AXIS
    y, x = 200, 250
    img = img[y:y + 480, x:x + 640]         # CROPS THE WEBCAM IMAGE TO ACCOMM0DATE THE TEMPLATE
    # E.B. EQUIVALENT TO success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)    # Finds the isolated encoding of the face

    imgBackground[162:162 + 480, 53:53 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceloc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #print("matches: ", matches)
            #print("faceDis: ", faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:             #Checks if a known face is detected
                #print("Known face detected")
                #print(studentIds[matchIndex])
                cv2.waitKey(4)
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scaling by 4 accounts for the previous resizing
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)     # Setting the rectangle thickness to 0

                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "LOADING", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Get the image from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance

                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()


                #Updates the attendance
                if secondsElapsed >5:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(100, 100, 100),1)
                    cv2.putText(imgBackground, str(studentInfo['role']), (990, 550),
                                cv2.FONT_HERSHEY_COMPLEX,0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (990, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (955, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175+216, 909:909+216] = imgStudent
                    time.sleep(2)


                counter +=1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    imgStudent = []
    else:
        modeType = 0
        counter = 0

    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
