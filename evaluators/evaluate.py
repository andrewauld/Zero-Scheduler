import pandas as pd
import sys
import glob

ml_mode = sys.argv[1] if len(sys.argv) > 1 else "default"
ml_file = glob.glob(f"data/{ml_mode}/combined_metrics.csv")
default_mode = sys.argv[2] if len(sys.argv) > 2 else "default"
default_file = glob.glob(f"data/{default_mode}/combined_metrics.csv")

print("\nOVERALL: ML vs Default Scheduler Comparison")
print("==============================================\n")

ml = pd.read_csv("../data/gradual_increase_ml/combined_metrics.csv")
default = pd.read_csv("../data/gradual_increase_default/combined_metrics.csv")

# Std = more even distribution
print("ML cpu std:", ml.groupby("timestamp")["cpu_usage"].std().mean())
print("Default cpu std:", default.groupby("timestamp")["cpu_usage"].std().mean())

# Power efficiency
print("\nML mean power efficiency:", ml["power_efficiency"].mean())
print("Default mean power efficiency:", default["power_efficiency"].mean())

# Power usage
print("\nML mean estimated power usage:", ml["estimated_power"].mean())
print("Default mean estimated power usage:", default["estimated_power"].mean())

print("\nPER RUN VARIANCE CHECK: ML vs Default Scheduler Comparison")
print("==============================================\n")

ml_runs = ml.groupby("test_run")["estimated_power"].mean()
default_runs = default.groupby("test_run")["estimated_power"].mean()

print("ML mean estimated power:", ml_runs.mean(), "± std:", ml_runs.std())
print("Default mean estimated power:", default_runs.mean(), "± std:", default_runs.std())