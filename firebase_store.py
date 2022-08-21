import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime



class FirebaseStore:
  def __init__(self) -> None:
    cred = credentials.Certificate("./key/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
      'projectId': 'convenience-store-sale-data',
    })
    self.db = firestore.client()
    


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
    collection_ref = self.db.collection(u'sale')
    batch = self.db.batch()

    #임시로 키 값으로 시간 : 번호 로 할까하고....
    now = datetime.now().strftime('%y-%m-%d-%H:%M:%S') + ':'
    
    for i, data in enumerate(datas):
        #add timestamp 추가 하고 data에 additional data 결합
        data['add_timestamp'] = firestore.SERVER_TIMESTAMP
        data.update(additional_datas)
        key = now + f'{i:04}'
        #batch로 일괄 처리 가능한 최대수가 500개 이기에 500개 처리마다 commit
        if i % 500 == 499:
            batch.commit()
            batch = self.db.batch()
        batch.set(collection_ref.document(key),data)

    batch.commit()
