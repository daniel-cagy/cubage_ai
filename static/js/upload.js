import { dropzone, fileInput, previewImg, previewWrap, removeBtn } from './dom.js';

function showPreview(file, onFileChange) {
  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    previewWrap.style.display = 'block';
    dropzone.style.display = 'none';
    onFileChange(true);
  };
  reader.readAsDataURL(file);
}

export function setupUpload({ onFileChange }) {
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) showPreview(fileInput.files[0], onFileChange);
  });

  removeBtn.addEventListener('click', () => {
    previewImg.src = '';
    previewWrap.style.display = 'none';
    dropzone.style.display = 'block';
    fileInput.value = '';
    onFileChange(false);
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
      showPreview(file, onFileChange);
    }
  });
}
