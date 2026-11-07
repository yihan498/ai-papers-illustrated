// 论文页导航：顶部返回条 + 章节导航。章节导航从正文的 h2（大节）和 h3（小节）自动生成，不需要手写目录。
// 标题的写法约定：<h2><span class="no">1</span>标题</h2>、<h3><span class="no">1.3</span>标题</h3>。
// 没有 id 的标题按编号补一个稳定的 id（1.3 → s1-3），这样链接可以分享到具体小节。
(function () {
  // 顶部细条（design-library 的 pageheader-06 粘性压缩页头）：常驻页面顶部，滚到哪里都看得见。
  // 左边「‹ AI 论文解读」回主页，后面跟着本篇编号和标题。页眉里原来那行「← AI 论文解读 · 编号」和它重复，隐藏掉。
  var header = document.querySelector('header');
  var home = header && header.querySelector('.eyebrow a');
  var h1 = header && header.querySelector('h1');
  var eb = header && header.querySelector('.eyebrow');
  var num = eb ? (eb.textContent.split('·').pop() || '').trim() : '';
  var bar = document.createElement('div');
  bar.className = 'pbar';
  bar.innerHTML = '<a class="pbar-home" href="#"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg>AI 论文解读</a>' +
    '<span class="pbar-sep" aria-hidden="true">/</span><span class="pbar-t"></span>';
  bar.querySelector('a').href = home ? home.getAttribute('href') : '../../index.html';
  bar.querySelector('.pbar-t').textContent = (num ? num + ' · ' : '') + (h1 ? h1.textContent.trim() : document.title);
  document.body.appendChild(bar);
  if (eb) eb.hidden = true;

  var main = document.querySelector('main');
  if (!main) return;
  var heads = Array.prototype.slice.call(main.querySelectorAll('h2, h3'));
  if (!heads.length) return;

  var items = heads.map(function (h, i) {
    var noEl = h.querySelector('.no');
    var no = noEl ? noEl.textContent.trim() : '';
    var label = h.textContent.replace(no, '').trim();
    if (!h.id) h.id = no ? 's' + no.replace(/\./g, '-') : 'h' + i;
    return { el: h, id: h.id, no: no, label: label, lvl: h.tagName === 'H2' ? 2 : 3 };
  });
  // 每个小节记住它属于哪个大节
  var cur2 = null;
  items.forEach(function (it) { if (it.lvl === 2) cur2 = it; it.parent = it.lvl === 2 ? it : cur2; });

  // 标题里可能有 <EOS> 这类文字，拼进 innerHTML 前要转义，否则会被当成标签吞掉
  function esc(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  function build(cls, title) {
    var nav = document.createElement('nav');
    nav.className = 'ptoc ' + cls;
    nav.setAttribute('aria-label', '本篇章节');
    var html = '<div class="head">' + title + '</div><ol>';
    items.forEach(function (it) {
      html += '<li class="l' + it.lvl + '" data-id="' + it.id + '" data-p="' + (it.parent ? it.parent.id : '') + '">' +
        '<a href="#' + it.id + '"><span class="n">' + esc(it.no) + '</span><span>' + esc(it.label) + '</span></a></li>';
    });
    nav.innerHTML = html + '</ol>';
    return nav;
  }

  var side = build('ptoc-side', '本篇章节');
  document.body.appendChild(side);

  // 窄屏：按钮 + 弹出目录
  var fab = document.createElement('button');
  fab.className = 'ptoc-fab';
  fab.type = 'button';
  fab.textContent = '目录';
  fab.setAttribute('aria-expanded', 'false');
  var veil = document.createElement('div');
  veil.className = 'ptoc-veil';
  veil.hidden = true;
  var sheet = build('ptoc-sheet', '本篇章节');
  sheet.hidden = true;
  sheet.id = 'ptoc-sheet';
  fab.setAttribute('aria-controls', 'ptoc-sheet');
  document.body.appendChild(veil);
  document.body.appendChild(sheet);
  document.body.appendChild(fab);

  function setOpen(open) {
    sheet.hidden = veil.hidden = !open;
    fab.setAttribute('aria-expanded', String(open));
    fab.textContent = open ? '关闭' : '目录';
    if (open) {
      var on = sheet.querySelector('.on');
      if (on) on.scrollIntoView({ block: 'center' });
    }
  }
  fab.addEventListener('click', function () { setOpen(sheet.hidden); });
  veil.addEventListener('click', function () { setOpen(false); });
  sheet.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !sheet.hidden) { setOpen(false); fab.focus(); } });

  // 滚动时高亮当前所在的章节
  var lis = Array.prototype.slice.call(document.querySelectorAll('.ptoc li'));
  var last = null;
  function spy() {
    var y = 140, active = null;
    for (var i = 0; i < items.length; i++) {
      if (items[i].el.getBoundingClientRect().top <= y) active = items[i]; else break;
    }
    var id = active ? active.id : '';
    if (id === last) return;
    last = id;
    var pid = active ? active.parent.id : '';
    lis.forEach(function (li) {
      var mine = li.getAttribute('data-id');
      li.classList.toggle('on', mine === id || (li.classList.contains('l2') && mine === pid));
      if (li.classList.contains('l3')) li.classList.toggle('open', li.getAttribute('data-p') === pid);
    });
    var onSide = side.querySelector('li.l3.on, li.l2.on');
    if (onSide) {
      var r = onSide.getBoundingClientRect(), s = side.getBoundingClientRect();
      if (r.top < s.top || r.bottom > s.bottom) onSide.scrollIntoView({ block: 'nearest' });
    }
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; spy(); }); }
  }, { passive: true });
  window.addEventListener('resize', spy);
  spy();
})();
