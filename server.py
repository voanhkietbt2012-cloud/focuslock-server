from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://focuslock-61fc0-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

@app.route("/")
def home():
    return "FocusLock Server Running"

@app.route("/approve")
def approve():
    request_id = request.args.get("id")

    if not request_id:
        return "Missing id"

    db.reference(f"unlock_requests/{request_id}").update({
        "status": "approved"
    })

    return "Approved"

@app.route("/deny")
def deny():
    request_id = request.args.get("id")

    if not request_id:
        return "Missing id"

    db.reference(f"unlock_requests/{request_id}").update({
        "status": "denied"
    })

    return "Denied"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)