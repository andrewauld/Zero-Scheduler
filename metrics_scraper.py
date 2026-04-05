import os
import pandas as pd
import datetime
import sys
from prometheus_api_client import PrometheusConnect

mode = sys.argv[1] if len(sys.argv) > 1 else "default"
output_dir = f"data/{mode}"
os.makedirs(output_dir, exist_ok=True)

prometheus = PrometheusConnect(url="http://localhost:9090", disable_ssl=True)

end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(minutes=14)
step_size = "15s"

def get_node_ip_mapping():
    result = prometheus.custom_query(query="kube_node_info")

    mapping = {}

    for series in result:
        node_name = series["metric"].get("node")
        internal_ip = series["metric"].get("internal_ip")

        if node_name and internal_ip:
            mapping[internal_ip] = node_name

    return mapping

ip_to_node_map = get_node_ip_mapping()

if not ip_to_node_map:
    print("WARNING: No node IP mapping found. Falling back to raw labels.")

def get_metrics(query, label):
    result = prometheus.custom_query_range(query=query, start_time=start_time, end_time=end_time, step=step_size)

    rows = []
    for series in result:
        raw_node = (
            series["metric"].get("node")
            or series["metric"].get("kubernetes_node")
            or series["metric"].get("instance")
            or "unknown"
        )

        if ":" in raw_node:
            ip = raw_node.split(":")[0]
            node = ip_to_node_map.get(ip, raw_node)
        else:
            node = raw_node

        for timestamp, value in series["values"]:
            rows.append({"timestamp": timestamp, "node": node, label: float(value)})

    metrics_df = pd.DataFrame(rows)
    if metrics_df.empty or "node" not in metrics_df.columns:
        print(f"WARNING: No valid data returned for label '{label}'. Returning empty DataFrame.")
        return pd.DataFrame(columns=["timestamp", "node", label])

    return metrics_df

# Node metrics
cpu_df = get_metrics(query='instance:node_cpu_utilisation:rate5m', label="cpu_usage")
memory_df = get_metrics(query='instance:node_memory_utilisation:ratio', label="memory_usage")
node_load_df = get_metrics(query='instance:node_load1_per_cpu:ratio', label="node_load")

# Pod metrics
pod_cpu_query = 'sum(rate(container_cpu_usage_seconds_total[1m])) by (node)'
pod_cpu_df = get_metrics(query=pod_cpu_query, label="pod_cpu_usage")
pod_memory_query = 'sum(container_memory_working_set_bytes) by (node)'
pod_memory_df = get_metrics(query=pod_memory_query, label="pod_memory_usage")
network_in_query = 'sum(rate(container_network_receive_bytes_total[1m])) by (node)'
network_in_df = get_metrics(query=network_in_query, label="network_in")
network_out_query = 'sum(rate(container_network_transmit_bytes_total[1m])) by (node)'
network_out_df = get_metrics(query=network_out_query, label="network_out")
cpu_throttling_query = 'sum(rate(container_cpu_cfs_throttled_periods_total[1m])) by (node)'
cpu_throttling_df = get_metrics(query=cpu_throttling_query, label="cpu_throttling")
disk_in_query = 'sum(rate(container_fs_reads_bytes_total[1m])) by (node)'
disk_in_df = get_metrics(query=disk_in_query, label="disk_in")
disk_out_query = 'sum(rate(container_fs_writes_bytes_total[1m])) by (node)'
disk_out_df = get_metrics(query=disk_out_query, label="disk_out")

# Cluster metrics
pod_count_query = 'count(kube_pod_info * on(pod, namespace) group_left() (kube_pod_status_phase{phase="Running"} == 1)) by (node)'
pod_count_df = get_metrics(query=pod_count_query, label="pod_count")

df = cpu_df.copy()
for i in [memory_df,
          node_load_df,
          pod_cpu_df,
          pod_memory_df,
          network_in_df,
          network_out_df,
          cpu_throttling_df,
          disk_in_df,
          disk_out_df,
          pod_count_df]:
    df = pd.merge(df, i, on=["timestamp", "node"], how="outer")

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df.sort_values(["node", "timestamp"], inplace=True)
df = df.groupby(["node", "timestamp"], as_index=False).mean()

metrics_columns = [c for c in df.columns if c not in ["node", "timestamp"]]
df[metrics_columns] = df.groupby("node")[metrics_columns].ffill().bfill()

print(df.head())
print(f"\nCollected {len(df)} rows across {df['node'].unique()} nodes.")

filename = f"metrics_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
df.to_csv(f"{output_dir}/{filename}", index=False)
print(f"Metrics saved to {output_dir}/{filename}")