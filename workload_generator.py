import datetime
import time
import requests
import random
from concurrent.futures import ThreadPoolExecutor

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
    print(f"Invoked {function_name}: {response.status_code} - {response.text[:100]}")
    return True

def ramp_up(phase, calls_per_second, duration_minutes):
    print(f"Ramping up phase {phase} for {duration_minutes} minutes at {calls_per_second} calls per second.\n")

    phase_start_time = datetime.datetime.now()
    phase_end_time = phase_start_time + datetime.timedelta(minutes=duration_minutes)
    period = 1.0 / calls_per_second
    invocation_count = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        while datetime.datetime.now() < phase_end_time:
            loop_start_time = time.time()
            function_name = random.choice(list(FUNCTIONS.keys()))
            function_config = FUNCTIONS[function_name]
            executor.submit(invoke_function, function_name, function_config)
            invocation_count += 1

            elapsed_time = time.time() - loop_start_time
            sleep_time = period - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    print(f"\nPhase {phase} finished. Generated {invocation_count} invocations.\n")
    return invocation_count

def generate_workload(duration_minutes=10, delay_seconds=5):
    print(f"Workload generator started. Generating workload for {duration_minutes} minutes.")
    total_invocations = 0

    total_invocations += ramp_up(1, 10, duration_minutes=2)
    total_invocations += ramp_up(2, 30, duration_minutes=3)
    total_invocations += ramp_up(3, 50, duration_minutes=3)
    total_invocations += ramp_up(4, 100, duration_minutes=2)

    print(f"Workload generator finished. Generated {total_invocations} total invocations.")

if __name__ == "__main__":
    generate_workload(duration_minutes=10, delay_seconds=5)