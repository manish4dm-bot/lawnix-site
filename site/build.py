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


def money(v: float) -> str:
    return f"${v:,.2f}"


def product_url(p) -> str:
    return f"/products/{p['slug']}/"


def buy_href(p) -> str:
    link = S["stripe_links"].get(p["id"], "")
    return link or "/contact/"


def amazon_href(p) -> str:
    asin = S["amazon_asins"].get(p["id"], "")
    return f"https://www.amazon.com/dp/{asin}" if asin else ""


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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,700;0,800;0,900;1,900&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.1/src/regular/style.css">
<link rel="stylesheet" href="/static/css/lawnix.css">
{schema}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="header">
  <div class="wrap">
    <a class="logo" href="/" aria-label="Lawnix home">Lawn<b>ix</b><sup>TM</sup></a>
    <nav class="nav" aria-label="Main">
      {''.join(f'<a href="{h}">{E(t)}</a>' for t, h in C.NAV)}
      <a class="btn btn-primary" href="{product_url(C.PRODUCTS[0])}">Buy the LX-30</a>
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
        <a class="logo" href="/">Lawn<b>ix</b><sup>TM</sup></a>
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
<script src="/static/js/lawnix.js" defer></script>
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

    return f"""<section class="section" id="sizes">
  <div class="wrap">
    <div class="section-head reveal"><h2>Pick your <span class="em">width</span></h2>
      <p class="lede">Same stainless plate, same 78-inch handle. The only question is how much lawn you cover per pass.</p></div>
    <div class="compare">{col(a, 30)}{col(b, 48)}</div>
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

def home() -> None:
    p = C.PRODUCTS[0]
    body = f"""<section class="hero">
  <div class="wrap">
    <div>
      <h1 class="reveal in">Level your lawn with <span class="em">the right rake.</span></h1>
      <p class="lede reveal in" data-delay="1">Stainless steel leveling rakes and garden tools for homeowners who want a lawn that looks professionally cut.</p>
      <div class="hero-actions reveal in" data-delay="2">
        <a class="btn btn-primary" href="/shop/">Shop the rakes</a>
        <a class="btn btn-ghost" href="#how">How leveling works</a>
      </div>
    </div>
    <div class="hero-media reveal in" data-delay="1">
      <img src="/static/img/hero.jpg" alt="Lawnix LX-30 leveling rake spreading sand across a lawn" width="1200" height="1500" fetchpriority="high">
      <a class="hero-price" href="{product_url(p)}"><strong>{money(p['price'])}</strong><span>{E(p['short'])}</span></a>
    </div>
  </div>
</section>
{lineup()}
{why_band()}
{build_bento()}
{steps()}
{compare()}
{faq_block(C.FAQ[:6])}
{signup()}"""
    schema = org_schema()
    page("/", "Lawnix | Stainless Lawn Leveling Rakes and Garden Tools", "Lawnix makes 30 and 48 inch stainless steel lawn leveling rakes and a rotary cultivator for homeowners who want a flat, even lawn.", body, "/static/img/hero.jpg", schema)


def shop() -> None:
    body = f"""<section class="section page-head">
  <div class="wrap">
    <div class="section-head"><h1>Shop <span class="em">Lawnix</span></h1><p class="lede">Every tool ships from US warehouses. {E(S['returns'])}. {E(S['warranty'])}.</p></div>
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
    actions = f'<a class="btn btn-primary btn-block" href="{buy_href(p)}"{rel}>{E(buy_label)}</a>'
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
      <div><i class="ph ph-shield-check" aria-hidden="true"></i>{E(S['warranty'])}</div>
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
  <div class="lockup reveal"><img src="/static/img/lawnix-logo-lockup.png" alt="Lawnix logo: Power. Precision. Performance." loading="lazy" width="1536" height="1024"></div>
</div></section>
{signup()}"""
    page("/about/", "About Lawnix | Stainless Lawn Tools", "Lawnix Industry Co makes stainless steel lawn leveling rakes and garden tools for people who do the work themselves.", body)


def faq_page() -> None:
    body = f"""<section class="section page-head"><div class="wrap">
  <div class="section-head"><h1>Help and <span class="em">FAQ</span></h1><p class="lede">Shipping, returns, warranty and how to use the tools. Email {S['email']} for anything else.</p></div>
  <div class="faq" id="shipping">{''.join(f'<details><summary>{E(q)}<i class="ph ph-plus" aria-hidden="true"></i></summary><p>{E(a)}</p></details>' for q, a in C.FAQ)}</div>
  <div class="prose" id="warranty" style="margin-top:56px">
    <h2>Warranty</h2>
    <p>Every Lawnix tool carries a {E(S['warranty'])} covering defects in materials and workmanship from the date of delivery. It does not cover normal wear, surface marks from sand, or damage from misuse. To claim, email {S['email']} with your order number and a photo.</p>
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
  <h2>Warranty</h2><p>{E(S['warranty'])} against defects in materials and workmanship. See the FAQ page for what is covered and how to claim.</p>
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
