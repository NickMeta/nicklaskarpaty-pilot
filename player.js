/* Delad videospelare: klick på [data-play] öppnar Vimeo/YouTube i ett fönster. Länkobjekt öppnas på nuvarande sidan. */
(function () {
  var css = '.nkp{border:0;padding:0;background:#000;width:min(1200px,94vw);max-width:none;max-height:94vh;color:#eee;overflow:hidden}' +
    '.nkp::backdrop{background:rgba(0,0,0,.86)}.nkp .box{position:relative;aspect-ratio:16/9;background:#000}' +
    '.nkp iframe{position:absolute;inset:0;width:100%;height:100%;border:0}' +
    '.nkp .bar{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;font:400 14px/1.4 Montserrat,system-ui,sans-serif;background:#0a0a0a;border-top:1px solid #222}' +
    '.nkp button{font:500 12px Jost,sans-serif;letter-spacing:.16em;text-transform:uppercase;background:none;color:#eee;border:1px solid #b87333;padding:9px 16px;cursor:pointer}' +
    '.nkp button:hover,.nkp button:focus-visible{background:#b87333;color:#000}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  var dlg = document.createElement('dialog'); dlg.className = 'nkp'; dlg.setAttribute('aria-label', 'Video');
  dlg.innerHTML = '<div class="box"></div><div class="bar"><span></span><button type="button">Close</button></div>';
  document.body.appendChild(dlg);
  var box = dlg.querySelector('.box'), cap = dlg.querySelector('.bar span');
  function close() { box.innerHTML = ''; if (dlg.open) dlg.close(); }
  dlg.querySelector('button').addEventListener('click', close);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
  dlg.addEventListener('cancel', function () { box.innerHTML = ''; });
  function src(it) {
    if (it.p === 'vimeo') return 'https://player.vimeo.com/video/' + it.id + '?autoplay=1&title=0&byline=0&portrait=0';
    if (it.p === 'youtube') return 'https://www.youtube-nocookie.com/embed/' + it.id + '?autoplay=1&rel=0';
    return '';
  }
  window.NKplay = function (it, into) {
    if (it.p === 'link') { window.open(it.href, '_blank', 'noopener'); return; }
    var f = document.createElement('iframe');
    f.src = src(it); f.allow = 'autoplay; fullscreen; picture-in-picture'; f.allowFullscreen = true; f.title = it.t;
    if (into) { into.innerHTML = ''; into.appendChild(f); return; }
    box.innerHTML = ''; box.appendChild(f); cap.textContent = it.t + ' · ' + it.s; dlg.showModal();
  };
})();
