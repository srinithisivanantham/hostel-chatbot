# ---------- IMPORTS ----------
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import requests

# ---------- FLASK APP ----------
app = Flask(__name__)
app.secret_key = "openonlyforme"

# ---------- DATABASE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hostel.db")

# ---------- SMS FUNCTION ----------
def send_sms(phone, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": "bQq8c6ZJs4hCi7DX92MfYj3BA1kTvpHmuOtdLGURzKxIgawoFlfrZwB0muX2kVlnDQSFpde5P6tL7oI3",
        "Content-Type": "application/json"
    }

    payload = {
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "v3",
        "numbers": phone
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print("SMS Error:", e)
        return {"error": "SMS Failed"}

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Student table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            register_no TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            room_no TEXT
        );
    """)

    # Insert dummy students only once
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany("""
            INSERT INTO students VALUES (?, ?, ?, ?)
        """, [
            ("231cs048", "Srinithi", "9345518460", "12"),
            ("231cs025", "Manisha", "9788618924", "13"),
            ("PKR003", "Madhu", "6369231372", "14"),
        ])

    # Leave table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            name TEXT,
            room_no TEXT,
            reason TEXT,
            from_date TEXT,
            to_date TEXT,
            status TEXT DEFAULT 'Pending'
        );
    """)

    # Complaint table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            name TEXT,
            room_no TEXT,
            complaint TEXT,
            status TEXT DEFAULT 'Pending'
        );
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- CHATBOT ----------
@app.route("/get")
def chatbot():
    msg = request.args.get("msg", "").lower()

    if "hi" in msg or "hello" in msg:
        return "Hello! Welcome to PKR Hostel 😊"

    elif "rules" in msg:
        return "• Entry before 9 PM<br>• Maintain silence<br>• No outsiders allowed"

    elif "menu" in msg:
        return "Breakfast: Idli/Dosa<br>Lunch: Rice, Sambar<br>Dinner: Chapati"

    elif "leave" in msg:
        return "Apply for leave here: <a href='/leave'>Leave Form</a>"

    elif "complaint" in msg:
        return "Register complaint here: <a href='/complaint'>Complaint Form</a>"

    else:
        return "Ask about rules, menu, leave or complaint."

# ---------- LEAVE ----------
@app.route("/leave")
def leave_form():
    return render_template("leave.html")

@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    register_no = request.form["register_no"]
    reason = request.form["reason"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, room_no FROM students WHERE register_no=?", (register_no,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return "❌ Invalid Register Number"

    name, room_no = student

    cursor.execute("""
        INSERT INTO leave_applications 
        (register_no, name, room_no, reason, from_date, to_date, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
    """, (register_no, name, room_no, reason, from_date, to_date))

    conn.commit()
    conn.close()
    return redirect("/")

# ---------- COMPLAINT ----------
@app.route("/complaint")
def complaint_form():
    return render_template("complaint.html")

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    register_no = request.form["register_no"]
    complaint = request.form["complaint"]

    conn = sqlite3.co
