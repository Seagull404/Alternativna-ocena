from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(
    __name__,
    template_folder="templates1",
    static_folder="static1"
)

app.secret_key = "Basket!!24"

db = TinyDB("db.json")
users = db.table("users")
notes = db.table("notes")

User = Query()
Notes = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)

        if user:
            #če ni v hasha
            if user["password"] == password:
                #s tem pretvorim v hash
                new_hash = generate_password_hash(password)
                users.update({"password": new_hash}, User.username == username)

                session["user"] = username
                return redirect("dashboard")
            
            #če hash je
            elif check_password_hash(user["password"], password):
                session["user"] = username
                return redirect("/dashboard")
        return "Napačno geslo ali uporabniško ime"

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)