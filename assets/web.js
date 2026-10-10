// Menú desplegable, vídeos de YouTube sota demanda i selector de proposta (només versió de prova)
(function () {
  var boto = document.querySelector('.boto-menu');
  var menu = document.getElementById('menu-plafo');
  if (boto && menu) {
    boto.addEventListener('click', function () {
      var obert = boto.getAttribute('aria-expanded') === 'true';
      boto.setAttribute('aria-expanded', String(!obert));
      menu.hidden = obert;
      if (!obert) { var a = menu.querySelector('a'); if (a) a.focus(); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) { menu.hidden = true; boto.setAttribute('aria-expanded', 'false'); boto.focus(); }
    });
  }

  // Els vídeos només es carreguen (amb youtube-nocookie) quan algú els vol veure
  document.querySelectorAll('.video-marc').forEach(function (marc) {
    var a = marc.querySelector('.video-inici');
    if (window.UTAC_PROVA) return; // a la versió de prova el vídeo s'obre a YouTube
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var id = marc.getAttribute('data-youtube');
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      f.title = a.textContent.trim() || 'Vídeo';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      marc.replaceChildren(f);
      f.focus();
    });
  });

  // Selector de proposta de disseny (versió de prova)
  var radios = document.querySelectorAll('input[name="tema"]');
  if (radios.length) {
    var guardat = null;
    try { guardat = localStorage.getItem('utac-tema'); } catch (e) {}
    var params = new URLSearchParams(location.search);
    var inicial = params.get('tema') || guardat || 'plafo';
    function aplica(t) {
      document.documentElement.setAttribute('data-proposta', t);
      radios.forEach(function (r) { r.checked = r.value === t; });
      try { localStorage.setItem('utac-tema', t); } catch (e) {}
    }
    aplica(inicial);
    radios.forEach(function (r) { r.addEventListener('change', function () { aplica(r.value); }); });
  }

  // Fitxes d'icones: tots els requadres de la pàgina fan la mateixa alçada
  var fitxesIcones = document.querySelectorAll('.fitxes-icones .fitxa');
  function igualaFitxes() {
    var max = 0;
    fitxesIcones.forEach(function (f) { f.style.minHeight = ''; });
    fitxesIcones.forEach(function (f) { max = Math.max(max, f.offsetHeight); });
    fitxesIcones.forEach(function (f) { f.style.minHeight = max + 'px'; });
  }
  if (fitxesIcones.length) {
    igualaFitxes();
    window.addEventListener('resize', igualaFitxes);
    if (document.fonts) document.fonts.ready.then(igualaFitxes);
  }
})();
