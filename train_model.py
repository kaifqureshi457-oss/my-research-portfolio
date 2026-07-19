import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Generate Data
np.random.seed(42)
num_samples = 2000
pm25 = np.random.uniform(10, 350, num_samples)
no2 = np.random.uniform(5, 150, num_samples)
aqi = (pm25 * 1.2) + (no2 * 0.8) + np.random.normal(0, 10, num_samples)
aqi = np.clip(aqi, 0, 500)

df = pd.DataFrame({"PM2.5": pm25, "NO2": no2, "AQI": aqi})
X = df[["PM2.5", "NO2"]]
y = df["AQI"]

# Train Model
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# Save Model
joblib.dump(model, "aqi_model.pkl")
print("Model saved successfully!")