# ---------- IMPORTS ----------
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

# ---------- FLASK APP ----------
app = Flask(__name__)
app.secret_key = "openonlyforme"

# ---------- DATABASE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hostel.db")

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            name TEXT,
            room_no TEXT,
            reason TEXT,
            from_date TEXT,
            to_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            name TEXT,
            room_no TEXT,
            complaint TEXT
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
        return "Hello! Welcome to PKR Hostel 😊 How can I hel you?"

    elif "hostel rules" in msg or "rules" in msg:
        return "• Entry before 9 PM<br>• Maintain silence<br>• No outsiders allowed"

    elif "mess menu" in msg or "food" in msg or "menu" in msg:
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
    name = request.form["name"]
    room_no = request.form["room_no"]
    reason = request.form["reason"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
    name = request.form["name"]
    room_no = request.form["room_no"]
    complaint = request.form["complaint"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

    return render_template(
        "admin_dashboard.html",
        leaves=leaves,
        complaints=complaints
    )

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
