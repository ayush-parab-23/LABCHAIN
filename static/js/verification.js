/**
 * LABCHAIN — Document Upload & Verification UI Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  setupDragAndDrop();
  setupSubmitLoading();
});

/**
 * Handles accessible drag-and-drop for PDF file selection
 */
function setupDragAndDrop() {
  const dropZones = document.querySelectorAll('.upload-drag-zone');

  dropZones.forEach(zone => {
    const inputId = zone.getAttribute('data-input-id');
    const fileInput = document.getElementById(inputId);
    if (!fileInput) return;

    zone.addEventListener('dragover', (e) => {
      e.preventDefault();
      zone.classList.add('drag-active');
    });

    zone.addEventListener('dragleave', () => {
      zone.classList.remove('drag-active');
    });

    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('drag-active');

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        fileInput.files = files;
        updateFileFeedback(zone, files[0].name, files[0].size);
      }
    });

    zone.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files.length > 0) {
        updateFileFeedback(zone, fileInput.files[0].name, fileInput.files[0].size);
      }
    });
  });
}

function updateFileFeedback(zone, filename, bytes) {
  const textEl = zone.querySelector('.drag-zone-text');
  const hintEl = zone.querySelector('.drag-zone-hint');

  const formattedSize = bytes ? (bytes / 1024).toFixed(1) + ' KB' : '';

  if (textEl) {
    textEl.innerHTML = `<strong>Selected:</strong> <code style="font-family: var(--font-mono);">${filename}</code> ${formattedSize ? '(' + formattedSize + ')' : ''}`;
  }
  if (hintEl) {
    hintEl.innerText = 'Click or drag another PDF to replace file';
  }
}

/**
 * Prevents double-submission and displays quiet processing state
 */
function setupSubmitLoading() {
  const forms = document.querySelectorAll('.form-loading-trigger');

  forms.forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.innerText = 'Processing on ledger...';
      }
    });
  });
}
