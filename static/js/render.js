import { result, resultBody } from './dom.js';
import { escapeHtml, formatNumber, formatRange, metric } from './format.js';
import { renderKnownMeasuresSummary } from './knownMeasures.js';

export function renderResult(payload) {
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

export function renderError(message) {
  result.classList.add('error');
  resultBody.innerHTML = escapeHtml(message);
}
