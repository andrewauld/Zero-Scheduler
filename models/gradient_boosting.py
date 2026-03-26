import os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

root_dir = '../'
training_data_path = root_dir + 'data/combined_metrics.csv'

df_data = pd.read_csv(training_data_path)

# Not sure if this section is necessary
features = df_data.columns.tolist()

preprocessor = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])

preprocessed_data = preprocessor.fit_transform(df_data)

X_train, X_test, y_train, y_test = train_test_split(preprocessed_data, test_size=0.2, random_state=42)

model = GradientBoostingRegressor()
model.fit(X_train, y_train)

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

rmse_train = np.sqrt(mean_squared_error(y_train, y_train_pred))
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))

print(f"RMSE for training data is {rmse_train}.")
print(f"RMSE for test data is {rmse_test}.")
