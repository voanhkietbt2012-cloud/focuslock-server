from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db

# KẾT NỐI FIREBASE
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://focuslock-61fc0-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

app = Flask(__name__)

# ===== YES =====
@app.route("/approve")
def approve():

    request_id = request.args.get("id")

    db.reference(f"unlock_requests/{request_id}").update({
        "status": "approved"
    })

    return "APPROVED"

# ===== NO =====
@app.route("/deny")
def deny():

    request_id = request.args.get("id")

    db.reference(f"unlock_requests/{request_id}").update({
        "status": "denied"
    })

    return "DENIED"

app.run(host="0.0.0.0", port=5000)