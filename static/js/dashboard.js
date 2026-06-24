// ── Nacho HelpDesk Dashboard JS ──────────────────────────

// Animate bar fills on load
document.addEventListener('DOMContentLoaded', () => {
  // Bars start at 0 and animate to their target
  const fills = document.querySelectorAll('.bar-fill');
  fills.forEach(fill => {
    const target = fill.style.width;
    fill.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => { fill.style.width = target; }, 100);
    });
  });

  // Animate KPI numbers counting up
  document.querySelectorAll('.kpi-value').forEach(el => {
    const target = parseInt(el.textContent.replace('%',''), 10);
    const isPercent = el.textContent.includes('%');
    if (isNaN(target)) return;
    let current = 0;
    const step = Math.max(1, Math.floor(target / 30));
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current + (isPercent ? '%' : '');
      if (current >= target) clearInterval(timer);
    }, 30);
  });
});
