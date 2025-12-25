from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "openonlyforme"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("hostel.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leave_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        room_no TEXT,
        from_date TEXT,
        to_date TEXT,
        reason TEXT
    )
    """)

    cur.execute("""
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

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- CHATBOT ----------
@app.route("/get")
def chatbot():
    msg = request.args.get("msg", "").lower()

    if "hi" in msg or "hello" in msg:
        return "Hello! Welcome to our College Hostel 😊"

    elif "rule" in msg:
        return "• Entry before 9 PM<br>• Maintain silence<br>• No outsiders allowed"

    elif "mess" in msg:
        return "Breakfast: Idli/Dosa<br>Lunch: Rice, Sambar<br>Dinner: Chapati"

    elif "leave" in msg:
        return "Apply for leave here 👉 <a href='/leave'>Leave Form</a>"

    elif "complaint" in msg:
        return "Register complaint here 👉 <a href='/complaint'>Complaint Form</a>"

    elif "warden" in msg or "contact" in msg:
        return "Warden Contact: +91-9876543210"

    else:
        return "You can ask about: hostel rules, mess menu, leave, complaint, warden contact"

# ---------- LEAVE ----------
@app.route("/leave")
def leave():
    return render_template("leave.html")

@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    data = (
        request.form["name"],
        request.form["room_no"],
        request.form["from_date"],
        request.form["to_date"],
        request.form["reason"]
    )

    conn = sqlite3.connect("hostel.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO leave_applications (name, room_no, from_date, to_date, reason) VALUES (?, ?, ?, ?, ?)",
        data
    )
    conn.commit()
    conn.close()

    return "Leave applied successfully ✅ <a href='/'>Go back</a>"

# ---------- COMPLAINT ----------
@app.route("/complaint")
def complaint():
    return render_template("complaint.html")

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    data = (
        request.form["name"],
        request.form["room_no"],
        request.form["complaint"]
    )

    conn = sqlite3.connect("hostel.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO complaints (name, room_no, complaint) VALUES (?, ?, ?)",
        data
    )
    conn.commit()
    conn.close()

    return "Complaint registered successfully ✅ <a href='/'>Go back</a>"

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = sqlite3.connect("hostel.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM leave_applications")
    leaves = cur.fetchall()
    cur.execute("SELECT * FROM complaints")
    complaints = cur.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", leaves=leaves, complaints=complaints)

@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin")
