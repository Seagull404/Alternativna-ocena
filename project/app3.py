from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates3",
    static_folder="static3"
)


@app.route("/")
def index():

    return render_template("index1.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)