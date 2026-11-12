#!/usr/bin/env python3
"""Build the Lawnix static site from content.py into ../docs (GitHub Pages).

Run:  python3 site/build.py
"""
from __future__ import annotations

import html
import os
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402

OUT = HERE.parent / "docs"
STATIC = HERE / "static"
S = C.SITE
E = html.escape


def asset_v(rel: str) -> str:
    """Short content hash so browsers refetch CSS/JS after every deploy."""
    import hashlib
    return hashlib.sha1((STATIC / rel).read_bytes()).hexdigest()[:8]


def money(v: float) -> str:
    return f"${v:,.2f}"


def product_url(p) -> str:
    return f"/products/{p['slug']}/"


def buy_href(p) -> str:
    link = S["stripe_links"].get(p["id"], "")
    return link or "/contact/"


def amazon_href(p) -> str:
    import re
    asin = S["amazon_asins"].get(p["id"], "").strip()
    # Only a real 10-character ASIN makes a button; anything else is ignored.
    return f"https://www.amazon.com/dp/{asin}" if re.fullmatch(r"[A-Z0-9]{10}", asin) else ""


def warranty_ok() -> bool:
    return bool(S.get("warranty_confirmed"))


def track(event: str, placement: str, p=None) -> str:
    """data-* hooks read by lawnix.js and pushed to window.dataLayer."""
    attrs = f' data-track="{event}" data-placement="{placement}"'
    if p:
        attrs += f' data-product="{p["sku"]}" data-value="{p["price"]:.2f}"'
    return attrs


# ---------- shell ----------

def head(title: str, desc: str, path: str, image: str = "/static/img/og-default.jpg", schema: str = "") -> str:
    url = S["domain"] + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Lawnix">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{S['domain']}{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0c0a">
<link rel="icon" href="/static/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/static/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/static/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,700;0,800;1,800;1,900&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.1/src/regular/style.css">
<link rel="stylesheet" href="/static/css/lawnix.css?v={asset_v('css/lawnix.css')}">
{schema}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="header">
  <div class="wrap">
    <a class="logo" href="/" aria-label="Lawnix home"><img class="logo-img" src="/static/img/logo-wordmark.svg" alt="Lawnix" width="1260" height="205"></a>
    <nav class="nav" aria-label="Main">
      {''.join(f'<a href="{h}">{E(t)}</a>' for t, h in C.NAV)}
      <a class="btn btn-primary btn-sm" href="{buy_href(C.PRODUCTS[0])}"{track("buy_click", "header", C.PRODUCTS[0])}>Buy now <span class="btn-price">{money(C.PRODUCTS[0]['price'])}</span></a>
    </nav>
    <button class="menu-btn" aria-label="Menu" aria-expanded="false"><i class="ph ph-list" aria-hidden="true"></i></button>
  </div>
</header>
<main id="main">
"""


def footer() -> str:
    cols = "".join(
        f"<div><h4>{E(k)}</h4><ul>" + "".join(f'<li><a href="{h}">{E(t)}</a></li>' for t, h in v) + "</ul></div>"
        for k, v in C.FOOTER_LINKS.items()
    )
    return f"""</main>
<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="logo" href="/" aria-label="Lawnix home"><img class="logo-img" src="/static/img/logo-wordmark.svg" alt="Lawnix" width="1260" height="205" loading="lazy"></a>
        <p>{E(S['tagline'])} Stainless lawn and garden tools from {E(S['legal_name'])}.</p>
        <p><a href="mailto:{S['email']}">{S['email']}</a></p>
      </div>
      {cols}
    </div>
    <div class="footer-bottom">
      <span>&copy; {S['year']} {E(S['legal_name'])}. All rights reserved.</span>
      <span>Lawnix is a trademark of {E(S['legal_name'])}.</span>
    </div>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/static/js/lawnix.js?v={asset_v('js/lawnix.js')}" defer></script>
<script src="/static/js/motion.js?v={asset_v('js/motion.js')}" defer></script>
</body>
</html>
"""


def page(path: str, title: str, desc: str, body: str, image: str = "/static/img/og-default.jpg", schema: str = "") -> None:
    dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(head(title, desc, path, image, schema) + body + footer(), encoding="utf-8")
    PAGES.append(path)


PAGES: list[str] = []


# ---------- blocks ----------

def product_card(p, big=False) -> str:
    img = p.get("card_image_big", p["image"]) if big else p["image"]
    return f"""<article class="card reveal">
  <div class="card-media"><img src="/static/img/{img}" alt="{E(p['image_alt'])}" loading="lazy" width="1200" height="900"></div>
  <div class="card-body">
    <span class="kicker">{E(p['kicker'])}</span>
    <div class="row"><h3>{E(p['short'])}</h3><span class="price">{money(p['price'])}<s>{money(p['compare'])}</s></span></div>
    <p>{E(p['summary'])}</p>
    <a class="card-link" href="{product_url(p)}" aria-label="View {E(p['name'])}"></a>
  </div>
</article>"""


def lineup() -> str:
    return f"""<section class="section" id="shop">
  <div class="wrap">
    <div class="section-head reveal"><h2>Three tools. <span class="em">One flat lawn.</span></h2>
      <p class="lede">Start with the rake that fits your yard, then add the cultivator for beds and bare spots.</p></div>
    <div class="lineup">{''.join(product_card(p, big=(i == 0)) for i, p in enumerate(C.PRODUCTS))}</div>
  </div>
