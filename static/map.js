// map.js — Leaflet map logic for EcoStress Index

let map;
let neighborhoodLayers = [];
let currentNeighborhood = null;

// Auth guard
const token = localStorage.getItem("esi_token");
if (!token) window.location.href = "/";

function getToken() {
  return localStorage.getItem("esi_token");
}

// Init map on load
document.addEventListener("DOMContentLoaded", () => {
  map = L.map("map").setView([32.2226, -110.9747], 11); // Default: Tucson

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 19,
  }).addTo(map);

  // Sign out
  document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("esi_token");
    window.location.href = "/";
  });

  // Close side panel
  document.getElementById("close-panel").addEventListener("click", () => {
    document.getElementById("side-panel").classList.add("hidden");
  });

  // Default load: Tucson
  searchCity("Tucson, AZ");
});

// Color scale: green (0) → yellow (0.5) → red (1)
function esiToColor(score) {
  const r = Math.round(255 * score);
  const g = Math.round(255 * (1 - score));
  return `rgb(${r}, ${g}, 0)`;
}

async function searchCity(query) {
  showLoading(true);
  clearLayers();

  try {
    const res = await fetch(`/api/city?name=${encodeURIComponent(query)}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    if (res.status === 401) {
      localStorage.removeItem("esi_token");
      window.location.href = "/";
      return;
    }

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    renderNeighborhoods(data.neighborhoods);
    showWeightsPanel(data.weights, data.gemini_reasoning, data.city);
    logSearch(query, data.city);
  } catch (err) {
    console.error("City search failed:", err);
    alert("Failed to load city data. Please try again.");
  } finally {
    showLoading(false);
  }
}

function renderNeighborhoods(neighborhoods) {
  neighborhoods.forEach((n) => {
    // If real GeoJSON available, use it; otherwise render a placeholder circle
    if (n.geojson) {
      const layer = L.geoJSON(n.geojson, {
        style: {
          fillColor: esiToColor(n.esi_score),
          fillOpacity: 0.6,
          color: "#333",
          weight: 1,
        },
      })
        .bindTooltip(`<b>${n.name}</b><br>ESI: ${n.esi_score.toFixed(2)}`)
        .on("click", () => openSidePanel(n))
        .addTo(map);
      neighborhoodLayers.push(layer);
    } else {
      // Fallback: colored markers
      const marker = L.circleMarker(getNeighborhoodLatLng(n.name), {
        radius: 18,
        fillColor: esiToColor(n.esi_score),
        fillOpacity: 0.75,
        color: "#333",
        weight: 1.5,
      })
        .bindTooltip(`<b>${n.name}</b><br>ESI: ${n.esi_score.toFixed(2)}`)
        .on("click", () => openSidePanel(n))
        .addTo(map);
      neighborhoodLayers.push(marker);
    }
  });
}

// Rough lat/lng for Tucson neighborhoods (fallback when no GeoJSON)
const TUCSON_COORDS = {
  Downtown:        [32.2219, -110.9695],
  "University Area": [32.2315, -110.9490],
  Foothills:       [32.3500, -110.9200],
  "South Side":    [32.1800, -110.9700],
  Midtown:         [32.2400, -110.9600],
  "Rincon Heights":[32.2100, -110.9150],
};

function getNeighborhoodLatLng(name) {
  return TUCSON_COORDS[name] || [32.2226, -110.9747];
}

function clearLayers() {
  neighborhoodLayers.forEach((l) => map.removeLayer(l));
  neighborhoodLayers = [];
}

function openSidePanel(neighborhood) {
  currentNeighborhood = neighborhood;
  const panel = document.getElementById("side-panel");

  document.getElementById("panel-name").textContent = neighborhood.name;
  document.getElementById("panel-esi").textContent = neighborhood.esi_score.toFixed(2);
  document.getElementById("panel-price").textContent =
    `$${neighborhood.dynamic_price_per_kwh}/kWh`;

  // Gauge bar
  const fill = document.getElementById("gauge-fill");
  fill.style.width = `${(neighborhood.esi_score * 100).toFixed(0)}%`;
  fill.style.background = esiToColor(neighborhood.esi_score);

  // Component bars
  setComponentBar("aq", neighborhood.components.air_quality);
  setComponentBar("lp", neighborhood.components.light_pollution);
  setComponentBar("hi", neighborhood.components.heat_island);
  setComponentBar("eu", neighborhood.components.energy_use);

  // Reset async fields
  document.getElementById("panel-explanation").textContent = "Loading...";
  document.getElementById("baseline").textContent = "--";
  document.getElementById("projected").textContent = "--";
  document.getElementById("reduction").textContent = "--";
  document.getElementById("sim-insight").textContent = "";

  panel.classList.remove("hidden");

  // Load neighborhood detail (explanation + simulation)
  loadNeighborhoodDetail(neighborhood);
}

function setComponentBar(id, value) {
  const bar = document.getElementById(`bar-${id}`);
  const val = document.getElementById(`val-${id}`);
  bar.style.width = `${(value * 100).toFixed(0)}%`;
  bar.style.background = esiToColor(value);
  val.textContent = value.toFixed(2);
}

async function loadNeighborhoodDetail(neighborhood) {
  const cityQuery = document.getElementById("city-search").value || "Tucson, AZ";

  // Fetch explanation
  try {
    const res = await fetch(
      `/api/neighborhood?city=${encodeURIComponent(cityQuery)}&n=${encodeURIComponent(neighborhood.name)}`,
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    const data = await res.json();
    document.getElementById("panel-explanation").textContent =
      data.gemini_explanation || "No explanation available.";
  } catch {
    document.getElementById("panel-explanation").textContent = "Could not load explanation.";
  }

  // Fetch simulation
  loadSimulation(cityQuery, neighborhood.name);
}

async function loadSimulation(city, neighborhoodName) {
  try {
    const res = await fetch(
      `/api/simulate?city=${encodeURIComponent(city)}&neighborhood=${encodeURIComponent(neighborhoodName)}`,
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    const data = await res.json();
    document.getElementById("baseline").textContent = data.baseline_kwh?.toLocaleString() ?? "--";
    document.getElementById("projected").textContent = data.projected_kwh?.toLocaleString() ?? "--";
    document.getElementById("reduction").textContent = data.reduction_pct ?? "--";
    document.getElementById("sim-insight").textContent = data.gemini_insight ?? "";
  } catch {
    document.getElementById("sim-insight").textContent = "Simulation unavailable.";
  }
}

function showWeightsPanel(weights, reasoning, city) {
  const panel = document.getElementById("weights-panel");
  document.getElementById("weights-city").textContent = city;
  document.getElementById("weights-reasoning").textContent = reasoning;

  const barsEl = document.getElementById("weights-bars");
  barsEl.innerHTML = "";
  const labels = {
    air_quality: "Air Quality",
    light_pollution: "Light Pollution",
    heat_island: "Heat Island",
    energy_use: "Energy Use",
  };
  Object.entries(weights).forEach(([key, val]) => {
    const pct = (val * 100).toFixed(0);
    barsEl.innerHTML += `
      <div class="weight-row">
        <span>${labels[key] || key}</span>
        <div class="weight-bar-wrap">
          <div class="weight-bar" style="width:${pct}%"></div>
        </div>
        <span>${pct}%</span>
      </div>`;
  });
  panel.classList.remove("hidden");
}

async function logSearch(query, city) {
  try {
    await fetch("/api/search-log", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, city }),
    });
  } catch {
    // Non-critical — ignore failures
  }
}

function showLoading(visible) {
  document.getElementById("loading").classList.toggle("hidden", !visible);
}
