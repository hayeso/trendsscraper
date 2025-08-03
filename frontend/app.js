/*
 * Minimal frontend module to request backend trends comparison.
 */

async function fetchTrendsCompare(payload) {
  const res = await fetch('/api/trends/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error('Backend request failed');
  }
  return res.json();
}

export async function runAnalysis(master, competitors, options = {}) {
  const payload = {
    master,
    competitors,
    anchor: options.anchor || 'car insurance',
    timeframe: options.timeframe || 'today 3-m',
    geo: options.geo || 'IE',
    category: options.category || null,
    gprop: options.gprop || '',
  };
  return fetchTrendsCompare(payload);
}
