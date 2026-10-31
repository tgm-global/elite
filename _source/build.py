#!/usr/bin/env python3
"""Builds the whole static site from js/config.js + _source/content.py.
Run from the site folder:   python3 _source/build.py
Header, footer and the fixed contact bar are defined ONCE here and written into every page."""
import os, sys, re, json, html as H, urllib.parse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import *

# ---------- settings come from js/config.js (single place) ----------
_txt = open(os.path.join(ROOT, "js", "config.js"), encoding="utf-8").read()
CFG = json.loads(re.search(r"window\.SITE_CONFIG\s*=\s*(\{.*\})\s*;", _txt, re.S).group(1))
BRAND = CFG["brandName"]; ACCENT = CFG.get("brandAccent", ""); TAG = CFG.get("tagline", "")
PHONE = CFG["phone"]; PHONE_SHOW = CFG["phoneDisplay"]; EMAIL = CFG["email"]
ADDRESS = CFG.get("address", ""); W3F = CFG["web3formsKey"]
SOCIAL = {k: CFG.get(k, "") for k in ("linkedin", "youtube", "facebook", "instagram")}
if CFG.get("customDomain"):
    SITE_URL, BASE = "https://" + CFG["customDomain"], ""
else:
    SITE_URL, BASE = f"https://{CFG['githubUser']}.github.io/{CFG['repo']}", "/" + CFG["repo"]
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
E = H.escape

def wa(text):
    return f"https://wa.me/{PHONE}?text=" + urllib.parse.quote(text)
WA_GENERAL = wa(f"Hello {BRAND}, I would like to know more about your automation solutions.")
WA_ICON = ('<svg viewBox="0 0 24 24" width="{s}" height="{s}" aria-hidden="true"><path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>')
def waicon(s=22): return WA_ICON.replace("{s}", str(s))
PHONE_ICON = '<svg viewBox="0 0 24 24" width="{s}" height="{s}" aria-hidden="true"><path fill="currentColor" d="M6.600 10.800a15 15 0 0 0 6.600 6.600l2.200-2.200a1 1 0 0 1 1-.25c1.100.37 2.300.57 3.600.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.500a1 1 0 0 1 1 1c0 1.300.2 2.500.57 3.600a1 1 0 0 1-.25 1z"/></svg>'
def phicon(s=20): return PHONE_ICON.replace("{s}", str(s))
SOC_ICONS = {
 "linkedin": ("LinkedIn", '<path fill="currentColor" d="M4.500 3A2.500 2.500 0 1 0 4.500 8 2.500 2.500 0 0 0 4.500 3zM2 9.500h5V22H2zM9.500 9.500h4.800v1.800h.1c.7-1.300 2.300-2.100 4.100-2.100 4.200 0 5 2.800 5 6.300V22h-5v-5.600c0-1.400 0-3.100-1.900-3.100s-2.200 1.500-2.200 3V22h-5z"/>'),
 "youtube": ("YouTube", '<path fill="currentColor" d="M23 7.200a3 3 0 0 0-2.100-2.100C19 4.600 12 4.600 12 4.600s-7 0-8.900.5A3 3 0 0 0 1 7.200 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.800a3 3 0 0 0 2.100 2.100c1.900.5 8.900.5 8.900.5s7 0 8.900-.5a3 3 0 0 0 2.100-2.100 31 31 0 0 0 .5-4.800 31 31 0 0 0-.5-4.800zM10 15V9l5.200 3z"/>'),
 "facebook": ("Facebook", '<path fill="currentColor" d="M13.500 22v-8h2.700l.5-3.300h-3.200V8.600c0-1 .4-1.700 1.800-1.700h1.500V4a20 20 0 0 0-2.400-.1c-2.500 0-4.200 1.500-4.200 4.300v2.500H7.200V14h2.700v8z"/>'),
 "instagram": ("Instagram", '<path fill="currentColor" d="M12 7.300A4.700 4.700 0 1 0 12 16.700 4.700 4.700 0 0 0 12 7.300zm0 7.700a3 3 0 1 1 0-6 3 3 0 0 1 0 6zM17.200 5.500a1.100 1.100 0 1 0 0 2.200 1.100 1.100 0 0 0 0-2.200zM12 2.500c-2.600 0-2.900 0-3.900.1-3.300.1-4.800 1.700-4.900 4.900C3.100 8.500 3.100 8.800 3.100 12s0 3.500.1 4.500c.1 3.200 1.700 4.800 4.900 4.900 1 .1 1.300.1 3.900.1s2.900 0 3.900-.1c3.200-.1 4.800-1.700 4.900-4.900.1-1 .1-1.300.1-4.500s0-3.500-.1-4.500c-.1-3.200-1.700-4.800-4.900-4.900-1-.1-1.300-.1-3.900-.1zm0 1.700c2.500 0 2.800 0 3.800.1 2.300.1 3.400 1.200 3.500 3.500.1 1 .1 1.300.1 3.800s0 2.800-.1 3.800c-.1 2.300-1.200 3.400-3.500 3.500-1 .1-1.300.1-3.800.1s-2.800 0-3.800-.1c-2.300-.1-3.400-1.200-3.500-3.500-.1-1-.1-1.300-.1-3.800s0-2.800.1-3.800C4.800 5.500 5.900 4.400 8.200 4.300c1-.1 1.300-.1 3.800-.1z"/>'),
}

