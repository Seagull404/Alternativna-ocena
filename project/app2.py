from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

app.secret_key = "Basket!!24"

UPLOAD_FOLDER = "static2/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#DATABASE
def get_db():
    conn = sqlite3.connect("db/social.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        text TEXT,
        opis TEXT,
        image TEXT,
        likes INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user TEXT,
        text TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS likes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        post_id INTEGER,
        UNIQUE(user, post_id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

#Home page
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    
    conn = get_db()

    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    comments = conn.execute("SELECT * FROM comments").fetchall()

    conn.close()

    return render_template("index.html", posts=posts, comments=comments, user=session["user"])

#Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        try:
            conn.execute("INSERT INTO users(username, password) VALUES(?,?)",
                         (username, password))
            conn.commit()
        except:
            return "Uporabnik že obstaja"
        conn.close()

        return redirect("/login")

    return render_template("register.html")



if __name__ == "__main__":
    app.run(debug=True)