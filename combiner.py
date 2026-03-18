import glob
import pandas as pd

files = glob.glob("data/metrics_*.csv")
df = pd.concat(map(pd.read_csv, files), ignore_index=True)

node_map = {
    '172.18.0.4:9100': 'control-plane',
    '172.18.0.5:9100': 'worker-1',
    '172.18.0.2:9100': 'worker-2',
    '172.18.0.3:9100': 'worker-3'
}

df['node'] = df['node'].map(node_map).fillna(df['node'])

df.sort_values(["node", "timestamp"], inplace=True)
print(f"Combined dataset: {len(df)} rows across {df['node'].unique()} nodes.")
print(f"Files combined: {len(files)}")

df['node_score'] = 1 - (0.7 * df['cpu_usage'] + 0.3 * df['memory_usage'])

df['node_score'] = (df['node_score'] - df['node_score'].min()) / (df['node_score'].max() - df['node_score'].min())

df.to_csv("data/combined_metrics.csv", index=False)
print("\nCombined dataset saved to data/combined_metrics.csv")