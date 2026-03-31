import numpy as np
import pandas as pd
import joblib

from sklearn import ensemble
from sklearn.metrics import mean_squared_error, r2_score

metrics = pd.read_csv("../data/combined_metrics.csv")

test_run_id = metrics["test_run"].max()
train_df = metrics[metrics["test_run"] != test_run_id]
test_df = metrics[metrics["test_run"] == test_run_id]

X_train = train_df.drop(columns=["power_efficiency", "node", "timestamp", "test_run"])
y_train = train_df["power_efficiency"]
X_test = test_df.drop(columns=["power_efficiency", "node", "timestamp", "test_run"])
y_test = test_df["power_efficiency"]

params = {
    "n_estimators": 500,
    "max_depth": 4,
    "min_samples_split": 5,
    "random_state": 13
}

rfm = ensemble.RandomForestRegressor(**params)
rfm.fit(X_train, y_train)

y_pred = rfm.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, rfm.predict(X_test)))
r2 = r2_score(y_test, y_pred)
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R2 score: {r2}")

joblib.dump(rfm, "random_forrest.pk1")
print("\nGradient Boosting model saved to models/random_forrest.pk1")