</section>"""


def ticker() -> str:
    items = ["<b>304</b> stainless steel", "<b>30</b> and <b>48</b> inch plates", "<b>78</b> inch handle", "tool-free assembly",
             "center mount, anti-flip", "ships from US warehouses", "<b>30</b>-day returns", "<b>10</b> inch deep plate"]
    row = "".join(f"<span>{i}</span>" for i in items)
    return f'<div class="ticker" aria-hidden="true"><div class="ticker-track"><div class="ticker-row">{row}</div><div class="ticker-row">{row}</div></div></div>'


def exploded() -> str:
    art = (HERE / "templates" / "rake.svg").read_text()
    parts = [
        ("01", "Plate", "30 x 10 inch 304 stainless frame. The size that floats over grass instead of digging in."),
        ("02", "Bars", "Three parallel bars, spot welded. They cut the sand into an even layer on every pass."),
        ("03", "Center mount", "Handle meets plate in the middle so it tracks straight and never rolls over on the pull."),
        ("04", "Lower handle", "Satin stainless tube. Threads into the mount by hand, no tools."),
        ("05", "Upper handle", "Second section brings the reach to 78 inches, or stop at 50 for tight spots."),
        ("06", "Grip", "Non-slip lime grip. Dry hands or wet, it stays put."),
    ]
    labels = "".join(f'<div class="exploded-label{" on" if i == 0 else ""}"><span class="num">{n}</span><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (n, t, d) in enumerate(parts))
    return f"""<section class="exploded" id="engineered" aria-labelledby="eng-h">
  <div class="wrap">
    <div class="exploded-copy">
      <h2 id="eng-h">Six parts. <span class="em">No weak one.</span></h2>
      <p class="lede">Scroll to assemble the LX-30. Every part is there for a reason, and none of them is painted steel.</p>
      <div class="exploded-labels">{labels}</div>
      <div class="exploded-readout">Assembly <b>0%</b></div>
    </div>
    <div>
      <div class="exploded-art">{art}</div>
      <p class="exploded-note">Technical drawing, not to scale</p>
    </div>
  </div>
</section>"""


def why_band() -> str:
    cols = "".join(f'<div class="reveal" data-delay="{i}"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (t, d) in enumerate(C.WHY))
    return f"""<section class="band" aria-labelledby="why-h">
  <img src="/static/img/lifestyle-lawn.jpg" alt="Freshly leveled lawn with a stripe pattern" loading="lazy" width="1800" height="1000">
  <div class="wrap">
    <h2 id="why-h" class="reveal">Why level <span class="em">at all?</span></h2>
    <div class="why-grid">{cols}</div>
  </div>
</section>"""


def build_bento() -> str:
    tiles = []
    for i, item in enumerate(C.BUILD, 1):
        t, d = item[0], item[1]
        img = item[2] if len(item) > 2 else None
        cls = f"tile tile-{i} reveal" + (" has-img" if img else "")
        im = f'<img src="/static/img/{img}" alt="" loading="lazy" width="1200" height="900">' if img else ""
        tiles.append(f'<div class="{cls}">{im}<h3>{E(t)}</h3><p>{E(d)}</p></div>')
    return f"""<section class="section" id="build">
  <div class="wrap">
    <div class="section-head reveal"><h2>Built like a <span class="em">pro tool</span></h2>
      <p class="lede">The parts that matter on a leveling rake, and why we built them this way.</p></div>
    <div class="bento">{''.join(tiles)}</div>
  </div>
</section>"""


def steps() -> str:
    items = "".join(f'<div class="step reveal" data-delay="{i % 4}"><div class="num">{i + 1}</div><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (t, d) in enumerate(C.STEPS))
    return f"""<section class="section-tight" id="how">
  <div class="wrap">
    <div class="section-head reveal"><h2>Level a lawn in <span class="em">four passes</span></h2></div>
    <div class="steps">{items}</div>
    <p style="margin-top:28px"><a class="btn btn-ghost" href="/guides/{C.GUIDE['slug']}/">Read the full guide <i class="ph ph-arrow-right" aria-hidden="true"></i></a></p>
  </div>
</section>"""


def compare() -> str:
    a, b = C.PRODUCTS[0], C.PRODUCTS[1]

    def col(p, width):
        return f"""<a href="{product_url(p)}" class="reveal">
      <div class="big">{width}<small>inch</small></div>
      <h3>{E(p['short'])}</h3>
      <dl><dt>Best for</dt><dd>{E(p['best_for'])}</dd><dt>Weight</dt><dd>{E(p['specs'][3][1])}</dd><dt>Price</dt><dd>{money(p['price'])}</dd></dl>
      <span class="cta">View the {E(p['sku'])} <i class="ph ph-arrow-right" aria-hidden="true"></i></span>
    </a>"""

    bars = f"""<div class="wbars reveal">
      <div class="wbar"><span class="name">{E(a['sku'])}</span><div class="wbar-track"><div class="wbar-fill" data-pct="62.5"></div></div><span class="val"><span data-count="30">0</span><small>in</small></span></div>
      <div class="wbar"><span class="name">{E(b['sku'])}</span><div class="wbar-track"><div class="wbar-fill" data-pct="100"></div></div><span class="val"><span data-count="48">0</span><small>in</small></span></div>
    </div>"""
    return f"""<section class="section" id="sizes">
  <div class="wrap">
    <div class="section-head reveal"><h2>Pick your <span class="em">width</span></h2>
      <p class="lede">Same stainless plate, same 78-inch handle. The only question is how much lawn you cover per pass.</p></div>
    {bars}
    <div class="compare" style="margin-top:28px">{col(a, 30)}{col(b, 48)}</div>
  </div>
</section>"""


def faq_block(items, heading=True) -> str:
    qs = "".join(f'<details><summary>{E(q)}<i class="ph ph-plus" aria-hidden="true"></i></summary><p>{E(a)}</p></details>' for q, a in items)
    h = '<div class="section-head reveal"><h2>Questions, <span class="em">answered</span></h2></div>' if heading else ""
    return f'<section class="section" id="faq"><div class="wrap">{h}<div class="faq reveal">{qs}</div></div></section>'


def signup() -> str:
    ep = S["form_endpoint"]
    return f"""<section class="section-tight">
  <div class="wrap">
    <div class="signup reveal">
      <div><h2 style="font-size:clamp(30px,3.6vw,46px)">Get the launch price</h2>
        <p class="lede" style="margin-top:12px">Join the list for launch pricing, lawn leveling tips and first word on new tools.</p></div>
      <form data-signup data-endpoint="{E(ep)}" data-mail="{S['email']}" action="{E(ep) or '#'}" method="post">
        <label for="signup-email">Email address</label>
        <div class="field"><input id="signup-email" name="email" type="email" required placeholder="you@example.com" autocomplete="email">
          <button class="btn btn-primary" type="submit">Join the list</button></div>
        <p class="form-msg" aria-live="polite"></p>
        <p class="form-note">No spam. Unsubscribe any time.</p>
      </form>
    </div>
  </div>
