#!/usr/bin/env python3
"""Build Lawnix logo concepts as clean SVG files (no image generation, no credits).

Run with: ~/.venvs/onetake/bin/python brand/build_logo.py
Outputs:  brand/logo/<concept>/*.svg  and  brand/preview.html
"""
from __future__ import annotations

import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = HERE / "logo"

LIME = "#BBD022"
INK = "#0B0C0A"
PAPER = "#F4F5F0"
STEEL = "#9AA09B"


class Face:
    def __init__(self, path: Path):
        self.font = TTFont(path)
        self.upm = self.font["head"].unitsPerEm
        self.glyphset = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font["hmtx"]
        try:
            self.kern = self.font["GPOS"]  # not used directly; Barlow has little kerning
        except KeyError:
            self.kern = None

    def text_path(self, text: str, size: float, x: float = 0, y: float = 0, tracking: float = 0):
        """Return (svg_path_d, advance_width) for text with baseline at y. Y grows down."""
        scale = size / self.upm
        d_parts = []
        pen_x = x
        for ch in text:
            gname = self.cmap[ord(ch)]
            glyph = self.glyphset[gname]
            pen = SVGPathPen(self.glyphset)
            # flip y, scale, translate
            tpen = TransformPen(pen, (scale, 0, 0, -scale, pen_x, y))
            glyph.draw(tpen)
            d = pen.getCommands()
            if d:
                d_parts.append(d)
            adv = self.hmtx[gname][0] * scale
            pen_x += adv + tracking
        return " ".join(d_parts), pen_x - x - tracking


black_it = Face(FONTS / "BarlowCondensed-BlackItalic.ttf")
black = Face(FONTS / "BarlowCondensed-Black.ttf")
semi = Face(FONTS / "BarlowCondensed-SemiBold.ttf")


def wordmark(size: float, ink: str, accent: str, italic=True, x=0.0, y=0.0):
    """LAWN in ink, IX in accent. Returns (svg_group, width)."""
    face = black_it if italic else black
    tracking = size * -0.01
    d1, w1 = face.text_path("LAWN", size, x, y, tracking)
    d2, w2 = face.text_path("IX", size, x + w1 + tracking, y, tracking)
    g = f'<path fill="{ink}" d="{d1}"/><path fill="{accent}" d="{d2}"/>'
    return g, w1 + tracking + w2


def small_caps(text: str, size: float, fill: str, x: float, y: float, tracking_em=0.18):
    d, w = semi.text_path(text, size, x, y, size * tracking_em)
    return f'<path fill="{fill}" d="{d}"/>', w


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{rect}{body}</svg>')


# ---------------- Concept A: hex nut monogram ----------------

def hexagon(cx, cy, r):
    import math
    pts = [(cx + r * math.cos(math.radians(60 * i - 30)), cy + r * math.sin(math.radians(60 * i - 30))) for i in range(6)]
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


def mark_a(size=200, ink=INK, accent=LIME, on_dark=False):
    """Hex nut with LX monogram cut in. Hardware cue, lawn colour."""
    cx = cy = size / 2
    r_out = size * 0.48
    r_in = size * 0.36
    body = f'<path fill="{accent}" fill-rule="evenodd" d="{hexagon(cx, cy, r_out)} {hexagon(cx, cy, r_in)}"/>'
    # LX monogram
    d, w = black.text_path("LX", size * 0.46, 0, 0, size * -0.02)
    tx = cx - w / 2
    ty = cy + size * 0.165
    letter = "#FFFFFF" if on_dark else ink
    body += f'<path fill="{letter}" transform="translate({tx:.2f},{ty:.2f})" d="{d}"/>'
    return body


# ---------------- Concept B: leveling plate ----------------

