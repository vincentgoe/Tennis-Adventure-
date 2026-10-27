"""Generate the block-style SVG art for Plot Twist into assets/.

All images in assets/ are drawn by this script (no external art). Run it from
the project folder after changing a drawing:

    uv run python tools/draw_assets.py

It overwrites the SVG files in assets/. Story content (which image belongs to
which scene) lives in story.json.
"""

import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

W, H = 320, 180

# --- palette ----------------------------------------------------------------
SKY_TOP, SKY_BOTTOM = "#7cc8f2", "#cdeeff"
GRASS, GRASS_DARK = "#6dbb4a", "#5ea83f"
CLAY, CLAY_DARK = "#d9743a", "#c4642f"
LINE = "#fbf7ee"
WOOD, WOOD_DARK = "#9a6a3c", "#7a5230"
SKIN = "#f2c49b"
NAVY = "#2d3a5a"


def shade(hex_color, factor):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    if factor >= 1:
        r, g, b = (int(c + (255 - c) * (factor - 1)) for c in (r, g, b))
    else:
        r, g, b = (int(c * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def poly(points, fill, extra=""):
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" {extra}/>'


def block(x, y, w, h, color, d=5):
    """A voxel-style block: front face, lighter top, darker right side."""
    return "".join(
        [
            poly([(x, y), (x + d, y - d), (x + w + d, y - d), (x + w, y)], shade(color, 1.25)),
            poly([(x + w, y), (x + w + d, y - d), (x + w + d, y + h - d), (x + w, y + h)], shade(color, 0.75)),
            rect(x, y, w, h, color),
        ]
    )


def svg(body, defs="", w=W, h=H):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges"><defs>{defs}</defs>{body}</svg>\n'
    )


def sky_defs(top=SKY_TOP, bottom=SKY_BOTTOM, gid="sky"):
    return (
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>'
        "</linearGradient>"
    )


def outdoor(horizon=92, top=SKY_TOP, bottom=SKY_BOTTOM):
    parts = [rect(0, 0, W, horizon, "url(#sky)"), rect(0, horizon, W, H - horizon, GRASS)]
    for i, y in enumerate(range(horizon, H, 12)):
        if i % 2:
            parts.append(rect(0, y, W, 6, GRASS_DARK))
    return "".join(parts)


def cloud(x, y, s=1.0):
    drift = 18 * s
    dur = 9 + int(x) % 5
    return (
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="0 0;{drift:.1f} 0;0 0" dur="{dur}s" repeatCount="indefinite"/>'
        + _cloud_parts(x, y, s) + "</g>"
    )


def _cloud_parts(x, y, s):
    return "".join(
        [
            rect(x, y + 6 * s, 34 * s, 8 * s, "#ffffff"),
            rect(x + 6 * s, y, 18 * s, 8 * s, "#ffffff"),
            rect(x + 4 * s, y + 12 * s, 26 * s, 3 * s, "#e6f4fb"),
        ]
    )


def tree(x, y):
    cx, cy = x + 10, y + 20
    dur = 1.8 + (int(x) % 5) * 0.15
    sway = (
        f'<g><animateTransform attributeName="transform" type="rotate" '
        f'values="-2 {cx} {cy};2 {cx} {cy};-2 {cx} {cy}" dur="{dur:.1f}s" '
        f'repeatCount="indefinite"/>' + block(x, y, 20, 20, "#3f9a3a", 5) + "</g>"
    )
    return rect(x + 7, y + 18, 6, 14, WOOD_DARK) + sway


# Same design, three colours (specs/outfit-choice.md)
KITS = {
    "white": {"shirt": "#ffffff", "shorts": "#f0f0f0", "socks": "#ffffff", "shoes": "#fafafa", "accent": "#d9743a"},
    "black": {"shirt": "#1c1c1c", "shorts": "#161616", "socks": "#222222", "shoes": "#111111", "accent": "#4a4a4a"},
    "pink":  {"shirt": "#ff7eb6", "shorts": "#ff6aa8", "socks": "#ffd1e5", "shoes": "#ff9cc7", "accent": "#d63384"},
}


def player_tennis(x, y, s=1.0, arms_up=False, kit="white"):
    """The player after changing: sport shirt, shorts, socks, sport shoes, headband."""
    k = KITS[kit]
    return person(x, y, k["shirt"], hair="#5b3a22", s=s, arms_up=arms_up,
                  shorts=k["shorts"], shoes=k["shoes"], socks=k["socks"],
                  extra=[(2, 3, 10, 2, k["accent"]),     # headband
                         (0, 18, 14, 2, k["accent"]),    # shirt stripe
                         (0, 39, 6, 1, k["accent"]),     # shoe soles
                         (8, 39, 6, 1, k["accent"])])


def player_street(x, y, s=1.0):
    """The player before changing: hoodie, jeans, street shoes."""
    return person(x, y, "#6f8aa8", pants="#35507a", hair="#5b3a22", s=s,
                  shoes="#6b4a2e",
                  extra=[(2, 12, 10, 3, "#5d7693"),      # hood collar
                         (5, 14, 1, 5, "#f0f0f0"),       # hoodie strings
                         (8, 14, 1, 5, "#f0f0f0"),
                         (3, 21, 8, 4, "#5d7693")])      # front pocket


def tuft(x, y, c=None):
    """A small grass tuft standing on (x, y)."""
    c = c or "#4f9a35"
    return rect(x, y - 4, 1, 4, c) + rect(x + 2, y - 6, 1, 6, c) + rect(x + 4, y - 3, 1, 3, c)


def flower(x, y, petal):
    """A tiny flower on (x, y) that sways a little."""
    dur = 1.4 + (int(x) % 4) * 0.2
    head = (
        rect(x - 1, y - 8, 3, 1, petal) + rect(x, y - 9, 1, 3, petal)
        + rect(x, y - 8, 1, 1, "#f1c40f")
    )
    return (
        rect(x, y - 6, 1, 6, "#3f8a2f")
        + f'<g><animateTransform attributeName="transform" type="rotate" '
        f'values="-8 {x} {y - 6};8 {x} {y - 6};-8 {x} {y - 6}" dur="{dur:.1f}s" '
        f'repeatCount="indefinite"/>{head}</g>'
    )


def meadow(tufts=(), flowers=()):
    return "".join(tuft(x, y) for x, y in tufts) + "".join(flower(x, y, c) for x, y, c in flowers)


def bird(y, dur, begin, s=1.0, color="#3a3a3a"):
    """A distant bird flying from left to right across the sky."""
    a = 3 * s
    up = f"M {-a} 0 L 0 {a / 2} L {a} 0"
    down = f"M {-a} {a / 2} L 0 0 L {a} {a / 2}"
    return (
        f'<g shape-rendering="auto"><animateTransform attributeName="transform" type="translate" '
        f'values="-10 {y};{W + 10} {y - 6}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
        f'<path d="{up}" fill="none" stroke="{color}" stroke-width="{0.9 * s:.1f}">'
        f'<animate attributeName="d" values="{up};{down};{up}" dur="0.45s" repeatCount="indefinite"/></path></g>'
    )


def birds(ys=(18, 26, 12), color="#3a3a3a"):
    return "".join(
        bird(y, 14 + i * 4, -i * 5, s=1.0 - i * 0.15, color=color) for i, y in enumerate(ys)
    )


def butterfly(x, y, color="#ffffff"):
    """A butterfly fluttering in a small loop around (x, y)."""
    wings = (
        f'<rect x="-3" y="-2" width="3" height="3" fill="{color}">'
        '<animate attributeName="width" values="3;1;3" dur="0.25s" repeatCount="indefinite"/>'
        '<animate attributeName="x" values="-3;-1;-3" dur="0.25s" repeatCount="indefinite"/></rect>'
        f'<rect x="0" y="-2" width="3" height="3" fill="{color}">'
        '<animate attributeName="width" values="3;1;3" dur="0.25s" repeatCount="indefinite"/></rect>'
        '<rect x="-0.5" y="-2" width="1" height="3" fill="#333333"/>'
    )
    return (
        f'<g><animateMotion path="M {x} {y} c 10 -8 20 8 30 0 s -20 10 -30 0" dur="6s" '
        f'repeatCount="indefinite"/>{wings}</g>'
    )


def bouncing_ball(points, dur=2.4):
    """A tennis ball bouncing between the given points."""
    x0, y0 = points[0]
    d = f"M {x0} {y0}"
    for (x1, y1) in points[1:] + points[:1]:
        d += f" Q {(x0 + x1) / 2} {min(y0, y1) - 26} {x1} {y1}"
        x0, y0 = x1, y1
    return (
        f'<g shape-rendering="auto"><circle r="2" fill="#d7e84a" stroke="#9fb02c" stroke-width="0.5">'
        f'<animateMotion path="{d}" dur="{dur}s" repeatCount="indefinite"/></circle></g>'
    )


def flashes(y0, y1, n=6):
    """Camera flashes in the crowd."""
    out = []
    for i in range(n):
        x = 20 + (i * 53) % (W - 40)
        y = y0 + (i * 7) % (y1 - y0)
        out.append(
            f'<g shape-rendering="auto"><circle cx="{x}" cy="{y}" r="3" fill="#ffffff" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0" keyTimes="0;0.85;0.88;1" '
            f'dur="{1.6 + (i % 4) * 0.35:.2f}s" begin="{i * 0.3:.1f}s" repeatCount="indefinite"/></circle></g>'
        )
    return "".join(out)


def person(x, y, shirt, pants=NAVY, skin=SKIN, hair="#5b3a22", cap=None, s=1.0, arms_up=False,
           shorts=None, shoes="#222222", socks="#ffffff", extra=(), asleep=False):
    """Blocky person. (x, y) is the top-left of the head."""
    def r(dx, dy, w, h, c):
        return rect(x + dx * s, y + dy * s, w * s, h * s, c)

    if shorts:
        legs = [r(1, 26, 5, 5, shorts), r(8, 26, 5, 5, shorts),
                r(1, 31, 5, 4, skin), r(8, 31, 5, 4, skin),
                r(1, 35, 5, 2, socks), r(8, 35, 5, 2, socks)]
    else:
        legs = [r(1, 26, 5, 12, pants), r(8, 26, 5, 12, pants)]
    if asleep:
        eyes = [r(4, 6, 2, 1, "#2b2b2b"), r(8, 6, 2, 1, "#2b2b2b")]
    else:
        eyes = [r(4, 5, 2, 2, "#2b2b2b"), r(8, 5, 2, 2, "#2b2b2b")]
    parts = legs + [
        r(0, 37, 6, 3, shoes),  # shoes
        r(8, 37, 6, 3, shoes),
        r(0, 12, 14, 15, shirt),  # body
        r(2, 0, 10, 11, skin),  # head
        r(2, 0, 10, 3, hair),
    ] + eyes
    if arms_up:
        parts += [r(-4, 4, 4, 10, shirt), r(14, 4, 4, 10, shirt), r(-4, 2, 4, 3, skin), r(14, 2, 4, 3, skin)]
    else:
        parts += [r(-3, 13, 3, 11, shirt), r(14, 13, 3, 11, shirt), r(-3, 23, 3, 3, skin), r(14, 23, 3, 3, skin)]
    if cap:
        parts += [r(1, -2, 12, 4, cap), r(10, 1, 6, 2, cap)]
    parts += [r(*e) for e in extra]
    # Different rhythm per person (from its position), so nobody moves in sync
    seed = int(x * 7 + y * 3)
    blink_dur = 3.4 + (seed % 7) * 0.45
    blink_begin = (seed % 5) * 0.7
    bob_dur = 1.6 + (seed % 4) * 0.2
    bob_begin = (seed % 3) * 0.4
    lids = "" if asleep else (
        f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;0" '
        f'keyTimes="0;0.92;0.96;1" dur="{blink_dur:.2f}s" begin="{blink_begin:.1f}s" '
        f'repeatCount="indefinite"/>{r(4, 5, 2, 2, skin)}{r(8, 5, 2, 2, skin)}</g>'
    )
    return (
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="0 0;0 {-1 * s:.2f};0 0" keyTimes="0;0.5;1" calcMode="spline" '
        f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1" dur="{bob_dur:.1f}s" begin="{bob_begin:.1f}s" '
        f'repeatCount="indefinite"/>' + "".join(parts) + lids + "</g>"
    )


def racket(cx, cy, frame, grip, strings="#f5f1e6", angle=0, worn=False, s=1.0):
    """A racket centred on its head. Not crisp-edged: curves look better smooth."""
    rx, ry = 13 * s, 17 * s
    parts = [f'<g transform="rotate({angle} {cx} {cy})" shape-rendering="auto">']
    parts.append(rect(cx - 2 * s, cy + ry - 1, 4 * s, 8 * s, frame))  # throat
    parts.append(rect(cx - 2.5 * s, cy + ry + 7 * s, 5 * s, 14 * s, grip))  # handle
    parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{frame}" stroke-width="{3.5 * s}"/>')
    for i in range(-3, 4):
        x = cx + i * 3.2 * s
        h = ry * (1 - (i * 3.2 * s / rx) ** 2) ** 0.5 if abs(i * 3.2 * s) < rx else 0
        parts.append(f'<line x1="{x}" y1="{cy - h + 1}" x2="{x}" y2="{cy + h - 1}" stroke="{strings}" stroke-width="{0.8 * s}"/>')
    for j in range(-4, 5):
        y = cy + j * 3.2 * s
        w = rx * (1 - (j * 3.2 * s / ry) ** 2) ** 0.5 if abs(j * 3.2 * s) < ry else 0
        parts.append(f'<line x1="{cx - w + 1}" y1="{y}" x2="{cx + w - 1}" y2="{y}" stroke="{strings}" stroke-width="{0.8 * s}"/>')
    if worn:
        for dx, dy in [(-10, -6), (9, 4), (-6, 12), (7, -12)]:
            parts.append(f'<rect x="{cx + dx * s}" y="{cy + dy * s}" width="{3 * s}" height="{2 * s}" fill="#d8d2c4"/>')
        parts.append(rect(cx - 2.5 * s, cy + ry + 12 * s, 5 * s, 3 * s, "#cfc6b0"))  # worn grip
    parts.append("</g>")
    return "".join(parts)


def court_surface(x, y, w, h):
    """Clay court seen from behind, as a trapezoid."""
    inset = w * 0.12
    parts = [poly([(x + inset, y), (x + w - inset, y), (x + w, y + h), (x, y + h)], CLAY)]
    parts.append(poly([(x + inset + 6, y + 3), (x + w - inset - 6, y + 3), (x + w - 8, y + h - 4), (x + 8, y + h - 4)], "none", f'stroke="{LINE}" stroke-width="2"'))
    mid = x + w / 2
    parts.append(f'<line x1="{mid}" y1="{y + 3}" x2="{mid}" y2="{y + h - 4}" stroke="{LINE}" stroke-width="2"/>')
    return "".join(parts)


def net(x, y, w):
    parts = [rect(x, y, w, 12, "#2f2f2f", 'opacity="0.55"')]
    for i in range(0, int(w), 4):
        parts.append(rect(x + i, y, 1, 12, "#1d1d1d"))
    parts += [rect(x, y - 1, w, 3, LINE), rect(x - 3, y - 4, 4, 18, "#3a3a3a"), rect(x + w - 1, y - 4, 4, 18, "#3a3a3a")]
    return "".join(parts)


def save(path, content):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


# --- scenes -----------------------------------------------------------------


def grounds():
    b = [outdoor(88), cloud(30, 14), cloud(200, 24, 0.8), cloud(250, 8, 0.6)]
    # fence at the back
    for x in range(0, W, 10):
        b.append(rect(x, 80, 2, 10, "#ffffff"))
    b.append(rect(0, 82, W, 2, "#ffffff"))
    # office building (left)
    b.append(block(14, 52, 74, 46, "#efe6d2", 6))
    b.append(block(10, 44, 82, 9, "#c0392b", 6))
    b.append(rect(44, 74, 14, 24, WOOD))
    b.append(rect(20, 62, 16, 12, "#9fd6f2"))
    b.append(rect(66, 62, 16, 12, "#9fd6f2"))
    # flags
    for i, (fx, col) in enumerate([(104, "#e74c3c"), (118, "#f1c40f"), (132, "#2980b9")]):
        b.append(rect(fx, 40, 2, 50, "#cccccc"))
        b.append(f'<rect x="{fx + 2}" y="40" width="10" height="6" fill="{col}"><animate attributeName="width" values="10;7;10" dur="{0.7 + i * 0.15:.2f}s" repeatCount="indefinite"/></rect>')
    # locker room building (behind the court)
    b.append(block(176, 58, 64, 40, "#3d6fb6", 6))
    b.append(block(172, 51, 72, 8, "#2c528a", 6))
    b.append(rect(201, 76, 14, 22, "#2c528a"))
    b.append(rect(182, 66, 12, 8, "#9fd6f2"))
    b.append(rect(222, 66, 12, 8, "#9fd6f2"))
    # steward in a yellow vest, on the way to the locker room
    b.append(person(154, 66, "#f1c40f", pants=NAVY, cap=NAVY, hair="#3b2416", s=0.8,
                    extra=[(0, 20, 14, 2, "#ffffff")]))
    # court (middle)
    b.append(court_surface(110, 104, 140, 62))
    b.append(net(126, 128, 108))
    # shed (right corner)
    b.append(block(268, 70, 36, 28, WOOD, 5))
    b.append(block(264, 63, 44, 8, WOOD_DARK, 5))
    b.append(rect(280, 80, 10, 18, WOOD_DARK))
    b.append(rect(288, 87, 3, 3, "#b0b0b0"))
    # trees
    b += [tree(2, 104), tree(290, 112), tree(94, 60)]
    # life: grass, flowers, birds, a ball on the court, a butterfly
    b.append(meadow(
        tufts=[(20, 152), (40, 172), (60, 142), (64, 168), (106, 176), (258, 150), (268, 174), (304, 164), (30, 128), (252, 120)],
        flowers=[(50, 158, "#ffffff"), (36, 140, "#ff8fb1"), (60, 176, "#ffe14d"), (276, 160, "#ffffff"), (300, 176, "#ff8fb1")],
    ))
    # two players rallying on the court
    b.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;6 0;0 0" dur="2.2s" repeatCount="indefinite"/>'
             + person(150, 102, "#e74c3c", pants="#ffffff", shorts="#ffffff", s=0.5)
             + racket(163, 106.5, "#2d3a5a", "#111111", angle=35, s=0.24) + '</g>')
    b.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;-5 0;0 0" dur="2.2s" repeatCount="indefinite"/>'
             + person(196, 138, "#2980b9", pants="#ffffff", shorts="#ffffff", s=0.6)
             + racket(189, 143.7, "#c0392b", "#111111", angle=-35, s=0.28) + '</g>')
    b.append('<g shape-rendering="auto"><circle r="1.4" fill="#d7e84a">'
             '<animateMotion path="M 158 112 Q 170 104 182 152 Q 188 138 193 146 Q 182 110 166 120 Q 162 110 158 112" '
             'dur="2.2s" repeatCount="indefinite"/></circle></g>')
    b.append(butterfly(40, 132, "#ffe14d"))
    b.append(birds())
    return svg("".join(b), sky_defs())


