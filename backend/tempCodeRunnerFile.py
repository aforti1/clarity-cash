from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from .utils import auth, db, plaid_client, verify_firebase_token
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest

app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to extract token from Authorization header
def get_token_from_header(request: Request):
    """Extract Firebase token from Authorization header."""
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(status_code=403, detail="Authorization token is missing")
    return token.split(" ")[1]  # Assuming token is sent as "Bearer <id_token>"

@app.get("/plaid/link-token/{uid}")
def create_link_token(uid: str, request: Request):
    """Generate a Plaid Link token for a specific user."""
    # Verify the Firebase ID token (you can pass token from frontend here)
    id_token = get_token_from_header(request)  # Get token from header
    user_uid = verify_firebase_token(id_token)  # Verify and get Firebase UID
    
    # Now, proceed with creating a link token for the specific user
    if user_uid != uid:
        raise HTTPException(status_code=403, detail="Unauthorized: Firebase UID does not match")

    try:
        request = LinkTokenCreateRequest(
            user={"client_user_id": uid},  # Use the Firebase UID as the client_user_id
            client_name="Hackathon App",  # Name of your app
            products=[Products.TRANSACTIONS],  # You can add other products if needed
            country_codes=[CountryCode.US],  # Assuming US is the target country
            language="en"  # Default language for the link interface
        )
        
        # Send request to Plaid API
        response = plaid_client.link_token_create(request)
        
        # Return the link token to the frontend
        return response.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating link token: {str(e)}")

@app.post("/plaid/exchange-public-token")
def exchange_public_token(public_token: str, uid: str, request: Request):
    """Exchange the public token for an access token and store it in Firebase."""
    # Verify the Firebase ID token (you can pass token from frontend here)
    id_token = get_token_from_header(request)  # Get token from header
    user_uid = verify_firebase_token(id_token)  # Verify and get Firebase UID
    
    # Ensure the user making the request is authorized
    if user_uid != uid:
        raise HTTPException(status_code=403, detail="Unauthorized: Firebase UID does not match")

    try:
        # Exchange the public token for an access token
        exchange_response = plaid_client.item_public_token_exchange(public_token)
        access_token = exchange_response['access_token']

        # Store the access token in Firebase Firestore under the user's document
        db.collection('users').document(uid).set({
            'plaid_access_token': access_token  # Store the access token securely in Firebase
        }, merge=True)

        return {"message": "Access token saved successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exchanging public token: {str(e)}")
