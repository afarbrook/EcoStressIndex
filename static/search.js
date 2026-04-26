// search.js — City search bar wiring

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("city-search");
  const btn = document.getElementById("search-btn");

  btn.addEventListener("click", () => {
    const query = input.value.trim();
    if (query) searchCity(query);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const query = input.value.trim();
      if (query) searchCity(query);
    }
  });

  // Re-search with new rate when the base rate input changes
  let rateTimer;
  document.getElementById("base-rate").addEventListener("change", () => {
    clearTimeout(rateTimer);
    rateTimer = setTimeout(() => {
      const query = input.value.trim();
      if (query) searchCity(query);
    }, 400);
  });
});
