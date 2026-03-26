import pandas as pd
import datetime
from prometheus_api_client import PrometheusConnect

prometheus = PrometheusConnect(url="http://localhost:9090", disable_ssl=True)

def get_node_metrics(query, label):
    result = prometheus.custom_query_range(query=query, start_time=start_time, end_time=end_time, step=step_size)

    rows = []
    for series in result:
        instance = series["metric"].get("instance", "unknown")
        for timestamp, value in series["values"]:
            rows.append({"timestamp": timestamp, "node": instance, label: float(value)})

    return pd.DataFrame(rows)

def get_knative_metrics(query, label):
    result = prometheus.custom_query_range(query=query, start_time=start_time, end_time=end_time, step=step_size)

    rows = []
    for series in result:
        revision = series["metric"].get("kn_revision_name", series["metric"].get("revision_name", "unknown"))
        service = series["metric"].get("kn_service_name", series["metric"].get("kn_configuration_name", "unknown"))
        namespace = series["metric"].get("k8s_namespace_name", "default")
        for timestamp, value in series["values"]:
            rows.append({"timestamp": timestamp, "revision": revision, "service": service, "namespace": namespace, label: float(value)})

    return pd.DataFrame(rows)

def get_pod_node_mapping():
    result = prometheus.custom_query('kube_pod_info{namespace="default"}')
    mapping = {}
    for series in result:
        pod = series["metric"].get("pod", "")
        node = series["metric"].get("node", "")
        if pod and node:
            mapping[pod] = node
    return mapping

def get_node_name_mapping():
    result = prometheus.custom_query('node_uname_info')
    return {res['metric']['instance']: res['metric']['node'] for res in result}

end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(minutes=14)
step_size = "15s"

cpu_df = get_node_metrics(query='instance:node_cpu_utilisation:rate5m', label="cpu_usage")
cpu_saturation_df = get_node_metrics(query='instance:node_cpu_saturation_cpu_wait:rate5m', label="cpu_saturation")
memory_df = get_node_metrics(query='instance:node_memory_utilisation:ratio', label="memory_usage")
available_memory_df = get_node_metrics(query='instance:node_memory_MemAvailable_bytes', label="available_memory")

network_query = 'sum by (instance) (rate(node_network_receive_bytes_total[5m]) + rate(node_network_transmit_bytes_total[5m]))'
network_df = get_node_metrics(network_query, label="network_io")

disk_df = get_node_metrics(query='instance:node_disk_io_time_seconds_total:rate5m', label="disk_io_time_seconds_total")

latency_query = 'histogram_quantile(0.99, sum by (le, revision_name) (rate(knative_serving_revision_request_latencies_bucket[5m])))'
latency_df = get_knative_metrics(query=latency_query, label="latency_99th_percentile")

rps_query = 'sum by (revision_name) (rate(knative_serving_revision_request_count[5m]))'
rps_df = get_knative_metrics(query=rps_query, label="request_rate")

concurrency_df = get_knative_metrics(query='kn_revision_request_concurrency', label="request_concurrency")
pods_count_df = get_knative_metrics(query='kn_revision_pods_count', label="pods_count")
pods_desired_df = get_knative_metrics(query='kn_revision_pods_desired', label="pods_desired")
concurrency_target_df = get_knative_metrics(query='kn_revision_concurrency_target', label="concurrency_target")
concurrency_stable_df = get_knative_metrics(query='kn_revision_concurrency_stable', label="concurrency_stable")

node_df = cpu_df.copy()
for df in [cpu_saturation_df,
           memory_df,
           available_memory_df,
           network_df,
           disk_df,
           latency_df,
           rps_df,
           concurrency_df,
           pods_count_df,
           pods_desired_df,
           concurrency_target_df,
           concurrency_stable_df]:
    node_df = pd.merge(node_df, df, on=["timestamp", "node"], how="outer")

knative_df = concurrency_df.copy()
for df in [pods_count_df,pods_desired_df,concurrency_target_df,concurrency_stable_df]:
    knative_df = pd.merge(knative_df, df, on=["timestamp", "revision", "service"], how="outer")

node_map = get_node_name_mapping()

node_df['node_raw'] = node_df['node']
ip_mask = node_df['node'].str.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', na=False)
node_df.loc[ip_mask, 'node'] = node_df.loc[ip_mask, 'node'].map(node_map)

node_df["timestamp"] = pd.to_datetime(node_df["timestamp"], unit="s")
knative_df["timestamp"] = pd.to_datetime(knative_df["timestamp"], unit="s")

node_df.sort_values(["node", "timestamp"], inplace=True)
knative_df.sort_values(["revision", "timestamp"], inplace=True)

pod_node_map = get_pod_node_mapping()

print(node_df.head())
print(f"\nCollected {len(node_df)} rows across {node_df['node'].unique()} nodes.")

node_filename = f"node_metrics_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
knative_filename = f"knative_metrics_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

node_df.to_csv(f"data/{node_filename}", index=False)
knative_df.to_csv(f"data/{knative_filename}", index=False)

print(f"Node metrics saved to data/{node_filename}")
print(f"Knative metrics saved to data/{knative_filename}")