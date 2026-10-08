/* Desktop keeps filters visible; phones use the same controls in disclosures. */
(function () {
  var wide = window.matchMedia('(min-width:681px)');
  function syncDisclosures() {
    document.querySelectorAll('.settings-switcher,.market-filters').forEach(function (details) {
      details.open = wide.matches;
    });
  }
  syncDisclosures();
  wide.addEventListener('change', syncDisclosures);

  document.querySelectorAll('#kcCatTabs,#kcSubTabs').forEach(function (group) {
    function syncSelection() {
      group.querySelectorAll('button').forEach(function (button) {
        button.setAttribute('aria-pressed', String(button.classList.contains('on')));
      });
      if (group.id === 'kcSubTabs') {
        var active = group.querySelector('.on');
        var summary = document.querySelector('.market-filters>summary span');
        if (summary && active) summary.textContent = active.textContent.trim() === 'All' ? 'All leagues' : active.textContent.trim();
      }
    }
    syncSelection();
    group.addEventListener('click', syncSelection);
  });
})();

(function(){var note=document.querySelector(".wallet-value-note"); if(note && !localStorage.getItem("ft_market_v1")) note.textContent+=" Preview illustration: 1,000,000 tokens at $20 each implies a $20m token market value. Live exchange quotes determine actual value; signups do not guarantee growth.";})();
