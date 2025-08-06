from flask import Flask, request, jsonify
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# === Firebase config (replace with your real values) ===
with open("firebase_client_config.json") as f:
    firebase_config = json.load(f)

# === Init Firebase Auth (for login/signup) ===
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# === Init Firestore (admin SDK) ===
# у Cloud Run, Cloud Functions, App Engine — ти можеш не використовувати .json ключ взагалі!
# Google автоматично підставляє обліковий запис сервісу через Workload Identity.
# Сервісний акаунт, під яким запускається Cloud Run, має мати роль: Cloud Datastore User (для Firestore), або Editor (для доступу до Firestore + іншого)

cred = None
if os.path.exists("firebase_config.json"):
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
else:
    firebase_admin.initialize_app()

db = firestore.client()

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    return "👋 Firebase Auth + Firestore (Python)"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    try:
        user = auth.create_user_with_email_and_password(email, password)
        return jsonify({"message": "User created", "email": user["email"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return jsonify({"message": "Login success", "idToken": user["idToken"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/user/<email>", methods=["GET", "POST"])
def user_data(email):
    if request.method == "POST":
        data = request.get_json()
        db.collection("users").document(email).set(data)
        return jsonify({"message": "Data saved"})

    doc = db.collection("users").document(email).get()
    if doc.exists:
        return jsonify(doc.to_dict())
    return jsonify({"error": "User not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
