let priceBarChartInstance = null;

// Database for 12 FMCG Commodities
const cropDatabase = {
  Rice: {
    name: "Rice (Paddy)",
    ogPrice: 2200,
    sensitivity: 1.0,
    notes: "Heavily dependent on June–September Kharif monsoon rainfall across key producing states like Punjab, West Bengal, and UP."
  },
  Wheat: {
    name: "Wheat Grain",
    ogPrice: 2275,
    sensitivity: 0.65,
    notes: "A Rabi crop with extensive canal irrigation, making it less vulnerable to dry spells, though post-El Niño winter temperature spikes still constrain yield."
  },
  Maize: {
    name: "Maize (Corn)",
    ogPrice: 2150,
    sensitivity: 1.15,
    notes: "Primarily rainfed coarse grain with tight margins in animal feed and poultry industries, causing quick price transmission."
  },
  Barley: {
    name: "Barley",
    ogPrice: 1950,
    sensitivity: 0.70,
    notes: "Mainly irrigated in northern basins; moderate drought resilience offsets large swings."
  },
  Tur_Arhar: {
    name: "Tur / Arhar (Pulse)",
    ogPrice: 7000,
    sensitivity: 1.75,
    notes: "Over 85% rainfed in Marathwada and central India. Rainfall deficits directly trigger severe mandi supply collapse and speculative hoarding."
  },
  Chana_Gram: {
    name: "Chana (Bengal Gram)",
    ogPrice: 5400,
    sensitivity: 0.85,
    notes: "Winter pulse reliant on residual soil moisture; buffers prevent rapid price inflation compared to summer pulses."
  },
  Moong: {
    name: "Moong Dal",
    ogPrice: 8200,
    sensitivity: 1.60,
    notes: "Short-duration crop vulnerable to dry spells during critical flowering phases."
  },
  Urad: {
    name: "Urad Dal",
    ogPrice: 7400,
    sensitivity: 1.65,
    notes: "Concentrated Kharif pulse with high sensitivity to monsoon anomalies, driving sharp wholesale and packaged price spikes."
  },
  Soybean: {
    name: "Soybean (Oilseed)",
    ogPrice: 4600,
    sensitivity: 1.90,
    notes: "India's primary domestic edible oil feed. Highly concentrated in rainfed Madhya Pradesh and Maharashtra; monsoon droughts immediately escalate cooking oil costs."
  },
  Mustard: {
    name: "Mustard Seed",
    ogPrice: 5350,
    sensitivity: 0.75,
    notes: "Rabi oilseed benefiting from controlled tube-well irrigation in Rajasthan and Haryana, dampening peak climate shocks."
  },
  Groundnut: {
    name: "Groundnut (Peanut)",
    ogPrice: 6300,
    sensitivity: 1.45,
    notes: "Cultivated in Saurashtra and peninsular belts; irregular rainfall during pod-development directly slashes yield."
  },
  Sugarcane: {
    name: "Sugarcane",
    ogPrice: 350,
    sensitivity: 0.90,
    notes: "Water-intensive perennial crop. El Niño reduces reservoir levels, impairing crushing cycles and elevating sweetener input costs for FMCG bakeries and beverages."
  }
};

const scenarioSurgeFactors = {
  mild: { factor: 0.12, label: "Mild El Niño Price", desc: "weak SST warming with minor rainfall deviations (~5-8% deficit)" },
  moderate: { factor: 0.22, label: "Moderate El Niño Price", desc: "oceanic temperature anomalies (+1.0°C to +1.4°C) causing ~10-15% monsoon rainfall deficits" },
  severe: { factor: 0.38, label: "Severe El Niño Price", desc: "widespread drought conditions (>18% rainfall shortfall) similar to the 2002 and 2009 disruptions" }
};

function runSimulation() {
  const cropKey = document.getElementById("cropSelect").value;
  const scenarioKey = document.getElementById("scenarioSelect").value;
  const diversified = document.getElementById("diversifiedSourcing").checked;

  const crop = cropDatabase[cropKey];
  const scenario = scenarioSurgeFactors[scenarioKey];

  // Show results container and hide initial placeholder
  document.getElementById("placeholderBox").style.display = "none";
  const resultsWrapper = document.getElementById("resultsWrapper");
  resultsWrapper.classList.remove("results-hidden");

  // Damping logic for regional mitigation
  const mitigationDamping = diversified ? 0.60 : 1.0;
  const surgePct = scenario.factor * crop.sensitivity * mitigationDamping;

  const ogPrice = crop.ogPrice;
  const simPrice = Math.round(ogPrice * (1.0 + surgePct));
  const deltaPrice = simPrice - ogPrice;
  const displaySurgePct = Math.round(surgePct * 100);

  // 1. Update Metric Cards
  document.getElementById("cardOgPrice").innerText = `₹${ogPrice.toLocaleString('en-IN')}`;
  document.getElementById("cardOgRetail").innerText = `(₹${(ogPrice / 100).toFixed(1)}/kg)`;

  document.getElementById("selectedScenarioLabel").innerText = scenario.label;
  document.getElementById("cardSimPrice").innerText = `₹${simPrice.toLocaleString('en-IN')}`;
  document.getElementById("cardSimRetail").innerText = `(₹${(simPrice / 100).toFixed(1)}/kg)`;
  document.getElementById("cardSurgeTag").innerText = `+${displaySurgePct}% Surge`;

  document.getElementById("cardDeltaPrice").innerText = `+₹${deltaPrice.toLocaleString('en-IN')}`;
  document.getElementById("cardDeltaRetail").innerText = `(+₹${(deltaPrice / 100).toFixed(1)}/kg)`;

  document.getElementById("chartCropTitle").innerText = crop.name;

  // 2. Generate Dynamic Diagnostic Explanation
  const mitigationText = diversified 
    ? "Active <strong>Regional Sourcing Mitigation</strong> damped the price hike by 40% through cross-zone procurement."
    : "No sourcing diversification was applied, exposing the procurement budget to the full brunt of regional mandi shortages.";

  const explanationHTML = `Under <strong>${scenario.label}</strong> (${scenario.desc}), <strong>${crop.name}</strong> experiences a wholesale price surge of <strong>+${displaySurgePct}% (+₹${deltaPrice.toLocaleString('en-IN')}/quintal)</strong>. ${crop.notes} ${mitigationText}`;
  
  document.getElementById("explanationText").innerHTML = explanationHTML;

  // 3. Render 2-Bar Comparison Chart
  renderTwoBarChart(crop.name, scenario.label, ogPrice, simPrice);
}

function renderTwoBarChart(cropName, scenarioLabel, ogPrice, simPrice) {
  const ctx = document.getElementById("priceComparisonChart").getContext("2d");
  if (priceBarChartInstance) priceBarChartInstance.destroy();

  priceBarChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Original Price (Normal)", scenarioLabel],
      datasets: [{
        data: [ogPrice, simPrice],
        backgroundColor: ["#34d399", "#fbbf24"],
        borderRadius: 8,
        barThickness: 65
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { 
          grid: { display: false }, 
          ticks: { color: "#cbd5e1", font: { size: 13, weight: "bold" } } 
        },
        y: { 
          title: { display: true, text: "Modal Price (₹ / Quintal)", color: "#94a3b8" }, 
          grid: { color: "#1e293b" }, 
          ticks: { color: "#94a3b8" } 
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Price: ₹${ctx.parsed.y.toLocaleString('en-IN')} / Quintal (₹${(ctx.parsed.y / 100).toFixed(1)}/kg)`
          }
        }
      }
    }
  });
}

document.getElementById("runSimBtn").addEventListener("click", runSimulation);