from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "hostel.db"

def get_db():
    return sqlite3.connect(DB_NAME)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get")
def chatbot():
    msg = request.args.get("msg", "").lower()

    if "hi" in msg:
        return "Hello! How can I help you?"
    elif "leave" in msg:
        return "Click here to apply leave"
    elif "complaint" in msg:
        return "Click here to register complaint"
    elif "mess menu" in msg:
        return "Breakfast, Lunch, Dinner served daily"
    elif "hostel rules" in msg:
        return "Follow hostel rules and timings"
    else:
        return "Ask about leave, complaint, mess menu, or hostel rules"

@app.route("/leave")
def leave():
    return render_template("leave.html")

@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    name = request.form["name"]
    room = request.form["room"]
    reason = request.form["reason"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO leave_applications (name, room, reason, from_date, to_date) VALUES (?,?,?,?,?)",
        (name, room, reason, from_date, to_date),
    )
    con.commit()
    con.close()

    return redirect(url_for("index"))

@app.route("/complaint")
def complaint():
    return render_template("complaint.html")

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    name = request.form["name"]
    room = request.form["room"]
    complaint = request.form["complaint"]

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO complaints (name, room, complaint) VALUES (?,?,?)",
        (name, room, complaint),
    )
    con.commit()
    con.close()

    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT id, name, reason, from_date, to_date FROM leave_applications")
    leaves = cur.fetchall()

    cur.execute("SELECT id, name, complaint FROM complaints")
    complaints = cur.fetchall()

    con.close()
    return render_template("admin_dashboard.html", leaves=leaves, complaints=complaints)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
