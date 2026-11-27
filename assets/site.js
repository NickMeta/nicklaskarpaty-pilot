/* nicklaskarpaty.com: allt innehåll finns redan i HTML. Skriptet sköter bara meny, filmfönster,
   referenser, ramguide och bildjämförelse. Utan skript fungerar sidan och alla länkar ändå. */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Meny
  var header = $('.site-header');
  if (header && !document.body.classList.contains('page')) {
    var sc = function () { header.classList.toggle('solid', window.scrollY > 60); };
    sc(); window.addEventListener('scroll', sc, { passive: true });
  }
  var mb = $('.menu-btn'), nav = $('#nav');
  if (mb && nav) {
    mb.addEventListener('click', function () { var o = nav.classList.toggle('open'); mb.setAttribute('aria-expanded', o); mb.textContent = o ? 'Close' : 'Menu'; });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) { nav.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); mb.textContent = 'Menu'; } });
  }

  // Filmfönster för Vimeo och YouTube
  var dlg = document.createElement('dialog');
  dlg.className = 'player'; dlg.setAttribute('aria-label', 'Video');
  dlg.innerHTML = '<div class="pbox"></div><div class="pbar"><span></span><button type="button">Close</button></div>';
  var st = document.createElement('style');
  st.textContent = '.player{border:0;padding:0;background:#000;width:min(1200px,94vw);max-width:none;max-height:94vh;overflow:hidden;color:#f1ece6}' +
    '.player::backdrop{background:rgba(0,0,0,.88)}.pbox{position:relative;aspect-ratio:16/9}.pbox iframe{position:absolute;inset:0;width:100%;height:100%;border:0}' +
    '.pbar{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;font:300 14px/1.4 Montserrat,system-ui,sans-serif;border-top:1px solid #222}' +
    '.pbar button{font:400 12px Jost,sans-serif;letter-spacing:.16em;text-transform:uppercase;background:none;color:#f1ece6;border:1px solid #b87333;padding:9px 16px;cursor:pointer}.pbar button:hover{background:#b87333;color:#000}';
  document.head.appendChild(st); document.body.appendChild(dlg);
  var box = $('.pbox', dlg), cap = $('.pbar span', dlg);
  function close() { box.innerHTML = ''; if (dlg.open) dlg.close(); }
  $('.pbar button', dlg).addEventListener('click', close);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
  dlg.addEventListener('cancel', function () { box.innerHTML = ''; });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-play]'); if (!b) return;
    e.preventDefault();
    var p = b.getAttribute('data-play').split(':'), src = p[0] === 'vimeo'
      ? 'https://player.vimeo.com/video/' + p[1] + '?autoplay=1&title=0&byline=0&portrait=0'
      : 'https://www.youtube-nocookie.com/embed/' + p[1] + '?autoplay=1&rel=0';
    var f = document.createElement('iframe');
    f.src = src; f.allow = 'autoplay; fullscreen; picture-in-picture'; f.allowFullscreen = true; f.title = b.getAttribute('data-title') || 'Video';
    box.innerHTML = ''; box.appendChild(f); cap.textContent = b.getAttribute('data-title') || '';
    if (dlg.showModal) dlg.showModal(); else window.open(src, '_blank', 'noopener');
  });

  // Referenser
  var figs = $$('.qbox figure'), dots = $$('.qdots i'), qi = 0, qt;
  function show(n) { qi = (n + figs.length) % figs.length; figs.forEach(function (f, i) { f.classList.toggle('on', i === qi); }); dots.forEach(function (d, i) { d.classList.toggle('on', i === qi); }); }
  function auto() { clearInterval(qt); if (!reduce && figs.length > 1) qt = setInterval(function () { show(qi + 1); }, 8000); }
  if (figs.length) {
    var qp = $('#qp'), qn = $('#qn');
    if (qp) qp.addEventListener('click', function () { show(qi - 1); auto(); });
    if (qn) qn.addEventListener('click', function () { show(qi + 1); auto(); });
    var qb = $('.qbox'); qb.addEventListener('mouseenter', function () { clearInterval(qt); }); qb.addEventListener('mouseleave', auto);
    show(0); auto();
  }

  // Ramguide och tidkod
  var v = $('#hero-video'), tc = $('#tc'), gd = $('#guide'), gt = $('#gt');
  if (v) {
    var vb = $('#vplay');
    var showBtn = function () { if (vb) vb.hidden = false; };
    if (vb) vb.addEventListener('click', function () { v.play().then(function () { vb.hidden = true; }).catch(function () {}); });
    if (reduce) { v.pause(); v.removeAttribute('autoplay'); showBtn(); }
    else {
      v.muted = true;
      var p = v.play();
      if (p && p.catch) p.catch(showBtn);
      // Om filmen fortfarande står still efter några sekunder visas knappen
      setTimeout(function () { if (v.paused) showBtn(); }, 2500);
    }
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var tick = function () { var t = v.currentTime || 0; if (tc) tc.textContent = pad(Math.floor(t / 3600)) + ':' + pad(Math.floor(t / 60) % 60) + ':' + pad(Math.floor(t) % 60) + ':' + pad(Math.floor((t % 1) * 25)); if (!v.paused) requestAnimationFrame(tick); };
    v.addEventListener('play', tick); v.addEventListener('timeupdate', function () { if (v.paused) tick(); });
  }
  if (gd && gt) {
    var toggle = function () { var on = gd.hidden; gd.hidden = !on; gt.setAttribute('aria-pressed', on); gt.textContent = 'Frame guide: ' + (on ? 'on' : 'off'); };
    gt.addEventListener('click', toggle);
  }

  // LOG mot gradering
  var wipe = $('.wipe'), wr = $('#wr');
  if (wipe && wr) wr.addEventListener('input', function () { wipe.style.setProperty('--p', wr.value + '%'); });

  // Loggor som inte laddar ersätts med namnet
  $$('img.lg').forEach(function (im) { var swap = function () { var s = document.createElement('span'); s.className = 'lgtxt'; s.textContent = im.alt; im.replaceWith(s); }; if (im.complete && im.naturalWidth === 0 && im.currentSrc) swap(); else im.addEventListener('error', swap); });
})();
