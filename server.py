from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

import random
import os

# =========================
# FLASK APP
# =========================

app = Flask(__name__)

CORS(app)

# =========================
# MAIL CONFIG
# =========================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# Render Environment Variables
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# =========================
# FIREBASE ADMIN SDK
# =========================

if not firebase_admin._apps:

    cred = credentials.Certificate(
        "serviceAccountKey.json"
    )

    firebase_admin.initialize_app(cred)

# =========================
# OTP STORAGE
# =========================

otp_store = {}

# =========================
# HOME ROUTE
# =========================

@app.route('/')
def home():

    return jsonify({
        "success": True,
        "message": "Flask Server Running Successfully"
    })

# =========================
# SEND OTP
# =========================

@app.route('/send-otp', methods=['POST'])
def send_otp():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON Data"
            }), 400

        email = data.get('email')

        if not email:

            return jsonify({
                "success": False,
                "message": "Email Required"
            }), 400

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP
        otp_store[email] = otp

        # Email Message
        msg = Message(
            subject="Your OTP Code",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f"""
Your OTP Code is:

{otp}

Do not share this OTP with anyone.
"""

        # Send Email
        mail.send(msg)

        print(f"OTP SENT: {email} -> {otp}")

        return jsonify({
            "success": True,
            "message": "OTP Sent Successfully"
        })

    except Exception as e:

        print("SEND OTP ERROR:")
        print(str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================
# VERIFY OTP
# =========================

@app.route('/verify-otp', methods=['POST'])
def verify_otp():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON Data"
            }), 400

        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:

            return jsonify({
                "success": False,
                "message": "Email and OTP Required"
            }), 400

        # Check OTP
        if email in otp_store and otp_store[email] == otp:

            return jsonify({
                "success": True,
                "message": "OTP Verified Successfully"
            })

        return jsonify({
            "success": False,
            "message": "Invalid OTP"
        }), 400

    except Exception as e:

        print("VERIFY OTP ERROR:")
        print(str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================
# CHANGE PASSWORD
# =========================

@app.route('/change-password', methods=['POST'])
def change_password():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON Data"
            }), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and Password Required"
            }), 400

        # Firebase User
        user = auth.get_user_by_email(email)

        # Update Password
        auth.update_user(
            user.uid,
            password=password
        )

        return jsonify({
            "success": True,
            "message": "Password Changed Successfully"
        })

    except Exception as e:

        print("CHANGE PASSWORD ERROR:")
        print(str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================
# RUN SERVER
# =========================

if __name__ == '__main__':

    print("===================================")
    print("FLASK SERVER STARTED")
    print("PORT: 5000")
    print("===================================")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )