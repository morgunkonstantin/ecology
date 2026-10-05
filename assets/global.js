/* ЭкоСознание — общий скрипт для всех страниц.
   Всё написано защитно: если элемента на странице нет, блок просто не выполняется. */
(function () {
  'use strict';

  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── 1. Выпадающие меню ─────────────────────────────────────────── */
  document.querySelectorAll('.g-drop-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var li = btn.closest('li');
      if (!li) return;
      var open = li.classList.toggle('g-drop-open');
      btn.setAttribute('aria-expanded', open);
      document.querySelectorAll('.g-drop-open').forEach(function (el) {
        if (el !== li) el.classList.remove('g-drop-open');
      });
    });
  });
  document.addEventListener('click', function () {
    document.querySelectorAll('.g-drop-open').forEach(function (el) {
      el.classList.remove('g-drop-open');
    });
  });

  /* ── 2. Бургер и полноэкранное меню ─────────────────────────────── */
  var burger = document.getElementById('gBurger');
  var overlay = document.getElementById('gOverlay');

  function closeOverlay() {
    if (!overlay) return;
    overlay.classList.remove('open');
    if (burger) {
      burger.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    }
    document.body.style.overflow = '';
  }

  if (burger && overlay) {
    burger.setAttribute('aria-expanded', 'false');
    burger.addEventListener('click', function () {
      var open = overlay.classList.toggle('open');
      burger.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) {
        var first = overlay.querySelector('a[href]');
        if (first) first.focus();
      }
    });
    overlay.querySelectorAll('a[href]').forEach(function (a) {
      a.addEventListener('click', closeOverlay);
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.g-drop-open').forEach(function (el) {
      el.classList.remove('g-drop-open');
    });
    if (overlay && overlay.classList.contains('open')) {
      closeOverlay();
      if (burger) burger.focus();
    }
  });

  /* ── 3. Подсветка текущей страницы ──────────────────────────────── */
  var pg = location.pathname.split('/').pop() || 'index.html';

  document.querySelectorAll('.g-dd-link, .g-ov-link').forEach(function (a) {
    if (a.getAttribute('href') === pg) {
      a.classList.add('g-current');
      a.setAttribute('aria-current', 'page');
    }
  });

  document.querySelectorAll('.g-links > li > a').forEach(function (a) {
    var href = a.getAttribute('href') || '';
    var isFeed = href.indexOf('#latest') > -1 &&
                 (pg.indexOf('essay') === 0 || pg.indexOf('lab') === 0);
    if (href === pg || isFeed) {
      a.classList.add('g-active');
      if (href === pg) a.setAttribute('aria-current', 'page');
    }
  });

  if (pg.indexOf('section-') === 0) {
    var btn = document.querySelector('.g-drop-btn');
    if (btn) btn.classList.add('g-active');
  }

  /* ── 4. Появление блоков при прокрутке ──────────────────────────── */
  var revealables = document.querySelectorAll('.reveal');
  if (revealables.length) {
    if (reduced || !('IntersectionObserver' in window)) {
      revealables.forEach(function (el) { el.classList.add('visible'); });
    } else {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('visible');
            obs.unobserve(e.target);
          }
        });
      }, { threshold: 0.06 });
      revealables.forEach(function (el) { obs.observe(el); });
    }
  }

  /* ── 5. Полоса прогресса чтения и оглавление ────────────────────── */
  var bar = document.getElementById('readingBar') || document.getElementById('rb');
  var tocLinks = document.querySelectorAll('.toc-bar a');
  var sections = document.querySelectorAll('section[id]');
  var ticking = false;

  function onScroll() {
    if (bar) {
      var h = document.documentElement;
      var range = h.scrollHeight - h.clientHeight;
      bar.style.width = (range > 0 ? (h.scrollTop / range) * 100 : 0) + '%';
    }
    if (tocLinks.length && sections.length) {
      var current = '';
      sections.forEach(function (s) {
        if (window.scrollY >= s.offsetTop - 120) current = s.id;
      });
      tocLinks.forEach(function (a) {
        a.classList.toggle('active', a.getAttribute('href') === '#' + current);
      });
    }
    ticking = false;
  }

  if (bar || (tocLinks.length && sections.length)) {
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
    }, { passive: true });
    onScroll();
  }
})();