</section>"""


# ---------- pages ----------

# ---------- LX-30 landing (home) ----------

def lawn_profile_svg(after: bool) -> str:
    """Cross-section illustration of a lawn, before or after leveling. Not a photo."""
    import math
    W, H, top = 1200, 360, 168
    knots = [178, 172, 214, 246, 222, 182, 170, 190, 238, 252, 214, 176, 180]
    def y(x):
        f = x / 100; i = min(int(f), len(knots) - 2); t = f - i
        t = (1 - math.cos(t * math.pi)) / 2
        return knots[i] * (1 - t) + knots[i + 1] * t
    xs = list(range(0, W + 1, 8))
    prof = [(x, y(x)) for x in xs]
    soil = "M0 " + f"{H} " + " ".join(f"L{x} {v:.1f}" for x, v in prof) + f" L{W} {H} Z"
    out = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">',
           f'<rect width="{W}" height="{H}" fill="#e9ebe2"/>']
    if after:
        out.append(f'<path d="{soil}" class="lp-soil"/>')
        # sand layer sits on top of the soil in the dips
        sand = f"M0 {top} L{W} {top} " + " ".join(f"L{x} {max(v, top):.1f}" for x, v in reversed(prof)) + " Z"
        out.append(f'<path d="{sand}" class="lp-sand"/>')
        surface = [(x, top) for x in xs]
    else:
        lvl = 218
        segs, cur = [], []
        for x, v in prof:
            if v > lvl: cur.append((x, v))
            elif cur: segs.append(cur); cur = []
        if cur: segs.append(cur)
        out.append(f'<path d="{soil}" class="lp-soil"/>')
        for seg in segs:
            d = f"M{seg[0][0]} {lvl} " + " ".join(f"L{x} {v:.1f}" for x, v in seg) + f" L{seg[-1][0]} {lvl} Z"
            out.append(f'<path d="{d}" class="lp-water"/>')
        surface = prof
    blades = []
    for x, v in surface[::2]:
        h = 14 + (x * 7919 % 11)
        lean = ((x * 31) % 9) - 4
        blades.append(f"M{x} {v:.1f} l{lean} -{h}")
    out.append(f'<path d="{" ".join(blades)}" class="lp-grass"/>')
    out.append("</svg>")
    return "".join(out)


def before_after() -> str:
    tags_before = '<span class="ba-tag" style="left:30%;top:30%">Standing water</span><span class="ba-tag" style="left:12%;top:16%">Scalped high spot</span>'
    tags_after = '<span class="ba-tag ba-tag-lime" style="left:63%;top:13%">Dips filled with sand</span><span class="ba-tag ba-tag-lime" style="left:84%;top:13%">One level surface</span>'
    return f"""<figure class="ba reveal" data-ba>
      <div class="ba-stage">
        <div class="ba-layer">{lawn_profile_svg(False)}{tags_before}</div>
        <div class="ba-layer ba-after">{lawn_profile_svg(True)}{tags_after}</div>
        <span class="ba-label ba-label-l">Before</span><span class="ba-label ba-label-r">After</span>
        <span class="ba-handle" aria-hidden="true"><i class="ph ph-arrows-left-right"></i></span>
        <input class="ba-range" type="range" min="0" max="100" value="50" aria-label="Compare the lawn before and after leveling">
      </div>
      <figcaption>Illustration of a lawn cross-section. Drag to level it. Product photos follow below.</figcaption>
    </figure>"""


def trust_row(dark: bool = True) -> str:
    items = [("truck", S["shipping"]), ("arrow-u-up-left", S["returns"]), ("lock-simple", "Secure checkout by Stripe")]
    if warranty_ok():
        items.append(("shield-check", S["warranty"]))
    return '<ul class="trust">' + "".join(f'<li><i class="ph ph-{i}" aria-hidden="true"></i>{E(t)}</li>' for i, t in items) + "</ul>"


def buy_button(p, placement: str, label: str = "Buy the LX-30", cls: str = "btn btn-primary btn-lg") -> str:
    rel = ' rel="noopener"' if S["stripe_links"].get(p["id"]) else ""
    return f'<a class="{cls}" href="{buy_href(p)}"{rel}{track("buy_click", placement, p)}>{E(label)} <i class="ph ph-arrow-right" aria-hidden="true"></i></a>'


def price_tag(p) -> str:
    save = p["compare"] - p["price"]
    return f"""<div class="price-tag"><span class="now">{money(p['price'])}</span><span class="was"><s>{money(p['compare'])}</s> list</span><span class="flag">Launch price, save {money(save)}</span></div>"""


def landing_hero(p) -> str:
    L = C.LANDING
    return f"""<section class="lp-hero" data-section="hero">
  <div class="wrap">
    <div class="lp-hero-copy">
      <p class="eyebrow reveal in">{E(L['eyebrow'])}</p>
      <h1 class="reveal in" data-delay="1">{E(L['h1'][0])} <span class="em">{E(L['h1'][1])}</span></h1>
      <p class="lede reveal in" data-delay="2">{E(L['lede'])}</p>
      <div class="lp-buy reveal in" data-delay="3">
        {price_tag(p)}
        <div class="lp-buy-actions">{buy_button(p, 'hero')}<a class="text-link" href="#how"{track('nav_click', 'hero_how')}>See how it works <i class="ph ph-arrow-down" aria-hidden="true"></i></a></div>
      </div>
      <div class="reveal in" data-delay="3">{trust_row()}</div>
    </div>
    <div class="lp-hero-media reveal in" data-delay="1">
      <div class="lp-hero-frame">
        <img src="/static/img/hero.jpg" alt="Lawnix LX-30 leveling rake spreading sand across a lawn at sunset" width="1024" height="1280" fetchpriority="high">
        <div class="hero-scan"></div>
        <svg class="hero-bp" viewBox="0 0 400 500" preserveAspectRatio="none" aria-hidden="true">
          <path class="bp-corner" d="M14 44 V14 H44 M356 14 H386 V44 M386 456 V486 H356 M44 486 H14 V456"/>
          <path class="bp-line" d="M60 470 H340 M60 462 V478 M340 462 V478"/>
          <path class="bp-line" d="M372 120 V440 M364 120 H380 M364 440 H380"/>
          <text class="bp-tag accent" x="200" y="492" text-anchor="middle">30 in plate</text>
          <text class="bp-tag" x="372" y="110" text-anchor="middle">78 in</text>
        </svg>
      </div>
      <div class="lp-hero-stats" aria-label="Key specs">
        <div><b data-count="304">304</b><span>stainless</span></div>
        <div><b data-count="30">30</b><span>inch plate</span></div>
        <div><b data-count="5.2">5.2</b><span>pounds</span></div>
      </div>
    </div>
  </div>
</section>"""


def landing_problem() -> str:
    L = C.LANDING
    items = "".join(f'<li class="reveal" data-delay="{i}"><span class="n">0{i + 1}</span><div><h3>{E(t)}</h3><p>{E(d)}</p></div></li>' for i, (t, d) in enumerate(L["problems"]))
    return f"""<section class="paper slant" id="problem" data-section="problem">
  <div class="wrap">
    <div class="split">
      <div class="reveal"><p class="eyebrow">The problem</p><h2>A bumpy lawn <span class="em">costs you</span> every mow.</h2></div>
      <ol class="problems">{items}</ol>
    </div>
    {before_after()}
  </div>
</section>"""


def landing_benefits() -> str:
    rows = []
    for i, (t, d, img, alt, proof) in enumerate(C.LANDING["benefits"]):
        chips = "".join(f'<div><b>{E(v)}</b><span>{E(k)}</span></div>' for v, k in proof)
        rows.append(f"""<article class="benefit reveal{' flip' if i % 2 else ''}">
      <div class="benefit-media"><img src="/static/img/{img}" alt="{E(alt)}" loading="lazy" width="1200" height="900"><span class="benefit-n">0{i + 1}</span></div>
      <div class="benefit-copy"><h3>{E(t)}</h3><p>{E(d)}</p><div class="proof">{chips}</div></div>
    </article>""")
    return f"""<section class="paper slant" id="benefits" data-section="benefits">
  <div class="wrap">
    <div class="section-head reveal"><p class="eyebrow">Why the LX-30</p><h2>Built to do one job <span class="em">properly.</span></h2></div>
    <div class="benefits">{''.join(rows)}</div>
  </div>
