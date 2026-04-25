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
});
