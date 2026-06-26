export function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

export function formatNumber(value, maximumFractionDigits = 2) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits }).format(value);
}

export function formatRange(range, unit, maximumFractionDigits = 2) {
  if (!range) return '—';
  const estimate = formatNumber(range.estimativa, maximumFractionDigits);
  const min = formatNumber(range.min, maximumFractionDigits);
  const max = formatNumber(range.max, maximumFractionDigits);
  return `${estimate} ${unit} <small>(${min}–${max} ${unit})</small>`;
}

export function metric(label, value) {
  return `
    <div class="metric">
      <div class="metric-label">${escapeHtml(label)}</div>
      <div class="metric-value">${value}</div>
    </div>
  `;
}
