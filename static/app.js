const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const previewWrap = document.getElementById('preview-wrap');
const previewImg = document.getElementById('preview-img');
const removeBtn = document.getElementById('remove-btn');
const description = document.getElementById('description');
const charNum = document.getElementById('char-num');
const form = document.getElementById('cubage-form');
const submitBtn = document.getElementById('submit-btn');
const spinner = document.getElementById('spinner');
const btnIcon = document.getElementById('btn-icon');
const btnLabel = document.getElementById('btn-label');
const result = document.getElementById('result');
const resultBody = document.getElementById('result-body');
const exportActions = document.getElementById('export-actions');
const exportJsonBtn = document.getElementById('export-json-btn');
const exportCsvBtn = document.getElementById('export-csv-btn');
const knownMeasuresList = document.getElementById('known-measures-list');
const addKnownMeasureBtn = document.getElementById('add-known-measure-btn');
const step3 = document.getElementById('step-3');

let hasFile = false;
let latestPayload = null;

const KNOWN_MEASURE_OPTIONS = [
  { value: 'comprimento', label: 'Comprimento', unit: 'cm' },
  { value: 'largura', label: 'Largura', unit: 'cm' },
  { value: 'altura', label: 'Altura', unit: 'cm' },
  { value: 'peso', label: 'Peso', unit: 'kg' },
];

function updateSubmit() {
  const hasText = description.value.trim().length > 0;
  submitBtn.disabled = !(hasFile && hasText);
}

function resetExport() {
  latestPayload = null;
  exportActions.hidden = true;
}

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

function addKnownMeasureRow() {
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
    resetExport();
  });

  input.addEventListener('input', resetExport);

  removeButton.addEventListener('click', () => {
    row.remove();
    rebuildKnownMeasureSelects();
    resetExport();
  });

  row.append(select, input, unit, removeButton);
  knownMeasuresList.append(row);
  rebuildKnownMeasureSelects();
  input.focus();
}

function collectKnownMeasures() {
  return Array.from(knownMeasuresList.querySelectorAll('.known-measure-row'))
    .map(row => {
      const tipo = row.querySelector('.known-measure-select').value;
      const valor = Number(row.querySelector('.known-measure-value').value);
      return { tipo, valor };
    })
    .filter(item => item.tipo && Number.isFinite(item.valor) && item.valor > 0);
}

function renderKnownMeasuresSummary(knownMeasures) {
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

addKnownMeasureBtn.addEventListener('click', addKnownMeasureRow);

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    previewWrap.style.display = 'block';
    dropzone.style.display = 'none';
    hasFile = true;
    resetExport();
    updateSubmit();
  };
  reader.readAsDataURL(file);
}

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showPreview(fileInput.files[0]);
});

removeBtn.addEventListener('click', () => {
  previewImg.src = '';
  previewWrap.style.display = 'none';
  dropzone.style.display = 'block';
  fileInput.value = '';
  hasFile = false;
  resetExport();
  updateSubmit();
});

dropzone.addEventListener('dragover', e => {
  e.preventDefault();
  dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('drag-over');
});

dropzone.addEventListener('drop', e => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    fileInput.files = e.dataTransfer.files;
    showPreview(file);
  }
});

description.addEventListener('input', () => {
  charNum.textContent = description.value.length;
  updateSubmit();
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading || !(hasFile && description.value.trim().length > 0);
  spinner.style.display = isLoading ? 'block' : 'none';
  btnIcon.style.display = isLoading ? 'none' : 'block';
  btnLabel.textContent = isLoading ? 'Analisando...' : 'Analisar produto';
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatNumber(value, maximumFractionDigits = 2) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits }).format(value);
}

function formatRange(range, unit, maximumFractionDigits = 2) {
  if (!range) return '—';
  const estimate = formatNumber(range.estimativa, maximumFractionDigits);
  const min = formatNumber(range.min, maximumFractionDigits);
  const max = formatNumber(range.max, maximumFractionDigits);
  return `${estimate} ${unit} <small>(${min}–${max} ${unit})</small>`;
}

function metric(label, value) {
  return `
    <div class="metric">
      <div class="metric-label">${escapeHtml(label)}</div>
      <div class="metric-value">${value}</div>
    </div>
  `;
}

