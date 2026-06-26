import { imageProcessingModeInputs } from './dom.js';

export function setupAdvancedSettings({ onChange }) {
  imageProcessingModeInputs.forEach(input => {
    input.addEventListener('change', onChange);
  });
}

export function getImageProcessingMode() {
  const selectedInput = Array.from(imageProcessingModeInputs).find(input => input.checked);
  return selectedInput?.value || 'resized';
}
