import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException

# Initialize Firebase Admin SDK with the service account credentials
cred = credentials.Certificate("path/to/firebase-credentials.json")  # Replace with your credentials path
firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str) -> str:
    """Verify Firebase ID token."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return uid  # Return the Firebase UID if token is valid
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Firebase token")
