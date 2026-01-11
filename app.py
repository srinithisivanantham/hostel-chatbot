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

# ---------- SMS FUNCTION (SIMULATION) ----------
def send_sms(phone, message):
    print("📩 SMS SENT TO:", phone)
    print("MESSAGE:", message)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # STUDENT TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            reg_no TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT
        )
    """)

    # INSERT DUMMY STUDENTS (only once)
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students = [
            ("231cs048", "Srinithi", "9345518460"),
            ("231cs024", "Madhu sree", "6369231372"),
            ("231cs025", "Manisha", "9788618924")
        ]
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?)", students)

    # LEAVE TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT,
            name TEXT,
            room_no TEXT,
            reason TEXT,
            from_date TEXT,
            to_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # COMPLAINT TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT,
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

    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "Hello! Welcome to PKR Hostel 😊 How can I help you?"

    elif any(word in msg for word in ["rules", "hostel rules"]):
        return "• Entry before 9 PM<br>• Maintain silence<br>• No outsiders allowed"

    elif any(word in msg for word in ["menu", "food", "mess"]):
        return "Breakfast: Idli/Dosa<br>Lunch: Rice, Sambar<br>Dinner: Chapati"

    elif any(word in msg for word in ["leave", "permission"]):
        return "Apply for leave here: <a href='/leave'>Leave Form</a>"

    elif any(word in msg for word in ["complaint", "problem", "issue"]):
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
    reg_no = request.form["reg_no"]
    room_no = request.form["room_no"]
    reason = request.form["reason"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch student info
    cursor.execute("SELECT name FROM students WHERE reg_no=?", (reg_no,))
    student = cursor.fetchone()
    if not student:
        return "Invalid Register Number"

    name = student[0]

    cursor.execute("""
        INSERT INTO leave_applications
        (reg_no, name, room_no, reason, from_date, to_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (reg_no, name, room_no, reason, from_date, to_date))

    conn.commit()
    conn.close()

    return redirect("/")

# ---------- COMPLAINT ----------
@app.route("/complaint")
def complaint_form():
    return render_template("complaint.html")

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    reg_no = request.form["reg_no"]
    room_no = request.form["room_no"]
    complaint = request.form["complaint"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM students WHERE reg_no=?", (reg_no,))
    student = cursor.fetchone()
    if not student:
        return "Invalid Register Number"

    name = student[0]

    cursor.execute("""
        INSERT INTO complaints (reg_no, name, room_no, complaint)
        VALUES (?, ?, ?, ?)
    """, (reg_no, name, room_no, complaint))

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

# ---------- ACTION BUTTONS ----------
@app.route("/leave_action/<int:id>/<action>")
def leave_action(id, action):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT reg_no FROM leave_applications WHERE id=?", (id,))
    reg_no = cursor.fetchone()[0]

    cursor.execute("SELECT phone FROM students WHERE reg_no=?", (reg_no,))
    phone = cursor.fetchone()[0]

    cursor.execute("UPDATE leave_applications SET status=? WHERE id=?", (action, id))
    conn.commit()
    conn.close()

    send_sms(phone, f"Your leave request has been {action}")

    return redirect("/admin/dashboard")

@app.route("/complaint_action/<int:id>/<action>")
def complaint_action(id, action):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT reg_no FROM complaints WHERE id=?", (id,))
    reg_no = cursor.fetchone()[0]

    cursor.execute("SELECT phone FROM students WHERE reg_no=?", (reg_no,))
    phone = cursor.fetchone()[0]

    cursor.execute("UPDATE complaints SET status=? WHERE id=?", (action, id))
    conn.commit()
    conn.close()

    send_sms(phone, f"Your complaint has been {action}")

    return redirect("/admin/dashboard")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
