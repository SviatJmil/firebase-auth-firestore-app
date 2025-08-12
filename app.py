from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# === Firebase config ===
with open("firebase_client_config.json") as f:
    firebase_config = json.load(f)

# === Init Firebase Auth (for login/signup) ===
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# === Init Firestore (admin SDK) ===
if os.path.exists("firebase_config.json"):
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
else:
    firebase_admin.initialize_app()

db = firestore.client()

# === FastAPI App ===
app = FastAPI(title="Firebase Auth + Firestore API")

# === Pydantic models for requests ===
class AuthRequest(BaseModel):
    email: str
    password: str

class UserData(BaseModel):
    data: dict

@app.get("/")
async def home():
    return {"message": "👋 Firebase Auth + Firestore (Python, FastAPI)"}

@app.post("/signup")
async def signup(request: AuthRequest):
    try:
        user = auth.create_user_with_email_and_password(request.email, request.password)
        return {"message": "User created", "email": user["email"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
async def login(request: AuthRequest):
    try:
        user = auth.sign_in_with_email_and_password(request.email, request.password)
        return {"message": "Login success", "idToken": user["idToken"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/user/{email}")
async def get_user(email: str = Path(..., description="User email")):
    doc = db.collection("users").document(email).get()
    if doc.exists:
        return doc.to_dict()
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/user/{email}")
async def save_user(email: str, data: dict):
    db.collection("users").document(email).set(data)
    return {"message": "Data saved"}