def mark_b(size=200, ink=INK, accent=LIME, on_dark=False):
    """A level plate with handle: a flat bar, a centred stem, two tine stubs."""
    s = size
    bar_h = s * 0.16
    bar_y = s * 0.60
    stem_w = s * 0.14
    body = ""
    # handle stem, angled slightly like a rake handle
    body += (f'<path fill="{"#FFFFFF" if on_dark else ink}" d="M{s*0.50 - stem_w/2:.1f},{bar_y:.1f} '
             f'L{s*0.56 - stem_w/2:.1f},{s*0.06:.1f} L{s*0.56 + stem_w/2:.1f},{s*0.06:.1f} '
             f'L{s*0.50 + stem_w/2:.1f},{bar_y:.1f} Z"/>')
    # plate bar
    body += f'<rect x="{s*0.06:.1f}" y="{bar_y:.1f}" width="{s*0.88:.1f}" height="{bar_h:.1f}" rx="{s*0.02:.1f}" fill="{accent}"/>'
    # three tines
    for fx in (0.16, 0.50, 0.84):
        body += f'<rect x="{s*fx - s*0.045:.1f}" y="{bar_y + bar_h:.1f}" width="{s*0.09:.1f}" height="{s*0.18:.1f}" rx="{s*0.015:.1f}" fill="{accent}"/>'
    return body


# ---------------- Concept C: level badge ----------------

def mark_c(size=200, ink=INK, accent=LIME, on_dark=False):
    """Rounded square badge, LX monogram, spirit-level bubble above."""
    s = size
    body = f'<rect x="{s*0.04:.1f}" y="{s*0.04:.1f}" width="{s*0.92:.1f}" height="{s*0.92:.1f}" rx="{s*0.18:.1f}" fill="{ink if not on_dark else accent}"/>'
    letter = accent if not on_dark else ink
    # level vial
    vx, vy, vw, vh = s * 0.26, s * 0.20, s * 0.48, s * 0.12
    body += f'<rect x="{vx:.1f}" y="{vy:.1f}" width="{vw:.1f}" height="{vh:.1f}" rx="{vh/2:.1f}" fill="none" stroke="{letter}" stroke-width="{s*0.035:.1f}"/>'
    body += f'<circle cx="{s*0.5:.1f}" cy="{vy + vh/2:.1f}" r="{vh*0.28:.1f}" fill="{letter}"/>'
    for fx in (0.44, 0.56):
        body += f'<rect x="{s*fx - s*0.012:.1f}" y="{vy - s*0.03:.1f}" width="{s*0.024:.1f}" height="{vh + s*0.06:.1f}" fill="{letter}"/>'
    d, w = black.text_path("LX", s * 0.44, 0, 0, s * -0.02)
    body += f'<path fill="{letter}" transform="translate({s*0.5 - w/2:.2f},{s*0.80:.2f})" d="{d}"/>'
    return body


CONCEPTS = {
    "a-hex": ("Hex nut monogram", mark_a, "Hardware first: a hex-nut ring in brand lime with the LX monogram inside. Reads as a tool brand at a glance and scales to a favicon."),
    "b-plate": ("Leveling plate", mark_b, "Garden first: a level plate on a handle with three tines. Literal to the launch product, still simple enough for hardware later."),
    "c-level": ("Level badge", mark_c, "Precision: a rounded badge with a spirit-level vial over LX. Works for any tool that promises accuracy, garden or hardware."),
}


