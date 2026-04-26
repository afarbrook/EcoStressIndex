// change to our custom domain
const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5000';

function authHeaders() {
  const token = localStorage.getItem('esi_token');
  return { Authorization: `Bearer ${token}` };
}

export async function fetchCity(name) {
  const res = await fetch(`${BASE}/api/city?name=${encodeURIComponent(name)}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('City fetch failed');
  return res.json();
}

export async function fetchNeighborhood(city, name) {
  const res = await fetch(
    `${BASE}/api/neighborhood?city=${encodeURIComponent(city)}&n=${encodeURIComponent(name)}`,
    { headers: authHeaders() }
  );
  if (!res.ok) throw new Error('Neighborhood fetch failed');
  return res.json();
}

export async function fetchSimulation(city, neighborhood) {
  const res = await fetch(
    `${BASE}/api/simulate?city=${encodeURIComponent(city)}&neighborhood=${encodeURIComponent(neighborhood)}`,
    { headers: authHeaders() }
  );
  if (!res.ok) throw new Error('Simulation fetch failed');
  return res.json();
}

export async function logSearch(query, city) {
  fetch(`${BASE}/api/search-log`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, city }),
  }).catch(() => {});
}