function renderResult(payload) {
  const resposta = payload.resposta || {};
  const produto = resposta.produto || {};
  const dimensoes = produto.dimensoes_estimadas_cm || {};
  const peso = produto.peso_estimado_kg || {};
  const metricas = payload.metricas_logisticas || {};
  const validacao = payload.validacao || { status: false, erros: [], alertas: [] };
  const confidence = resposta.nivel_confianca === 'alto' ? 'alto' : 'baixo';

  const validationItems = [...(validacao.erros || []), ...(validacao.alertas || [])]
    .map(item => `<li>${escapeHtml(item)}</li>`)
    .join('');

  latestPayload = payload;
  exportActions.hidden = false;
  result.classList.remove('error');
  resultBody.innerHTML = `
    <div class="result-summary">
      <div class="result-name">${escapeHtml(resposta.produto_identificado || 'Produto identificado')}</div>
      <div class="result-description">${escapeHtml(resposta.descricao_resumida || '')}</div>
      ${renderKnownMeasuresSummary(payload.medidas_conhecidas_informadas)}
      <span class="confidence ${confidence === 'baixo' ? 'low' : ''}">Confiança ${confidence}</span>
      <div class="result-grid">
        ${metric('Comprimento', formatRange(dimensoes.comprimento, 'cm'))}
        ${metric('Largura', formatRange(dimensoes.largura, 'cm'))}
        ${metric('Altura', formatRange(dimensoes.altura, 'cm'))}
        ${metric('Peso estimado', formatRange(peso, 'kg', 3))}
        ${metric('Peso cubado', `${formatNumber(metricas.peso_cubado_kg, 2)} kg`)}
        ${metric('Peso cobrável', `${formatNumber(metricas.peso_cobravel_estimado_kg, 2)} kg`)}
      </div>
      ${validationItems ? `<ul class="validation-list">${validationItems}</ul>` : ''}
    </div>
  `;
}

function renderError(message) {
  resetExport();
  result.classList.add('error');
  resultBody.innerHTML = escapeHtml(message);
}

function getExportBaseName() {
  const productName = latestPayload?.resposta?.produto_identificado || 'estimativa-produto';
  const safeProductName = productName
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/gi, '-')
    .replace(/^-|-$/g, '')
    .toLowerCase() || 'estimativa-produto';
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  return `${safeProductName}-${timestamp}`;
}

function downloadBlob(content, type, filename) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function csvEscape(value) {
  const text = String(value ?? '');
  return `"${text.replaceAll('"', '""')}"`;
}

function addRangeFields(data, prefix, range) {
  data[`${prefix}_min`] = range?.min ?? '';
  data[`${prefix}_estimativa`] = range?.estimativa ?? '';
  data[`${prefix}_max`] = range?.max ?? '';
}

function buildCsv(payload) {
  const resposta = payload.resposta || {};
  const produto = resposta.produto || {};
  const dimensoes = produto.dimensoes_estimadas_cm || {};
  const metricas = payload.metricas_logisticas || {};
  const validacao = payload.validacao || {};
  const knownMeasures = payload.medidas_conhecidas_informadas || {};
  const data = {
    produto_identificado: resposta.produto_identificado || '',
    descricao_resumida: resposta.descricao_resumida || '',
    nivel_confianca: resposta.nivel_confianca || '',
  };

  addRangeFields(data, 'comprimento_cm', dimensoes.comprimento);
  addRangeFields(data, 'largura_cm', dimensoes.largura);
  addRangeFields(data, 'altura_cm', dimensoes.altura);
  addRangeFields(data, 'peso_kg', produto.peso_estimado_kg);

  data.medida_conhecida_comprimento_cm = knownMeasures.comprimento ?? '';
  data.medida_conhecida_largura_cm = knownMeasures.largura ?? '';
  data.medida_conhecida_altura_cm = knownMeasures.altura ?? '';
  data.medida_conhecida_peso_kg = knownMeasures.peso ?? '';
  data.volume_produto_cm3 = metricas.volume_produto_cm3 ?? '';
  data.densidade_produto_kg_cm3 = metricas.densidade_produto_kg_cm3 ?? '';
  data.peso_cubado_kg = metricas.peso_cubado_kg ?? '';
  data.peso_cobravel_estimado_kg = metricas.peso_cobravel_estimado_kg ?? '';
  data.fator_cubagem = metricas.fator_cubagem ?? '';
  data.validacao_status = validacao.status ?? '';
  data.validacao_erros = (validacao.erros || []).join(' | ');
  data.validacao_alertas = (validacao.alertas || []).join(' | ');

  const headers = Object.keys(data);
  const values = headers.map(header => csvEscape(data[header]));
  return `${headers.join(',')}\n${values.join(',')}\n`;
}

exportJsonBtn.addEventListener('click', () => {
  if (!latestPayload) return;
  downloadBlob(
    JSON.stringify(latestPayload, null, 2),
    'application/json;charset=utf-8',
    `${getExportBaseName()}.json`,
  );
});

exportCsvBtn.addEventListener('click', () => {
  if (!latestPayload) return;
  downloadBlob(
    buildCsv(latestPayload),
    'text/csv;charset=utf-8',
    `${getExportBaseName()}.csv`,
  );
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  if (submitBtn.disabled) return;

  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  const knownMeasures = collectKnownMeasures();
  formData.append('image', file);
  formData.append('description', description.value.trim());
  formData.append('known_measures', JSON.stringify(knownMeasures));

  setLoading(true);
  resetExport();
  result.style.display = 'none';

  try {
    const response = await fetch('/estimate', {
      method: 'POST',
      body: formData,
    });

    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(payload?.detail || 'Não foi possível analisar o produto.');
    }

    step3.classList.add('active');
    step3.querySelector('.step-num').style.background = 'var(--green)';
    step3.querySelector('.step-num').style.color = '#fff';

    renderResult(payload);
  } catch (error) {
    renderError(error.message || 'Erro inesperado ao analisar o produto.');
  } finally {
    result.style.display = 'block';
    setLoading(false);
  }
});
