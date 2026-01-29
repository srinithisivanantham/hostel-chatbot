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

# ---------- FAST2SMS CONFIG ----------
FAST2SMS_API_KEY = "bQq8c6ZJs4hCi7DX92MfYj3BA1kTvpHmuOtdLGURzKxIgawoFlfrZwB0muX2kVlnDQSFpde5P6tL7oI3"

def send_sms(phone, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    params = {
        "authorization": FAST2SMS_API_KEY,
        "route": "q",
        "message": message,
        "numbers": phone,
        "flash": 0
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print("SMS Response:", response.text)
        return response.json()
    except Exception as e:
        print("SMS Error:", e)
        return {"error": str(e)}

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
            ("231cs024", "Madhu", "6369231372", "14"),
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
        return """
    <b>📜 Hostel Rules:</b><br>
    1️⃣ The hostel management is not responsible for missing jewellery or valuables.<br>
    2️⃣ Students must be properly dressed until 10:00 PM.<br>
    3️⃣ Students must go for dinner sharply at 8:00 PM.<br>
    4️⃣ Snacks time is at 5:00 PM in the evening.<br>
    5️⃣ Study time is from 6:00 PM to 8:00 PM.<br>
    6️⃣ Mobile phones must be submitted at 10:00 PM and collected the next morning at 6:00 AM.<br>
    7️⃣ Students must go to class sharply at 9:00 AM.
    """
    elif "menu" in msg or "mess" in msg:
        return """🍽️ <b>PKR Hostel Weekly Mess Menu</b><br><br>

<b>Sunday</b><br>
Morning: Poori / Bread<br>
Lunch: Non-Veg – Chicken Biriyani | Veg – Sambar<br>
Dinner: Sadham, Parupu Sambar, Rasam<br><br>

<b>Monday</b><br>
Morning: Idly<br>
Lunch: Cabbage Poriyal, Rice, Vendaikai Sambar, Rasam, Curd<br>
Dinner: Parupu Sadham, Idly Upma<br><br>

<b>Tuesday</b><br>
Morning: Patani Sadham, Potato Fry<br>
Lunch: Parupu Sambar, Rice, Rasam, Curd<br>
Dinner: Chapati<br><br>

<b>Wednesday</b><br>
Morning: Idly<br>
Lunch: Egg Gravy, Rice, Rasam, Curd, Sorakai Poriyal<br>
Dinner: Thakkali Sadham<br><br>

<b>Thursday</b><br>
Morning: Sambar Sadham, Appalam<br>
Lunch: Beetroot Poriyal, Sundal Kulambu, Rice, Rasam, Curd<br>
Dinner: Dosa<br><br>

<b>Friday</b><br>
Morning: Coconut Rice / Lemon Rice<br>
Lunch: Pachai Payaru Kulambu, Rice, Rasam, Curd<br>
Dinner: Idly<br><br>

<b>Saturday</b><br>
Morning: Thattai Payaru, Idly Upma<br>
Lunch: Vazhakai Poriyal, Rice, Rasam, Curd, Parupu Sambar<br>
Dinner: Dosa
"""
    elif "leave" in msg:
        return "Apply for leave here: <a href='/leave'>Leave Form</a>"
    elif "complaint" in msg:
        return "Register complaint here: <a href='/complaint'>Complaint Form</a>"
    elif "warden" in msg:
        return "Warden Contact: +91-9876543210"
    else:
        return "Please ask about hostel rules, mess menu, leave, complaint or warden."

# ---------- FETCH STUDENT API ----------
@app.route("/get_student/<register_no>")
def get_student(register_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, phone, room_no FROM students WHERE register_no=?",
        (register_no,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "name": row[0],
            "phone": row[1],
            "room": row[2]
        }
    else:
        return {"error": "Student not found"}

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

# ---------- LEAVE ACTION ----------
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

    cursor.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (complaint_id,))

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
    app.run(debug=True)
