import { addKnownMeasureBtn, knownMeasuresList } from './dom.js';
import { formatNumber } from './format.js';

const KNOWN_MEASURE_OPTIONS = [
  { value: 'comprimento', label: 'Comprimento', unit: 'cm' },
  { value: 'largura', label: 'Largura', unit: 'cm' },
  { value: 'altura', label: 'Altura', unit: 'cm' },
  { value: 'peso', label: 'Peso', unit: 'kg' },
];

function getKnownMeasureOption(value) {
  return KNOWN_MEASURE_OPTIONS.find(option => option.value === value);
}

function getSelectedKnownMeasureTypes(exceptSelect = null) {
  return Array.from(knownMeasuresList.querySelectorAll('.known-measure-select'))
    .filter(select => select !== exceptSelect)
    .map(select => select.value)
    .filter(Boolean);
}

function updateKnownMeasureUnit(row) {
  const select = row.querySelector('.known-measure-select');
  const unit = row.querySelector('.measure-unit');
  const option = getKnownMeasureOption(select.value);
  unit.textContent = option?.unit || '';
}

function rebuildKnownMeasureSelects() {
  const selects = Array.from(knownMeasuresList.querySelectorAll('.known-measure-select'));

  selects.forEach(select => {
    const currentValue = select.value;
    const unavailableValues = getSelectedKnownMeasureTypes(select);
    const availableOptions = KNOWN_MEASURE_OPTIONS.filter(option => (
      option.value === currentValue || !unavailableValues.includes(option.value)
    ));

    select.innerHTML = availableOptions
      .map(option => `<option value="${option.value}">${option.label}</option>`)
      .join('');

    if (availableOptions.some(option => option.value === currentValue)) {
      select.value = currentValue;
    }

    updateKnownMeasureUnit(select.closest('.known-measure-row'));
  });

  addKnownMeasureBtn.disabled = selects.length >= KNOWN_MEASURE_OPTIONS.length;
}

function addKnownMeasureRow(onChange) {
  const selectedValues = getSelectedKnownMeasureTypes();
  const firstAvailableOption = KNOWN_MEASURE_OPTIONS.find(option => !selectedValues.includes(option.value));
  if (!firstAvailableOption) return;

  const row = document.createElement('div');
  row.className = 'known-measure-row';

  const select = document.createElement('select');
  select.className = 'known-measure-select';
  select.setAttribute('aria-label', 'Tipo da medida conhecida');
  select.innerHTML = `<option value="${firstAvailableOption.value}">${firstAvailableOption.label}</option>`;
  select.value = firstAvailableOption.value;

  const input = document.createElement('input');
  input.className = 'known-measure-value';
  input.type = 'number';
  input.min = '0';
  input.step = '0.01';
  input.placeholder = 'Valor';
  input.setAttribute('aria-label', 'Valor da medida conhecida');

  const unit = document.createElement('span');
  unit.className = 'measure-unit';

  const removeButton = document.createElement('button');
  removeButton.type = 'button';
  removeButton.className = 'remove-measure-btn';
  removeButton.textContent = 'x';
  removeButton.setAttribute('aria-label', 'Remover medida conhecida');

  select.addEventListener('change', () => {
    rebuildKnownMeasureSelects();
    onChange();
  });

  input.addEventListener('input', onChange);

  removeButton.addEventListener('click', () => {
    row.remove();
    rebuildKnownMeasureSelects();
    onChange();
  });

  row.append(select, input, unit, removeButton);
  knownMeasuresList.append(row);
  rebuildKnownMeasureSelects();
  input.focus();
}

export function setupKnownMeasures({ onChange }) {
  addKnownMeasureBtn.addEventListener('click', () => addKnownMeasureRow(onChange));
}

export function collectKnownMeasures() {
  return Array.from(knownMeasuresList.querySelectorAll('.known-measure-row'))
    .map(row => {
      const tipo = row.querySelector('.known-measure-select').value;
      const valor = Number(row.querySelector('.known-measure-value').value);
      return { tipo, valor };
    })
    .filter(item => item.tipo && Number.isFinite(item.valor) && item.valor > 0);
}

export function renderKnownMeasuresSummary(knownMeasures) {
  const entries = Object.entries(knownMeasures || {});
  if (!entries.length) return '';

  const items = entries
    .map(([type, value]) => {
      const option = getKnownMeasureOption(type);
      if (!option) return '';
      return `<span>${option.label}: ${formatNumber(value, 3)} ${option.unit}</span>`;
    })
    .filter(Boolean)
    .join('');

  if (!items) return '';
  return `<div class="known-measures-summary">${items}</div>`;
}
