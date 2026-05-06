import datetime
import time
import requests
import random
from concurrent.futures import ThreadPoolExecutor
import math

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
    },
    "fanout-func": {
        "url": "http://fanout-func.default.127.0.0.1.sslip.io:8080/fanout",
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

def sinusoidal_workload(duration_minutes=10, min_rate=10, max_rate=100, cycles=2):
    print(f"Sinusoidal workload for {duration_minutes} minutes "
          f"({min_rate}-{max_rate} rq/s, {cycles} cycles)\n")

    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)
    total_seconds = duration_minutes * 60
    period_seconds = total_seconds / cycles  # one full sine wave per cycle
    invocation_count = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        while datetime.datetime.now() < end_time:
            elapsed = (datetime.datetime.now() - start_time).total_seconds()

            # sin goes -1 to 1; map to [min_rate, max_rate]
            rate = min_rate + (max_rate - min_rate) * (
                0.5 + 0.5 * math.sin(2 * math.pi * elapsed / period_seconds)
            )

            loop_start = time.time()
            function_name = random.choice(list(FUNCTIONS.keys()))
            executor.submit(invoke_function, function_name, FUNCTIONS[function_name])
            invocation_count += 1

            sleep_time = (1.0 / rate) - (time.time() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    print(f"Sinusoidal workload finished. Generated {invocation_count} invocations.\n")
    return invocation_count

def generate_workload(duration_minutes=10, delay_seconds=5):
    print(f"Workload generator started. Generating workload for {duration_minutes} minutes.")
    total_invocations = 0

    total_invocations += ramp_up(1, 10, duration_minutes=1)
    total_invocations += ramp_up(2, 100, duration_minutes=2)
    total_invocations += ramp_up(3, 50, duration_minutes=3)
    total_invocations += ramp_up(4, 25, duration_minutes=4)

    print(f"Workload generator finished. Generated {total_invocations} total invocations.")

# def generate_workload_sinusoidal(duration_minutes=10):
#     print(f"Workload generator started (sinusoidal). Duration: {duration_minutes} minutes.")
#     total = sinusoidal_workload(duration_minutes=duration_minutes, min_rate=10, max_rate=100, cycles=2)
#     print(f"Workload generator finished. Generated {total} total invocations.")

if __name__ == "__main__":
    generate_workload(duration_minutes=10)