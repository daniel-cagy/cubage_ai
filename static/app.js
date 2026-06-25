const dropzone    = document.getElementById('dropzone');
    const fileInput   = document.getElementById('file-input');
    const previewWrap = document.getElementById('preview-wrap');
    const previewImg  = document.getElementById('preview-img');
    const removeBtn   = document.getElementById('remove-btn');
    const description = document.getElementById('description');
    const charNum     = document.getElementById('char-num');
    const form        = document.getElementById('cubage-form');
    const submitBtn   = document.getElementById('submit-btn');
    const spinner     = document.getElementById('spinner');
    const btnIcon     = document.getElementById('btn-icon');
    const btnLabel    = document.getElementById('btn-label');
    const result      = document.getElementById('result');
    const resultBody  = document.getElementById('result-body');
    const step3       = document.getElementById('step-3');

    let hasFile = false;

    function updateSubmit() {
      const hasText = description.value.trim().length > 0;
      submitBtn.disabled = !(hasFile && hasText);
    }

    function showPreview(file) {
      const reader = new FileReader();
      reader.onload = e => {
        previewImg.src = e.target.result;
        previewWrap.style.display = 'block';
        dropzone.style.display = 'none';
        hasFile = true;
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
      result.classList.add('error');
      resultBody.innerHTML = escapeHtml(message);
    }

    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (submitBtn.disabled) return;

      const file = fileInput.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('image', file);
      formData.append('description', description.value.trim());

      setLoading(true);
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
