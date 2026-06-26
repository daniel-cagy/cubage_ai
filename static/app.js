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
const step3 = document.getElementById('step-3');

let hasFile = false;
let latestPayload = null;

function updateSubmit() {
  const hasText = description.value.trim().length > 0;
  submitBtn.disabled = !(hasFile && hasText);
}

function resetExport() {
  latestPayload = null;
  exportActions.hidden = true;
}

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
  const data = {
    produto_identificado: resposta.produto_identificado || '',
    descricao_resumida: resposta.descricao_resumida || '',
    nivel_confianca: resposta.nivel_confianca || '',
  };

  addRangeFields(data, 'comprimento_cm', dimensoes.comprimento);
  addRangeFields(data, 'largura_cm', dimensoes.largura);
  addRangeFields(data, 'altura_cm', dimensoes.altura);
  addRangeFields(data, 'peso_kg', produto.peso_estimado_kg);

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
  formData.append('image', file);
  formData.append('description', description.value.trim());

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
