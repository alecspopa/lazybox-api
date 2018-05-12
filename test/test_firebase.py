import os
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(os.environ['FIREBASE_APPLICATION_CREDENTIALS'])

lazybox_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lazybox-cfb9a.firebaseio.com/'
})

ref = db.reference('states')

# Add to stack
ref.push('kitchen|D4|off')
# ref.push('last')

# Retrieve and delete from stack
print('-' * 20)

snapshot = ref.order_by_key().limit_to_first(1).get()
for key, val in snapshot.items():
    print(key, val)

    del_ref = db.reference('states/' + key)
    del_ref.delete()

print('-' * 20)