# ---------- navigation ----------
NAV = [
 ("Home", "index.html", []),
 ("About", "about.html", [("About Us", "about.html"), ("Vision & Mission", "about.html#vision-mission"), ("Associations", "associations.html")]),
 ("Products", "products.html", [(p["name"], f"products/{p['slug']}.html") for p in PRODUCTS]),
 ("Industries", "industries.html", []),
 ("Gallery", "gallery.html", []),
 ("Careers", "careers.html", []),
 ("Testimonials", "testimonials.html", []),
 ("Contact", "contact.html", []),
]
FOOT_LINKS = [("Home", "index.html"), ("About Us", "about.html"), ("Products", "products.html"), ("Industries", "industries.html"),
              ("Associations", "associations.html"), ("Gallery", "gallery.html"), ("Careers", "careers.html"),
              ("Testimonials", "testimonials.html"), ("Contact", "contact.html")]

def svg_icon(name, size=40, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 48 48" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2.200" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

LOGO_MARK = ('<svg viewBox="0 0 36 36" width="36" height="36" aria-hidden="true"><rect width="36" height="36" rx="8" fill="#ff6a13"/>'
             '<path d="M11 9h15v4H15.500v3.500H24v4h-8.500V24H26v4H11z" fill="#fff"/></svg>')

def logo_text():
    b, a = E(BRAND), E(ACCENT)
    return b.replace(a, f"<span>{a}</span>", 1) if a and a in b else b

def logo_inner():
    if CFG.get("logoImage"):
        return f'<img class="logo-img" src="__P__{E(CFG["logoImage"])}" alt="{E(BRAND)} logo" height="40">'
    return f'<span class="logo-mark">{LOGO_MARK}</span><span class="logo-text">{logo_text()}</span>'

# ---------- page shell ----------
def jsonld(o): return f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>'

def org_schema():
    o = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE_URL + "/",
         "description": f"{BRAND} designs and builds industrial automation and robotic systems: welding, material handling, press line automation, vision inspection, battery assembly and special purpose machines.",
         "telephone": "+" + PHONE, "email": EMAIL, "slogan": TAG}
    same = [v for v in SOCIAL.values() if v]
    if same: o["sameAs"] = same
    if ADDRESS: o["address"] = {"@type": "PostalAddress", "streetAddress": " ".join(ADDRESS.split("\n"))}
    return o

def bc_schema(items):
    lst = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + "/" + u} for i, (n, u) in enumerate(items)]
    return jsonld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": lst})

def faq_schema(faqs):
    return jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})

def head(title, desc, path, depth, extra="", noindex=False, og="website"):
    p = "../" * depth
    url = f"{SITE_URL}/{path}" if path != "index.html" else SITE_URL + "/"
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    canon = "" if noindex else f'<link rel="canonical" href="{url}">'
    t, d = E(title), E(desc, quote=True)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<meta name="description" content="{d}">
{robots}
{canon}
<meta name="author" content="{E(BRAND)}">
<meta name="theme-color" content="#0b1f3a">
<meta property="og:type" content="{og}">
<meta property="og:site_name" content="{E(BRAND)}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 36 36'%3E%3Crect width='36' height='36' rx='8' fill='%23ff6a13'/%3E%3Cpath d='M11 9h15v4H15.500v3.500H24v4h-8.500V24H26v4H11z' fill='%23fff'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{p}css/style.css">
{extra}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''

def header(active, depth):
    p = "../" * depth
    items = []
    for label, href, kids in NAV:
        cls = ' class="active" aria-current="page"' if href == active or (kids and active.startswith("products/") and label == "Products") else ""
        if kids:
            sub = "".join(f'<li><a href="{p}{h}">{E(l)}</a></li>' for l, h in kids)
            items.append(f'<li class="has-sub"><a href="{p}{href}"{cls}>{label}</a><ul class="sub">{sub}</ul></li>')
        else:
            items.append(f'<li><a href="{p}{href}"{cls}>{label}</a></li>')
    return f'''<header class="site-header">
  <div class="navbar">
    <a class="logo" data-c="logo" href="{p}index.html" aria-label="{E(BRAND)} home">{logo_inner().replace("__P__", p)}</a>
    <nav aria-label="Main"><ul id="navMenu">{"".join(items)}</ul></nav>
    <div class="hdr-actions">
      <a class="hdr-call" data-c="tel" href="tel:+{PHONE}" aria-label="Call us">{phicon(18)}<span data-c="phone-text">{PHONE_SHOW}</span></a>
      <a class="hdr-wa" href="{WA_GENERAL}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{waicon(24)}</a>
      <button class="menu-toggle" id="menuToggle" aria-label="Open menu" aria-expanded="false" aria-controls="navMenu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
'''

