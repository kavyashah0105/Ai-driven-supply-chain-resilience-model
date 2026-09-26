import pandas as pd
import numpy as np

climate_records = {
    2000: (-0.5, -8.0), 2001: (-0.1, -8.0), 2002: (1.1, -19.2), 2003: (0.3, 2.0),
    2004: (0.7, -13.8), 2005: (0.3, -1.0), 2006: (0.8, 0.0), 2007: (-0.8, 5.7),
    2008: (-0.2, -1.7), 2009: (1.4, -21.8), 2010: (-1.2, 2.1), 2011: (-0.7, 1.6),
    2012: (0.4, -7.1), 2013: (-0.3, 5.6), 2014: (0.6, -11.9), 2015: (2.2, -14.3),
    2016: (-0.4, -3.0), 2017: (-0.4, -5.0), 2018: (0.8, -9.0), 2019: (0.3, 10.0),
    2020: (-0.9, 8.8), 2021: (-0.6, -0.7), 2022: (-1.0, 6.5), 2023: (1.6, -5.6),
    2024: (-0.3, 7.6)
}

crop_library = {
    "Rice": {"base_price": 540, "trend": 74.0, "sens": 1.0, "type": "Kharif Grain"},
    "Wheat": {"base_price": 580, "trend": 68.0, "sens": 0.65, "type": "Rabi Grain"},
    "Maize": {"base_price": 450, "trend": 65.0, "sens": 1.15, "type": "Coarse Grain"},
    "Barley": {"base_price": 480, "trend": 58.0, "sens": 0.70, "type": "Rabi Grain"},
    "Tur_Arhar": {"base_price": 1350, "trend": 240.0, "sens": 1.75, "type": "Pulse"},
    "Chana_Gram": {"base_price": 1100, "trend": 160.0, "sens": 0.85, "type": "Pulse"},
    "Moong": {"base_price": 1400, "trend": 250.0, "sens": 1.60, "type": "Pulse"},
    "Urad": {"base_price": 1300, "trend": 230.0, "sens": 1.65, "type": "Pulse"},
    "Soybean": {"base_price": 900, "trend": 165.0, "sens": 1.90, "type": "Oilseed"},
    "Mustard": {"base_price": 1200, "trend": 170.0, "sens": 0.75, "type": "Oilseed"},
    "Groundnut": {"base_price": 1300, "trend": 190.0, "sens": 1.45, "type": "Oilseed"},
    "Sugarcane": {"base_price": 85, "trend": 12.0, "sens": 0.90, "type": "Commercial"}
}

rows = []
for year in range(2000, 2025):
    oni, rain_deficit = climate_records[year]
    year_idx = year - 2000
    is_el_nino = oni >= 0.5
    shock_potency = (abs(rain_deficit) / 100.0) if (is_el_nino and rain_deficit < 0) else 0.0

    for month in range(1, 13):
        for crop, info in crop_library.items():
            trend_price = info["base_price"] + (year_idx * info["trend"])
            climate_factor = 1.0 + (shock_potency * info["sens"])
            price_qtl = round(trend_price * climate_factor, 1)

            rows.append({
                "year": year,
                "month": month,
                "crop": crop,
                "category": info["type"],
                "oceanic_nino_index": oni,
                "rainfall_anomaly_pct": rain_deficit,
                "modal_price_rs_per_quintal": price_qtl,
                "retail_equivalent_rs_per_kg": round(price_qtl / 100.0, 2)
            })

df = pd.DataFrame(rows)
df.to_csv("comprehensive_12_crops_fmcg_dataset.csv", index=False)
print("Saved 3,600 rows to 'comprehensive_12_crops_fmcg_dataset.csv'")