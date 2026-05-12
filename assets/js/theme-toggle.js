// Dark/light theme toggle. Persists the choice to localStorage.
// Initial theme detection runs inline in <head> (see head.html) to avoid a
// flash of the wrong theme on load.
(function () {
  const btn = document.querySelector('.theme-toggle');
  if (!btn) return;

  function syncAria() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    btn.setAttribute('aria-pressed', String(isDark));
    btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
  }
  syncAria();

  btn.addEventListener('click', function () {
    const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    if (next === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    try { localStorage.setItem('mc-theme', next); } catch (e) {}
    syncAria();
  });
})();
