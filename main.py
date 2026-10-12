import base64
import io
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AgroPulse ENSO Enterprise Platform")
templates = Jinja2Templates(directory="templates")

# Master Commodity Database
CROP_DATABASE = {
    "Rice": {"name": "Rice (Paddy)", "base_price": 2200, "sensitivity": 1.00, "category": "Grains"},
    "Wheat": {"name": "Wheat", "base_price": 2275, "sensitivity": 0.65, "category": "Grains"},
    "Maize": {"name": "Maize", "base_price": 2090, "sensitivity": 1.15, "category": "Grains"},
    "Barley": {"name": "Barley", "base_price": 1850, "sensitivity": 0.70, "category": "Grains"},
    "Tur": {"name": "Tur / Arhar", "base_price": 7000, "sensitivity": 1.75, "category": "Pulses"},
    "Chana": {"name": "Chana (Gram)", "base_price": 5440, "sensitivity": 0.85, "category": "Pulses"},
    "Moong": {"name": "Moong", "base_price": 8558, "sensitivity": 1.60, "category": "Pulses"},
    "Urad": {"name": "Urad", "base_price": 6950, "sensitivity": 1.65, "category": "Pulses"},
    "Soybean": {"name": "Soybean", "base_price": 4600, "sensitivity": 1.90, "category": "Oilseeds"},
    "Groundnut": {"name": "Groundnut", "base_price": 6375, "sensitivity": 1.45, "category": "Oilseeds"},
    "Mustard": {"name": "Mustard Seed", "base_price": 5650, "sensitivity": 0.75, "category": "Oilseeds"},
    "Sugarcane": {"name": "Sugarcane", "base_price": 315, "sensitivity": 0.90, "category": "Cash Crops"}
}

SCENARIOS = ["Mild", "Moderate", "Severe"]
SCENARIO_FACTORS = {"Mild": 0.12, "Moderate": 0.22, "Severe": 0.38}

def determine_yield_quality(stress_score: float) -> dict:
    if stress_score < 0.30:
        return {
            "grade": "Grade A (Premium / Export Quality)",
            "css_class": "grade-a",
            "grain_health": "Uniform plump grain filling; high test weight (>79 kg/hL)",
            "defect_pct": "< 2.0% shriveled or discolored kernels",
            "market_impact": "Procured at premium rates without APMC docking."
        }
    elif stress_score < 0.54:
        return {
            "grade": "Grade B (Fair Average Quality - FAQ)",
            "css_class": "grade-b",
            "grain_health": "Moderate size variation; mild thermal stress marks",
            "defect_pct": "4.5% - 8.0% shriveled grains",
            "market_impact": "Standard mandi price; acceptable for industrial FMCG processing."
        }
    else:
        return {
            "grade": "Grade C (Sub-Standard / Distressed)",
            "css_class": "grade-c",
            "grain_health": "Severe grain shrinkage, low moisture test weight, thermal discoloration",
            "defect_pct": "> 14.0% damaged / pinhole insect damage",
            "market_impact": "Subject to 12-20% quality dockage penalties at factory gates."
        }

# Initial GET route - loads defaults without calculations
@app.get("/", response_class=HTMLResponse)
def index_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "crops": CROP_DATABASE,
            "scenarios": SCENARIOS,
            "has_results": False,
            "selected_crop": "Tur",
            "selected_scenario": "Moderate",
            "selected_iod": "Neutral",
            "soil_moisture_deficit": 25.0,
            "heat_stress_days": 8,
            "reservoir_level_pct": 55.0,
            "pest_index": 1.2,
            "ndvi_anomaly": -0.15,
            "water_table_depth": 12.0,
            "freight_index": 115.0,
            "mitigation_checked": False
        }
    )

# POST route - receives inputs, computes physics/pricing, passes results
@app.post("/simulate", response_class=HTMLResponse)
def simulate_view(
    request: Request,
    crop: str = Form(...),
    scenario: str = Form(...),
    iod_phase: str = Form(...),
    soil_moisture_deficit: float = Form(...),
    heat_stress_days: int = Form(...),
    reservoir_level_pct: float = Form(...),
    pest_index: float = Form(...),
    ndvi_anomaly: float = Form(...),
    water_table_depth: float = Form(...),
    freight_index: float = Form(...),
    mitigation: bool = Form(False)
):
    crop_info = CROP_DATABASE.get(crop, CROP_DATABASE["Tur"])
    scenario_factor = SCENARIO_FACTORS.get(scenario, 0.22)

    iod_modifier = {"Positive": 0.80, "Neutral": 1.00, "Negative": 1.25}.get(iod_phase, 1.00)
    thermal_stress = (heat_stress_days / 30.0) * 0.20
    soil_stress = (soil_moisture_deficit / 100.0) * 0.25
    reservoir_stress = max(0.0, (60.0 - reservoir_level_pct) / 100.0) * 0.18
    vegetation_stress = max(0.0, -ndvi_anomaly) * 0.20
    groundwater_stress = max(0.0, (water_table_depth - 10.0) / 20.0) * 0.12
    biotic_stress = (pest_index - 1.0) * 0.15
    logistics_stress = max(0.0, (freight_index - 100.0) / 100.0) * 0.10

    composite_stress = (
        (scenario_factor * iod_modifier) +
        thermal_stress +
        soil_stress +
        reservoir_stress +
        vegetation_stress +
        groundwater_stress +
        biotic_stress +
        logistics_stress
    )

    mitigation_factor = 0.60 if mitigation else 1.00
    net_surge_pct = composite_stress * crop_info["sensitivity"] * 0.40 * mitigation_factor
    base_price = crop_info["base_price"]
    simulated_price = round(base_price * (1 + net_surge_pct))
    price_delta = simulated_price - base_price

    quality_report = determine_yield_quality(composite_stress)

    # System Dynamics: 52-week inventory simulation
    safety_stock = 1000.0
    inventory = safety_stock
    performance_loss = 0.0
    for _ in range(52):
        inflow = 200.0 * (1.0 - min(0.85, net_surge_pct * 0.55))
        outflow = 200.0
        inventory = max(0.0, inventory + (inflow - outflow))
        if inventory < safety_stock:
            performance_loss += (safety_stock - inventory)

    scri_score = round(max(0.1, 1.0 - (performance_loss / (safety_stock * 52))), 3)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "crops": CROP_DATABASE,
            "scenarios": SCENARIOS,
            "has_results": True,
            "selected_crop": crop,
            "selected_scenario": scenario,
            "selected_iod": iod_phase,
            "soil_moisture_deficit": soil_moisture_deficit,
            "heat_stress_days": heat_stress_days,
            "reservoir_level_pct": reservoir_level_pct,
            "pest_index": pest_index,
            "ndvi_anomaly": ndvi_anomaly,
            "water_table_depth": water_table_depth,
            "freight_index": freight_index,
            "mitigation_checked": mitigation,
            "crop_name": crop_info["name"],
            "raw_base_price": base_price,
            "raw_price_delta": price_delta,
            "raw_simulated_price": simulated_price,
            "base_price": f"{base_price:,}",
            "simulated_price": f"{simulated_price:,}",
            "base_retail": f"{(base_price / 100):.1f}",
            "simulated_retail": f"{(simulated_price / 100):.1f}",
            "price_delta": f"{price_delta:+,}",
            "surge_pct_display": f"{round(net_surge_pct * 100, 1)}%",
            "scri_score": scri_score,
            "quality": quality_report
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)