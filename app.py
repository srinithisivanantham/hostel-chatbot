from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"


# ---------------- DATABASE INIT ----------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reg_no TEXT UNIQUE,
            department TEXT,
            year TEXT
        )
    """)

    # Leave table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reg_no TEXT,
            reason TEXT,
            from_date TEXT,
            to_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Complaint table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reg_no TEXT,
            complaint TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- STUDENT FETCH API ----------------

@app.route("/get_student")
def get_student():
    reg_no = request.args.get("reg_no")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name, department, year FROM students WHERE reg_no=?", (reg_no,))
    student = cursor.fetchone()

    conn.close()

    if student:
        return jsonify({
            "name": student[0],
            "department": student[1],
            "year": student[2]
        })
    else:
        return jsonify({"error": "Student not found"})


# ---------------- CHATBOT ----------------

@app.route("/get")
def chatbot():
    user_msg = request.args.get("msg").lower()

    if "leave" in user_msg:
        return "Open leave form: <a href='/leave'>Click here</a>"

    elif "complaint" in user_msg:
        return "Open complaint form: <a href='/complaint'>Click here</a>"

    elif "admin" in user_msg:
        return "Admin panel: <a href='/admin'>Click here</a>"

    else:
        return "Hello! Type leave, complaint or admin."


# ---------------- LEAVE ----------------

@app.route("/leave")
def leave():
    return render_template("leave.html")


@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    name = request.form["name"]
    reg_no = request.form["reg_no"]
    reason = request.form["reason"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leaves (name, reg_no, reason, from_date, to_date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, reg_no, reason, from_date, to_date))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ---------------- COMPLAINT ----------------

@app.route("/complaint")
def complaint():
    return render_template("complaint.html")


@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    name = request.form["name"]
    reg_no = request.form["reg_no"]
    complaint = request.form["complaint"]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints (name, reg_no, complaint)
        VALUES (?, ?, ?)
    """, (name, reg_no, complaint))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leaves")
    leaves = cursor.fetchall()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html",
                           leaves=leaves,
                           complaints=complaints)


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
