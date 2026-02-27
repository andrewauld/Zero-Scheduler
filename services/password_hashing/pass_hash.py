from flask import Flask, render_template, request
import os
import hashlib

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def main():
    return "At least the root is working..."

@app.route("/hash", methods=["GET", "POST"])
def hash():
    if request.method == "POST":
        password = request.form['password']
        salt = os.urandom(16)
        key = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        return str(salt + key)
    return render_template('password_form.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8080)))