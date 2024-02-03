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
        
    def disable_data(self,select_keys,change_datas):
        """
        새로운 크롤링 데이터를 넣기 위해 기존의 데이터들의 값을 변경하기 위해 사용
        
        Args : 
            select_keys(dict) : 바꾸고자 하는 데이터의 조건 ex) {'enable':True , 'store' : 'gs'}
            change_datas(dict) : 바꿀 데이터 ex) {'enable' : False}
        """
        
        query_ref = self.db.reference(u'sale')
        for field, val in select_keys.items():
            query_ref = query_ref.where(field,u'==',val)
        
        query_datas = query_ref.stream()

        
        collection_ref = self.db.collection(u'sale')

        batch = self.db.batch()
        for i,data in enumerate(query_datas):
            update_ref = collection_ref.document(data.id)
            
            if i % 500 == 499:
                batch.commit()
                batch = self.db.batch()
            batch.update(update_ref,change_datas)
        batch.commit()

    def test(self):
        query = self.db_ref.child('sale').order_by_child('enable').equal_to(True)
        for key in query:
            print(key)
        pass

#test = FirebaseRealtime()

#test.test()
