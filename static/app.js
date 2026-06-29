import {
  btnIcon,
  btnLabel,
  charNum,
  description,
  fileInput,
  form,
  result,
  spinner,
  step3,
  submitBtn,
} from './js/dom.js';
import { resetExport, setExportPayload, setupExportActions } from './js/exportResults.js';
import { collectKnownMeasures, setupKnownMeasures } from './js/knownMeasures.js';
import { renderError, renderResult } from './js/render.js';
import { getCubageFactor, getImageProcessingMode, getSelectedModel, setupAdvancedSettings } from './js/settings.js';
import { setupUpload } from './js/upload.js';

let hasFile = false;

function updateSubmit() {
  const hasText = description.value.trim().length > 0;
  submitBtn.disabled = !(hasFile && hasText);
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading || !(hasFile && description.value.trim().length > 0);
  spinner.style.display = isLoading ? 'block' : 'none';
  btnIcon.style.display = isLoading ? 'none' : 'block';
  btnLabel.textContent = isLoading ? 'Analisando...' : 'Analisar produto';
}

setupUpload({
  onFileChange(fileIsSelected) {
    hasFile = fileIsSelected;
    resetExport();
    updateSubmit();
  },
});

setupKnownMeasures({
  onChange() {
    resetExport();
  },
});

setupExportActions();

setupAdvancedSettings({
  onChange() {
    resetExport();
  },
});

description.addEventListener('input', () => {
  charNum.textContent = description.value.length;
  updateSubmit();
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
  formData.append('image_processing_mode', getImageProcessingMode());
  formData.append('model', getSelectedModel());
  formData.append('cubage_factor', getCubageFactor());

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

    setExportPayload(payload);
    renderResult(payload);
  } catch (error) {
    resetExport();
    renderError(error.message || 'Erro inesperado ao analisar o produto.');
  } finally {
    result.style.display = 'block';
    setLoading(false);
  }
});
