// Priority-nav pattern for the header utility row.
// If the time + utility links won't fit on one row, collapse the links
// into a "More ▾" dropdown. Re-evaluate on resize.
(function () {
  const nav = document.querySelector('.site-nav-utility');
  if (!nav) return;
  const row = nav.closest('.site-header__utility');
  const toggle = nav.querySelector('.site-nav-utility__toggle');
  if (!row || !toggle) return;

  function fit() {
    // Reset to inline state to measure natural width
    nav.setAttribute('data-collapsed', 'false');
    nav.setAttribute('data-open', 'false');
    toggle.setAttribute('aria-expanded', 'false');

    // Read after a forced reflow
    const overflowing = row.scrollWidth > row.clientWidth + 1;
    if (overflowing) {
      nav.setAttribute('data-collapsed', 'true');
    }
  }

  toggle.addEventListener('click', function (e) {
    e.stopPropagation();
    const open = nav.getAttribute('data-open') === 'true';
    nav.setAttribute('data-open', open ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
  });

  document.addEventListener('click', function (e) {
    if (!nav.contains(e.target)) {
      nav.setAttribute('data-open', 'false');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      nav.setAttribute('data-open', 'false');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  fit();
  let timer;
  window.addEventListener('resize', function () {
    clearTimeout(timer);
    timer = setTimeout(fit, 80);
  });
})();
