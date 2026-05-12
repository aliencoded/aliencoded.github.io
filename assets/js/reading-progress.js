// Thin progress bar at the top of the viewport that tracks how far the
// reader has scrolled through the article body.
(function () {
  const bar = document.querySelector('.reading-progress');
  const article = document.querySelector('.post-content');
  if (!bar || !article) return;

  let ticking = false;

  function update() {
    const rect = article.getBoundingClientRect();
    const total = rect.height;
    const winHeight = window.innerHeight;

    // No scrollable region in the article (very short post) → leave at 0.
    const maxScroll = total - winHeight;
    if (maxScroll <= 0) {
      setBar(0);
      ticking = false;
      return;
    }

    let progress;
    if (rect.top >= 0) {
      progress = 0;
    } else if (rect.top + total <= winHeight) {
      progress = 100;
    } else {
      progress = Math.min(100, Math.max(0, (-rect.top / maxScroll) * 100));
    }
    setBar(progress);
    ticking = false;
  }

  function setBar(progress) {
    bar.style.width = progress + '%';
    bar.setAttribute('aria-valuenow', Math.round(progress));
  }

  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  update();
})();
