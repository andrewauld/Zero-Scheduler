import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib

from sklearn import datasets, ensemble
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.utils.fixes import parse_version

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
    "learning_rate": 0.01,
    "loss": "squared_error"
}

gbm = ensemble.GradientBoostingRegressor(**params)
gbm.fit(X_train, y_train)

rmse = np.sqrt(mean_squared_error(y_test, gbm.predict(X_test)))
y_pred = gbm.predict(X_test)
r2 = r2_score(y_test, y_pred)
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R2 score: {r2}")

joblib.dump(gbm, "gradient_boosting.pk1")
print("\nGradient Boosting model saved to models/gradient_boosting.pk1")