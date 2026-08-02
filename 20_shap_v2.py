import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import shap
import matplotlib.pyplot as plt

df = pd.read_csv('karachi_final_dataset_v3.csv')

X = df[['NDVI', 'NDBI', 'Elevation', 'road_length_m', 'distance_to_coast_m']]
y = df['LST_Celsius']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

print("Computing SHAP values... this may take a minute")
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# --- Global summary plot ---
plt.figure()
shap.summary_plot(shap_values, X_test, show=False)
plt.tight_layout()
plt.savefig('shap_summary_karachi_v3.png', dpi=150)
print("Saved shap_summary_karachi_v3.png")

# --- Explain the same hottest cell as before, for comparison ---
hottest_idx = y_test.idxmax()
hottest_row_position = X_test.index.get_loc(hottest_idx)

print(f"\nHottest cell in test set:")
print(f"Actual temp: {y_test.loc[hottest_idx]:.2f}°C")
predicted = model.predict(X_test.loc[[hottest_idx]])[0]
print(f"Predicted temp: {predicted:.2f}°C")
print(f"NDVI: {X_test.loc[hottest_idx, 'NDVI']:.3f}")
print(f"NDBI: {X_test.loc[hottest_idx, 'NDBI']:.3f}")
print(f"Elevation: {X_test.loc[hottest_idx, 'Elevation']:.1f}m")
print(f"Road length: {X_test.loc[hottest_idx, 'road_length_m']:.0f}m")

plt.figure()
shap.plots.waterfall(shap_values[hottest_row_position], show=False)
plt.tight_layout()
plt.savefig('shap_hottest_cell_karachi_v3.png', dpi=150)
print("Saved shap_hottest_cell_karachi_v3.png")