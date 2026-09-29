/**
 * LABCHAIN — Laboratory Analytics & Chart.js Integration
 * Dynamically styled with CSS Design Tokens
 */

let charts = {};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('testTypesChart')) {
    renderAllAnalytics();

    // Re-render when theme switches so charts instantly adopt token colors
    window.addEventListener('labchain-theme-changed', () => {
      destroyAllCharts();
      renderAllAnalytics();
    });
  }
});

function getThemeColors() {
  const root = getComputedStyle(document.documentElement);
  return {
    primary: root.getPropertyValue('--primary').trim(),
    primarySoft: root.getPropertyValue('--primary-soft').trim(),
    surface2: root.getPropertyValue('--surface-2').trim(),
    border: root.getPropertyValue('--border').trim(),
    text: root.getPropertyValue('--text').trim(),
    textMuted: root.getPropertyValue('--text-muted').trim(),
    success: root.getPropertyValue('--success').trim(),
    danger: root.getPropertyValue('--danger').trim(),
    accent: root.getPropertyValue('--accent').trim()
  };
}

function destroyAllCharts() {
  Object.keys(charts).forEach(key => {
    if (charts[key]) {
      charts[key].destroy();
    }
  });
  charts = {};
}

function renderAllAnalytics() {
  const c = getThemeColors();

  // Common font styling for Chart.js
  Chart.defaults.font.family = '"IBM Plex Sans", system-ui, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.color = c.textMuted;

  // 1. Summary Stats
  fetch('/api/analytics/summary')
    .then(r => r.json())
    .then(stats => {
      setText('stat-total', stats.total_reports);
      setText('stat-active', stats.active_reports);
      setText('stat-superseded', stats.superseded_reports);
      setText('stat-revoked', stats.revoked_reports);
      setText('stat-verified', stats.verified_count);
      setText('stat-failed', stats.failed_count);

      const alertEl = document.getElementById('anomaly-alert');
      if (alertEl) {
        if (stats.is_anomaly) {
          alertEl.style.display = 'flex';
          const msg = document.getElementById('anomaly-details');
          if (msg) {
            msg.innerText = `Observed ${stats.recent_hour_verifications} verification requests in the last hour.`;
          }
        } else {
          alertEl.style.display = 'none';
        }
      }
    })
    .catch(e => console.error('Summary error:', e));

  // 2. Test Types (Horizontal/Vertical Bar)
  fetch('/api/analytics/test_types')
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById('testTypesChart');
      if (!el) return;
      const ctx = el.getContext('2d');
      charts.testTypes = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Reports',
            data: data.data,
            backgroundColor: c.primary,
            borderRadius: 4,
            borderSkipped: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: c.textMuted }
            },
            y: {
              grid: { color: c.border },
              ticks: { stepSize: 1, color: c.textMuted },
              beginAtZero: true
            }
          }
        }
      });
    });

  // 3. Verification Ratio (Donut)
  fetch('/api/analytics/verification_ratio')
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById('verificationRatioChart');
      if (!el) return;
      const ctx = el.getContext('2d');
      charts.ratio = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.labels,
          datasets: [{
            data: data.data,
            backgroundColor: [c.success, c.danger],
            borderWidth: 1,
            borderColor: c.border
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { boxWidth: 12, padding: 14, color: c.text }
            }
          }
        }
      });
    });

  // 4. Monthly Trends (Line)
  fetch('/api/analytics/monthly_trends')
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById('monthlyTrendsChart');
      if (!el) return;
      const ctx = el.getContext('2d');
      charts.monthly = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Registrations',
            data: data.data,
            borderColor: c.primary,
            backgroundColor: c.primarySoft,
            fill: true,
            tension: 0.2,
            borderWidth: 2,
            pointBackgroundColor: c.primary,
            pointRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: c.textMuted } },
            y: {
              grid: { color: c.border },
              ticks: { stepSize: 1, color: c.textMuted },
              beginAtZero: true
            }
          }
        }
      });
    });

  // 5. 7-Day Activity
  fetch('/api/analytics/activity_log')
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById('activityChart');
      if (!el) return;
      const ctx = el.getContext('2d');
      charts.activity = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [
            {
              label: 'Verified',
              data: data.success,
              borderColor: c.success,
              backgroundColor: 'transparent',
              tension: 0.2,
              borderWidth: 2,
              pointRadius: 3
            },
            {
              label: 'Failed',
              data: data.failure,
              borderColor: c.danger,
              backgroundColor: 'transparent',
              borderDash: [4, 4],
              tension: 0.2,
              borderWidth: 2,
              pointRadius: 3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { boxWidth: 12, padding: 14, color: c.text }
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: c.textMuted } },
            y: {
              grid: { color: c.border },
              ticks: { stepSize: 1, color: c.textMuted },
              beginAtZero: true
            }
          }
        }
      });
    });
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.innerText = val !== undefined ? val : '-';
}
