from flask import Flask, render_template, request
import os
import hashlib
import random

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def main():
    return "Root is working. Check out /hash for the password hashing service."

@app.route("/hash", methods=["POST"])
def hash():
    # Retrieve password from form and hash using 'scrypt'
    iterations = random.randint(1000, 5000)
    results = []
    password = request.form.get('password', 'default')
    for i in range(iterations):
        salt = os.urandom(16)
        key = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        results.append(salt.hex() + ":" + key.hex())

    return f"Computed {iterations} hashes."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))