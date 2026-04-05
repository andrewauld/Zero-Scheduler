from flask import Flask, request, jsonify
from prometheus_api_client import PrometheusConnect
import os
import logging
import numpy as np
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)
app = Flask(__name__)

MODEL_PATH = os.environ.get("MODEL_PATH", "../models/gradient_boosting.pkl")
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus-service:9090")

model = joblib.load(MODEL_PATH)
prometheus = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

log.info(f"Model loaded from {MODEL_PATH}")
log.info(f"Prometheus URL: {PROMETHEUS_URL}")

FEATURES_COLS = [
    "cpu_usage", "memory_usage", "node_load", "pod_cpu_usage", "pod_memory_usage_mb", "pod_count",
    "cpu_throttling", "disk_in_kb", "disk_out_kb", "network_total_kb", "request_rate", "estimated_power"
]

P_IDLE = 0.2
P_MAX = 1.0

def query_scalar(promql):
    return float(prometheus.custom_query(promql)[0]["value"][1])

def get_node_features(node_name):
    queries = {
        "cpu_usage": f'instance:node_cpu_utilisation:rate5m{{node="{node_name}"}}',
        "memory_usage": f'instance:node_memory_utilisation:ratio{{node="{node_name}"}}',
        "node_load": f'instance:node_load1_per_cpu:ratio{{node="{node_name}"}}',
        "pod_cpu_usage": f'sum(rate(container_cpu_usage_seconds_total[1m])) by (node) * on(node) group_left() (kube_node_info{{node="{node_name}"}} > 0)',
        "pod_memory_usage_mb": f'sum(container_memory_working_set_bytes{{node="{node_name}"}}) / 1024 / 1024',
        "pod_count": f'count(kube_pod_info{{node="{node_name}"}})',
        "cpu_throttling": f'sum(rate(container_cpu_cfs_throttled_periods_total[1m]{{node="{node_name}"}}))',
        "disk_in_kb": f'sum(rate(container_fs_reads_bytes_total[1m]{{node="{node_name}"}})) / 1024',
        "disk_out_kb": f'sum(rate(container_fs_writes_bytes_total[1m]{{node="{node_name}"}})) / 1024',
        "network_total_kb": f'(sum(rate(container_network_receive_bytes_total[1m]{{node="{node_name}"}})) + sum(rate(container_network_transmit_bytes_total[1m]{{node="{node_name}"}}))) / 1024',
    }

    features = {}
    for key, query in queries.items():
        val = query_scalar(query)
        features[key] = val

    features["estimated_power"] = P_IDLE + (P_MAX - P_IDLE) * features["cpu_usage"]
    features["request_rate"] = 10

    return features

@app.route("/")
def main():
    return "ML Extender is operational."

@app.route("/filter", methods=["POST"])
def filter_nodes():
    data = request.get_json()
    nodes = data.get("Nodes", {})
    return jsonify({
        "Nodes": nodes,
        "FailedNodes": {},
        "Error": ""
    })

@app.route("/prioritise", methods=["POST"])
def prioritise():
    data = request.get_json()
    candidate_nodes = data.get("Nodes", {}).get("items", [])

    if not candidate_nodes:
        log.warning("No candidate nodes found in request")
        return jsonify([])

    node_names = [n["metadata"]["name"] for n in candidate_nodes]
    node_features = {}

    for name in node_names:
        features = get_node_features(name)
        node_features[name] = features
        log.info(f"Features for node {name}: {features}")

    if not node_features:
        log.error("No features extracted for any nodes - returning equal scores")
        return jsonify([
            {"Host": n, "Score": 5.0} for n in node_names
        ])

    feature_matrix = np.array([
        [node_features[n][col] for col in FEATURES_COLS] for n in node_names
    ])
    predicted_efficiency = model.predict(feature_matrix)

    min_efficiency = predicted_efficiency.min()
    max_efficiency = predicted_efficiency.max()

    scores = []
    for i, name in enumerate(node_features):
        if max_efficiency == min_efficiency:
            normalised = 5
        else:
            inverted = max_efficiency - predicted_efficiency[i]
            normalised=  int(round((inverted / (max_efficiency - min_efficiency)) * 10))
        scores.append({"Host": name, "Score": normalised})
        log.info(f" {name}: predicted efficiency: {predicted_efficiency[i]:.6f}, score: {normalised}")

    scored_names = {s["Host"] for s in scores}
    for name in node_names:
        if name not in scored_names:
            scores.append({"Host": name, "Score": 0.0})
            log.warning(f" {name}: no score available - setting to 0")

    log.info(f"Prioritisation complete: {scores}")
    return jsonify(scores)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)