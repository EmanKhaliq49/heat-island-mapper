import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb

df = pd.read_csv('karachi_final_dataset_v3.csv')

# Now using all 4 features instead of 2
X = df[['NDVI', 'NDBI', 'Elevation', 'road_length_m', 'distance_to_coast_m']]
y = df['LST_Celsius']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training on {len(X_train)} cells, testing on {len(X_test)} cells")

rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train)
rf_preds = rf_model.predict(X_test)

print(f"\n--- Random Forest (4 features) ---")
print(f"MAE: {mean_absolute_error(y_test, rf_preds):.3f} °C")
print(f"R²: {r2_score(y_test, rf_preds):.3f}")

xgb_model = xgb.XGBRegressor(n_estimators=200, random_state=42)
xgb_model.fit(X_train, y_train)
xgb_preds = xgb_model.predict(X_test)

print(f"\n--- XGBoost (4 features) ---")
print(f"MAE: {mean_absolute_error(y_test, xgb_preds):.3f} °C")
print(f"R²: {r2_score(y_test, xgb_preds):.3f}")

print(f"\n--- Feature Importance (Random Forest) ---")
for feature, importance in sorted(
    zip(X.columns, rf_model.feature_importances_),
    key=lambda x: -x[1]
):
    print(f"{feature}: {importance:.3f}")