def social_links():
    out = []
    for k, (name, path) in SOC_ICONS.items():
        v = SOCIAL[k]
        hid = "" if v else " hidden"
        out.append(f'<a data-c="{k}" href="{E(v) or "#"}" target="_blank" rel="noopener me" aria-label="{name}"{hid}><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">{path}</svg></a>')
    return "".join(out)

def footer(depth):
    p = "../" * depth
    links = "".join(f'<li><a href="{p}{h}">{l}</a></li>' for l, h in FOOT_LINKS)
    prods = "".join(f'<li><a href="{p}products/{x["slug"]}.html">{E(x["name"])}</a></li>' for x in PRODUCTS)
    addr = E(ADDRESS).replace("\n", "<br>")
    ahid = "" if ADDRESS else " hidden"
    return f'''
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <a class="logo logo-foot" data-c="logo" href="{p}index.html" aria-label="{E(BRAND)} home">{logo_inner().replace("__P__", p)}</a>
      <p>{E(BRAND)} designs, builds and supports industrial automation and robotic systems that help manufacturers produce with consistent quality, speed and safety.</p>
      <p class="social">{social_links()}</p>
    </div>
    <div><h3>Quick Links</h3><ul>{links}</ul></div>
    <div><h3>Solutions</h3><ul>{prods}</ul></div>
    <div>
      <h3>Contact Us</h3>
      <ul class="contact-list">
        <li><a data-c="tel" href="tel:+{PHONE}">{phicon(16)} <span data-c="phone-text">{PHONE_SHOW}</span></a></li>
        <li><a href="{WA_GENERAL}" target="_blank" rel="noopener">{waicon(16)} WhatsApp</a></li>
        <li><a data-c="mail" href="mailto:{E(EMAIL)}">&#9993; <span data-c="email-text">{E(EMAIL)}</span></a></li>
        <li data-c="address-wrap"{ahid}>&#9906; <span data-c="address">{addr}</span></li>
      </ul>
    </div>
  </div>
  <div class="container footer-bottom">
    <p>&copy; <span data-c="year">{YEAR}</span> <span data-c="brand">{E(BRAND)}</span>. All rights reserved. <a href="{p}privacy-policy.html">Privacy Policy</a> &middot; <a href="{p}terms.html">Terms of Use</a></p>
  </div>
</footer>
<div class="fixed-bar" role="complementary" aria-label="Quick contact">
  <a class="fb-call" data-c="tel" href="tel:+{PHONE}">{phicon(20)} <span>Call <b data-c="phone-text">{PHONE_SHOW}</b></span></a>
  <a class="fb-wa" href="{WA_GENERAL}" target="_blank" rel="noopener">{waicon(22)} <span>WhatsApp</span></a>
  <a class="fb-quote" href="{p}contact.html">Get a Quote</a>
</div>
<script src="{p}js/config.js" defer></script>
<script src="{p}js/main.js" defer></script>
</body>
</html>
'''

def crumbs(items, depth):
    p = "../" * depth
    out = [f'<a href="{p}index.html">Home</a>']
    for l, h in items:
        out.append(f'<a href="{p}{h}">{E(l)}</a>' if h else f'<span aria-current="page">{E(l)}</span>')
    return '<nav class="breadcrumb" aria-label="Breadcrumb">' + " &rsaquo; ".join(out) + "</nav>"

def page_hero(h1, lead, bc):
    return f'<section class="page-hero"><div class="container">{bc}<h1>{E(h1)}</h1><p>{E(lead)}</p></div></section>'

def cta_band(depth, text="Ready to automate your production?"):
    p = "../" * depth
    return f'''<section class="cta-band"><div class="container">
  <h2>{E(text)}</h2><p>Share your part drawings, target output and current process. Our engineers will review them and reply with a clear proposal.</p>
  <a class="btn" href="{p}contact.html">Request a Quote</a>
  <a class="btn btn-wa" href="{WA_GENERAL}" target="_blank" rel="noopener">{waicon(20)} Chat on WhatsApp</a>
</div></section>'''

def faq_html(faqs):
    items = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    return f'<div class="faq">{items}</div>'

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)

def build_page(path, title, desc, active, body, extra="", noindex=False, og="website"):
    depth = path.count("/")
    write(path, head(title, desc, path, depth, extra, noindex, og) + header(active, depth)
          + '<main id="main">\n' + body + "\n</main>" + footer(depth))

def form_open(kind, subject, redirect="thank-you.html", attrs=""):
    return f'''<form class="js-form"{attrs} action="https://api.web3forms.com/submit" method="POST" data-redirect="{redirect}">
  <input type="hidden" name="access_key" value="{E(W3F)}">
  <input type="hidden" name="subject" value="{E(subject)}">
  <input type="hidden" name="from_name" value="{E(BRAND)} Website">
  <input type="hidden" name="form_type" value="{kind}">
  <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">'''

def product_card(x, p=""):
    return (f'<a class="card prod-card" href="{p}products/{x["slug"]}.html">{svg_icon(x["icon"], 44)}'
            f'<h3>{E(x["name"])}</h3><p>{E(x["short"])}</p><span class="more">Learn more &rarr;</span></a>')

