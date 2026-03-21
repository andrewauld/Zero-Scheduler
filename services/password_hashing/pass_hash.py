from flask import Flask
import os
import hashlib
import random
import string

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def main():
    return "Root is working. Check out /hash for the password hashing service."

@app.route("/hash")
def hash():
    iterations = random.randint(1, 5)
    results = []
    password = random_string(random.randint(10, 20))
    for i in range(iterations):
        salt = os.urandom(16)
        key = hashlib.scrypt(password.encode(), salt=salt, n=1024, r=8, p=1)
        results.append(salt.hex() + ":" + key.hex())

    return f"Computed {iterations} hashes."

def random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))