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

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        
        if users.search(User.username == username):
            return "Uporabniško ime že obstaja."
        
        users.insert({
            "username": username,
            "password": password,
        })
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/forgot", methods = ["GET", "POST"])
def forgot():
    if request.method == "POST":
        username = request.form["username"]
        user = users.get(User.username == username)

        if "answer" in request.form:
            answer = request.form["answer"].lower()
            new_password = generate_password_hash(request.form["password"])

            if user and user["answer"] == answer:
                users.update({"password": new_password}, User.username == username)
                return redirect("/login")
            return "Napačen odgovor."
        
        if user:
            return render_template("forgot.html", question=user["question"], user=username)

        return "Uporabnik ne obstaja."
    
    return render_template("forgot.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    userNotes = notes.search(Notes.username == session["user"])
    return render_template("dashboard.html", user = session["user"], notes = userNotes)


@app.route("/saveNote", methods=["POST"])
def saveNote():
    if request.method == "POST":
        data = request.form
        print(data)

        notes.insert({'username': session["user"], 'title': data["title"], 'content': data["content"]})

        return {"status": 200}
    
@app.route("/deleteNote/<int:id>", methods=["POST"])
def deleteNote(id):
    if "user" not in session:
        return {"status": 400}
    
    notes.remove(doc_ids=[id])
    return {"status": 200}

@app.route("/editNote/<int:id>", methods=["POST"])
def editNote(id):
    if "user" not in session:
        return {"status": 403}
    
    title = request.form["title"]
    content = request.form["content"]

    notes.update(
        {"title": title, "content": content},
        doc_ids=[id]
    )

    return {"status": 200}

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()

    return {"status": 200}


app.run(debug=True)