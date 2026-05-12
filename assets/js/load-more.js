// Progressive disclosure for card grids. Any `.cards-container[data-page-size]`
// paired with a `.load-more-btn` sibling (under a `.cards-with-loadmore` wrapper)
// will hide cards past the page-size and reveal them in batches on click.
(function () {
  const DEFAULT_PAGE_SIZE = 10;

  document.querySelectorAll('.cards-container').forEach(function (container) {
    const cards = Array.from(container.children).filter(function (el) {
      return el.classList.contains('card');
    });

    const pageSize = parseInt(container.dataset.pageSize, 10) || DEFAULT_PAGE_SIZE;
    if (cards.length <= pageSize) return;

    const wrapper = container.closest('.cards-with-loadmore') || container.parentElement;
    const button = wrapper ? wrapper.querySelector('.load-more-btn') : null;
    if (!button) return;

    let shown = pageSize;

    function apply() {
      cards.forEach(function (card, i) {
        card.classList.toggle('card--hidden', i >= shown);
      });
      const remaining = cards.length - shown;
      if (remaining <= 0) {
        button.style.display = 'none';
      } else {
        button.style.display = '';
        button.textContent = 'Load more (' + remaining + ' remaining)';
      }
    }

    apply();

    button.addEventListener('click', function () {
      shown = Math.min(cards.length, shown + pageSize);
      apply();
    });
  });
})();
