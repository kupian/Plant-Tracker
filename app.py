from flask import Flask, render_template, request, session, redirect, jsonify, json
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, connect
import os

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Return homepage along with whether user is logged in or not
@app.route("/")
def main(): 
    username = None  
    if "username" in session:
        username = session["username"]  
    return render_template("index.html", username = username)


# When recieving post request to login check database against password hash to see if password correct. If correct, log in user
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with connect("plantapp.db") as con:
            db = con.cursor()
            query = db.execute("SELECT password FROM users WHERE username = ?", [username])
            con.commit()
            passhash = None
            for row in query:
                passhash = row[0]
            if check_password_hash(passhash, password):
                session["username"] = username
    return redirect("/")

# If recieve post request to register, check username and passwords for validity then check username against existing users. If unique, add user to database and redirect to login
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if len(username) < 1:
            return {"response" :"Username not valid"}
            # return username not valid
        if password != confirmation:
            #todo return passwords dont match
            return redirect("/register")
        with connect("plantapp.db") as con:
            db = con.cursor()
            passhash = generate_password_hash(password)
            query = db.execute("SELECT username FROM users WHERE username = ?", [username])
            for row in query:
                if row[0] == username:
                    return redirect("/register")
                    # todo return username exists
            query = db.execute("SELECT email FROM users WHERE email = ?", [email])
            for row in query:
                if row[0] == email:
                    return redirect("/register")
                    #todo return email exists
            query = db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", [username, email, passhash])
            con.commit()
            return json.dumps({'status': 'OK'})
            return redirect("/login")
    else:
        session.clear()
        return render_template("register.html")
