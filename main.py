from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

class SimulationParams(BaseModel):
    crop: str = "Rice"
    shock_intensity: str = "moderate"
    initial_buffer: float = 600.0
    procurement_policy: bool = True
    diversified_sourcing: bool = True
    time_horizon_weeks: int = 52

@app.post("/api/simulate")
def simulate(p: SimulationParams):
    # 1. Shock calibration based on intensity and crop resilience
    shock_map = {"mild": 0.10, "moderate": 0.25, "severe": 0.40}
    crop_multipliers = {"Wheat": 0.7, "Rice": 1.0, "Tur_Arhar": 1.6, "Soybean": 1.8}
    
    base_shock = shock_map.get(p.shock_intensity.lower(), 0.25) * crop_multipliers.get(p.crop, 1.0)
    effective_shock = base_shock * (0.55 if p.diversified_sourcing else 1.0)

    # 2. Initial Stock Values
    farm = 800.0
    dc = 1200.0
    retail = 900.0
    buffer = p.initial_buffer

    # Output storage
    weeks = list(range(p.time_horizon_weeks + 1))
    farm_stocks, dc_stocks, retail_stocks, buffer_stocks, prices = [], [], [], [], []
    stockout_weeks = 0
    performance_loss = 0.0

    # 3. Direct Step-by-Step Simulation Loop (Slide 10 Equation)
    for t in weeks:
        farm_stocks.append(round(farm, 1))
        dc_stocks.append(round(dc, 1))
        retail_stocks.append(round(retail, 1))
        buffer_stocks.append(round(buffer, 1))

        # Price inflation and performance tracking
        price = 50.0 + max(0.0, (500.0 - retail) * 0.12)
        prices.append(round(price, 2))
        if retail < 100.0: stockout_weeks += 1
        if retail < 450.0: performance_loss += (450.0 - retail)

        # Flows for the next week
        shock = effective_shock if (12 <= t <= 32) else (effective_shock * 0.2)
        production = 1000.0 * (1.0 - shock)
        procurement = min(farm, 950.0)
        distribution = min(dc * 0.7, 920.0)

        # Buffer stock policy
        buffer_release = 0.0
        if retail < 400.0 and buffer > 0.0 and p.procurement_policy:
            buffer_release = min(buffer, 400.0 - retail)

        demand = 900.0
        consumption = min(retail + buffer_release, demand)
        spoilage = 0.015 * dc

        # Update stocks for t + 1 (Stock = Previous + Inflows - Outflows)
        farm = max(0.0, farm + production - procurement)
        dc = max(0.0, dc + procurement - distribution - spoilage)
        retail = max(0.0, retail + distribution + buffer_release - consumption)
        buffer = max(0.0, buffer - buffer_release)

    # SCRI = 1 - (Performance Loss / Max Expected Safety Baseline)
    scri = max(0.0, round(1.0 - (performance_loss / (450.0 * len(weeks))), 3))

    return {
        "weeks": weeks,
        "farm_stocks": farm_stocks,
        "dc_stocks": dc_stocks,
        "retail_stocks": retail_stocks,
        "buffer_stocks": buffer_stocks,
        "prices": prices,
        "scri": scri,
        "stockout_weeks": stockout_weeks,
        "max_price": max(prices)
    }

# Serve the static folder (HTML/CSS/JS)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)