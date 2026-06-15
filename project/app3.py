from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query
import random

app = Flask(
    __name__,
    template_folder="templates3",
    static_folder="static3"
)

app.secret_key = "Basket!!24"

db = TinyDB("project/db/rand.json")
users = db.table("users")
doc = db.table("doc")

User = Query()
Doc = Query()

def gen_password(dolzina, words, num, sign):
    prostor=""

    if words:
        prostor+="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num:
        prostor+="0123456789"
    if sign:
        prostor+="!@#$%&?"
    if prostor == "":
        prostor = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&?"

    password = ""

    for _ in range(dolzina):
        password += random.choice(prostor)
    return password

def preveri(password):
    if len(password) <= 4:
        return "Weak"
    if len(password) <= 6:
        return "Medium"
    else:
        return "Strong"
    

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        if users.search(User.username == username):
            return "Uporabnik že obstaja"
        users.insert({
            "username" : username,
            "password" : password,
            "note" : ""
            })
        return redirect("/login")      
    return render_template("register.html")

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
    
        user = users.get(User.username == username)
        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard")
        return "Napačno geslo ali uporabniško ime"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    password = None
    strength = None
    user_docs = doc.search(Doc.owner == session["user"])

    if request.method == "POST":
        try:
            dolzina = int(request.form["dolzina"])
        except:
            dolzina = 4
        

        words= request.form.get("option1")
        num= request.form.get("option2")
        sign= request.form.get("option3")

        password= gen_password(dolzina, words, num, sign)
        strength= preveri(password)

    return render_template(
        "dashboard.html", user=session["user"], password=password, strength=strength, doc= user_docs)

@app.route("/shrani", methods=["POST"])
def shrani():
    if "user" not in session:
        return redirect("/login")
    
    name=request.form["name"]
    password=request.form["password"]

    doc.insert({
        "owner":session["user"],
        "name":name,
        "password": password
    })

    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)