import { advancedSettings, imageProcessingModeInputs } from './dom.js';

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

export function setupAdvancedSettings({ onChange }) {
  imageProcessingModeInputs.forEach(input => {
    input.addEventListener('change', onChange);
  });

  animateAdvancedSettings();
}

export function getImageProcessingMode() {
  const selectedInput = Array.from(imageProcessingModeInputs).find(input => input.checked);
  return selectedInput?.value || 'resized';
}
