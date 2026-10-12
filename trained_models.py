"""
AgroPulse ENSO - Advanced Multi-Parameter Machine Learning Pipeline
1. LSTM: Deep sequential time-series modeling of coupled climate-vegetation interactions.
2. XGBoost: Multi-factor tabular gradient boosting for commodity price volatility.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

# ==========================================
# 1. LOAD MERGED DATASET
# ==========================================
print("[1/4] Loading Multi-Parameter Dataset...")
df = pd.read_csv("comprehensive_12_crops_fmcg_dataset.csv")

# ==========================================
# 2. LSTM: SEQUENTIAL CLIMATE & SATELLITE DISRUPTION
# ==========================================
print("\n[2/4] Training LSTM on Sequential Climate & Satellite Indicators...")

# Temporal feature sequence
lstm_features = [
    'oceanic_nino_index', 
    'rainfall_anomaly_pct', 
    'indian_ocean_dipole', 
    'soil_moisture_deficit_pct', 
    'ndvi_anomaly'
]
target_arrival = 'arrival_volume_qtl'

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

scaled_X = scaler_X.fit_transform(df[lstm_features])
scaled_y = scaler_y.fit_transform(df[[target_arrival]])

TIME_STEPS = 6
X_seq, y_seq = [], []
for i in range(len(scaled_X) - TIME_STEPS):
    X_seq.append(scaled_X[i:i + TIME_STEPS])
    y_seq.append(scaled_y[i + TIME_STEPS])

X_seq, y_seq = np.array(X_seq), np.array(y_seq)

lstm_model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(TIME_STEPS, len(lstm_features))),
    Dropout(0.2),
    LSTM(32),
    Dense(16, activation='relu'),
    Dense(1)
])

lstm_model.compile(optimizer='adam', loss='mean_squared_error')
lstm_model.fit(X_seq, y_seq, epochs=8, batch_size=32, verbose=1)
print("✓ Multi-variable LSTM successfully trained.")

# ==========================================
# 3. XGBOOST: TABULAR MULTI-PARAMETER PRICING
# ==========================================
print("\n[3/4] Training XGBoost with Full Agronomic & Market Indicators...")

# Encode categorical metadata
df_encoded = pd.get_dummies(df, columns=['crop', 'category', 'yield_quality_grade'], drop_first=True)

xgb_features = [
    'oceanic_nino_index',
    'rainfall_anomaly_pct',
    'indian_ocean_dipole',
    'soil_moisture_deficit_pct',
    'heat_stress_days',
    'reservoir_level_pct',
    'pest_index',
    'ndvi_anomaly',
    'water_table_depth_m',
    'freight_index',
    'arrival_volume_qtl'
] + [c for c in df_encoded.columns if c.startswith(('crop_', 'category_', 'yield_quality_grade_'))]

target_price = 'modal_price_rs_per_quintal'

X_xgb = df_encoded[xgb_features]
y_xgb = df_encoded[target_price]

X_train, X_test, y_train, y_test = train_test_split(X_xgb, y_xgb, test_size=0.2, random_state=42)

xgb_regressor = xgb.XGBRegressor(
    n_estimators=180,
    learning_rate=0.04,
    max_depth=6,
    subsample=0.85,
    colsample_bytree=0.85,
    random_state=42
)

xgb_regressor.fit(X_train, y_train)

# Evaluation
y_pred = xgb_regressor.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
print(f"✓ XGBoost Evaluated: RMSE = ₹{rmse:.2f}, R² Score = {r2:.3f}")

# Feature Importance Breakdown
top_features = pd.Series(xgb_regressor.feature_importances_, index=xgb_features).nlargest(5)
print("\nTop 5 Price Surge Drivers (Feature Importance):")
for feat, imp in top_features.items():
    print(f"  - {feat}: {imp * 100:.1f}%")

# ==========================================
# 4. EXPORT & PIPELINE COMPLETION
# ==========================================
print("\n[4/4] Pipeline Complete. Multi-factor parameters calibrated for main.py runtime.")