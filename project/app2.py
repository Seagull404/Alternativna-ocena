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


#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["is_admin"] = user["is_admin"]
            return redirect("/")
        
        return "Napaka pri loginu."
    return render_template("login.html")

#Logout
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")

#Objavi
@app.route("/add_post", methods=["POST"])
def add_post():
    if "user" not in session:
        return redirect("/login")
    text = request.form["text"]
    opis = request.form["opis"]
    image = request.files["image"]
    filename = None
    if image:
        filename = image.filename
        image.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_db()
    conn.execute(
        "INSERT INTO posts(user, text, opis, image) VALUES(?,?,?,?)", (session["user"], text, opis, filename))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)