// Copy-link button on article share toolbars. Uses the async Clipboard API
// (Safari 13.1+, Chrome 66+, Firefox 63+). Falls back silently on older browsers.
(function () {
  const buttons = document.querySelectorAll('.share-button--copy');
  if (!buttons.length || !navigator.clipboard) return;

  buttons.forEach(function (btn) {
    btn.addEventListener('click', async function () {
      const url = btn.dataset.shareUrl;
      if (!url) return;
      try {
        await navigator.clipboard.writeText(url);
        btn.classList.add('is-copied');
        btn.setAttribute('aria-label', 'Link copied');
        setTimeout(function () {
          btn.classList.remove('is-copied');
          btn.setAttribute('aria-label', 'Copy link');
        }, 1500);
      } catch (e) {
        /* swallow — older browsers without clipboard permissions */
      }
    });
  });
})();
