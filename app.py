from flask import Flask, render_template, request, session
app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def main():
    loggedIn = 0
    username = "User"
    return render_template("index.html", loggedIn = loggedIn, username = username)
