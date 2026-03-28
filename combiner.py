import glob
import pandas as pd
import numpy as np

files = glob.glob("data/metrics_*.csv")
df = pd.concat(map(pd.read_csv, files), ignore_index=True)

df.sort_values(["node", "timestamp"], inplace=True)
df.reset_index(drop=True, inplace=True)

print(f"Combined dataset: {len(df)} rows across {df['node'].unique()} nodes.")
print(f"Files combined: {len(files)}")

# Carry out feature engineering here (cpu/request, memory/request, power consumption, target label, etc.)
df["pod_memory_usage_mb"] = df["pod_memory_usage"] / 1024 / 1024
df["network_in_mb"] = df["network_in"] / 1024 / 1024
df["network_out_mb"] = df["network_out"] / 1024 / 1024
df["disk_in_mb"] = df["disk_in"] / 1024 / 1024
df["disk_out_mb"] = df["disk_out"] / 1024 / 1024

df.drop(columns=["pod_memory_usage", "network_in", "network_out", "disk_in", "disk_out"], inplace=True)

df.to_csv("data/combined_metrics.csv", index=False)
print("\nCombined dataset saved to data/combined_metrics.csv")