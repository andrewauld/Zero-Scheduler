import pandas as pd

root_dir = '../'
training_data_path = root_dir + 'data/combined_metrics.csv'

df_data = pd.read_csv(training_data_path)
print(df_data.columns)

new_df = df_data.drop('timestamp', axis=1)
print(new_df.columns)