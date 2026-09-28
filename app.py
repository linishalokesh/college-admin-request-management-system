from flask import Flask, render_template, request
import mysql.connector
import os
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="adminnova"
)

print("MySQL connected successfully!")
app = Flask(__name__)

users = {
    "1BM23CS001": {
        "password": "student123",
        "role": "student"
    },
    "STAFF001": {
        "password": "staff123",
        "role": "staff"
    }
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if username in users:
            user = users[username]

            if user["password"] == password and user["role"] == role:
                if role == "student":
                    return render_template("student_dashboard.html", username=username)

                if role == "staff":
                    return render_template("staff_dashboard.html", username=username)

        return "Invalid username, password, or role."

    role = request.args.get("role", "student")

    return render_template("login.html", role=role)


@app.route("/submit-request", methods=["GET", "POST"])
def submit_request():
    if request.method == "POST":
        request_type = request.form["request_type"]
        description = request.form["description"]

        return f"Request submitted successfully! Type: {request_type}"

    return render_template("submit_request.html")


if __name__ == "__main__":
    app.run(debug=True)