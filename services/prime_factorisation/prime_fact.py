from flask import Flask
import os
import random

app = Flask(__name__)
@app.route("/")
def main():
    return "At least the root is working..."

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