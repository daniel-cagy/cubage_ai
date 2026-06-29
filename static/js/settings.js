import { advancedSettings, cubageFactorInput, cubageFactorPreset, imageProcessingModeInputs, modelInput, modelPreset } from './dom.js';

const ANIMATION_DURATION = 220;
const ANIMATION_EASING = 'ease';
let currentAnimation = null;

function animateAdvancedSettings() {
  if (!advancedSettings) return;

  const summary = advancedSettings.querySelector('summary');
  if (!summary) return;

  summary.addEventListener('click', event => {
    event.preventDefault();

    if (currentAnimation) {
      currentAnimation.cancel();
    }

    const startHeight = `${advancedSettings.offsetHeight}px`;

    if (advancedSettings.open) {
      const endHeight = `${summary.offsetHeight}px`;
      currentAnimation = advancedSettings.animate(
        { height: [startHeight, endHeight] },
        { duration: ANIMATION_DURATION, easing: ANIMATION_EASING },
      );

      currentAnimation.onfinish = () => {
        advancedSettings.open = false;
        advancedSettings.style.height = '';
        currentAnimation = null;
      };
      return;
    }

    advancedSettings.open = true;
    const endHeight = `${advancedSettings.scrollHeight}px`;
    currentAnimation = advancedSettings.animate(
      { height: [startHeight, endHeight] },
      { duration: ANIMATION_DURATION, easing: ANIMATION_EASING },
    );

    currentAnimation.onfinish = () => {
      advancedSettings.style.height = '';
      currentAnimation = null;
    };
  });
}

function syncModelPresetFromInput() {
  if (!modelInput || !modelPreset) return;

  const typedModel = modelInput.value.trim();
  const matchingOption = Array.from(modelPreset.options).find(option => option.value === typedModel);
  modelPreset.value = matchingOption ? typedModel : 'custom';
}

function syncCubageFactorPresetFromInput() {
  if (!cubageFactorInput || !cubageFactorPreset) return;

  const typedFactor = cubageFactorInput.value.trim();
  const matchingOption = Array.from(cubageFactorPreset.options).find(option => option.value === typedFactor);
  cubageFactorPreset.value = matchingOption ? typedFactor : 'custom';
}

export function setupAdvancedSettings({ onChange }) {
  imageProcessingModeInputs.forEach(input => {
    input.addEventListener('change', onChange);
  });

  if (modelPreset && modelInput) {
    modelPreset.addEventListener('change', () => {
      if (modelPreset.value !== 'custom') {
        modelInput.value = modelPreset.value;
      }
      onChange();
    });

    modelInput.addEventListener('input', () => {
      syncModelPresetFromInput();
      onChange();
    });

    syncModelPresetFromInput();
  }

  if (cubageFactorPreset && cubageFactorInput) {
    cubageFactorPreset.addEventListener('change', () => {
      if (cubageFactorPreset.value !== 'custom') {
        cubageFactorInput.value = cubageFactorPreset.value;
      }
      onChange();
    });

    cubageFactorInput.addEventListener('input', () => {
      syncCubageFactorPresetFromInput();
      onChange();
    });

    syncCubageFactorPresetFromInput();
  }

  animateAdvancedSettings();
}

export function getImageProcessingMode() {
  const selectedInput = Array.from(imageProcessingModeInputs).find(input => input.checked);
  return selectedInput?.value || 'quantized';
}

export function getSelectedModel() {
  return modelInput?.value.trim() || 'gpt-5.4-mini';
}

export function getCubageFactor() {
  return cubageFactorInput?.value.trim() || '6000';
}