</section>"""


def landing_how(p) -> str:
    items = "".join(f'<li class="how-step reveal" data-delay="{i}"><span class="how-dot">{i + 1}</span><h3>{E(t)}</h3><p>{E(d)}</p></li>' for i, (t, d) in enumerate(C.LANDING["steps"]))
    return f"""<section class="lp-how slant-dark" id="how" data-section="how">
  <div class="wrap">
    <div class="section-head reveal"><p class="eyebrow">How it works</p><h2>Spread. Pull. Level. <span class="em">Finish.</span></h2>
      <p class="lede">Four moves, repeated across the lawn. Most home lawns take one afternoon.</p></div>
    <div class="how-track" aria-hidden="true"><span class="how-fill"></span></div>
    <ol class="how">{items}</ol>
    <div class="how-foot reveal">{buy_button(p, 'how', 'Get yours')}<a class="text-link" href="/guides/{C.GUIDE['slug']}/">Read the full leveling guide <i class="ph ph-arrow-right" aria-hidden="true"></i></a></div>
  </div>
</section>"""


def landing_proof() -> str:
    if C.REVIEWS:
        cards = "".join(
            f'<figure class="review reveal"><div class="stars" aria-label="{r[2]} out of 5 stars">' + "".join('<i class="ph-fill ph-star" aria-hidden="true"></i>' for _ in range(r[2])) +
            f'</div><blockquote>{E(r[3])}</blockquote><figcaption>{E(r[0])}<span>{E(r[1])} · Verified buyer</span></figcaption></figure>'
            for r in C.REVIEWS)
        intro = "What owners say"
        note = ""
    else:
        cards = "".join(
            f'<div class="review review-slot reveal" data-delay="{i}"><span class="slot-tag">Placeholder</span><div class="stars dim" aria-hidden="true">' + "".join('<i class="ph ph-star"></i>' for _ in range(5)) +
            '</div><p>Verified buyer review will appear here after the first deliveries.</p></div>'
            for i in range(3))
        intro = "Reviews open after launch"
        note = '<p class="proof-note">We only publish reviews from verified buyers. No paid, gifted or invented reviews, ever.</p>'
    facts = [("304 stainless steel plate and frame", "check-circle"), ("30-day returns from delivery", "check-circle"),
             ("Checkout handled by Stripe", "check-circle"), (S["shipping"], "check-circle")]
    fact_list = "".join(f'<li><i class="ph ph-{ic}" aria-hidden="true"></i>{E(t)}</li>' for t, ic in facts)
    return f"""<section class="paper slant" id="proof" data-section="proof">
  <div class="wrap">
    <div class="split">
      <div class="reveal"><p class="eyebrow">Proof</p><h2>{E(intro)}</h2>{note}
        <h3 class="facts-h">What you can count on today</h3><ul class="facts">{fact_list}</ul></div>
      <div class="reviews">{cards}</div>
    </div>
  </div>
</section>"""


def landing_objections(p) -> str:
    cells = []
    for i, (q, a, link) in enumerate(C.LANDING["objections"]):
        more = f'<a class="text-link" href="{link[1]}">{E(link[0])} <i class="ph ph-arrow-right" aria-hidden="true"></i></a>' if link else ""
        cells.append(f'<div class="obj reveal" data-delay="{i % 2}"><h3>{E(q)}</h3><p>{E(a)}</p>{more}</div>')
    skip = {"Which size should I buy?", "How long does assembly take?", "Can I return it?"}
    qs = "".join(f'<details><summary>{E(q)}<i class="ph ph-plus" aria-hidden="true"></i></summary><p>{E(a)}</p></details>' for q, a in C.FAQ if q not in skip)
    return f"""<section class="paper alt" id="faq" data-section="faq">
  <div class="wrap">
    <div class="section-head reveal"><p class="eyebrow">Before you buy</p><h2>The honest <span class="em">answers.</span></h2></div>
    <div class="objs">{''.join(cells)}</div>
    <div class="faq faq-light reveal">{qs}</div>
  </div>
</section>"""


def landing_final(p) -> str:
    L = C.LANDING
    return f"""<section class="lp-final" id="buy" data-section="final">
  <img class="lp-final-bg" src="/static/img/lifestyle-lawn.jpg" alt="" loading="lazy" width="1536" height="864">
  <div class="wrap">
    <div class="lp-final-card reveal">
      <div class="lp-final-copy">
        <h2>{E(L['final_h'][0])} <span class="em">{E(L['final_h'][1])}</span></h2>
        <p class="lede">{E(L['final_lede'])}</p>
        {price_tag(p)}
        <div class="lp-buy-actions">{buy_button(p, 'final', 'Buy now')}</div>
        {trust_row()}
      </div>
      <div class="lp-final-product"><img src="/static/img/{p['image']}" alt="{E(p['image_alt'])}" loading="lazy" width="1024" height="1024"></div>
    </div>
  </div>
</section>"""


def sticky_cta(p) -> str:
    return f"""<div class="sticky-buy" data-sticky hidden>
  <div class="sticky-info"><b>{E(p['sku'])}</b><span>{money(p['price'])} <s>{money(p['compare'])}</s></span></div>
  {buy_button(p, 'sticky_mobile', 'Buy now', 'btn btn-primary')}
