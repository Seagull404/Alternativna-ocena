from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates1",
    static_folder="static1"
)

User = Query()

@app.route("/index1", methods = ["GET", "POST"])
def index1():
    return render_template("index1.html")


@app.route("/edit1", methods = ["GET", "POST"])
def index1():
    return render_template("edit1.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)