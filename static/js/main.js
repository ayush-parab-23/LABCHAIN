/**
 * LABCHAIN — Core Frontend Interaction Script
 * Clinical Teal Design System
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initCopyButtons();
  initSegmentedControls();
});

/**
 * Initializes Theme Switcher (Light / Dark)
 */
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle');
  if (!toggleBtn) return;

  toggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', nextTheme);
    try {
      localStorage.setItem('labchain-theme', nextTheme);
    } catch (e) {
      console.warn('localStorage not accessible:', e);
    }

    // Dispatch event so Chart.js and dynamic widgets can re-theme
    window.dispatchEvent(new CustomEvent('labchain-theme-changed', { detail: { theme: nextTheme } }));
  });
}

/**
 * Copy-to-clipboard functionality with inline icon feedback
 */
function initCopyButtons() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.hash-copy-btn, .btn-copy');
    if (!btn) return;

    e.preventDefault();
    let textToCopy = btn.getAttribute('data-copy-text');
    const targetId = btn.getAttribute('data-copy-target');

    if (!textToCopy && targetId) {
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        textToCopy = targetEl.innerText || targetEl.value;
      }
    }

    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy.trim()).then(() => {
        const copyIcon = btn.querySelector('.copy-icon');
        const copiedIcon = btn.querySelector('.copied-icon');
        
        if (copyIcon && copiedIcon) {
          copyIcon.style.display = 'none';
          copiedIcon.style.display = 'inline';
          setTimeout(() => {
            copyIcon.style.display = 'inline';
            copiedIcon.style.display = 'none';
          }, 1500);
        } else {
          const originalText = btn.innerText;
          btn.innerText = 'Copied';
          setTimeout(() => {
            btn.innerText = originalText;
          }, 1500);
        }
      }).catch(err => {
        console.error('Failed to copy text: ', err);
      });
    }
  });
}

/**
 * Accessible Segmented Controls (Tabs)
 */
function initSegmentedControls() {
  const controls = document.querySelectorAll('.segmented-control');
  controls.forEach(ctrl => {
    const buttons = ctrl.querySelectorAll('.segmented-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        if (!targetId) return;

        // Toggle button states
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Toggle pane visibility
        const container = ctrl.closest('.segmented-wrapper') || document;
        const panes = container.querySelectorAll('.tab-pane');
        panes.forEach(pane => {
          if (pane.id === targetId) {
            pane.classList.add('active');
          } else {
            pane.classList.remove('active');
          }
        });
      });
    });
  });
}