</div>"""


def home() -> None:
    p = C.PRODUCTS[0]
    body = f"""{landing_hero(p)}
{ticker()}
{landing_problem()}
{exploded()}
{landing_benefits()}
{landing_how(p)}
{landing_proof()}
{landing_objections(p)}
{landing_final(p)}
{sticky_cta(p)}"""
    schema = org_schema() + f"""<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Product","name":{json_s(p['name'])},"sku":"{p['sku']}","brand":{{"@type":"Brand","name":"Lawnix"}},"description":{json_s(p['summary'])},"image":"{S['domain']}/static/img/{p['image']}","offers":{{"@type":"Offer","priceCurrency":"USD","price":"{p['price']:.2f}","availability":"https://schema.org/PreOrder","url":"{S['domain']}/"}}}}</script>"""
    page("/", "Lawnix LX-30 Lawn Leveling Rake | Flat Lawn in One Afternoon",
         "The Lawnix LX-30 is a 30-inch, 304 stainless steel lawn leveling rake. Spread sand into low spots, skim the bumps and get a flat lawn in one afternoon.",
         body, "/static/img/hero.jpg", schema)


def shop() -> None:
    body = f"""<section class="section page-head">
  <div class="wrap">
    <div class="section-head"><h1>Shop <span class="em">Lawnix</span></h1><p class="lede">Every tool ships from US warehouses. {E(S['returns'])}.{(' ' + E(S['warranty']) + '.') if warranty_ok() else ''}</p></div>
    <div class="lineup">{''.join(product_card(p, big=(i == 0)) for i, p in enumerate(C.PRODUCTS))}</div>
  </div>
</section>
{compare()}
{signup()}"""
    page("/shop/", "Shop Lawn Leveling Rakes and Garden Tools | Lawnix", "Buy the Lawnix LX-30 and LX-48 stainless steel lawn leveling rakes and the RC-01 rotary cultivator.", body)


def product_page(p) -> None:
    stripe = S["stripe_links"].get(p["id"], "")
    amz = amazon_href(p)
    buy_label = f"Buy now, {money(p['price'])}" if stripe else "Ask about availability"
    rel = ' rel="noopener"' if stripe else ""
    actions = f'<a class="btn btn-primary btn-block" href="{buy_href(p)}"{rel}{track("buy_click", "product_page", p)}>{E(buy_label)}</a>'
    if amz:
        actions += f'<a class="btn btn-amazon btn-block" href="{amz}" rel="noopener"><i class="ph ph-amazon-logo" aria-hidden="true"></i>Buy on Amazon</a>'
    save = int(round((1 - p["price"] / p["compare"]) * 100))
    spec_cards = "".join(f'<div class="spec-card"><span class="label">{E(l)}</span><span class="value">{E(v)}</span><span class="why">{E(w)}</span></div>' for l, v, w in p["specs"])
    more = "".join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k, v in p["more_specs"])
    inbox = "".join(f'<li><i class="ph ph-check" aria-hidden="true"></i>{E(i)}</li>' for i in p["in_box"])
    others = [q for q in C.PRODUCTS if q["id"] != p["id"]]
    gallery_imgs = [p["image"], f"{p['id']}-detail.jpg", "lifestyle-sand.jpg"]
    thumbs = "".join(
        f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}" aria-label="Image {i + 1}"><img src="/static/img/{g}" data-full="/static/img/{g}" alt="{E(p["image_alt"]) if i == 0 else E(p["short"]) + " detail"}" loading="lazy" width="300" height="300"></button>'
        for i, g in enumerate(gallery_imgs)
    )
    body = f"""<section class="wrap pdp">
  <div class="gallery">
    <div class="gallery-main"><img src="/static/img/{p['image']}" alt="{E(p['image_alt'])}" width="1200" height="1200" fetchpriority="high"></div>
    <div class="gallery-thumbs">{thumbs}</div>
  </div>
  <div class="buy">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/shop/">Shop</a><i class="ph ph-caret-right" aria-hidden="true"></i><span>{E(p['sku'])}</span></nav>
    <h1>{E(p['name'])}</h1>
    <p class="lede">{E(p['summary'])}</p>
    <div class="price-row"><span class="now">{money(p['price'])}</span><s>{money(p['compare'])}</s><span class="save">Save {save}%</span></div>
    <div class="buy-actions">{actions}</div>
    <div class="assure">
      <div><i class="ph ph-truck" aria-hidden="true"></i>{E(S['shipping'])}</div>
      <div><i class="ph ph-arrow-u-up-left" aria-hidden="true"></i>{E(S['returns'])}</div>
      <div><i class="ph ph-{'shield-check' if warranty_ok() else 'lock-simple'}" aria-hidden="true"></i>{E(S['warranty']) if warranty_ok() else 'Secure checkout by Stripe'}</div>
    </div>
    <h3 style="margin:30px 0 12px">Specs</h3>
    <div class="spec-cards">{spec_cards}</div>
    <details class="more"><summary>Full specifications <i class="ph ph-caret-down" aria-hidden="true"></i></summary><dl>{more}</dl></details>
    <div class="inbox"><h3>In the box</h3><ul>{inbox}</ul></div>
    <p style="margin-top:28px;color:var(--muted)"><strong style="color:var(--text)">Best for:</strong> {E(p['best_for'])}</p>
  </div>
</section>
{faq_block(C.FAQ[:4])}
<section class="section-tight"><div class="wrap">
  <div class="section-head reveal"><h2>Also in the <span class="em">lineup</span></h2></div>
  <div class="lineup" style="grid-template-rows:auto">{''.join(product_card(q) for q in others)}</div>
</div></section>
{signup()}"""
    schema = f"""<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Product","name":{json_s(p['name'])},"sku":"{p['sku']}","brand":{{"@type":"Brand","name":"Lawnix"}},"description":{json_s(p['summary'])},"image":"{S['domain']}/static/img/{p['image']}","offers":{{"@type":"Offer","priceCurrency":"USD","price":"{p['price']:.2f}","availability":"https://schema.org/PreOrder","url":"{S['domain']}{product_url(p)}"}}}}</script>"""
    page(product_url(p), f"{p['name']} | Lawnix", p["summary"], body, f"/static/img/{p['image']}", schema)


