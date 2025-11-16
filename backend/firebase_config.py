# # backend/firebase_config.py
# import os
# import firebase_admin
# from firebase_admin import credentials, auth, firestore

# FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_JSON")

# if not firebase_admin._apps:
#     cred = credentials.Certificate(FIREBASE_CRED_PATH)
#     firebase_admin.initialize_app(cred)

# db = firestore.client()
