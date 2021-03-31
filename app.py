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
        username = request.form.get("l_username")
        password = request.form.get("l_password")
        if len(username) < 1:
            return redirect("/")
        if len(password) < 1:
            return redirect("/")
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
        email = request.form.get("r_email")
        username = request.form.get("r_username")
        password = request.form.get("r_password")
        confirmation = request.form.get("r_confirmation")
        if len(username) < 1:
            return {"response" : "Username not valid"}
            # return username not valid
        if password != confirmation:
            #todo return passwords dont match
            return {"response" : "Passwords do not match"}
        with connect("plantapp.db") as con:
            db = con.cursor()
            passhash = generate_password_hash(password)
            query = db.execute("SELECT username FROM users WHERE username = ?", [username])
            for row in query:
                if row[0] == username:
                    # todo return username exists
                    return {"response" : "Username already registered"}
            query = db.execute("SELECT email FROM users WHERE email = ?", [email])
            for row in query:
                if row[0] == email:
                    #todo return email exists
                    return {"response" : "Email already registered"}
            query = db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", [username, email, passhash])
            con.commit()   
        return {"response": "OK"}           
    else:
        session.clear()
        return render_template("register.html")

# Clear session dict on logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/plants", methods=["GET", "POST"])
@login_required
def plants():
    if request.method == "GET":
        plants = []
        with connect("plantapp.db") as con: # Select plants that user is growing
            db = con.cursor()
            query = db.execute("SELECT name FROM plants WHERE plantid IN (SELECT plantid FROM plantgrowth WHERE username=?)", [session["username"]])
            for row in query:
                plants.append(row[0])
            con.commit()
        return render_template("plants.html", plants=plants, username=session["username"])
    else:
        plant = request.form.get("planttype") # Get plant name from form
        if len(plant) < 1: # Check name is valid
            return redirect("/plants")
        with connect("plantapp.db") as con:
            db = con.cursor()
            query = db.execute("SELECT plantid FROM plants WHERE name = ?", [plant]) 
            if query.fetchall() == []: # Check to see if plant name already exists in DB
                db.execute("INSERT INTO plants (name) VALUES (?)", [plant]) # If no, insert plant into DB
                con.commit()
            db.execute("INSERT INTO plantgrowth (plantid, username) VALUES ((SELECT plantid FROM plants WHERE name = ?), ?)", [plant, session["username"]]) # Insert row for plant associated with user
            con.commit()
        return redirect("/plants")

@app.route("/searchplants", methods=["POST"])
@login_required
def plantsearch():
    plants = []
    plantsearch = request.json["planttype"] # Get JSON data for plant name
    with connect("plantapp.db") as con:
        db = con.cursor()
        query = db.execute("SELECT name FROM plants WHERE name LIKE ?", ['%'+plantsearch+'%']) # Select plants containing matching string
        for row in query: # Add plants to array
            plants.append({"name": row[0]})
        con.commit()
    return {"response": plants}