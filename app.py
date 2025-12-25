from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "openonlyforme"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            room_no TEXT,
            from_date TEXT,
            to_date TEXT,
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

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- CHATBOT ----------
@app.route("/get")
def chatbot():
    msg = request.args.get("msg", "").lower()

    if "hi" in msg:
        return "Hello! Welcome to our College Hostel 😊"
    elif "leave" in msg:
        return "Apply leave here 👉 <a href='/leave'>Leave Form</a>"
    elif "complaint" in msg:
        return "Register complaint 👉 <a href='/complaint'>Complaint Form</a>"
    else:
        return "Ask about leave, complaint, hostel rules, or warden."

# ---------- LEAVE ----------
@app.route("/leave")
def leave_form():
    return render_template("leave.html")

@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    name = request.form["name"]
    room_no = request.form["room_no"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]
    reason = request.form["reason"]

    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leave_applications
        (name, room_no, from_date, to_date, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (name, room_no, from_date, to_date, reason))

    conn.commit()
    conn.close()
    return "Leave submitted successfully! <a href='/'>Go back</a>"

# ---------- COMPLAINT ----------
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
    cursor.execute("""
        INSERT INTO complaints (name, room_no, complaint)
        VALUES (?, ?, ?)
    """, (name, room_no, complaint))

    conn.commit()
    conn.close()
    return "Complaint submitted! <a href='/'>Go back</a>"

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin_logged_in"] = True
            return redirect("/admin/dashboard")
        return render_template("admin_login.html", error="Invalid login")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = sqlite3.connect("hostel.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leave_applications")
    leaves = cursor.fetchall()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    conn.close()
    return render_template("admin_dashboard.html", leaves=leaves, complaints=complaints)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