def office():
    b = [rect(0, 0, W, 120, "#f3e7cf"), rect(0, 120, W, 60, "#b07a4a")]
    for x in range(0, W, 20):
        b.append(rect(x, 120, 1, 60, "#9c6a3e"))
    # window
    b += [rect(214, 22, 76, 50, "#ffffff"), rect(218, 26, 68, 42, "#9fd6f2"), rect(251, 26, 2, 42, "#ffffff"), cloud(224, 34, 0.6)]
    # draw-sheet board
    b += [rect(26, 18, 90, 60, "#ffffff"), rect(26, 18, 90, 8, "#d9743a")]
    b.append('<text x="71" y="24.5" font-family="monospace" font-size="6" font-weight="bold" text-anchor="middle" fill="#ffffff">DRAW</text>')
    for row in range(5):
        b.append(rect(34, 32 + row * 9, 30, 2, "#9a9a9a"))
        b.append(rect(74, 36 + (row // 2) * 18, 30, 2, "#9a9a9a"))
    # wall clock with moving hands
    b.append('<g shape-rendering="auto"><circle cx="170" cy="34" r="10" fill="#ffffff" stroke="#2d3a2a" stroke-width="2"/>'
             '<line x1="170" y1="34" x2="170" y2="27" stroke="#2d3a2a" stroke-width="1.5">'
             '<animateTransform attributeName="transform" type="rotate" values="0 170 34;360 170 34" dur="20s" repeatCount="indefinite"/></line>'
             '<line x1="170" y1="34" x2="175" y2="34" stroke="#d9743a" stroke-width="1.5">'
             '<animateTransform attributeName="transform" type="rotate" values="0 170 34;360 170 34" dur="240s" repeatCount="indefinite"/></line></g>')
    # potted plant that sways
    b.append(block(276, 146, 18, 16, "#c0392b", 4))
    b.append('<g><animateTransform attributeName="transform" type="rotate" values="-3 285 146;3 285 146;-3 285 146" dur="2.2s" repeatCount="indefinite"/>'
             + block(279, 132, 6, 14, "#3f9a3a", 3) + block(286, 126, 6, 20, "#4caf50", 3) + block(272, 136, 6, 10, "#3f9a3a", 3) + '</g>')
    # woman behind the desk
    b.append(person(150, 70, "#2a9d8f", hair="#3b2416", s=1.4))
    # desk
    b.append(block(96, 104, 150, 40, "#8a5a32", 7))
    b += [block(112, 98, 22, 4, "#ffffff", 3), block(138, 97, 18, 4, "#f7f2e4", 3), block(206, 98, 16, 4, "#ffffff", 3)]
    b.append(rect(160, 116, 26, 10, "#d9743a"))
    b.append('<text x="173" y="123.5" font-family="monospace" font-size="5" font-weight="bold" text-anchor="middle" fill="#ffffff">INFO</text>')
    return svg("".join(b))


def locker_room():
    b = [rect(0, 0, W, 130, "#dfe8ee")]
    for y in range(0, 130, 12):
        b.append(rect(0, y, W, 1, "#c9d5dc"))
    for x in range(0, W, 16):
        b.append(rect(x, 0, 1, 130, "#c9d5dc"))
    b.append(rect(0, 130, W, 50, "#8fa3b0"))
    b.append(
        '<rect x="110" y="0" width="100" height="5" fill="#fffbe6">'
        '<animate attributeName="opacity" values="1;1;0.4;1;0.6;1;1" '
        'keyTimes="0;0.8;0.82;0.84;0.86;0.88;1" dur="3.5s" repeatCount="indefinite"/></rect>'
    )
    for i in range(7):
        x = 18 + i * 40
        b.append(block(x, 22, 34, 96, "#3d6fb6", 5))
        for v in range(3):
            b.append(rect(x + 8, 30 + v * 4, 18, 2, "#2c528a"))
        b.append(rect(x + 26, 66, 3, 10, "#d6dde2"))
    # dripping pipe on the left
    b.append(rect(4, 0, 6, 14, "#9aa5ad"))
    b.append(rect(2, 12, 10, 3, "#7d8890"))
    b.append('<g shape-rendering="auto"><circle cx="7" cy="18" r="1.6" fill="#7fc4ea">'
             '<animate attributeName="cy" values="16;140" dur="1.1s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.9;1" dur="1.1s" repeatCount="indefinite"/></circle>'
             '</g>')
    # metal bucket that catches the drops: tapered body, rim, handle, water
    b.append('<g shape-rendering="auto">'
             '<path d="M 3 141 L 5.5 157 L 16.5 157 L 19 141 Z" fill="#a3acb3" stroke="#5f676e" stroke-width="0.8"/>'
             '<line x1="4" y1="146" x2="18" y2="146" stroke="#7d868d" stroke-width="0.8"/>'
             '<line x1="4.8" y1="152" x2="17.2" y2="152" stroke="#7d868d" stroke-width="0.8"/>'
             '<ellipse cx="11" cy="141" rx="8" ry="2.4" fill="#5aa9d6" stroke="#5f676e" stroke-width="1"/>'
             '<path d="M 3.5 141 Q 11 127 18.5 141" fill="none" stroke="#5f676e" stroke-width="1"/>'
             '<ellipse cx="7.5" cy="141" rx="1" ry="0.4" fill="none" stroke="#ffffff" stroke-width="0.7">'
             '<animate attributeName="rx" values="1;4.5" dur="1.1s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;0;1;0" keyTimes="0;0.85;0.9;1" dur="1.1s" repeatCount="indefinite"/></ellipse>'
             '</g>')
    # bench with towel and bag
    b.append(block(40, 132, 240, 8, WOOD, 5))
    b += [rect(56, 140, 6, 22, WOOD_DARK), rect(258, 140, 6, 22, WOOD_DARK)]
    b.append(block(90, 124, 30, 8, "#ffffff", 4))
    b.append(block(190, 116, 46, 16, "#c0392b", 5))
    b.append(rect(204, 112, 18, 4, "#8e2a20"))
    return svg("".join(b))


def umpire_chair(x, ground_y, asleep):
    """A tall umpire's chair with a ladder; the umpire sits on it."""
    seat_y = ground_y - 40
    green, light = "#1f6b45", "#2e8b57"
    parts = [rect(x, seat_y, 3, 40, green), rect(x + 17, seat_y, 3, 40, green)]
    for k in range(5):
        parts.append(rect(x + 3, seat_y + 6 + k * 7, 14, 2, light))     # ladder rungs
    parts.append(rect(x, seat_y - 22, 20, 14, "#17583a"))              # backrest
    parts.append(person(x + 3, seat_y - 24, "#ffffff", pants=NAVY, hair="#777777",
                        cap=green, s=0.6, asleep=asleep))
    parts.append(block(x - 2, seat_y - 9, 24, 10, green, 3))           # seat and rail
    if asleep:
        for i in range(3):
            parts.append(
                f'<text x="{x + 16 + i * 3}" y="{seat_y - 26}" font-family="monospace" font-size="{5 + i}" '
                f'font-weight="bold" fill="#2d3a5a" opacity="0">z'
                f'<animate attributeName="y" values="{seat_y - 26};{seat_y - 40}" dur="2.4s" begin="{i * 0.8}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;1;0" dur="2.4s" begin="{i * 0.8}s" repeatCount="indefinite"/></text>'
            )
    return "".join(parts)


def court(match_due=False, groundskeeper=False):
    b = [outdoor(70), cloud(40, 10), cloud(230, 18, 0.7)]
    # spectators behind the back fence
    for i, (sx, col) in enumerate([(24, "#e74c3c"), (60, "#f1c40f"), (104, "#8e44ad"),
                                   (196, "#27ae60"), (232, "#e67e22"), (300, "#2980b9")]):
        b.append(person(sx, 49 + (i % 2), col, hair=["#5b3a22", "#222222", "#c9a26b"][i % 3], s=0.45))
    for x in range(0, W, 10):
        b.append(rect(x, 62, 2, 10, "#2e7d4f"))
    b.append(rect(0, 62, W, 9, "#2e7d4f"))
    b.append(court_surface(50, 74, 220, 104))
    b.append(net(64, 108, 192))
    # players' benches left and right of the umpire's chair, with towels and bottles
    b.append(block(258, 108, 22, 5, "#c0392b", 3))
    b += [rect(260, 113, 2, 6, "#7a2318"), rect(276, 113, 2, 6, "#7a2318"), rect(262, 105, 6, 3, "#ffffff"), rect(272, 102, 2, 6, "#5aa9e6")]
    b.append(block(306, 108, 16, 5, "#c0392b", 3))
    b += [rect(308, 113, 2, 6, "#7a2318"), rect(310, 105, 6, 3, "#ffffff")]
    b.append(umpire_chair(284, 118, asleep=not match_due))
    # ball kid crouching at the net post
    b.append(person(44, 100, "#2e86de", pants="#1b4f72", shorts="#1b4f72", s=0.55))
    if match_due:
        b.append(
            '<g shape-rendering="auto">'
            '<circle cx="160" cy="92" r="9" fill="#ffe14d" stroke="#ffffff" stroke-width="2">'
            '<animate attributeName="r" values="8;11;8" dur="0.8s" repeatCount="indefinite"/></circle>'
            '<circle cx="160" cy="92" r="14" fill="none" stroke="#ffe14d" stroke-width="2">'
            '<animate attributeName="r" values="10;20;10" dur="0.8s" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/></circle>'
            '<text x="160" y="96" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle" fill="#7a4a00">!</text>'
            "</g>"
        )
    b.append(meadow(
        tufts=[(8, 92), (16, 176), (300, 96), (306, 172), (296, 132), (22, 100)],
        flowers=[(12, 104, "#ffffff"), (304, 150, "#ffe14d"), (300, 110, "#ff8fb1")],
    ))
    b.append(birds((16, 24)))
    if groundskeeper:
        b.append(person(6, 118, "#4f7f3a", pants="#3b4f2a", cap="#2f5d2a", hair="#888888", s=1.0))
        b.append(f'<g shape-rendering="auto"><line x1="24" y1="112" x2="36" y2="160" stroke="{WOOD}" stroke-width="2"/></g>')
        b.append(rect(30, 158, 14, 3, "#777777"))
    return svg("".join(b), sky_defs())


def court_2(with_groundskeeper=True):
    b = [outdoor(84), cloud(26, 16), cloud(210, 10, 0.8)]
    # Court 2 in the background (further away, so smaller)
    b.append(court_surface(176, 88, 150, 40))
    b.append(net(196, 104, 110))
    # wheelbarrow
    b.append(block(36, 134, 46, 20, "#2f5d2a", 6))
    b.append(f'<g shape-rendering="auto"><circle cx="44" cy="160" r="7" fill="#333333"/></g>')
    b.append(rect(80, 140, 22, 3, "#555555"))
    if with_groundskeeper:
        # groundskeeper with rake, same size as the player
        b.append(person(110, 100, "#4f7f3a", pants="#3b4f2a", cap="#2f5d2a", hair="#888888", s=1.5))
        b.append(f'<g shape-rendering="auto"><line x1="134" y1="122" x2="150" y2="166" stroke="{WOOD}" stroke-width="2"/></g>')
        b.append(rect(142, 165, 18, 3, "#777777"))
        for i in range(5):
            b.append(rect(143 + i * 4, 168, 1.5, 3, "#777777"))
    else:
        # only his rake, leaning against the wheelbarrow
        b.append(f'<g shape-rendering="auto"><line x1="90" y1="118" x2="104" y2="166" stroke="{WOOD}" stroke-width="2"/></g>')
        b.append(rect(96, 165, 18, 3, "#777777"))
    b.append(meadow(
        tufts=[(10, 100), (22, 176), (96, 112), (102, 176), (60, 100), (150, 96), (8, 140)],
        flowers=[(14, 120, "#ff8fb1"), (72, 112, "#ffffff"), (100, 150, "#ffe14d"), (30, 110, "#ffffff")],
    ))
    b.append(butterfly(46, 104, "#ffffff"))
    b.append(birds((14, 22)))
    return svg("".join(b), sky_defs())


def entrance():
    """Start screen: entrance gate with the steward, the office building."""
    b = [outdoor(88), cloud(30, 14), cloud(200, 24, 0.8), cloud(262, 8, 0.6)]
    for x in range(0, W, 10):                                   # fence, open at the gate
        if not 200 <= x <= 250:
            b.append(rect(x, 80, 2, 10, "#ffffff"))
    b.append(rect(0, 82, 200, 2, "#ffffff"))
    b.append(rect(252, 82, W - 252, 2, "#ffffff"))
    # sandy path from the front, through the gate, to the right
    sand = "#e3c28f"
    b.append(poly([(118, 180), (176, 180), (246, 100), (214, 100)], sand))
    b.append(poly([(214, 98), (W, 98), (W, 112), (240, 112)], sand))
    # office building (left), like before
    b.append(block(14, 52, 74, 46, "#efe6d2", 6))
    b.append(block(10, 44, 82, 9, "#c0392b", 6))
    b.append(rect(44, 74, 14, 24, WOOD))
    b.append(rect(20, 62, 16, 12, "#9fd6f2"))
    b.append(rect(66, 62, 16, 12, "#9fd6f2"))
    # flags
    for i, (fx, col) in enumerate([(104, "#e74c3c"), (118, "#f1c40f"), (132, "#2980b9")]):
        b.append(rect(fx, 40, 2, 50, "#cccccc"))
        b.append(f'<rect x="{fx + 2}" y="40" width="10" height="6" fill="{col}"><animate attributeName="width" values="10;7;10" dur="{0.7 + i * 0.15:.2f}s" repeatCount="indefinite"/></rect>')
    # the gate with a banner
    b.append(block(196, 48, 8, 52, "#8a8f94", 4))
    b.append(block(250, 48, 8, 52, "#8a8f94", 4))
    b.append(block(190, 38, 72, 12, "#d9743a", 4))
    b.append('<text x="226" y="46.5" font-family="monospace" font-size="6.5" font-weight="bold" text-anchor="middle" fill="#ffffff">TOURNAMENT</text>')
    # the steward stands in the gate
    b.append(person(214, 68, "#f1c40f", pants=NAVY, cap=NAVY, hair="#3b2416", s=0.8,
                    extra=[(0, 20, 14, 2, "#ffffff")]))
    b += [tree(2, 104), tree(160, 58), tree(292, 118)]
    b.append(meadow(
        tufts=[(20, 152), (40, 172), (60, 142), (96, 176), (200, 150), (270, 140), (230, 172), (300, 168)],
        flowers=[(50, 158, "#ffffff"), (36, 140, "#ff8fb1"), (210, 160, "#ffe14d"), (282, 150, "#ffffff")],
    ))
    b.append(butterfly(40, 132, "#ffe14d"))
    b.append(birds())
    return svg("".join(b), sky_defs())


def main_path():
    """The crossing in the middle of the grounds: lockers, food stand, signpost."""
    b = [outdoor(84), cloud(40, 12), cloud(220, 20, 0.8)]
    for x in range(0, W, 10):
        b.append(rect(x, 76, 2, 10, "#ffffff"))
    b.append(rect(0, 78, W, 2, "#ffffff"))
    sand = "#e3c28f"
    b.append(rect(0, 128, 160, 18, sand))                              # path from the entrance
    b.append(poly([(150, 84), (178, 84), (190, 180), (138, 180)], sand))   # up to the courts, down to the shed
    # locker room building
    b.append(block(20, 52, 80, 46, "#3d6fb6", 6))
    b.append(block(16, 45, 88, 8, "#2c528a", 6))
    b.append(rect(52, 74, 14, 24, "#2c528a"))
    b.append(rect(26, 62, 14, 8, "#9fd6f2"))
    b.append(rect(78, 62, 14, 8, "#9fd6f2"))
    # fountain with water jets
    b.append('<g shape-rendering="auto">'
             # basin: stone rim and water surface
             '<ellipse cx="258" cy="106" rx="38" ry="9" fill="#b8bec4"/>'
             '<rect x="220" y="106" width="76" height="12" fill="#a3aab1"/>'
             '<ellipse cx="258" cy="118" rx="38" ry="9" fill="#8f979e"/>'
             '<ellipse cx="258" cy="106" rx="33" ry="6.5" fill="#5aa9e6"/>'
             '<ellipse cx="258" cy="106" rx="20" ry="3.5" fill="none" stroke="#bfe3fb" stroke-width="0.8">'
             '<animate attributeName="rx" values="8;30" dur="1.6s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="1;0" dur="1.6s" repeatCount="indefinite"/></ellipse>'
             # column and upper bowl
             '<rect x="254" y="80" width="8" height="26" fill="#a3aab1"/>'
             '<ellipse cx="258" cy="80" rx="13" ry="3.5" fill="#b8bec4"/>'
             '<ellipse cx="258" cy="79.5" rx="10" ry="2.3" fill="#5aa9e6"/>'
             '<rect x="256.5" y="68" width="3" height="12" fill="#bfe3fb">'
             '<animate attributeName="height" values="12;9;12" dur="0.6s" repeatCount="indefinite"/>'
             '<animate attributeName="y" values="68;71;68" dur="0.6s" repeatCount="indefinite"/></rect>'
             + "".join(
                 f'<circle r="1.1" fill="#d6efff"><animateMotion path="M 258 69 Q {258 + dx} {60} {258 + dx * 2.2} {104}" '
                 f'dur="{0.9 + (i % 3) * 0.15:.2f}s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/></circle>'
                 for i, dx in enumerate([-12, -8, -4, 4, 8, 12, -10, 10]))
             + '</g>')
    # Two visitors admiring the fountain (bobbing and blinking like everyone)
    # Left: full ginger beard, black cap, shiny green bomber jacket with white
    # sleeve stripes over a black shirt, dark trousers, broad build.
    b.append(person(210, 116, "#1fa64a", pants="#3a3d42", hair="#c8642a", cap="#1a1a1a",
                    shoes="#2b2b2b", s=0.85,
                    extra=[(-2, 13, 2, 13, "#1fa64a"), (14, 13, 2, 13, "#1fa64a"),   # broad build
                           (5, 13, 4, 14, "#111111"),                                 # black shirt
                           (1, 7, 12, 6, "#c8642a"), (2, 13, 10, 5, "#c8642a"),        # long beard
                           (3, 18, 8, 3, "#b5561f"),
                           (-3, 18, 3, 1, "#ffffff"), (14, 18, 3, 1, "#ffffff"),     # sleeve stripes
                           (-3, 20, 3, 1, "#ffffff"), (14, 20, 3, 1, "#ffffff"),
                           (10, 15, 3, 1, "#ffffff"),                                 # chest lettering
                           (5, -1, 4, 2, "#2e8b3a")]))                                # cap badge
    # Right: blue cap with an orange badge, blue varsity jacket with orange
    # sleeves, an orange emblem and patches, jeans, short beard, broad build.
    b.append(person(286, 116, "#1f4fa8", pants="#2c3e66", skin="#7a4a2e", hair="#1a1a1a",
                    cap="#1f4fa8", shoes="#1a1a1a", s=0.85,
                    extra=[(-2, 13, 2, 13, "#1f4fa8"), (14, 13, 2, 13, "#1f4fa8"),   # broad build
                           (-3, 13, 3, 11, "#f28c28"), (14, 13, 3, 11, "#f28c28"),   # orange sleeves
                           (0, 12, 14, 1, "#f28c28"),                                 # collar stripe
                           (8, 15, 4, 4, "#f28c28"),                                  # emblem
                           (1, 14, 2, 2, "#ffffff"), (2, 20, 2, 2, "#d9d9d9"),        # patches
                           (3, 8, 8, 3, "#2b1a10"),                                   # short beard
                           (5, -1, 4, 2, "#f28c28")]))                                # cap badge
    # signpost at the crossing
    b.append(rect(126, 92, 3, 38, WOOD_DARK))
    b.append(poly([(106, 94), (138, 94), (142, 97.5), (138, 101), (106, 101)], "#a8743f"))
    b.append('<text x="122" y="99.5" font-family="monospace" font-size="4.6" font-weight="bold" text-anchor="middle" fill="#ffffff">COURTS</text>')
    b.append(poly([(106, 104), (138, 104), (142, 107.5), (138, 111), (106, 111)], "#a8743f"))
    b.append('<text x="122" y="109.5" font-family="monospace" font-size="4.6" font-weight="bold" text-anchor="middle" fill="#ffffff">SHED</text>')
    # a visitor strolling along the fence
    b.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;-70 0;0 0" dur="14s" repeatCount="indefinite"/>'
             + person(206, 84, "#8e44ad", hair="#c9a26b", s=0.55) + "</g>")
    b += [tree(110, 54), tree(204, 52), tree(302, 58)]
    b.append(meadow(
        tufts=[(20, 172), (60, 160), (100, 176), (210, 160), (240, 176), (300, 112), (8, 112)],
        flowers=[(30, 160, "#ffffff"), (112, 170, "#ffe14d"), (230, 150, "#ff8fb1"), (270, 172, "#ffffff")],
    ))
    b.append(butterfly(250, 136, "#ffffff"))
    b.append(birds())
    return svg("".join(b), sky_defs())


def shed(opened=False):
    b = [outdoor(80), cloud(40, 14), cloud(240, 22, 0.7), tree(14, 96), tree(282, 104)]
    b.append(block(90, 62, 140, 92, WOOD, 9))
    for y in range(68, 154, 9):
        b.append(rect(90, y, 140, 1, WOOD_DARK))
    b.append(block(82, 48, 156, 16, "#6b4426", 9))
    # peeling paint
    for px, py, pw in [(98, 72, 14), (196, 90, 18), (108, 130, 10), (214, 122, 8)]:
        b.append(rect(px, py, pw, 5, "#c79a6a"))
    # door
    b.append(rect(136, 86, 48, 68, "#6b4426"))
    b.append(rect(159, 86, 2, 68, "#563620"))
    if opened:
        # right door wing stands ajar: dark inside, padlock lies in the grass
        b.append(rect(160, 86, 24, 68, "#1f150d"))
        b.append(poly([(184, 86), (196, 82), (196, 158), (184, 154)], "#7a5230"))
        b.append(f'<g shape-rendering="auto"><path d="M 176 158 v -4 a 4 4 0 0 1 8 0 v 4" fill="none" stroke="#9aa0a6" stroke-width="1.8"/></g>')
        b.append(block(173, 158, 13, 9, "#7d848b", 2))
        b.append(meadow(
            tufts=[(40, 172), (60, 150), (20, 140), (74, 176), (300, 150), (290, 176), (250, 176)],
            flowers=[(50, 162, "#ffffff"), (68, 140, "#ffe14d"), (300, 168, "#ff8fb1"), (30, 176, "#ff8fb1")],
        ))
        b.append(butterfly(36, 128, "#ffe14d"))
        b.append(birds((16, 26)))
        return svg("".join(b), sky_defs())
    # padlock, swinging a little
    b.append('<g id="padlock"><g><animateTransform attributeName="transform" type="rotate" values="-5 162 104;5 162 104;-5 162 104" dur="2.2s" repeatCount="indefinite"/>')
    b.append(f'<g shape-rendering="auto"><path d="M 156 112 v -6 a 6 6 0 0 1 12 0 v 6" fill="none" stroke="#9aa0a6" stroke-width="2.5"/></g>')
    b.append(block(152, 112, 20, 16, "#7d848b", 3))
    b.append(rect(160, 118, 3, 5, "#3a3d40"))
    b.append("</g></g>")
    # weeds
    for wx in (94, 120, 200, 224):
        b.append(rect(wx, 148, 3, 8, "#3f8a2f"))
        b.append(rect(wx + 4, 150, 3, 6, "#3f8a2f"))
    b.append(meadow(
        tufts=[(40, 172), (60, 150), (20, 140), (74, 176), (300, 150), (290, 176), (250, 176)],
        flowers=[(50, 162, "#ffffff"), (68, 140, "#ffe14d"), (300, 168, "#ff8fb1"), (30, 176, "#ff8fb1")],
    ))
    b.append(butterfly(36, 128, "#ffe14d"))
    b.append(birds((16, 26)))
    return svg("".join(b), sky_defs())


def shed_inside(with_rackets=True):
    b = [rect(0, 0, W, H, "#5c3d24")]
    for x in range(0, W, 18):
        b.append(rect(x, 0, 2, 140, "#4a311d"))
    b.append(rect(0, 140, W, 40, "#3e2a19"))
    # light beam and dust
    b.append(poly([(196, 0), (236, 0), (190, 180), (120, 180)], "#fff3c4", 'opacity="0.18"'))
    for i, (dx, dy) in enumerate([(200, 40), (186, 80), (172, 120), (210, 60), (160, 150)]):
        b.append(f'<rect x="{dx}" y="{dy}" width="2" height="2" fill="#fff6d8"><animate attributeName="opacity" values="0;1;0" dur="{1 + i * 0.3:.1f}s" repeatCount="indefinite"/><animate attributeName="y" values="{dy};{dy - 6};{dy}" dur="{2 + i * 0.4:.1f}s" repeatCount="indefinite"/></rect>')
    # drag mat for smoothing the clay court, hanging on two hooks
    b.append(rect(20, 14, 3, 6, "#8a8f94"))
    b.append(rect(76, 14, 3, 6, "#8a8f94"))
    b.append(block(14, 20, 70, 6, "#a8743f", 3))                 # wooden pull bar
    b.append('<g shape-rendering="auto">'
             '<rect x="16" y="26" width="66" height="34" fill="#4a4e52" opacity="0.35"/>'
             + "".join(f'<line x1="{16 + i * 6}" y1="26" x2="{16 + i * 6 + 12}" y2="60" stroke="#b9bec2" stroke-width="0.8"/>' for i in range(-2, 11))
             + "".join(f'<line x1="{16 + i * 6 + 12}" y1="26" x2="{16 + i * 6}" y2="60" stroke="#b9bec2" stroke-width="0.8"/>' for i in range(-2, 11))
             + '<rect x="16" y="26" width="66" height="34" fill="none" stroke="#8a8f94" stroke-width="1.2"/>'
             # pull rope down to a T-handle
             '<path d="M 22 26 Q 49 70 49 92 M 76 26 Q 49 70 49 92" fill="none" stroke="#c9a26b" stroke-width="1"/>'
             '</g>')
    b.append(rect(42, 92, 14, 3, "#a8743f"))
    # mask the mesh lines that stick out of the mat
    b.append(rect(0, 26, 16, 34, "#5c3d24"))
    b.append(rect(82, 26, 14, 34, "#5c3d24"))
    b.append(rect(0, 26, 2, 34, "#4a311d"))
    b.append(rect(90, 26, 2, 34, "#4a311d"))
    # ball basket
    b.append(block(240, 118, 54, 30, "#8b8f94", 6))
    for k in range(6):
        b.append(f'<g shape-rendering="auto"><circle cx="{247 + k * 8}" cy="114" r="4" fill="#d7e84a"/></g>')
    # a small spider going up and down on its thread
    b.append('<g shape-rendering="auto"><line x1="222" y1="0" x2="222" y2="30" stroke="#d9d2bf" stroke-width="0.5">'
             '<animate attributeName="y2" values="18;40;18" dur="3s" repeatCount="indefinite"/></line>'
             '<g><animateTransform attributeName="transform" type="translate" values="0 18;0 40;0 18" dur="3s" repeatCount="indefinite"/>'
             '<circle cx="222" cy="0" r="2" fill="#1f1f1f"/>'
             '<path d="M 218 -2 L 222 0 L 226 -2 M 218 2 L 222 0 L 226 2" stroke="#1f1f1f" stroke-width="0.6" fill="none"/></g></g>')
    if with_rackets:
        # head down, handle up, leaning against the wall like real rackets
        b.append(racket(110, 127, "#1f5e3a", "#111111", angle=172, s=0.7))
        b.append(racket(170, 127, "#5aa9e6", "#6b5a45", strings="#d9d2bf", angle=187, worn=True, s=0.7))
    else:
        b.append(rect(96, 136, 80, 4, "#33231a"))
    return svg("".join(b))


# --- endings ----------------------------------------------------------------


def crowd(y, colors):
    parts = [rect(0, y, W, 40, "#45536b")]
    for i, x in enumerate(range(4, W, 14)):
        fan = rect(x, y + 6 + (i % 2) * 3, 10, 10, SKIN) + rect(
            x - 1, y + 16 + (i % 2) * 3, 12, 14, colors[i % len(colors)])
        parts.append(
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 -2;0 0" dur="{0.9 + (i % 4) * 0.15:.2f}s" '
            f'begin="{(i % 5) * 0.2:.1f}s" repeatCount="indefinite"/>{fan}</g>'
        )
    return "".join(parts)


def trophy(x, y, animated):
    t = [
        f'<g shape-rendering="auto">',
        f'<path d="M {x} {y} h 24 v 8 a 12 12 0 0 1 -24 0 z" fill="#f4c430" stroke="#c99a12" stroke-width="1.5"/>',
        f'<path d="M {x} {y + 3} h -6 a 6 6 0 0 0 6 8" fill="none" stroke="#c99a12" stroke-width="2"/>',
        f'<path d="M {x + 24} {y + 3} h 6 a 6 6 0 0 1 -6 8" fill="none" stroke="#c99a12" stroke-width="2"/>',
        rect(x + 10, y + 19, 4, 6, "#c99a12"),
        rect(x + 4, y + 25, 16, 5, "#8a6a10"),
        "</g>",
    ]
    if not animated:
        return "".join(t)
    sparkles = "".join(
        f'<path d="M {sx} {sy - 4} L {sx + 1} {sy - 1} L {sx + 4} {sy} L {sx + 1} {sy + 1} L {sx} {sy + 4} L {sx - 1} {sy + 1} L {sx - 4} {sy} L {sx - 1} {sy - 1} Z" fill="#ffffff">'
        f'<animate attributeName="opacity" values="0;1;0" dur="0.7s" begin="{delay}s" repeatCount="indefinite"/></path>'
        for sx, sy, delay in [(x - 6, y - 4, 0), (x + 30, y + 2, 0.4), (x + 12, y - 10, 0.8)]
    )
    return (
        "<g>"
        '<animateTransform attributeName="transform" type="translate" values="0 0; 0 -5; 0 0" dur="0.6s" repeatCount="indefinite"/>'
        + "".join(t)
        + f'<g shape-rendering="auto">{sparkles}</g>'
        + "</g>"
    )


def podium():
    """Stands with the crowd and a podium: 2 (left), 1 (middle), 3 (right)."""
    # Evening after the final: red sky, a low red sun behind the stands
    b = [rect(0, 0, W, H, "url(#evening)"),
         '<g shape-rendering="auto"><circle cx="262" cy="42" r="26" fill="#ff7043" opacity="0.35"/>'
         '<circle cx="262" cy="42" r="17" fill="#ff5a36"/></g>',
         crowd(40, ["#e74c3c", "#2980b9", "#f1c40f", "#27ae60", "#8e44ad"])]
    # A meadow, and a square of stone tiles for the podium
    b.append(rect(0, 80, W, 100, GRASS))
    for i, y in enumerate(range(80, H, 12)):
        if i % 2:
            b.append(rect(0, y, W, 6, GRASS_DARK))
    b.append(poly([(100, 140), (222, 140), (238, 178), (84, 178)], "#b9b4aa"))
    for k in range(1, 4):                       # tile rows
        y = 140 + k * 9.5
        b.append(rect(100 - k * 4, y, 122 + k * 8, 1, "#9d988e"))
    for k in range(1, 8):                       # tile columns, slightly fanning out
        x_top, x_bottom = 100 + k * 15.25, 84 + k * 19.25
        b.append(f'<line x1="{x_top}" y1="140" x2="{x_bottom}" y2="178" stroke="#9d988e" stroke-width="1"/>')
    b.append(meadow(tufts=[(20, 150), (60, 170), (270, 160), (300, 176), (40, 120), (290, 120)],
                    flowers=[(30, 168, "#ffffff"), (282, 140, "#ffe14d"), (60, 134, "#ff8fb1")]))
    # One podium, the three places touching: 2 | 1 | 3
    b.append(block(110, 138, 34, 30, "#c0c6cc", 5))    # 2nd place, silver
    b.append(block(144, 126, 34, 42, "#f4c430", 5))    # 1st place, gold
    b.append(block(178, 148, 34, 20, "#cd7f32", 5))    # 3rd place, bronze
    b.append('<text x="161" y="152" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle" fill="#8a6a10">1</text>')
    b.append('<text x="127" y="158" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle" fill="#6b7177">2</text>')
    b.append('<text x="195" y="162" font-family="monospace" font-size="9" font-weight="bold" text-anchor="middle" fill="#7a4a1c">3</text>')
    return b


def clapping(figure):
    """Small fast hop, like someone clapping and cheering."""
    return ('<g><animateTransform attributeName="transform" type="translate" '
            'values="0 0; 0 -2; 0 0" dur="0.5s" repeatCount="indefinite"/>' + figure + "</g>")


def ceremony_win(kit="white"):
    b = podium()
    b.append(clapping(person(121.4, 106, "#e67e22", hair="#222222", shorts="#ffffff", arms_up=True, s=0.8)))
    b.append(clapping(person(189.4, 116, "#27ae60", hair="#c9a26b", shorts="#ffffff", arms_up=True, s=0.8)))
    b.append(player_tennis(155.4, 94, s=0.8, arms_up=True, kit=kit))
    b.append(trophy(149, 68, animated=True))
    b.append(flashes(48, 72))
    # confetti
    colors = ["#e74c3c", "#f1c40f", "#2980b9", "#27ae60", "#ffffff"]
    for i in range(24):
        x = (i * 37) % W
        dur = 1.3 + (i % 5) * 0.25
        b.append(
            f'<rect x="{x}" y="-6" width="4" height="3" fill="{colors[i % 5]}">'
            f'<animate attributeName="y" values="-6;{H}" dur="{dur}s" begin="{(i % 7) * 0.3}s" repeatCount="indefinite"/></rect>'
        )
    return svg("".join(b), sky_defs("#e8553c", "#ffb36b", gid="evening"))


def ceremony_loss(kit="white"):
    b = podium()
    b.append(person(155.4, 94, "#e67e22", hair="#222222", shorts="#ffffff", arms_up=True, s=0.8))
    b.append(trophy(149, 68, animated=False))
    b.append(flashes(48, 72, n=4))
    # the player is runner-up on place 2 and claps for the winner
    b.append(clapping(player_tennis(121.4, 106, s=0.8, arms_up=True, kit=kit)))
    b.append(clapping(person(189.4, 116, "#27ae60", hair="#c9a26b", shorts="#ffffff", arms_up=True, s=0.8)))
    return svg("".join(b), sky_defs("#e8553c", "#ffb36b", gid="evening"))


def end_b(kit="white"):
    """Ending B, last page: the empty Center Court at sunset, the player alone
    on the bench with the Wilson; then THE END fades in."""
    defs = sky_defs("#5d4a8a", "#f08a5d", gid="dusk")
    b = [rect(0, 0, W, 70, "url(#dusk)")]
    # the sun, half gone behind the stands
    b.append('<g shape-rendering="auto"><circle cx="232" cy="46" r="22" fill="#ff7043" opacity="0.35"/>'
             '<circle cx="232" cy="46" r="14" fill="#ff5a36"/></g>')
    b.append(birds((18, 28), color="#3a2a3a"))
    # empty stands
    b.append(block(0, 46, W, 26, "#5c4b62", 4))
    for x in range(6, W, 16):
        b.append(rect(x, 54, 10, 3, "#4a3b50"))
        b.append(rect(x, 64, 10, 3, "#4a3b50"))
    # the court in evening light
    b.append(rect(0, 72, W, H - 72, "#4f8a3a"))
    b.append(court_surface(30, 78, 220, 102))
    b.append(rect(0, 72, W, H - 72, "#2a1a3a", 'opacity="0.18"'))   # dusk tint
    b.append(net(44, 110, 192))
    # the players' bench on the grass next to the court, the player sitting on it
    b.append(block(262, 124, 50, 4, "#a83226", 3))                    # backrest (behind the player)
    b.append(player_tennis(280, 106, s=1.15, kit=kit))
    b.append(block(262, 138, 50, 8, "#c0392b", 4))                    # seat (hides the legs)
    b += [rect(266, 146, 3, 14, "#7a2318"), rect(304, 146, 3, 14, "#7a2318")]
    # the Wilson leaning against the bench, a towel on it
    b.append(racket(258, 146, "#1f5e3a", "#111111", angle=14, s=0.42))
    b.append(block(296, 132, 12, 4, "#ffffff", 2))
    # THE END fades in after a few seconds
    b.append('<g opacity="0"><animate attributeName="opacity" values="0;1" dur="1.5s" begin="3.5s" fill="freeze"/>'
             '<rect x="0" y="0" width="320" height="180" fill="#1a1010" opacity="0.55"/>'
             '<text x="160" y="98" font-family="monospace" font-size="26" font-weight="bold" text-anchor="middle" '
             'fill="#fbf7ee" stroke="#2d1a10" stroke-width="1">THE END</text></g>')
    return svg("".join(b), defs)


def stranger(kit="white"):
    """Ending A, last scene. Plays once when the image appears (about 20 s)."""
    defs = sky_defs("#f39c6b", "#fbd9a6")
    b = [rect(0, 0, W, 110, "url(#sky)"), rect(0, 110, W, 70, CLAY_DARK)]
    b.append('<g shape-rendering="auto"><circle cx="262" cy="34" r="16" fill="#ffd27f" opacity="0.9"/>'
             '<circle cx="262" cy="34" r="20" fill="#ffd27f" opacity="0.25">'
             '<animate attributeName="r" values="18;24;18" dur="2s" repeatCount="indefinite"/></circle></g>')
    b.append(birds((20, 30, 14), color="#5a3a3a"))
    b.append(rect(0, 106, W, 4, "#a8562a"))
    b.append(block(0, 60, W, 46, "#6d5a73", 4))           # empty stands
    for x in range(6, W, 16):
        b.append(rect(x, 70, 10, 3, "#58475d"))
        b.append(rect(x, 86, 10, 3, "#58475d"))

    # Timeline in seconds (one run, everything freezes at the end)
    T = 27.0
    def kt(*times):
        return ";".join(f"{t / T:.4f}" for t in times)

    #  0.0-4.0  time to read the first caption, the stranger is not there yet
    #  4.0-8.5  the stranger walks in from the right (slowly)
    #  8.8-11.6 bubble 1: "May I take a look at that racket?"
    # 11.8-13.0 the player walks a few steps towards him
    # 13.2-14.0 the player hands the racket over (second caption at 14.0)
    # 14.2-19.2 the stranger turns the racket in his hands, looking closely
    # 19.4-22.8 bubble 2: "You made a good choice, kid."
    # 23.0-23.8 he hands it back, 24.2-25.2 he fades away, 25.6 THE END
    walk = 30            # how far the player walks
    give = (44, -2)      # from the player's hand to the stranger's hand

    # the player walks a few steps (and stays there)
    b.append(
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="0 0;0 0;{walk} 0;{walk} 0" keyTimes="{kt(0, 11.8, 13.0, T)}" dur="{T}s" fill="freeze"/>'
        + player_tennis(92, 98, s=1.6, kit=kit) + "</g>"
    )

    # the stranger: black trench coat and headband
    coat = "#161616"
    stranger_fig = person(190, 92, coat, pants=coat, hair="#2a2a2a", s=1.8, shoes="#000000",
                          extra=[(-1, 12, 16, 22, "#1d1d1d"),   # long trench coat
                                 (6, 15, 1, 19, "#000000"),     # coat opening
                                 (2, 12, 10, 3, "#2e2e2e"),     # raised collar
                                 (-1, 24, 16, 2, "#0d0d0d"),    # belt
                                 (2, 3, 10, 2, "#000000")])     # black tennis headband
    b.append(
        '<g><animateTransform attributeName="transform" type="translate" values="150 0;150 0;0 0" '
        'dur="8.5s" fill="freeze" calcMode="spline" keyTimes="0;0.47;1" keySplines="0 0 1 1;0.3 0 0.4 1"/>'
        '<animate attributeName="opacity" values="1;0" dur="1s" begin="24.2s" fill="freeze"/>'
        + stranger_fig + "</g>"
    )

    # The racket: realistic size, held by the grip, head up.
    # Outer group moves it (with the player, to the stranger, back);
    # inner group turns it while the stranger inspects it.
    hand_x, hand_y = 92 + 15.5 * 1.6, 98 + 24 * 1.6          # player's right hand
    rs = 0.47
    cx, cy = hand_x, hand_y - 38 * rs                         # head centre above the grip
    gx, gy = walk + give[0], give[1]
    move_values = f"0 0;0 0;{walk} 0;{walk} 0;{gx} {gy};{gx} {gy - 12};{gx} {gy - 12};{gx} {gy};{gx} {gy};{walk} 0;{walk} 0"
    move_times = kt(0, 11.8, 13.0, 13.2, 14.0, 14.4, 18.8, 19.2, 23.0, 23.8, T)
    turn_values = "0;0;-25;20;-15;30;-10;0;0"
    turn_times = kt(0, 14.4, 15.4, 16.4, 17.3, 18.1, 18.8, 19.1, T)
    b.append(
        f'<g><animateTransform attributeName="transform" type="translate" values="{move_values}" '
        f'keyTimes="{move_times}" dur="{T}s" fill="freeze"/>'
        f'<g><animateTransform attributeName="transform" type="rotate" '
        f'values="{";".join(f"{a} {cx:.1f} {cy:.1f}" for a in turn_values.split(";"))}" '
        f'keyTimes="{turn_times}" dur="{T}s" fill="freeze"/>'
        + racket(round(cx, 1), round(cy, 1), "#5aa9e6", "#6b5a45", strings="#d9d2bf", angle=8, worn=True, s=rs)
        + "</g></g>"
    )

    def bubble(text, begin, dur, width):
        """Black speech bubble with white text above the stranger's head."""
        x, y = 203 - width / 2, 64
        return (
            f'<g opacity="0" shape-rendering="auto">'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.9;1" '
            f'dur="{dur}s" begin="{begin}s" fill="freeze"/>'
            f'<rect x="{x}" y="{y}" width="{width}" height="15" rx="4" fill="#111111" stroke="#fbf7ee" stroke-width="1"/>'
            f'<path d="M 199 {y + 14.5} L 204 {y + 21} L 208 {y + 14.5}" fill="#111111" stroke="#fbf7ee" stroke-width="1"/>'
            f'<rect x="199.6" y="{y + 13.5}" width="8" height="2" fill="#111111"/>'
            f'<text x="203" y="{y + 10.2}" font-family="monospace" font-weight="bold" font-size="7" '
            f'text-anchor="middle" fill="#ffffff">{text}</text>'
            "</g>"
        )

    b.append(bubble("May I take a look at that racket?", 8.8, 2.8, 150))
    b.append(bubble("You made a good choice, kid.", 19.4, 3.4, 128))
    # The end card fades in after the stranger is gone
    b.append('<g opacity="0"><animate attributeName="opacity" values="0;1" dur="1.5s" begin="25.6s" fill="freeze"/>'
             '<rect x="0" y="0" width="320" height="180" fill="#1a1010" opacity="0.55"/>'
             '<text x="160" y="98" font-family="monospace" font-size="26" font-weight="bold" text-anchor="middle" '
             'fill="#fbf7ee" stroke="#2d1a10" stroke-width="1">THE END</text></g>')
    return svg("".join(b), defs)


# --- items ------------------------------------------------------------------


def item_key():
    b = [
        f'<g shape-rendering="auto"><circle cx="20" cy="32" r="11" fill="none" stroke="#b5652b" stroke-width="6"/></g>',
        rect(29, 29, 26, 6, "#b5652b"),
        rect(44, 35, 4, 8, "#b5652b"),
        rect(51, 35, 4, 6, "#b5652b"),
        rect(30, 29, 6, 2, "#d98c4f"),
        rect(15, 22, 4, 3, "#7a3f17"),
    ]
    return svg("".join(b), w=64, h=64)


def item_racket(frame, grip, strings, worn):
    return svg(racket(32, 24, frame, grip, strings=strings, angle=35, worn=worn, s=1.1), w=64, h=64)


def player_sprite(street=False, kit="white"):
    """The player figure. viewBox includes the arms and the bobbing."""
    body = player_street(0, 0) if street else player_tennis(0, 0, kit=kit)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -1 22 42" '
        f'shape-rendering="crispEdges">{body}</svg>\n'
    )


def closeup(frame, accent, grip, strings, worn, signature=None):
    """A big, detailed racket for the item reveal. Tall format, transparent."""
    cx, cy, rx, ry = 60, 62, 38, 50
    parts = ['<g shape-rendering="auto">']
    parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{frame}" stroke-width="9"/>')
    parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="14 10"/>')
    for i in range(-5, 6):
        x = cx + i * 6
        h = (ry - 4) * (1 - ((i * 6) / (rx - 4)) ** 2) ** 0.5 if abs(i * 6) < rx - 4 else 0
        parts.append(f'<line x1="{x}" y1="{cy - h}" x2="{x}" y2="{cy + h}" stroke="{strings}" stroke-width="1.3"/>')
    for j in range(-7, 8):
        y = cy + j * 6
        w = (rx - 4) * (1 - ((j * 6) / (ry - 4)) ** 2) ** 0.5 if abs(j * 6) < ry - 4 else 0
        parts.append(f'<line x1="{cx - w}" y1="{y}" x2="{cx + w}" y2="{y}" stroke="{strings}" stroke-width="1.3"/>')
    # throat (two arms forming a V) and shaft
    parts.append(f'<path d="M {cx - 16} {cy + ry - 6} L {cx - 4} {cy + ry + 26} L {cx + 4} {cy + ry + 26} L {cx + 16} {cy + ry - 6}" fill="none" stroke="{frame}" stroke-width="7" stroke-linejoin="round"/>')
    parts.append(f'<rect x="{cx - 5}" y="{cy + ry + 24}" width="10" height="16" fill="{frame}"/>')
    # grip with overgrip spiral and a butt cap
    parts.append(f'<rect x="{cx - 7}" y="{cy + ry + 40}" width="14" height="44" rx="2" fill="{grip}"/>')
    for k in range(7):
        parts.append(f'<line x1="{cx - 7}" y1="{cy + ry + 44 + k * 6}" x2="{cx + 7}" y2="{cy + ry + 40 + k * 6}" stroke="#ffffff" stroke-opacity="0.35" stroke-width="1.5"/>')
    parts.append(f'<rect x="{cx - 8}" y="{cy + ry + 82}" width="16" height="5" rx="2" fill="{accent}"/>')
    if worn:
        for dx, dy, w in [(-34, -20, 6), (30, 10, 5), (-22, 38, 7), (24, -40, 6), (-36, 12, 4)]:
            parts.append(f'<rect x="{cx + dx}" y="{cy + dy}" width="{w}" height="3" fill="#e7e1d2"/>')
        parts.append(f'<rect x="{cx - 7}" y="{cy + ry + 58}" width="14" height="8" fill="#cfc6b0"/>')
    if signature:
        # faded handwriting along the shaft
        # on the side of the frame, written along it
        sx = cx - rx
        parts.append(f'<text x="{sx}" y="{cy + 2}" transform="rotate(-90 {sx} {cy})" font-family="cursive" '
                     f'font-size="6.5" fill="#ffffff" fill-opacity="0.85" text-anchor="middle" '
                     f'font-style="italic">{signature}</text>')
    parts.append("</g>")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 210">'
        '<animate attributeName="opacity" values="1;1" dur="1s"/>'   # marks the file as animated
        + "".join(parts) + "</svg>\n"
    )


