import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

metrics = pd.read_csv("../data/combined_metrics.csv")

test_run_id = metrics["test_run"].max()
train_df = metrics[metrics["test_run"] != test_run_id]
test_df = metrics[metrics["test_run"] == test_run_id]

X_train = train_df.drop(columns=["power_efficiency", "node", "timestamp", "test_run"])
y_train = train_df["power_efficiency"]
X_test = test_df.drop(columns=["power_efficiency", "node", "timestamp", "test_run"])
y_test = test_df["power_efficiency"]

svr = Pipeline([
    ("scaler", StandardScaler()),
    ("svr", SVR(kernel="rbf", C=1.0, epsilon=0.01))
])

svm = svr.fit(X_train, y_train)

y_pred = svr.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R2 score: {r2}")

joblib.dump(svm, "support_vector.pkl")
print("\nSupport Vector Machine model saved to models/support_vector.pkl")