def json_s(s: str) -> str:
    import json
    return json.dumps(s)


def org_schema() -> str:
    return f"""<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Organization","name":"Lawnix","legalName":{json_s(S['legal_name'])},"url":"{S['domain']}","logo":"{S['domain']}/static/img/lawnix-logo-lockup.png","email":"{S['email']}"}}</script>"""


def about() -> None:
    pts = "".join(f'<div class="reveal" data-delay="{i}"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (t, d) in enumerate(C.ABOUT["points"]))
    body = f"""<section class="section page-head"><div class="wrap">
  <div class="prose"><h1>Tools we would <span class="em">use ourselves</span></h1><p class="lede">{E(C.ABOUT['intro'])}</p></div>
  <div class="about-points">{pts}</div>
  <div class="prose" style="margin-top:56px"><h2>What comes next</h2><p>{E(C.ABOUT['roadmap'])}</p></div>
  <div class="reveal"><img class="logo-lockup" src="/static/img/logo-lockup.svg" alt="Lawnix logo: Power. Precision. Performance." loading="lazy" width="1290" height="690"></div>
</div></section>
{signup()}"""
    page("/about/", "About Lawnix | Stainless Lawn Tools", "Lawnix Industry Co makes stainless steel lawn leveling rakes and garden tools for people who do the work themselves.", body)


def faq_page() -> None:
    body = f"""<section class="section page-head"><div class="wrap">
  <div class="section-head"><h1>Help and <span class="em">FAQ</span></h1><p class="lede">Shipping, returns, warranty and how to use the tools. Email {S['email']} for anything else.</p></div>
  <div class="faq" id="shipping">{''.join(f'<details><summary>{E(q)}<i class="ph ph-plus" aria-hidden="true"></i></summary><p>{E(a)}</p></details>' for q, a in C.FAQ)}</div>
  <div class="prose" id="warranty" style="margin-top:56px">
    <h2>Warranty</h2>
    <p>{(f"Every Lawnix tool carries a {E(S['warranty'])} covering defects in materials and workmanship from the date of delivery. It does not cover normal wear, surface marks from sand, or damage from misuse. To claim, email {S['email']} with your order number and a photo.") if warranty_ok() else f"Warranty terms are being finalized and will be published on this page before the first orders ship. Email {S['email']} with any question."}</p>
    <h2>Returns</h2>
    <p>{E(S['returns'])} from the day your order arrives, in resalable condition with the original packaging. Email us to start a return and we will send instructions and the return address.</p>
  </div>
</div></section>"""
    page("/faq/", "FAQ, Shipping, Returns and Warranty | Lawnix", "Answers on Lawnix leveling rake sizes, materials, shipping, returns and warranty.", body)


def contact() -> None:
    body = f"""<section class="section page-head"><div class="wrap contact-grid">
  <div class="prose"><h1>Talk to <span class="em">Lawnix</span></h1><p class="lede">Orders, availability, warranty claims, wholesale and press. One address reaches a person who can help.</p>
    <p><a class="mail" href="mailto:{S['email']}">{S['email']}</a></p>
    <p>We answer within one business day, Monday to Friday.</p></div>
  <div class="prose"><h2 style="margin-top:0">Before you write</h2>
    <ul><li>Order questions: include your order number.</li><li>Warranty: include a photo of the issue.</li><li>Wholesale and landscapers: tell us your volume and location.</li></ul>
    <p><a class="btn btn-ghost" href="/faq/">Read the FAQ first</a></p></div>
</div></section>"""
    page("/contact/", "Contact Lawnix", "Email Lawnix about orders, availability, warranty claims and wholesale.", body)


def guide() -> None:
    g = C.GUIDE
    secs = "".join(f"<h2>{E(t)}</h2><p>{E(d)}</p>" for t, d in g["sections"])
    body = f"""<section class="section page-head"><div class="wrap">
  <article class="prose">
    <nav class="breadcrumb" aria-label="Breadcrumb" style="margin-bottom:16px"><a href="/">Home</a><i class="ph ph-caret-right" aria-hidden="true"></i><span>Guides</span></nav>
    <h1>{E(g['title'])}</h1>
    <p class="lede">{E(g['intro'])}</p>
    <img src="/static/img/lifestyle-sand.jpg" alt="Spreading topdressing sand with a leveling rake" loading="lazy" width="1600" height="1000" style="border-radius:var(--radius);margin:32px 0">
    {secs}
    <div class="callout"><p>{E(g['tip'])}</p><a class="btn btn-primary" href="/shop/">Shop the rakes</a></div>
  </article>
</div></section>
{signup()}"""
    page(f"/guides/{g['slug']}/", f"{g['title']} | Lawnix", g["intro"], body, "/static/img/lifestyle-sand.jpg")


def legal() -> None:
    priv = f"""<section class="section page-head"><div class="wrap prose">
  <h1>Privacy</h1>
  <p class="lede">What Lawnix collects and why. Short version: only what it takes to ship your order and answer your email.</p>
  <h2>What we collect</h2><p>When you buy, our payment processor (Stripe) collects your name, shipping address, email and payment details. We never see your full card number. When you join the email list we store your email address.</p>
  <h2>How we use it</h2><p>To fulfil and ship orders, answer support requests, send order updates, and, if you opted in, occasional emails about Lawnix products. We do not sell personal data.</p>
  <h2>Who we share it with</h2><p>Payment processing (Stripe), order fulfilment and shipping partners, and the email service that sends our newsletter. Each receives only what it needs for that job.</p>
  <h2>Your choices</h2><p>Unsubscribe from any email with one click, or email {S['email']} to see, correct or delete the data we hold about you.</p>
  <h2>Cookies</h2><p>This site uses no tracking cookies. Our checkout and email providers may set cookies on their own pages under their own policies.</p>
  <p>Last updated {date.today().strftime('%B %Y')}.</p>
</div></section>"""
    page("/privacy/", "Privacy | Lawnix", "How Lawnix handles the personal data it collects for orders and email.", priv)
    terms = f"""<section class="section page-head"><div class="wrap prose">
  <h1>Terms of sale</h1>
  <p class="lede">The plain-language terms for buying from {E(S['legal_name'])} at lawnixindustry.com.</p>
  <h2>Orders and payment</h2><p>Prices are in US dollars. Payment is taken at checkout by Stripe. We confirm every order by email; if an item is unavailable we refund in full.</p>
  <h2>Shipping</h2><p>{E(S['shipping'])}. Delivery estimates are shown at checkout and in your confirmation email. Risk passes to you on delivery.</p>
  <h2>Returns</h2><p>{E(S['returns'])}, in resalable condition. Refunds go back to the original payment method within ten business days of receipt.</p>
  <h2>Warranty</h2><p>{(E(S['warranty']) + " against defects in materials and workmanship. See the FAQ page for what is covered and how to claim.") if warranty_ok() else "Warranty terms will be published on the FAQ page before the first orders ship."}</p>
  <h2>Use</h2><p>Lawnix tools are hand tools. Use them as described in the product guide, wear gloves and eye protection, and keep them away from children.</p>
  <h2>Contact</h2><p>{E(S['legal_name'])}, {S['email']}.</p>
  <p>Last updated {date.today().strftime('%B %Y')}.</p>
</div></section>"""
    page("/terms/", "Terms of sale | Lawnix", "Terms for ordering from Lawnix: payment, shipping, returns and warranty.", terms)


def not_found() -> None:
    body = """<section class="section page-head"><div class="wrap prose">
  <h1>That page <span class="em">is not here</span></h1>
  <p class="lede">The link may be old. Try the shop or the leveling guide.</p>
  <p><a class="btn btn-primary" href="/shop/">Go to the shop</a></p>
</div></section>"""
    dest = OUT / "404.html"
    dest.write_text(head("Page not found | Lawnix", "Page not found.", "/404.html") + body + footer(), encoding="utf-8")


def extras() -> None:
    (OUT / "CNAME").write_text("lawnixindustry.com\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {S['domain']}/sitemap.xml\n")
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{S['domain']}{p}</loc><lastmod>{today}</lastmod></url>" for p in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    (OUT / ".nojekyll").write_text("")
    (OUT / ".htaccess").write_text("""# Lawnix static site (cPanel / Apache)
ErrorDocument 404 /404.html
DirectoryIndex index.html
Options -Indexes
RewriteEngine On
# Force HTTPS (certificate issued by AutoSSL on 2026-11-09)
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !https
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# www -> apex
RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]
RewriteRule ^ https://%1%{REQUEST_URI} [L,R=301]
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 30 days"
  ExpiresByType image/png "access plus 30 days"
  ExpiresByType image/svg+xml "access plus 30 days"
  ExpiresByType text/css "access plus 7 days"
  ExpiresByType application/javascript "access plus 7 days"
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml
</IfModule>
""")
    # Old slugs from the May prototype
    for old, new in {"collections.html": "/shop/", "about.html": "/about/", "cart.html": "/shop/",
                     "product-lx30.html": product_url(C.PRODUCTS[0]), "product-lx48.html": product_url(C.PRODUCTS[1]),
                     "product-cultivator.html": product_url(C.PRODUCTS[2])}.items():
        (OUT / old).write_text(f'<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={new}"><link rel="canonical" href="{S["domain"]}{new}"><a href="{new}">Moved</a>')


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(STATIC, OUT / "static")
    home()
    shop()
    for p in C.PRODUCTS:
        product_page(p)
    about()
    faq_page()
    contact()
    guide()
    legal()
    not_found()
    extras()
    print(f"built {len(PAGES)} pages into {OUT}")
    missing = [p for p in C.OPEN_ITEMS]
    if missing:
        print("open items:")
        for m in missing:
            print("  -", m)


if __name__ == "__main__":
    main()