# ---------- pages ----------
def home():
    cards = "".join(product_card(x) for x in PRODUCTS)
    inds = "".join(f'<li class="ind">{svg_icon(i, 34)}<div><h3>{E(n)}</h3><p>{E(d)}</p></div></li>' for n, i, d in INDUSTRIES)
    why = "".join(f'<div class="why"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in WHY)
    steps = "".join(f'<li><span class="num">{i+1}</span><h3>{E(t)}</h3><p>{E(d)}</p></li>' for i, (t, d) in enumerate(PROCESS))
    body = f'''<section class="hero"><div class="container hero-in">
  <div class="hero-text">
    <p class="eyebrow">{E(TAG)}</p>
    <h1>Your Trusted Partner for Industrial Automation and Robotic Systems</h1>
    <p class="lead">{E(BRAND)} designs, builds and commissions robotic welding, material handling, press line, vision inspection and battery assembly systems that raise quality, output and safety on your shop floor.</p>
    <p class="hero-btns"><a class="btn" href="contact.html">Request a Quote</a><a class="btn btn-ghost" href="products.html">Explore Solutions</a></p>
    <ul class="hero-points"><li>Turnkey design to commissioning</li><li>Validated before shipping</li><li>Training and after-sales support</li></ul>
  </div>
  <div class="hero-art" aria-hidden="true">
    <svg viewBox="0 0 420 340" class="robot">
      <rect x="40" y="290" width="340" height="14" rx="4" fill="#1d3b6b"/>
      <rect x="150" y="262" width="120" height="28" rx="6" fill="#2a4f8a"/>
      <rect x="185" y="200" width="50" height="62" fill="#335b9c"/>
      <circle cx="210" cy="196" r="22" fill="#ff6a13"/>
      <path d="M210 196 L120 120" stroke="#4f78b8" stroke-width="30" stroke-linecap="round"/>
      <circle cx="120" cy="120" r="18" fill="#ff6a13"/>
      <path d="M120 120 L250 60" stroke="#6b93d1" stroke-width="24" stroke-linecap="round"/>
      <circle cx="250" cy="60" r="14" fill="#ff6a13"/>
      <path d="M250 60 L300 110 L286 124" stroke="#9db9e4" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <g stroke="#ffd36b" stroke-width="3" stroke-linecap="round"><path d="M286 128 l-8 12 M286 128 l10 10 M286 128 l-14 2 M286 128 l4 14"/></g>
      <rect x="230" y="150" width="130" height="14" rx="3" fill="#1d3b6b" opacity=".0"/>
    </svg>
  </div>
</div></section>
<section class="strip"><div class="container strip-in"><span>Design</span><span>Build</span><span>Install</span><span>Train</span><span>Support</span></div></section>
<section><div class="container">
  <div class="section-title"><h2>Our Automation Solutions</h2><p>Eight core solution areas, each engineered around your part, cycle time and quality target.</p></div>
  <div class="grid grid-4">{cards}</div>
  <p class="center-note"><a class="btn" href="products.html">View All Products</a></p>
</div></section>
<section class="bg-light"><div class="container">
  <div class="section-title"><h2>Why Manufacturers Choose {E(BRAND)}</h2><p>Practical engineering, clear communication and support that continues after commissioning.</p></div>
  <div class="grid grid-3">{why}</div>
</div></section>
<section><div class="container">
  <div class="section-title"><h2>Industries We Serve</h2><p>We bring automation expertise to a wide range of manufacturing sectors.</p></div>
  <ul class="ind-grid">{inds}</ul>
</div></section>
<section class="bg-dark"><div class="container">
  <div class="section-title light"><h2>How We Deliver a Project</h2><p>A clear, five-step process keeps your project predictable.</p></div>
  <ol class="steps">{steps}</ol>
</div></section>
<section class="bg-light" id="home-testimonials" hidden><div class="container">
  <div class="section-title"><h2>What Our Customers Say</h2></div>
  <div class="testimonial-grid" data-testi="3"></div>
  <p class="center-note"><a class="btn btn-outline" href="testimonials.html">Read More Reviews</a></p>
</div></section>
<section><div class="container narrow">
  <div class="section-title"><h2>Frequently Asked Questions</h2></div>
  {faq_html(HOME_FAQS)}
</div></section>
{cta_band(0)}'''
    build_page("index.html", f"{BRAND} | Industrial Automation & Robotic Systems Manufacturer",
               f"{BRAND} designs and builds robotic welding, material handling, press line automation, vision inspection, battery assembly and special purpose machines. Request a quote today.",
               "index.html", body, jsonld(org_schema()) + faq_schema(HOME_FAQS))

def about():
    why = "".join(f'<div class="why"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in WHY)
    body = page_hero("About Us", f"Meet {BRAND}, your automation and robotics engineering partner.", crumbs([("About Us", None)], 0)) + f'''
<section><div class="container two-col">
  <div>
    <h2>Engineering Automation That Works on the Shop Floor</h2>
    <p>{E(BRAND)} is an industrial automation company focused on robotics, special purpose machines and precision jigs and fixtures. We help manufacturers replace manual, inconsistent processes with reliable automated systems.</p>
    <p>Our approach is practical. We study your parts, your process and your targets first, then engineer a solution that your team can run and maintain with confidence. We believe that good automation is simple to operate, safe by design and easy to extend as your production grows.</p>
    <p>Our engineers combine mechanical design, robot programming, controls and process knowledge under one roof. That lets us take full responsibility for a project, from the first discussion to commissioning and long-term support, and keep improving the systems we deliver as technology and markets change.</p>
  </div>
  <div class="panel"><h3>What we do</h3><ul class="tick">
    <li>Robotic arc and spot welding cells</li><li>Robotic material handling and palletizing</li><li>Press line automation</li><li>Vision and inspection systems</li><li>Battery assembly automation</li><li>Special purpose machines, jigs and fixtures</li></ul></div>
</div></section>
<section class="bg-light" id="vision-mission"><div class="container">
  <div class="section-title"><h2>Vision &amp; Mission</h2></div>
  <div class="grid grid-2">
    <div class="card plain"><h3>Our Vision</h3><p>To be a trusted automation partner for manufacturers, known for dependable systems, honest engineering and long-term relationships.</p></div>
    <div class="card plain"><h3>Our Mission</h3><p>To deliver automation that improves quality, productivity and safety, and to support every customer with clear communication, training and responsive service.</p></div>
  </div>
</div></section>
<section><div class="container">
  <div class="section-title"><h2>Why {E(BRAND)}</h2></div>
  <div class="grid grid-3">{why}</div>
</div></section>
<section class="bg-light"><div class="container narrow center">
  <h2>Explore More</h2>
  <p>See our <a href="products.html">automation solutions</a>, the <a href="industries.html">industries we serve</a>, our <a href="associations.html">associations</a>, or <a href="careers.html">join our team</a>.</p>
</div></section>
{cta_band(0)}'''
    build_page("about.html", f"About Us | {BRAND} Industrial Automation Company",
               f"Learn about {BRAND}, an industrial automation company building robotic welding, handling and special purpose machines with turnkey engineering and support.",
               "about.html", body, bc_schema([("Home", ""), ("About Us", "about.html")]))

def products():
    cards = "".join(product_card(x) for x in PRODUCTS)
    body = page_hero("Products & Solutions", "Industrial automation systems engineered around your parts and process.", crumbs([("Products", None)], 0)) + f'''
<section><div class="container">
  <div class="section-title"><h2>Industrial Automation Solutions</h2><p>Choose a solution to see features, applications and benefits.</p></div>
  <div class="grid grid-4">{cards}</div>
</div></section>
{cta_band(0, "Not sure which solution fits your part?")}'''
    lst = jsonld({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": x["name"], "url": f"{SITE_URL}/products/{x['slug']}.html"} for i, x in enumerate(PRODUCTS)]})
    build_page("products.html", f"Industrial Automation Products & Solutions | {BRAND}",
               f"Explore {BRAND} products: robotic arc welding, spot welding, material handling, manipulators, vision inspection, press line, battery assembly and special purpose machines.",
               "products.html", body, bc_schema([("Home", ""), ("Products", "products.html")]) + lst)

def product_pages():
    for x in PRODUCTS:
        others = "".join(f'<li><a href="{y["slug"]}.html">{E(y["name"])}</a></li>' for y in PRODUCTS if y is not x)
        li = lambda xs: "".join(f"<li>{E(i)}</li>" for i in xs)
        intro = "".join(f"<p>{E(t)}</p>" for t in x["intro"])
        body = page_hero(x["name"], x["short"], crumbs([("Products", "products.html"), (x["name"], None)], 1)) + f'''
<section><div class="container two-col">
  <div>
    <h2>Overview</h2>{intro}
    <h2>Key Features</h2><ul class="tick">{li(x["features"])}</ul>
    <h2>Typical Applications</h2><ul class="tick">{li(x["apps"])}</ul>
    <h2>Benefits</h2><ul class="tick">{li(x["benefits"])}</ul>
  </div>
  <aside>
    <div class="panel sticky"><div class="panel-ico">{svg_icon(x["icon"], 56)}</div>
      <h3>Get a Quote</h3><p>Tell us about your part and target output. We will respond with a proposal.</p>
      <a class="btn btn-block" href="../contact.html">Request a Quote</a>
      <a class="btn btn-wa btn-block" href="{wa(f"Hello {BRAND}, I need details about {x['name']}.")}" target="_blank" rel="noopener">{waicon(20)} WhatsApp Us</a>
      <h4>Other Solutions</h4><ul class="side-links">{others}</ul>
    </div>
  </aside>
</div></section>
<section class="bg-light"><div class="container narrow"><div class="section-title"><h2>Frequently Asked Questions</h2></div>{faq_html(x["faqs"])}</div></section>
{cta_band(1)}'''
        svc = jsonld({"@context": "https://schema.org", "@type": "Service", "name": x["name"], "description": x["desc"],
                      "provider": {"@type": "Organization", "name": BRAND, "url": SITE_URL + "/"}, "areaServed": "IN"})
        build_page(f"products/{x['slug']}.html", f"{x['title']} | {BRAND}", x["desc"], f"products/{x['slug']}.html", body,
                   bc_schema([("Home", ""), ("Products", "products.html"), (x["name"], f"products/{x['slug']}.html")]) + svc + faq_schema(x["faqs"]))

def industries():
    items = "".join(f'<li class="ind">{svg_icon(i, 40)}<div><h2>{E(n)}</h2><p>{E(d)}</p></div></li>' for n, i, d in INDUSTRIES)
    body = page_hero("Industries We Serve", "Automation expertise for demanding manufacturing sectors.", crumbs([("Industries", None)], 0)) + f'''
<section><div class="container">
  <div class="section-title"><h2>Automation for Every Production Environment</h2><p>Whatever you manufacture, we design systems around your parts, volumes and quality standards.</p></div>
  <ul class="ind-grid big">{items}</ul>
  <p class="center-note">Do not see your industry? <a href="contact.html">Talk to our engineers</a>, we are happy to review your process.</p>
</div></section>
{cta_band(0)}'''
    build_page("industries.html", f"Industries We Serve | Automation for Automotive, Railway, EV | {BRAND}",
               f"{BRAND} delivers industrial automation for automotive, railway, EV and battery, heavy engineering, agricultural equipment, consumer durables and fabrication industries.",
               "industries.html", body, bc_schema([("Home", ""), ("Industries", "industries.html")]))

def associations():
    body = page_hero("Associations", "The partners and organisations we work with.", crumbs([("Associations", None)], 0)) + f'''
<section><div class="container">
  <div class="section-title"><h2>Our Technology and Industry Partners</h2><p>We work with trusted robot, controls, vision and component suppliers so that every system we deliver is reliable and well supported.</p></div>
  <div class="assoc-grid" data-assoc>
    <div class="assoc-empty">Partner logos will appear here. Add them to <code>associations</code> in <code>js/config.js</code>.</div>
  </div>
  <p class="center-note">Interested in partnering with {E(BRAND)}? <a href="contact.html">Contact us</a>.</p>
</div></section>
{cta_band(0)}'''
    build_page("associations.html", f"Associations & Technology Partners | {BRAND}",
               f"See the technology partners and industry associations behind {BRAND} automation solutions, and get in touch about partnering with us.",
               "associations.html", body, bc_schema([("Home", ""), ("Associations", "associations.html")]))

def gallery():
    tiles = "".join(f'<figure class="g-tile ph">{svg_icon(x["icon"], 54)}<figcaption>{E(x["name"])}</figcaption></figure>' for x in PRODUCTS)
    body = page_hero("Gallery", "A look at our automation cells, lines and machines.", crumbs([("Gallery", None)], 0)) + f'''
<section><div class="container">
  <div class="section-title"><h2>Project Gallery</h2><p>Photos of our robotic cells and special purpose machines.</p></div>
  <div class="gallery" data-gallery>{tiles}</div>
  <p class="center-note small">Project photos are managed from <code>js/config.js</code> (gallery list).</p>
</div></section>
{cta_band(0)}'''
    build_page("gallery.html", f"Project Gallery | Robotic Cells & Automation Systems | {BRAND}",
               f"Browse the {BRAND} gallery of robotic welding cells, material handling systems, press line automation and special purpose machines.",
               "gallery.html", body, bc_schema([("Home", ""), ("Gallery", "gallery.html")]))

def careers():
    jobs = "".join(f'''<details class="job"><summary><span>{E(t)}</span><small>{E(exp)}</small></summary>
  <div class="job-body"><p><b>Experience:</b> {E(exp)}</p><p><b>Qualification:</b> {E(q)}</p><p><b>Role:</b> {E(r)}</p>
  <a class="btn btn-sm" href="#apply" data-role="{E(t, quote=True)}">Apply Now</a></div></details>''' for t, exp, q, r in JOBS)
    opts = "".join(f"<option>{E(t)}</option>" for t, *_ in JOBS) + "<option>Other / General application</option>"
    body = page_hero("Careers", f"Build your career in automation and robotics with {BRAND}.", crumbs([("Careers", None)], 0)) + f'''
<section><div class="container two-col">
  <div>
    <h2>Current Openings</h2>
    <p>We are always looking for curious, hands-on people who like solving real production problems. Select a role to see details.</p>
    <div class="jobs">{jobs}</div>
  </div>
  <aside id="apply"><div class="form-card">
    <h2>Apply Now</h2>
    {form_open("career", "New Job Application from Website", "thank-you.html?type=career")}
    <label for="a-name">Full name</label><input id="a-name" name="name" type="text" required autocomplete="name">
    <label for="a-phone">Phone</label><input id="a-phone" name="phone" type="tel" required autocomplete="tel">
    <label for="a-email">Email</label><input id="a-email" name="email" type="email" required autocomplete="email">
    <label for="a-role">Position</label><select id="a-role" name="position" required><option value="">Select</option>{opts}</select>
    <label for="a-exp">Total experience (years)</label><input id="a-exp" name="experience" type="text">
    <label for="a-link">Resume link (Google Drive, LinkedIn, etc.)</label><input id="a-link" name="resume_link" type="url" placeholder="https://">
    <label for="a-msg">Message</label><textarea id="a-msg" name="message" placeholder="Tell us briefly about yourself"></textarea>
    <button type="submit" class="btn btn-block">Submit Application</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form></div>
  <p class="small">You can also email your resume to <a data-c="mail" href="mailto:{E(EMAIL)}"><span data-c="email-text">{E(EMAIL)}</span></a>.</p>
  </aside>
</div></section>'''
    build_page("careers.html", f"Careers | Automation & Robotics Jobs | {BRAND}",
               f"Join {BRAND}. View openings for robotics programming, PLC controls, mechanical design, service, sales and technician roles, and apply online.",
               "careers.html", body, bc_schema([("Home", ""), ("Careers", "careers.html")]))

def testimonials():
    body = page_hero("Testimonials", "What customers and partners say about working with us.", crumbs([("Testimonials", None)], 0)) + f'''
<section><div class="container">
  <div class="testimonial-grid" data-testi="all"></div>
  <p class="empty-note" data-testi-empty>Customer reviews will appear here. Be the first to share your experience using the form below.</p>
</div></section>
<section class="bg-light" id="share-feedback"><div class="container narrow">
  <div class="section-title"><h2>Share Your Feedback</h2>
  <p>Worked with {E(BRAND)}? Tell us about your experience. Your review will appear on this page after a quick check.</p></div>
  <div class="form-card">
  {form_open("testimonial", "New Testimonial from Website", "thank-you.html?type=feedback", " data-testi-form")}
    <label for="t-name">Your name</label><input id="t-name" name="name" type="text" required autocomplete="name">
    <label for="t-role">Designation (optional)</label><input id="t-role" name="role" type="text" placeholder="e.g. Plant Manager">
    <label for="t-co">Company (optional)</label><input id="t-co" name="company" type="text" autocomplete="organization">
    <fieldset class="rating"><legend>Your rating</legend>
      <input type="radio" id="r5" name="rating" value="5" required><label for="r5" title="5 stars">&#9733;</label>
      <input type="radio" id="r4" name="rating" value="4"><label for="r4" title="4 stars">&#9733;</label>
      <input type="radio" id="r3" name="rating" value="3"><label for="r3" title="3 stars">&#9733;</label>
      <input type="radio" id="r2" name="rating" value="2"><label for="r2" title="2 stars">&#9733;</label>
      <input type="radio" id="r1" name="rating" value="1"><label for="r1" title="1 star">&#9733;</label>
    </fieldset>
    <label for="t-msg">Your feedback</label><textarea id="t-msg" name="message" required placeholder="How did our solution help your production?"></textarea>
    <label class="check"><input type="checkbox" name="consent" value="yes" required> I allow my name and feedback to be shown on this website.</label>
    <button type="submit" class="btn">Submit Feedback</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form></div>
</div></section>'''
    build_page("testimonials.html", f"Customer Testimonials & Reviews | {BRAND}",
               f"Read what customers say about {BRAND} automation solutions and share your own experience.",
               "testimonials.html", body, bc_schema([("Home", ""), ("Testimonials", "testimonials.html")]))

def contact():
    opts = "".join(f"<option>{E(x['name'])}</option>" for x in PRODUCTS) + "<option>Other / Not sure</option>"
    ahid = "" if ADDRESS else " hidden"
    body = page_hero("Contact Us", "Tell us about your project. We usually respond within one working day.", crumbs([("Contact Us", None)], 0)) + f'''
<section><div class="container two-col">
  <div>
    <h2>Get in Touch</h2>
    <p>Send us your part drawings, current cycle time and target output, and our engineers will prepare a proposal for you.</p>
    <ul class="contact-cards">
      <li><h3>Phone</h3><a data-c="tel" href="tel:+{PHONE}"><span data-c="phone-text">{PHONE_SHOW}</span></a></li>
      <li><h3>WhatsApp</h3><a href="{WA_GENERAL}" target="_blank" rel="noopener">Chat with us on WhatsApp</a></li>
      <li><h3>Email</h3><a data-c="mail" href="mailto:{E(EMAIL)}"><span data-c="email-text">{E(EMAIL)}</span></a></li>
      <li data-c="address-wrap"{ahid}><h3>Address</h3><span data-c="address">{E(ADDRESS).replace(chr(10), "<br>")}</span></li>
    </ul>
  </div>
  <div class="form-card">
    <h2>Request a Quote</h2>
    {form_open("contact", "New Enquiry from Website")}
    <label for="c-name">Full name</label><input id="c-name" name="name" type="text" required autocomplete="name">
    <label for="c-co">Company</label><input id="c-co" name="company" type="text" autocomplete="organization">
    <label for="c-phone">Phone</label><input id="c-phone" name="phone" type="tel" required autocomplete="tel">
    <label for="c-email">Email</label><input id="c-email" name="email" type="email" required autocomplete="email">
    <label for="c-int">I am interested in</label><select id="c-int" name="interest"><option value="">Select</option>{opts}</select>
    <label for="c-msg">Project details</label><textarea id="c-msg" name="message" required placeholder="Part, process, target output, timeline"></textarea>
    <button type="submit" class="btn btn-block">Send Enquiry</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form></div>
</div></section>'''
    build_page("contact.html", f"Contact Us | Request an Automation Quote | {BRAND}",
               f"Contact {BRAND} for robotic welding, material handling and special purpose machine enquiries. Call {PHONE_SHOW}, WhatsApp or send an enquiry online.",
               "contact.html", body, bc_schema([("Home", ""), ("Contact Us", "contact.html")]))

def legal():
    priv = f'''<p>Last updated: {TODAY}</p>
<p>{E(BRAND)} ("we", "us") respects your privacy. This policy explains how we handle information you submit through this website.</p>
<h2>Information we collect</h2><p>When you use our contact, careers or feedback forms, we collect the details you enter, such as your name, phone number, email address, company, and message. Form submissions are delivered to us through the Web3Forms service. Reviews you choose to share may be stored in a Google Sheet that we control.</p>
<h2>How we use it</h2><p>We use your information to respond to enquiries, evaluate job applications, and, with your consent, display your feedback on this website. We do not sell your personal information.</p>
<h2>Cookies and analytics</h2><p>This website does not set tracking cookies of its own.</p>
<h2>Your choices</h2><p>You may ask us to correct or delete the information you submitted, or to remove a published review, by contacting us at <a data-c="mail" href="mailto:{E(EMAIL)}"><span data-c="email-text">{E(EMAIL)}</span></a>.</p>'''
    terms = f'''<p>Last updated: {TODAY}</p>
<p>By using this website you agree to these terms.</p>
<h2>Information on this website</h2><p>The content on this website is provided for general information about {E(BRAND)} and its solutions. Specifications and offerings may change. A binding offer is made only through a written quotation.</p>
<h2>Intellectual property</h2><p>The text, design and graphics of this website belong to {E(BRAND)} unless stated otherwise. Please do not copy them without permission.</p>
<h2>User submissions</h2><p>If you submit a review, you confirm that it is truthful, that it is your own, and that we may display it on this website. We may edit or decline to publish any submission.</p>
<h2>Limitation of liability</h2><p>We make reasonable efforts to keep this website accurate and available but provide it without warranties. We are not liable for loss arising from its use.</p>
<h2>Contact</h2><p>Questions about these terms: <a data-c="mail" href="mailto:{E(EMAIL)}"><span data-c="email-text">{E(EMAIL)}</span></a>.</p>'''
    for slug, h1, text, d in (("privacy-policy", "Privacy Policy", priv, f"How {BRAND} collects and uses information submitted through its website forms."),
                              ("terms", "Terms of Use", terms, f"Terms for using the {BRAND} website.")):
        body = page_hero(h1, f"{BRAND}", crumbs([(h1, None)], 0)) + f'<section><div class="container narrow article">{text}</div></section>'
        build_page(f"{slug}.html", f"{h1} | {BRAND}", d, "", body, bc_schema([("Home", ""), (h1, f"{slug}.html")]))

def thankyou():
    body = '''<section class="page-hero"><div class="container"><h1 id="ty-title">Thank you!</h1><p id="ty-text">We have received your message and will get back to you shortly.</p></div></section>
<section><div class="container narrow center"><p><a class="btn" href="index.html">Back to Home</a> <a class="btn btn-outline" href="products.html">Explore Solutions</a></p></div></section>'''
    build_page("thank-you.html", f"Thank You | {BRAND}", f"Thank you for contacting {BRAND}.", "", body, noindex=True)

def notfound():
    # absolute paths so it works from any URL depth on GitHub Pages
    html_ = head(f"Page Not Found | {BRAND}", "The page you are looking for could not be found.", "404.html", 0, noindex=True)
    html_ += header("", 0) + '<main id="main"><section class="page-hero"><div class="container"><h1>Page not found</h1><p>The page you are looking for does not exist or has moved.</p></div></section><section><div class="container narrow center"><p><a class="btn" href="index.html">Go to Home</a></p></div></section></main>' + footer(0)
    if BASE:
        html_ = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|data:)([^"]+)"', lambda m: f'{m.group(1)}="{BASE}/{m.group(2)}"', html_)
    write("404.html", html_)

def seo_files():
    urls = ["index.html", "about.html", "products.html"] + [f"products/{p['slug']}.html" for p in PRODUCTS] + \
           ["industries.html", "associations.html", "gallery.html", "careers.html", "testimonials.html", "contact.html", "privacy-policy.html", "terms.html"]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        loc = SITE_URL + "/" + ("" if u == "index.html" else u)
        pr = "1.0" if u == "index.html" else ("0.8" if u in ("products.html", "contact.html", "about.html") or u.startswith("products/") else "0.6")
        xml += f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n"
    write("sitemap.xml", xml + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write(".nojekyll", "")

if __name__ == "__main__":
    home(); about(); products(); product_pages(); industries(); associations(); gallery(); careers()
    testimonials(); contact(); legal(); thankyou(); notfound(); seo_files()
    print("Site built in", ROOT)
