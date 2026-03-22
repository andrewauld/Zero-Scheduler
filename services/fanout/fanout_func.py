from flask import Flask
import os
import requests
import random
import time

app = Flask(__name__)

SERVICES = [
    "http://matrix-mult.default.127.0.0.1.sslip.io:8080/matrix_mult",
    "http://pass-hash.default.127.0.0.1.sslip.io:8080/hash",
    "http://prime-fact.default.127.0.0.1.sslip.io:8080/prime_fact"
]

@app.route("/")
def main():
    return "Root is working. Check out /fanout for the fanout service."

@app.route("/fanout")
def fanout():
    num_requests = random.randint(3, 8)
    targets = random.choices(SERVICES, k=num_requests)
    results = []

    for i in targets:
        start_time = time.time()
        response = requests.get(i)
        latency = time.time() - start_time
        results.append({
            "url": i,
            "status": response.status_code,
            "latency": round(latency, 3)
        })

    return f"Fanout complete: {len(results)} requests made."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))