def lockups(key, title, mark_fn, blurb):
    out = OUT / key
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for theme, ink, bg in (("light", INK, PAPER), ("dark", "#FFFFFF", INK)):
        on_dark = theme == "dark"
        # mark only
        files[f"mark-{theme}"] = svg(200, 200, mark_fn(200, INK if not on_dark else "#FFFFFF", LIME, on_dark), None)
        # horizontal: mark + wordmark + web address
        g, w = wordmark(150, ink, LIME, x=0, y=0)
        mark_w = 150
        gap = 28
        total_w = mark_w + gap + w
        body = f'<g transform="translate(0,25)">{mark_fn(150, INK if not on_dark else "#FFFFFF", LIME, on_dark)}</g>'
        body += f'<g transform="translate({mark_w + gap},140)">{g}</g>'
        sc, scw = small_caps("LAWNIXINDUSTRY.COM", 24, STEEL if not on_dark else "#B8BDB3", mark_w + gap + 4, 182)
        body += sc
        files[f"horizontal-{theme}"] = svg(round(total_w + 10), 200, body, None)
        # stacked: mark above wordmark
        g2, w2 = wordmark(170, ink, LIME)
        W = max(w2, 240) + 40
        body = f'<g transform="translate({(W-200)/2:.1f},0)">{mark_fn(200, INK if not on_dark else "#FFFFFF", LIME, on_dark)}</g>'
        body += f'<g transform="translate({(W-w2)/2:.1f},360)">{g2}</g>'
        sc, scw = small_caps("LAWNIXINDUSTRY.COM", 26, STEEL if not on_dark else "#B8BDB3", 0, 405)
        body += f'<g transform="translate({(W-scw)/2:.1f},0)">{sc}</g>'
        files[f"stacked-{theme}"] = svg(round(W), 430, body, None)
    # wordmark only (light/dark)
    for theme, ink in (("light", INK), ("dark", "#FFFFFF")):
        g, w = wordmark(200, ink, LIME)
        files[f"wordmark-{theme}"] = svg(round(w + 10), 200, f'<g transform="translate(5,190)">{g}</g>')
    # favicon 64
    files["favicon"] = svg(64, 64, f'<rect width="64" height="64" rx="12" fill="{INK}"/><g transform="translate(6,6) scale(0.26)">{mark_fn(200, "#FFFFFF", LIME, True)}</g>')
    for name, content in files.items():
        (out / f"{name}.svg").write_text(content)
    return files


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = []
    for key, (title, fn, blurb) in CONCEPTS.items():
        files = lockups(key, title, fn, blurb)
        cards.append((key, title, blurb, files))
    # preview board
    css = """
    body{margin:0;background:#1a1c18;color:#eee;font-family:-apple-system,Helvetica,Arial,sans-serif;padding:32px}
    h1{font-size:22px;margin:0 0 24px;font-weight:600}
    .concept{display:grid;gap:18px;margin-bottom:28px;background:#232620;border-radius:12px;padding:24px}
    .concept h2{margin:0 0 8px;font-size:20px}.concept p{margin:0;color:#b9bdb3;font-size:14px;line-height:1.5;max-width:70ch}
    .tiles{display:grid;grid-template-columns:1fr;gap:14px}
    .tile{border-radius:10px;padding:28px;display:flex;align-items:center;justify-content:center;min-height:150px}
    .light{background:#F4F5F0}.dark{background:#0B0C0A}
    .tile svg{width:100%;height:auto;max-height:180px}
    .row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
    .row .tile svg{width:auto;height:150px}
    .fav svg{width:72px;height:72px}
    .key{display:inline-block;background:#BBD022;color:#0B0C0A;font-weight:700;border-radius:6px;padding:2px 8px;font-size:13px;margin-bottom:10px}
    """
    html = [f"<!doctype html><meta charset='utf-8'><title>Lawnix logo concepts</title><style>{css}</style><body><h1>Lawnix logo concepts (SVG, built locally)</h1>"]
    for key, title, blurb, files in cards:
        html.append(f"<section class='concept'><div><span class='key'>{key.split('-')[0].upper()}</span><h2>{title}</h2><p>{blurb}</p></div><div>")
        html.append("<div class='tiles'>")
        html.append(f"<div class='tile light'>{files['horizontal-light']}</div><div class='tile dark'>{files['horizontal-dark']}</div>")
        html.append(f"<div class='tile light'>{files['stacked-light']}</div><div class='tile dark'>{files['stacked-dark']}</div>")
        html.append("</div><div class='row' style='margin-top:14px'>")
        html.append(f"<div class='tile light'>{files['mark-light']}</div><div class='tile dark'>{files['mark-dark']}</div><div class='tile dark fav'>{files['favicon']}</div>")
        html.append("</div></div></section>")
    (HERE / "preview.html").write_text("".join(html))
    print("wrote", HERE / "preview.html", "and", len(cards), "concepts to", OUT)


if __name__ == "__main__":
    main()
