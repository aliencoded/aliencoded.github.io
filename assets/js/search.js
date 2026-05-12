// Client-side article search.
// Index is generated at build time at /search.json — fetched lazily on first open.
// Initial state: 5 most recent articles. As the user types, filter title + excerpt + categories.
(function () {
  const trigger = document.querySelector('.search-trigger');
  const overlay = document.getElementById('search-overlay');
  const input = document.getElementById('search-input');
  const close = document.getElementById('search-close');
  const resultsEl = document.getElementById('search-results');
  if (!trigger || !overlay || !input || !close || !resultsEl) return;

  let articles = null;
  let loading = null;

  function ensureLoaded() {
    if (articles) return Promise.resolve(articles);
    if (loading) return loading;
    loading = fetch('/search.json')
      .then(function (r) { return r.json(); })
      .then(function (data) { articles = data; return data; })
      .catch(function () { articles = []; return []; });
    return loading;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function render(query) {
    if (!articles) {
      resultsEl.innerHTML = '<p class="search-empty">Loading…</p>';
      return;
    }
    let items;
    const q = (query || '').trim().toLowerCase();
    if (!q) {
      items = articles.slice(0, 5);
    } else {
      items = articles.filter(function (a) {
        const hay = (a.title + ' ' + (a.excerpt || '') + ' ' + (a.categories || []).join(' ')).toLowerCase();
        return hay.indexOf(q) !== -1;
      }).slice(0, 20);
    }
    if (!items.length) {
      resultsEl.innerHTML = '<p class="search-empty">No matches.</p>';
      return;
    }
    resultsEl.innerHTML = items.map(function (a) {
      return (
        '<a class="search-result" href="' + escapeHtml(a.url) + '">' +
          '<div class="search-result__title">' + escapeHtml(a.title) + '</div>' +
          (a.excerpt ? '<p class="search-result__excerpt">' + escapeHtml(a.excerpt) + '</p>' : '') +
          (a.date ? '<div class="search-result__meta">' + escapeHtml(a.date) + '</div>' : '') +
        '</a>'
      );
    }).join('');
  }

  function open() {
    overlay.hidden = false;
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    ensureLoaded().then(function () { render(input.value); });
    // Defer focus so iOS Safari doesn't fight us
    setTimeout(function () { input.focus(); input.select(); }, 0);
  }

  function dismiss() {
    overlay.style.display = 'none';
    overlay.hidden = true;
    document.body.style.overflow = '';
    input.value = '';
    resultsEl.innerHTML = '';
  }

  trigger.addEventListener('click', open);
  close.addEventListener('click', dismiss);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) dismiss();
  });
  input.addEventListener('input', function () { render(input.value); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.style.display === 'flex') {
      dismiss();
    } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      if (overlay.style.display === 'flex') dismiss(); else open();
    }
  });
})();
