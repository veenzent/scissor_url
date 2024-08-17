# - - - - - - - - - - FIREBASE REALTIME DB - - - - - - - -

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('../scissorurl-182fe-firebase-adminsdk-jlvfk-a6e66e1308.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://databaseName.firebaseio.com'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('restricted_access/secret_document')
print(ref.get())

def get_db():
    db = ref
    yield db
