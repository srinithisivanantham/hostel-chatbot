# ---------- IMPORTS ----------
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import requests

# ---------- FLASK APP ----------
app = Flask(__name__)
app.secret_key = "openonlyforme"

# ---------- DATABASE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hostel.db")

# ---------- FAST2SMS CONFIG ----------
FAST2SMS_API_KEY = "bQq8c6ZJs4hCi7DX92MfYj3BA1kTvpHmuOtdLGURzKxIgawoFlfrZwB0muX2kVlnDQSFpde5P6tL7oI3"

# ---------- SMS FUNCTION ----------
def send_sms(phone, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": FAST2SMS_API_KEY,
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
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print("SMS Response:", response.text)
        return response.text
    except Exception as e:
        print("SMS Error:", e)
        return None

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            register_no TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            room_no TEXT
        )
    """)

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

    # Leave Applications
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
        )
    """)

    # Complaints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            name TEXT,
            room_no TEXT,
            complaint TEXT,
            status TEXT DEFAULT 'Pending'
        )
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

    if "hi" in msg or "hello" in msg or "hey" in msg:
        return "Hello! Welcome to PKR Hostel 😊 How can I help you?"
    elif "hostel rules" in msg or "rules" in msg:
        return "• Entry before 9 PM<br>• Maintain silence<br>• No outsiders allowed"
    elif "mess menu" in msg or "menu" in msg:
        return "Breakfast: Idli/Dosa<br>Lunch: Rice, Sambar<br>Dinner: Chapati"
    elif "leave" in msg:
        return "Apply for leave here: <a href='/leave'>Leave Form</a>"
    elif "complaint" in msg:
        return "Register complaint here: <a href='/complaint'>Complaint Form</a>"
    elif "warden" in msg:
        return "Warden Contact: +91-9876543210"
    else:
        return "Please ask about hostel rules, mess menu, leave, complaint or warden."

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
        (register_no, name, room_no, reason, from_date, to_date)
        VALUES (?, ?, ?, ?, ?, ?)
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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, room_no FROM students WHERE register_no=?", (register_no,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return "❌ Invalid Register Number"

    name, room_no = student

    cursor.execute("""
        INSERT INTO complaints 
        (register_no, name, room_no, complaint)
        VALUES (?, ?, ?, ?)
    """, (register_no, name, room_no, complaint))

    conn.commit()
    conn.close()
    return redirect("/")

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "pkr@hostel@123":
            session["admin_logged_in"] = True
            return redirect("/admin/dashboard")
        return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_applications")
    leaves = cursor.fetchall()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", leaves=leaves, complaints=complaints)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin")

# ---------- LEAVE ACTION (ACCEPT / REJECT / DONE) ----------
@app.route("/leave_action/<int:leave_id>/<status>")
def leave_action(leave_id, status):
    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE leave_applications SET status=? WHERE id=?", (status, leave_id))

    cursor.execute("""
        SELECT students.phone, students.name
        FROM leave_applications
        JOIN students ON leave_applications.register_no = students.register_no
        WHERE leave_applications.id=?
    """, (leave_id,))
    data = cursor.fetchone()

    conn.commit()
    conn.close()

    if data:
        phone, name = data
        send_sms(phone, f"Hello {name}, your leave request has been {status}.")

    return redirect("/admin/dashboard")

# ---------- COMPLAINT ACTION ----------
@app.route("/complaint_action/<int:complaint_id>")
def complaint_action(complaint_id):
    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status='Resolved' WHERE id=?",
        (complaint_id,)
    )

    cursor.execute("""
        SELECT students.phone, students.name
        FROM complaints
        JOIN students ON complaints.register_no = students.register_no
        WHERE complaints.id=?
    """, (complaint_id,))

    data = cursor.fetchone()
    conn.commit()
    conn.close()

    if data:
        phone, name = data
        send_sms(phone, f"Hello {name}, your complaint has been resolved successfully.")

    return redirect("/admin/dashboard")
# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
