import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-5fd35-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "123456":
        {
            "name" : "Cesar Sanchez",
            "role" : "CEO",
            "starting_year" : 2023,
            "total_attendance" : 100,
            "standing" : "1",
            "last_attendance_time" : "2023-1-1 12:12:12",
        },
    "100001":
        {
            "name" : "Emily Blunt",
            "role" : "Engineer",
            "starting_year" : 2023,
            "total_attendance" : 80,
            "standing" : "2",
            "last_attendance_time" : "2023-1-2 12:12:12"
        },
    "100005":
        {
            "name" : "Elon Musk",
            "role" : "COO",
            "starting_year" : 2022,
            "total_attendance" : 80,
            "standing" : "3",
            "last_attendance_time" : "2023-1-2 12:12:12"
        },
    "100010":
        {
            "name" : "Dwayne Johnson",
            "role" : "Analyst",
            "starting_year" : 2022,
            "total_attendance" : 79,
            "standing" : "4",
            "last_attendance_time" : "2023-1-2 12:12:12"
        },
    "100015":
        {
            "name" : "Steve Carell",
            "role" : "Analyst",
            "starting_year" : 2022,
            "total_attendance" : 81,
            "standing" : "5",
            "last_attendance_time" : "2023-1-2 12:12:12"
        },
}

for key, value in data.items():
    ref.child(key).set(value)           # takes the key (unique ID) and value (Details)