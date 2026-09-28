from flask import Flask, render_template, request, session, redirect
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="adminnova"
)

print("MySQL connected successfully!")

app = Flask(__name__)
app.secret_key = "adminnova-secret-key"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s",
            (username, password, role)
        )

        user = cursor.fetchone()
        cursor.close()

        if user:
            session["username"] = username
            session["role"] = role

            if role == "student":
                return render_template(
                    "student_dashboard.html",
                    username=username
                )

            if role == "staff":
                return render_template(
                    "staff_dashboard.html",
                    username=username
                )

        return "Invalid username, password, or role."

    role = request.args.get("role", "student")

    return render_template(
        "login.html",
        role=role
    )


@app.route("/submit-request", methods=["GET", "POST"])
def submit_request():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        request_type = request.form["request_type"]
        description = request.form["description"]

        student_username = session["username"]

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO requests
            (student_username, request_type, description)
            VALUES (%s, %s, %s)
            """,
            (student_username, request_type, description)
        )

        db.commit()
        cursor.close()

        return "Request submitted successfully!"

    return render_template("submit_request.html")


@app.route("/my-requests")
def my_requests():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM requests
        WHERE student_username = %s
        ORDER BY submitted_at DESC
        """,
        (username,)
    )

    requests_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "my_requests.html",
        requests=requests_data
    )
@app.route("/staff-requests")
def staff_requests():

    if "username" not in session or session.get("role") != "staff":
        return redirect("/login?role=staff")

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM requests
        WHERE status = 'Submitted'
        ORDER BY submitted_at DESC
        """
    )

    requests_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "staff_requests.html",
        requests=requests_data
    )
@app.route("/update-request/<int:request_id>", methods=["POST"])
def update_request(request_id):

    if "username" not in session or session.get("role") != "staff":
        return redirect("/login?role=staff")

    action = request.form["action"]

    if action == "approve":
        new_status = "Approved"

    elif action == "reject":
        new_status = "Rejected"

    else:
        return "Invalid action."

    cursor = db.cursor()

    cursor.execute(
        "UPDATE requests SET status = %s WHERE request_id = %s",
        (new_status, request_id)
    )

    db.commit()
    cursor.close()

    return redirect("/staff-requests")
if __name__ == "__main__":
    app.run(debug=True)