import datetime
import time
import requests
import random

FUNCTIONS = {
    "matrix-mult": {
        "url": "http://matrix-mult.default.127.0.0.1.sslip.io:8080/matrix_mult",
        "method": "GET"
    },
    "pass-hash": {
        "url": "http://pass-hash.default.127.0.0.1.sslip.io:8080/hash",
        "method": "GET"
    },
    "prime-fact": {
        "url": "http://prime-fact.default.127.0.0.1.sslip.io:8080/prime_fact",
        "method": "GET"
    }
}

def invoke_function(function_name, function_config):

    response = requests.get(function_config["url"])
    print(f"Invoked {function_name}: {response.status_code} - {response.text[:50]}")
    return True

def generate_workload(duration_minutes=10, delay_seconds=5):
    print(f"Workload generator started. Generating workload for {duration_minutes} minutes.")

    end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
    invocation_count = 0

    while datetime.datetime.now() < end_time:
        function_name = random.choice(list(FUNCTIONS.keys()))
        function_config = FUNCTIONS[function_name]
        if invoke_function(function_name, function_config):
            invocation_count += 1

        time.sleep(delay_seconds)

    print(f"Workload generator finished. Generated {invocation_count} invocations.")

if __name__ == "__main__":
    generate_workload(duration_minutes=10, delay_seconds=5)