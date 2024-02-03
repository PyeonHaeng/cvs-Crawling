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
    
  def set_sync_key(self,sync_key):
    '''
    데이터를 갱신한후에 조회를 위해 필요한 sync_key값을 db에 업데이트 하기 위해 사용
    '''

    query_ref = self.db.collection(u'sale').document('sync_key')
    query_ref.update({u'month':sync_key})

  def set_datas(self,datas,additional_datas ={},sync_key='2022:11',set_coll = 'sale'):
    '''
        딕셔너리 리스트 형의 데이터를 일괄로 firebase에 set

        Args:
            datas : db에 set 할 데이터들
            additional_datas : 기존 datas에 추가로 붙여 들어갈 데이터들 ex) 어느 편의점 데이터인지 gs,cu
            sync_key : 하위 collection의 부모가 될 document의 이름  sale - 2022:11 - items - gs25:대추
            set_coll : set할 collection 이름
        Return:
            성공시...
    '''


    
    parents_collection_ref = self.db.collection(u'sale').document(sync_key)
    collection_ref = parents_collection_ref.collection(u'items')
    batch = self.db.batch()

    #임시로 키 값으로 시간 : 번호 로 할까하고....
    #now = datetime.now().strftime('%y-%m-%d-%H:%M:%S') + ':'
    
    for i, data in enumerate(datas):
        #add timestamp 추가 하고 data에 additional data 결합
        data['add_timestamp'] = firestore.SERVER_TIMESTAMP
        data.update(additional_datas)
        #key = now + f'{i:04}'
        key = data['store'] +':'+ data['name']
        #batch로 일괄 처리 가능한 최대수가 500개 이기에 500개 처리마다 commit
        if i % 500 == 499:
            batch.commit()
            batch = self.db.batch()
        batch.set(collection_ref.document(key.replace('/','')),data) #키로 쓰려는 문자열에 '/' 포함되어있을경우 경로로 인식하여 에러 발생 하는듯

    batch.commit()


  def disable_data(self,select_keys,change_datas):
    """
    더 이상 사용하지 않는 기능
    새로운 크롤링 데이터를 넣기 위해 기존의 데이터들의 값을 변경하기 위해 사용
    
    Args : 
        select_keys(dict) : 바꾸고자 하는 데이터의 조건 ex) {'enable':True , 'store' : 'gs'}
        change_datas(dict) : 바꿀 데이터 ex) {'enable' : False}
    """
    
    query_ref = self.db.collection(u'sale')
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

