// Eliteworks - applies js/config.js to every page, plus menu, forms, testimonials, gallery
(function () {
  var C = window.SITE_CONFIG;
  var q = function (s, f) { document.querySelectorAll(s).forEach(f); };
  var base = (function () { // folder prefix for images (works in sub-folders)
    var src = document.querySelector('script[src$="js/main.js"]');
    return src ? src.getAttribute('src').replace('js/main.js', '') : '';
  })();

  if (C) {
    // Name + logo
    if (C.brandName) {
      var acc = C.brandAccent || '';
      q('.logo-text', function (a) {
        a.textContent = '';
        var i = acc ? C.brandName.indexOf(acc) : -1;
        if (i < 0) { a.textContent = C.brandName; return; }
        a.appendChild(document.createTextNode(C.brandName.slice(0, i)));
        var sp = document.createElement('span'); sp.textContent = acc; a.appendChild(sp);
        a.appendChild(document.createTextNode(C.brandName.slice(i + acc.length)));
      });
      q('[data-c=brand]', function (e) { e.textContent = C.brandName; });
    }
    if (C.logoImage) {
      q('[data-c=logo]', function (a) {
        a.textContent = '';
        var im = document.createElement('img'); im.className = 'logo-img'; im.height = 40;
        im.src = base + C.logoImage; im.alt = (C.brandName || '') + ' logo'; a.appendChild(im);
      });
    }
    // Contact details
    q('[data-c=tel]', function (a) { a.href = 'tel:+' + C.phone; });
    q('[data-c=phone-text]', function (e) { e.textContent = C.phoneDisplay; });
    q('[data-c=mail]', function (a) { a.href = 'mailto:' + C.email; });
    q('[data-c=email-text]', function (e) { e.textContent = C.email; });
    q('a[href*="wa.me/"]', function (a) {
      a.href = a.href.replace(/wa\.me\/\d+/, 'wa.me/' + C.phone);
      if (C.brandName) a.href = a.href.replace(/Hello(%20|\+)[^%&+]*?(?=%2C|,)/, 'Hello%20' + encodeURIComponent(C.brandName));
    });
    q('[data-c=address-wrap]', function (w) {
      if (!C.address) { w.hidden = true; return; }
      w.hidden = false;
      w.querySelectorAll('[data-c=address]').forEach(function (s) {
        s.textContent = '';
        C.address.split('\n').forEach(function (line, i) { if (i) s.appendChild(document.createElement('br')); s.appendChild(document.createTextNode(line)); });
      });
    });
    ['linkedin', 'youtube', 'facebook', 'instagram'].forEach(function (k) {
      q('[data-c=' + k + ']', function (a) { if (C[k]) { a.href = C[k]; a.hidden = false; } else { a.hidden = true; } });
    });
    q('input[name=access_key]', function (i) { i.value = C.web3formsKey; });
    q('[data-c=year]', function (e) { e.textContent = new Date().getFullYear(); });
  }

  // Fixed header height -> body offset
  var h = document.querySelector('.site-header');
  function setH() { if (h) document.documentElement.style.setProperty('--hdr-h', h.offsetHeight + 'px'); }
  setH(); window.addEventListener('resize', setH); window.addEventListener('load', setH);

  // Mobile menu
  var t = document.getElementById('menuToggle'), m = document.getElementById('navMenu');
  if (t && m) {
    t.addEventListener('click', function () { var o = m.classList.toggle('show'); t.setAttribute('aria-expanded', o); });
    m.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { m.classList.remove('show'); t.setAttribute('aria-expanded', 'false'); }); });
  }

  // Careers: "Apply Now" preselects the role
  q('a[data-role]', function (a) {
    a.addEventListener('click', function () {
      var s = document.getElementById('a-role'); if (!s) return;
      for (var i = 0; i < s.options.length; i++) if (s.options[i].text === a.getAttribute('data-role')) s.selectedIndex = i;
    });
  });

  // Forms
  function msg(f, text, err) { var s = f.querySelector('.form-status'); if (s) { s.className = 'form-status' + (err ? ' err' : ''); s.textContent = text; } }
  document.querySelectorAll('form.js-form').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var cfg = window.SITE_CONFIG || {};
      var useSheet = f.hasAttribute('data-testi-form') && cfg.testimonialsApi;
      var b = f.querySelector('button[type=submit]'), old = b.textContent;
      msg(f, 'Sending...'); b.disabled = true; b.textContent = 'Sending...';
      function fail() { msg(f, 'Could not send. Please try again or message us on WhatsApp.', true); b.disabled = false; b.textContent = old; }
      var go = function () { window.location.href = f.dataset.redirect || 'thank-you.html'; };
      if (useSheet) {
        fetch(cfg.testimonialsApi, { method: 'POST', mode: 'no-cors', body: new URLSearchParams(new FormData(f)) }).then(go).catch(fail);
        return;
      }
      fetch(f.action, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(f))) })
        .then(function (r) { return r.json(); })
        .then(function (d) { if (d.success) go(); else throw new Error(d.message || 'Error'); })
        .catch(fail);
    });
  });

  // Thank-you page wording
  var ty = location.search, tt = document.getElementById('ty-title'), tp = document.getElementById('ty-text');
  if (tt && tp) {
    if (ty.indexOf('type=feedback') > -1) { tt.textContent = 'Thank you for your feedback!'; tp.textContent = 'Your review has been received. After a quick check it will appear on the Testimonials page.'; }
    else if (ty.indexOf('type=career') > -1) { tt.textContent = 'Application received'; tp.textContent = 'Thank you for applying. Our team will review your details and contact you if your profile matches.'; }
  }

  // Gallery + associations from config
  if (C) {
    var g = document.querySelector('[data-gallery]');
    if (g && C.gallery && C.gallery.length) {
      g.textContent = '';
      C.gallery.forEach(function (it) {
        var fg = document.createElement('figure'); fg.className = 'g-tile';
        var im = document.createElement('img'); im.src = base + it.src; im.alt = it.caption || 'Project photo'; im.loading = 'lazy';
        fg.appendChild(im);
        if (it.caption) { var c = document.createElement('figcaption'); c.textContent = it.caption; fg.appendChild(c); }
        g.appendChild(fg);
      });
      var n = g.parentNode.querySelector('.center-note.small'); if (n) n.hidden = true;
    }
    var as = document.querySelector('[data-assoc]');
    if (as && C.associations && C.associations.length) {
      as.textContent = '';
      C.associations.forEach(function (it) {
        var el = document.createElement(it.url ? 'a' : 'div'); el.className = 'assoc';
        if (it.url) { el.href = it.url; el.target = '_blank'; el.rel = 'noopener'; }
        if (it.logo) { var im = document.createElement('img'); im.src = base + it.logo; im.alt = it.name || 'Partner logo'; im.loading = 'lazy'; el.appendChild(im); }
        if (it.name) { var s = document.createElement('span'); s.textContent = it.name; el.appendChild(s); }
        as.appendChild(el);
      });
    }
  }

  // Live testimonials (approved rows from Google Sheet)
  var grids = document.querySelectorAll('.testimonial-grid[data-testi]');
  if (C && C.testimonialsApi && grids.length && window.fetch) {
    var card = function (t) {
      var fig = document.createElement('figure'); fig.className = 'testimonial-card';
      var r = Math.max(1, Math.min(5, parseInt(t.rating, 10) || 5));
      var st = document.createElement('div'); st.className = 'stars'; st.setAttribute('aria-label', r + ' out of 5 stars');
      st.textContent = new Array(r + 1).join('★') + new Array(6 - r).join('☆');
      var bq = document.createElement('blockquote'), p = document.createElement('p');
      p.textContent = '“' + String(t.message || '') + '”'; bq.appendChild(p);
      var cap = document.createElement('figcaption'); cap.className = 'testimonial-name';
      var meta = [t.role, t.company].filter(Boolean).join(', ');
      cap.textContent = '— ' + (t.name || 'Customer') + (meta ? ' (' + meta + ')' : '');
      fig.appendChild(st); fig.appendChild(bq); fig.appendChild(cap); return fig;
    };
    fetch(C.testimonialsApi).then(function (r) { return r.json(); }).then(function (d) {
      var list = (d && d.testimonials) || [];
      if (!list.length) return;
      grids.forEach(function (gr) {
        var lim = gr.getAttribute('data-testi') === 'all' ? Infinity : parseInt(gr.getAttribute('data-testi'), 10) || 3;
        gr.textContent = '';
        list.slice(0, lim).forEach(function (t) { gr.appendChild(card(t)); });
      });
      q('[data-testi-empty]', function (e) { e.hidden = true; });
      var hs = document.getElementById('home-testimonials'); if (hs) hs.hidden = false;
    }).catch(function () {});
  }
})();
