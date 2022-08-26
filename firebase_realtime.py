import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

from firebase_admin import db



class FirebaseRealtime:
    def __init__(self) -> None:
        cred = credentials.Certificate("./key/serviceAccountKey.json")
        firebase_admin.initialize_app(cred,{
            'databaseURL':"https://convenience-store-sale-data-default-rtdb.asia-southeast1.firebasedatabase.app/"
        })
        self.db_ref = db.reference('/')
    


    def set_datas(self,datas,additional_datas ={},set_coll = 'sale'):
        '''
            딕셔너리 리스트 형의 데이터를 일괄로 firebase에 set

            Args:
                datas : db에 set 할 데이터들
                additional_datas : 기존 datas에 추가로 붙여 들어갈 데이터들 ex) 어느 편의점 데이터인지 gs,cu
                set_coll : set할 collection 이름
            Return:
                성공시...
        '''
        #임시로 키 값으로 시간 : 번호 로 할까하고....
        now = datetime.now().strftime('%y-%m-%d-%H:%M:%S') + ':'
        
        for i, data in enumerate(datas):
            #add timestamp 추가 하고 data에 additional data 결합 - realtime 에서는 timestapm 어케 하지?
            #data['add_timestamp'] = firestore.SERVER_TIMESTAMP
            data.update(additional_datas)


        batch_data = {set_coll:{now + f'{i:04}' : data for i, data in enumerate(datas)}}

        
        #self.db_ref.set(batch_data)

        
        self.db_ref.set(batch_data)

    def test(self):
        
        self.db_ref.child('sale').set([{'img': '1111','test':'1112222'},{'img':None,'test':'test123'}])
