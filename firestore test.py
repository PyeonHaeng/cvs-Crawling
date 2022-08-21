
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./key/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)
firebase_admin.initialize_app(cred, {
  'projectId': 'convenience-store-sale-data',
})

db = firestore.client()

doc_ref = db.collection(u'sale').document(u'test1')
doc_ref.set({
    'name' : '바나나우유',
    'type' : '11',
    'store' : 'gs',
})