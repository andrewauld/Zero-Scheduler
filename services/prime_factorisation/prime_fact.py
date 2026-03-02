from flask import Flask, render_template
import os
import random

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def main():
    return render_template("root.html")

@app.route("/prime_fact")
def prime_fact_route():
    iterations = random.randint(1000, 10000)
    results = []

    for i in range(iterations):
        n = random.randint(10**11, 10**12)
        factors = naive_fact(n)
        results.append(factors)

    return str(results)

def naive_fact(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8080)))