def main():
    save("scenes/entrance.svg", entrance())
    save("scenes/main_path.svg", main_path())
    save("scenes/office.svg", office())
    save("scenes/locker_room.svg", locker_room())
    save("scenes/court.svg", court())
    save("scenes/court_match.svg", court(match_due=True))

    save("scenes/court_2.svg", court_2(with_groundskeeper=False))
    save("scenes/court_2_groundskeeper.svg", court_2(with_groundskeeper=True))
    save("scenes/shed.svg", shed())
    save("scenes/shed_open.svg", shed(opened=True))
    save("scenes/shed_inside.svg", shed_inside(True))
    save("scenes/shed_inside_empty.svg", shed_inside(False))
    save("endings/ceremony_win.svg", ceremony_win())
    save("endings/ceremony_loss.svg", ceremony_loss())
    save("endings/stranger.svg", stranger())
    save("endings/end_b.svg", end_b())
    save("items/key.svg", item_key())
    save("closeups/wilson.svg", closeup("#1f5e3a", "#7ccf8f", "#111111", "#f5f1e6", worn=False))
    save("closeups/yonex.svg", closeup("#5aa9e6", "#f4f0e6", "#6b5a45", "#d9d2bf", worn=True, signature="Roger F."))
    save("sprites/player.svg", player_sprite())
    save("sprites/player_street.svg", player_sprite(street=True))
    for kit in ("black", "pink"):
        save(f"sprites/player_{kit}.svg", player_sprite(kit=kit))
        save(f"endings/ceremony_win_{kit}.svg", ceremony_win(kit))
        save(f"endings/ceremony_loss_{kit}.svg", ceremony_loss(kit))
        save(f"endings/stranger_{kit}.svg", stranger(kit))
        save(f"endings/end_b_{kit}.svg", end_b(kit))
    save("items/wilson.svg", item_racket("#1f5e3a", "#111111", "#f5f1e6", False))
    save("items/yonex.svg", item_racket("#5aa9e6", "#6b5a45", "#d9d2bf", True))
    print("written:", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*.svg")))


main()
