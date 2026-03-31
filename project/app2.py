from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)