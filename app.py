app.secret_key = 'openonlyforme'
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            room_no TEXT,
            reason TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            room_no TEXT,
            complaint TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME PAGE ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- CHATBOT ----------
@app.route("/get")
def chatbot():
    msg = request.args.get("msg").lower()

    if "hi" in msg:
        return "Hello! Welcome to our College Hostel 😊"

    elif "hostel rules" in msg:
        return "• Entry before 9 PM<br>• Maintain silence<br>• No outsiders allowed"

    elif "mess menu" in msg:
        return "Breakfast: Idli/Dosa<br>Lunch: Rice, Sambar<br>Dinner: Chapati"

    elif "leave" in msg:
        return "Apply for leave here: <a href='/leave'>Leave Form</a>"

    elif "complaint" in msg:
        return "Register complaint here: <a href='/complaint'>Complaint Form</a>"

    elif "warden" in msg:
        return "Warden Contact: +91-9876543210"

    else:
        return "Sorry, please ask about hostel rules, mess menu, leave, complaint or warden."

# ---------- LEAVE FORM ----------
@app.route("/leave")
def leave_form():
    return render_template("leave.html")

@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    name = request.form["name"]
    room_no = request.form["room_no"]
    reason = request.form["reason"]

    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leave_applications (name, room_no, reason) VALUES (?, ?, ?)",
        (name, room_no, reason)
    )
    conn.commit()
    conn.close()

    return "Leave application submitted successfully! <a href='/'>Go back</a>"

# ---------- COMPLAINT FORM ----------
@app.route("/complaint")
def complaint_form():
    return render_template("complaint.html")

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    name = request.form["name"]
    room_no = request.form["room_no"]
    complaint = request.form["complaint"]

    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (name, room_no, complaint) VALUES (?, ?, ?)",
        (name, room_no, complaint)
    )
    conn.commit()
    conn.close()

    return "Complaint submitted successfully! <a href='/'>Go back</a>"

# ---------- ADMIN VIEW ----------
@app.route("/admin/leaves")
def view_leaves():
    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_applications")
    data = cursor.fetchall()
    conn.close()
    return render_template("view_leaves.html", leaves=data)

@app.route("/admin/complaints")
def view_complaints():
    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    data = cursor.fetchall()
    conn.close()
    return render_template("view_complaints.html", complaints=data)
# ---------------- Admin Routes ----------------
from flask import session

# Simple admin login (username: admin, password: admin123)
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    conn = sqlite3.connect('hostel_chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_applications")
    leaves = cursor.fetchall()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', leaves=leaves, complaints=complaints)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
