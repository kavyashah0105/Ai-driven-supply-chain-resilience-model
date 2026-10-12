import pandas as pd
import numpy as np

# Set random seed for reproducible research benchmark
np.random.seed(42)

CROPS = {
    "Rice": {"base_price": 2200, "sensitivity": 1.00, "category": "Grains"},
    "Wheat": {"base_price": 2275, "sensitivity": 0.65, "category": "Grains"},
    "Maize": {"base_price": 2090, "sensitivity": 1.15, "category": "Grains"},
    "Barley": {"base_price": 1850, "sensitivity": 0.70, "category": "Grains"},
    "Tur": {"base_price": 7000, "sensitivity": 1.75, "category": "Pulses"},
    "Chana": {"base_price": 5440, "sensitivity": 0.85, "category": "Pulses"},
    "Moong": {"base_price": 8558, "sensitivity": 1.60, "category": "Pulses"},
    "Urad": {"base_price": 6950, "sensitivity": 1.65, "category": "Pulses"},
    "Soybean": {"base_price": 4600, "sensitivity": 1.90, "category": "Oilseeds"},
    "Groundnut": {"base_price": 6375, "sensitivity": 1.45, "category": "Oilseeds"},
    "Mustard": {"base_price": 5650, "sensitivity": 0.75, "category": "Oilseeds"},
    "Sugarcane": {"base_price": 315, "sensitivity": 0.90, "category": "Cash Crops"}
}

YEARS = list(range(2000, 2025))  # 25 Years
MONTHS = list(range(1, 13))       # 12 Months

records = []

for year in YEARS:
    # Historical ENSO & IOD macro climate signals
    is_strong_el_nino = year in [2002, 2009, 2015, 2023]
    is_mild_el_nino = year in [2004, 2006, 2014, 2018]
    
    base_oni = 1.8 if is_strong_el_nino else (0.9 if is_mild_el_nino else -0.2)
    base_monsoon_def = -21.0 if is_strong_el_nino else (-11.0 if is_mild_el_nino else 2.5)

    for month in MONTHS:
        # Macro climate fluctuations
        oni = np.clip(np.random.normal(base_oni, 0.25), -1.8, 2.8)
        rainfall_anomaly = np.clip(np.random.normal(base_monsoon_def, 6.0), -45.0, 30.0)
        iod_index = np.clip(np.random.normal(-0.35 if is_strong_el_nino else 0.1, 0.3), -1.2, 1.2)
        
        # Micro climate & Agronomic variables
        soil_deficit = np.clip(np.random.normal(35.0 if oni > 1.0 else 15.0, 8.0), 0.0, 75.0)
        heat_days = int(np.clip(np.random.normal(12 if oni > 1.0 else 4, 3), 0, 28))
        reservoir_pct = np.clip(np.random.normal(45.0 if oni > 1.0 else 72.0, 10.0), 15.0, 98.0)
        pest_idx = np.clip(np.random.normal(1.45 if oni > 1.0 else 1.1, 0.15), 1.0, 2.2)
        
        # 3 Additional Parameters
        ndvi_anomaly = np.clip(np.random.normal(-0.25 if oni > 1.0 else 0.05, 0.08), -0.60, 0.30)
        water_table_depth = np.clip(np.random.normal(14.5 if oni > 1.0 else 8.0, 2.0), 3.0, 25.0)
        freight_index = np.clip(np.random.normal(118.0 if oni > 1.0 else 102.0, 5.0), 90.0, 150.0)

        for crop_name, info in CROPS.items():
            sens = info["sensitivity"]
            
            # Composite Disruption Score (0.0 to 1.0)
            stress_score = (
                (max(0, oni) * 0.22) +
                (max(0, -rainfall_anomaly) / 100.0 * 0.20) +
                (soil_deficit / 100.0 * 0.15) +
                (heat_days / 30.0 * 0.12) +
                (max(0, 60.0 - reservoir_pct) / 100.0 * 0.10) +
                (max(0, -ndvi_anomaly) * 0.10) +
                ((pest_idx - 1.0) * 0.06) +
                ((freight_index - 100.0) / 100.0 * 0.05)
            ) * (sens / 1.0)

            # Assign Yield Quality Grade based on composite stress
            if stress_score < 0.28:
                quality_grade = "Grade A"
            elif stress_score < 0.52:
                quality_grade = "Grade B"
            else:
                quality_grade = "Grade C"

            # Baseline arrival & wholesale price dynamics
            base_arrival = np.random.normal(15000, 2000)
            arrival_vol = max(1200.0, base_arrival * (1.0 - min(0.75, stress_score * 0.85)))
            
            # Modal price spike
            inflation_factor = 1.0 + ((year - 2000) * 0.035)
            price_surge = 1.0 + (stress_score * 0.65)
            modal_price = round(info["base_price"] * inflation_factor * price_surge)
            retail_price = round(modal_price / 100.0, 1)

            records.append({
                "year": year,
                "month": month,
                "crop": crop_name,
                "category": info["category"],
                "oceanic_nino_index": round(oni, 2),
                "rainfall_anomaly_pct": round(rainfall_anomaly, 1),
                "indian_ocean_dipole": round(iod_index, 2),
                "soil_moisture_deficit_pct": round(soil_deficit, 1),
                "heat_stress_days": heat_days,
                "reservoir_level_pct": round(reservoir_pct, 1),
                "pest_index": round(pest_idx, 2),
                "ndvi_anomaly": round(ndvi_anomaly, 3),
                "water_table_depth_m": round(water_table_depth, 1),
                "freight_index": round(freight_index, 1),
                "yield_quality_grade": quality_grade,
                "arrival_volume_qtl": round(arrival_vol, 1),
                "modal_price_rs_per_quintal": modal_price,
                "retail_equivalent_rs_per_kg": retail_price
            })

df_out = pd.DataFrame(records)
df_out.to_csv("comprehensive_12_crops_fmcg_dataset.csv", index=False)
print(f"[SUCCESS] Dataset saved successfully with {len(df_out)} rows and {len(df_out.columns)} columns.")