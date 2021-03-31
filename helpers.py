from functools import wraps
from flask import redirect, session, url_for
import sqlite3
from sqlite3 import Error

def connect(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connected to SQL")
    except Error as e:
        print(f"Error: {e}")

    return connection

# Decorator function taken from flask documentation
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function