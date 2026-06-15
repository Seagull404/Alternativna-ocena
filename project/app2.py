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

UPLOAD_FOLDER = "project/static2/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#DATABASE
def get_db():
    conn = sqlite3.connect("project/db/platform.db")
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

# Like
@app.route("/like/<int:id>", methods=["POST"])
def like(id):
    if "user" not in session:
        return {"status": 403}
    conn = get_db()
    existing = conn.execute(
    "SELECT * FROM likes WHERE user=? AND post_id=?",
    (session["user"], id)
).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM likes WHERE user=? AND post_id=?",
            (session["user"], id)
        )
        conn.execute(
            "UPDATE posts SET likes = likes - 1 WHERE id=?",
            (id,)
        )
    else:
        conn.execute(
            "INSERT INTO likes(user, post_id) VALUES(?,?)",
            (session["user"], id)
        )
        conn.execute(
            "UPDATE posts SET likes = likes + 1 WHERE id=?",
            (id,)
        )
        conn.commit()
        return {"status": "already_liked"}
    return {"status": "liked"}

#Izbriši
@app.route("/delete_post/<int:id>", methods=["POST"])
def delete_post(id):
    if "user" not in session:
        return {"status": 403}
    conn = get_db()
    post = conn.execute("SELECT * FROM posts WHERE id=?", (id,)).fetchone()
    if not post:
        return {"status": 404}
    #sam lastnik lahko izbrise
    if post["user"] != session["user"] and not session.get("is_admin"):
        return {"status": 403}
    #izbrisi
    if post["image"]:
        path = os.path.join("static2/uploads", post["image"])
        if os.path.exists(path):
            os.remove(path)
    #izbrisi post
    conn.execute("DELETE FROM posts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

#Koment
@app.route("/add_comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    if "user" not in session:
        return {"status": 403}
    text = request.form["text"]
    with get_db() as conn:
        conn.execute(
            "INSERT INTO comments(post_id, user, text) VALUES(?,?,?)",
            (post_id, session["user"], text)
        )
        conn.commit()
    return redirect("/")

#Izbrisi koment
@app.route("/delete_comment/<int:id>", methods=["POST"])
def delete_comment(id):
    if "user" not in session:
        return {"status": 403}
    conn = get_db()
    comment = conn.execute("SELECT * FROM comments WHERE id=?", (id,)).fetchone()

    if not comment:
        conn.close()
        return {"status": 404}
    
    post = conn.execute("SELECT * FROM posts WHERE id=?", (comment["post_id"],)).fetchone()

    post_user = post["user"] if post else None
    is_admin = session.get("is_admin") == 1
    post_owner = post["user"] if post else None

    allowed = (comment["user"] == session["user"] or post_owner == session["user"] or is_admin)

    if not allowed:
        conn.close()
        return {"status": 403}
    
    conn.execute("DELETE FROM comments WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"status": "deleted"}

@app.route("/admin/delete_user/<username>", methods=["POST"])
def delete_user(username):
    if "user" not in session or not session.get("is_admin"):
        return {"status": 403}
    
    conn = get_db()
    #izbrise LIKE od uporabnika
    conn.execute("DELETE FROM likes WHERE user=?", (username,))
    #izbrise KOMENTAR od uporabnika
    conn.execute("DELETE FROM comments WHERE user=?", (username,))
    #poišče vse POSTE od uporabnika
    posts = conn.execute("SELECT id FROM posts WHERE user=?", (username,)).fetchone()

    post_ids = [p["id"] for p in posts]


    if post_ids:
        #izbrisi komente na teh določenih postih
        conn.executemany("DELETE FROM comments WHERE post_id=?", [(pid,) for pid in post_ids])
        #izbrisi like na teh določenih postih
        conn.executemany("DELETE FROM likes WHERE post_id=?", [(pid,) for pid in post_ids])
    
    #izbrise poste
    conn.execute("DELETE FROM posts WHERE user=?", (username,))
    #izbrise userja
    conn.execute("DELETE FROM users WHERE username=?", (username,))

    conn.commit()
    conn.close()

    return {"status": "deleted"}

if __name__ == "__main__":
    app.run(debug=True)