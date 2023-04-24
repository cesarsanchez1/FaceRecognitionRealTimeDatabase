import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-5fd35-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-5fd35.appspot.com",
})


#Importing the student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    #print(path)
    #print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])
    fileName = f'{folderPath}/{path}'   #Automatically creates a folder called Images using the path
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(len(imgList))
print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("ENCODING STARTED")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("ENCODING COMPLETE")

file = open("EncodeFile.p",'wb')            #Extracts all the encodings, file created and saved "EncodeFile.p"
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")




