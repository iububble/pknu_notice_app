import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

#Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('myKey.json')
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://mypknu-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

with open('./test_2.json', 'r') as f:
    test_data = json.load(f)

print(test_data)

ref = db.reference('major_notice') #db 위치 지정
ref.update(test_data) #해당 변수가 없으면 생성한다.