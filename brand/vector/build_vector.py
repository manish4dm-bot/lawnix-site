#!/usr/bin/env python3
from __future__ import annotations
"""Turn the one-colour trace inside LAWNIX_logo.ai into clean two-colour SVG logo files.

Source:  ~/Downloads/LAWNIX_logo.ai (EPS, 1536x1024, 71 traced shapes, all one colour)
Colours: each shape is classified by sampling the original PNG under it (classes.json).
         lime -> brand lime, white -> white (dark version) or ink (light version),
         dark -> a counter (hole) cut out with a mask, so files stay transparent.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AI = Path.home() / "Downloads" / "LAWNIX_logo.ai"
OUT = HERE / "logo"
H = 1024
LIME = "#BED62C"   # matches the packaging label green
INK = "#131312"    # matches the packaging label black
WHITE = "#FFFFFF"

# viewBoxes (x, y, w, h) measured from the artwork
CROPS = {
    "full": (130, 120, 1290, 860),
    "lockup": (130, 120, 1290, 690),     # mark + wordmark + tagline, no mower
    "mark": (370, 130, 830, 410),        # LX + bolt + grass
    "wordmark": (150, 535, 1260, 205),   # LAWNIX + TM
}


def read_paths():
    lines = AI.read_bytes().decode("latin-1").splitlines()
    shapes, d = [], []
    for ln in lines:
        t = ln.split()
        if not t:
            continue
        op = t[-1]
        try:
            if op == "m":
                d.append(f"M{float(t[0]):g} {H - float(t[1]):g}")
            elif op == "L":
                d.append(f"L{float(t[0]):g} {H - float(t[1]):g}")
            elif op == "C":
                v = list(map(float, t[:6]))
                d.append("C" + " ".join(f"{v[i]:g} {H - v[i + 1]:g}" for i in (0, 2, 4)))
            elif op == "f":
                if d:
                    shapes.append(" ".join(d) + " Z")
                d = []
        except (ValueError, IndexError):
            pass
    return shapes[1:]  # drop the background rectangle


def classify(lime, white, dark):
    if lime > max(white, 0.2):
        return "lime"
    if white >= 0.3:
        return "white"
    return "hole"


def build(theme: str, crop: str, bg: str | None):
    paths = read_paths()
    classes = {i: classify(l, w, d) for i, l, w, d in json.loads((HERE / "classes.json").read_text())}
    fg_white = WHITE if theme == "dark" else INK
    x, y, w, h = CROPS[crop]
    pos, holes = [], []
    grass = json.loads((HERE / "grass_clip.json").read_text())
    grass_polys = "".join('<polygon points="' + " ".join(f"{a},{b}" for a, b in poly) + '"/>' for poly in grass)
    for i, d in enumerate(paths, 1):
        c = classes.get(i, "white")
        if c == "hole":
            holes.append(f'<path d="{d}"/>')
        else:
            pos.append(f'<path fill="{LIME if c == "lime" else fg_white}" d="{d}"/>')
            if i == 3:
                # the trace merged the grass tuft into the X; repaint only the grass area lime
                pos.append(f'<path fill="{LIME}" clip-path="url(#grass)" d="{d}"/>')
    if crop in ("lockup", "mark", "wordmark"):
        # keep only shapes whose first point sits inside the crop band
        def inside(p):
            try:
                py = float(p.split('d="M', 1)[1].split()[1].split('"')[0])
            except Exception:
                return True
            return y <= py <= y + h
        pos = [p for p in pos if inside(p)]
        holes = [p for p in holes if inside(p)]
    bg_rect = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    mask = (f'<mask id="m" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/><g fill="#000">{"".join(holes)}</g></mask>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}">'
            f'<title>Lawnix</title><defs>{mask}<clipPath id="grass">{grass_polys}</clipPath></defs>{bg_rect}<g mask="url(#m)">{"".join(pos)}</g></svg>')


def main():
    OUT.mkdir(exist_ok=True)
    made = []
    for crop in CROPS:
        for theme in ("dark", "light"):
            name = f"lawnix-{crop}-{'white' if theme == 'dark' else 'black'}.svg"
            (OUT / name).write_text(build(theme, crop, None)); made.append(name)
        (OUT / f"lawnix-{crop}-on-black.svg").write_text(build("dark", crop, INK)); made.append(f"lawnix-{crop}-on-black.svg")
    print("\n".join(made))


if __name__ == "__main__":
    main()
