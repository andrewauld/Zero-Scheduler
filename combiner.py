import glob
import pandas as pd
import numpy as np

files = glob.glob("data/metrics_*.csv")
df = pd.concat(map(pd.read_csv, files), ignore_index=True)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df.sort_values(["node", "timestamp"], inplace=True)
df.reset_index(drop=True, inplace=True)

print(f"Combined dataset: {len(df)} rows across {df['node'].unique()} nodes.")
print(f"Files combined: {len(files)}")

# Carry out feature engineering here (cpu/request, memory/request, power consumption, target label, etc.)
df["pod_memory_usage_mb"] = df["pod_memory_usage"] / 1024 / 1024
df["network_in_kb"] = df["network_in"] / 1024
df["network_out_kb"] = df["network_out"] / 1024
df["disk_in_kb"] = df["disk_in"] / 1024
df["disk_out_kb"] = df["disk_out"] / 1024

df.drop(columns=["pod_memory_usage", "network_in", "network_out", "disk_in", "disk_out"], inplace=True)

df = df.sort_values("timestamp").reset_index(drop=True)
time_jumps = df["timestamp"].diff().dt.total_seconds().fillna(0)
df["test_run"] = (time_jumps > 120).cumsum()

def assign_request_rate(group):
    run_id = group.name

    run_start = group["timestamp"].min()
    elapsed_time = (group["timestamp"] - run_start).dt.total_seconds() / 60

    conditions = [
        elapsed_time < 2,
        (elapsed_time >= 2) & (elapsed_time < 5),
        (elapsed_time >= 5) & (elapsed_time < 8),
        elapsed_time >= 8
    ]

    rates = [10, 30, 50, 100]
    group["request_rate"] = np.select(conditions, rates, default=10)
    group["test_run"] = [run_id] * len(group)
    return group

df = df.groupby("test_run", group_keys=False).apply(assign_request_rate)

P_IDLE = 0.2
P_MAX = 1.0
df["estimated_power"] = P_IDLE + (P_MAX - P_IDLE) * df["cpu_usage"]
df["pod_count_safe"] = df["pod_count"].replace(0, np.nan)

MAX_PODS = df["pod_count"].max()
df["pod_capacity_used"] = df["pod_count"] / MAX_PODS

df["power_efficiency"] = df["estimated_power"] * (0.5 + 0.5 * df["pod_capacity_used"])
df["network_total_kb"] = df["network_in_kb"] + df["network_out_kb"]

df.drop(columns=["pod_count_safe", "network_in_kb", "network_out_kb"], inplace=True)
df.drop(columns=["pod_capacity_used"], inplace=True)

timestamp_col = df.pop("timestamp")
df.insert(1, "timestamp", timestamp_col)

memory_per_pod_col = df.pop("pod_memory_usage_mb")
df.insert(6, "pod_memory_usage_mb", memory_per_pod_col)

pod_count_col = df.pop("pod_count")
df.insert(7, "pod_count", pod_count_col)

network_total_col = df.pop("network_total_kb")
df.insert(11, "network_total_kb", network_total_col)

df.to_csv("data/combined_metrics.csv", index=False)
print("\nCombined dataset saved to data/combined_metrics.csv")