import pandas as pd
import datetime
from prometheus_api_client import PrometheusConnect

prometheus = PrometheusConnect(url="http://localhost:9090", disable_ssl=True)

end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(minutes=14)
step_size = "15s"

def get_metrics(query, label):
    result = prometheus.custom_query_range(query=query, start_time=start_time, end_time=end_time, step=step_size)

    rows = []
    for series in result:
        node = series["metric"].get("node", series["metric"].get("instance", "unknown"))
        for timestamp, value in series["values"]:
            rows.append({"timestamp": timestamp, "node": node, label: float(value)})

    return pd.DataFrame(rows)

cpu_df = get_metrics(query='instance:node_cpu_utilisation:rate5m', label="cpu_usage")
memory_df = get_metrics(query='instance:node_memory_utilisation:ratio', label="memory_usage")

df = pd.merge(cpu_df, memory_df, on=["timestamp", "node"], how="outer")

# Make sure to check this with 'kubectl get nodes -o wide' to double-check they haven't changed
# every time you set up a new cluster.
node_map = {
    '172.18.0.4:9100': 'control-plane',
    '172.18.0.5:9100': 'worker-1',
    '172.18.0.2:9100': 'worker-2',
    '172.18.0.3:9100': 'worker-3'
}

df['node'] = df['node'].map(node_map)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df.sort_values(["node", "timestamp"], inplace=True)

print(df.head())
print(f"\nCollected {len(df)} rows across {df['node'].unique()} nodes.")

filename = f"metrics_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
df.to_csv(f"data/{filename}", index=False)
print(f"Metrics saved to data/{filename}")