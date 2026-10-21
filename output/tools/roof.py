"""Roof plan (view from above): roofs and terraces, stair head houses, the stair between the roofs, drainage."""
import math
from matplotlib.patches import FancyArrow, Circle
from model import *
from bim import Space as Sp
from fins import FINS, fin_rect, SPECIAL
from render import INK, GREY, RED

MEADOW = '#cfdcbd'      # extensive green roof (sedum, meadow)
GARDEN = '#d9e4c9'      # roof garden to walk on
PAVER = '#ece9e2'       # terraces: concrete pavers on pedestals
GLASS = '#e3ecf5'
HEAD = '#bdbab3'        # roofs of the head houses

# roof outline of every block: (geometry, finish, label, level, label position)
ROOFS = [
    (R(*BL['L']), GARDEN, 'roof garden · meadow, ferns, paths of light stone\nglass railing 1.1 m', '+7.50', (21.0, 2.7), (24.6, 9.0)),
    (R(*BL['C']), PAVER, 'cafe roof terrace · pavers, planters · glass railing 1.1 m', '+3.90', (22.0, 16.1), (21.0, 14.0)),
    (R(*BL['T']), PAVER, 'terrace of the peaks · view to the Ile-Alatau\nglass railing 1.1 m', '+12.30', (49.0, 9.6), (44.0, 7.0)),
    (R(*BL['K']), GLASS, 'glass roof\nof the cube\n(maintenance\nonly)', '+7.50', (61.8, 8.0), (62.4, 5.0)),
    (R(*BL['H']), MEADOW, 'meadow roof over the hall · extensive green roof\nmaintenance only (S3) · parapet + anchor line',
     '+11.70', (77.4, 10.6), (77.4, 8.4)),
    (R(*BL['A']), PAVER, 'terrace over\nthe stage', '+3.90', (79.0, 19.2), (83.6, 22.6)),
]
# head houses (top of the stair cores) and their roofs
HEADS = [
    (R(0.0, 0.0, 7.7, 3.6), 'S1', '+7.50', '+10.80'),
    (R(34.8, 0.0, 43.125, 7.0), 'S2 + lift', '+12.30', '+15.90'),
    (R(65.4, 0.0, 73.1, 3.6), 'S3', '+11.70', '+15.00'),
    (R(75.0, 21.0, 82.7, 24.6), 'S4', '+3.90', '+7.20'),
]
# exits from the head houses onto the roofs: (x, y, dx, dy)
EXITS = [(1.2, 3.6, 0, 1), (40.1, 7.0, 0, 1), (81.5, 21.0, 0, -1)]
# paths of light stone on the roof garden and the terrace of the peaks
PATHS = [R(1.0, 4.6, 29.9, 6.2), R(29.9, 4.6, 31.5, 12.1), R(8.6, 6.2, 10.2, 11.6), R(19.6, 6.2, 21.2, 11.6),
         R(1.0, 3.6, 2.6, 4.6)]
PLANTERS = [R(12.0, 17.8, 16.0, 18.8), R(18.0, 17.8, 22.0, 18.8), R(24.0, 17.8, 28.0, 18.8),
            R(44.0, 12.0, 47.0, 13.0), R(50.0, 12.0, 53.0, 13.0), R(54.6, 2.0, 57.4, 3.0)]
# roof outlets and falls (arrows point downhill, i = 1.5–2 %)
DRAINS = [(6.0, 11.4), (16.0, 11.4), (26.0, 11.4), (17.0, 18.9), (31.0, 18.9), (45.6, 1.2), (53.0, 1.2),
          (60.0, 4.3), (70.0, 16.4), (84.0, 16.4), (85.6, 18.4)]
FALLS = [(5.0, 8.2, 0, 1), (26.0, 8.2, 0, 1), (14.0, 14.0, 0, 1), (29.0, 14.0, 0, 1), (54.0, 6.6, 0, -1), (64.6, 9.4, 0, -1),
         (74.0, 12.6, 0, 1), (82.0, 12.6, 0, 1)]
# the stair between the terrace of the peaks (+12.30) and the roof garden (+7.50): open steel U-stair on the
# roof garden next to the wall of the three-storey block; 2 × 16 risers 150 / treads 320, flights 1.35 m
USTAIR = dict(x0=31.9, x1=34.7, y_mid=4.3, y_top=12.1, land=1.5, n=16, tread=0.32)


def build_roof():
    lv = Level('RF', 12.30, 'Roof plan')
    lv.blocks = []
    lv.add()
    lv.amphi = None
    return lv


def draw_ustair_top(S, u):
    x0, x1, ym0, yt = u['x0'], u['x1'], u['y_mid'], u['y_top']
    fw = (x1 - x0 - 0.1) / 2
    run = (u['n'] - 1) * u['tread']
    y_a = yt - u['land']               # top landing  y_a … yt  (+12.30), arrival of flight 2 below it
    y_b = y_a - run                    # mid landing  ym0 … y_b (+9.90)
    S.poly(R(x0, ym0, x1, yt), fc='white', ec=INK, lw=S.lw(0.18), z=4)
    for xs in ((x1 - fw, x1), (x0, x0 + fw)):
        for i in range(u['n']):
            y = y_a - i * u['tread']
            S.line([(xs[0], y), (xs[1], y)], c='#7a7a7a', lw_mm=0.1, z=4.1)
        S.line([(xs[0], y_b), (xs[0], y_a)], c='#7a7a7a', lw_mm=0.1, z=4.1)
        S.line([(xs[1], y_b), (xs[1], y_a)], c='#7a7a7a', lw_mm=0.1, z=4.1)
    S.line([(x0 + fw + 0.05, y_b), (x0 + fw + 0.05, y_a)], c=INK, lw_mm=0.18, z=4.2)    # stringer / railing
    # walking line: from the top landing down flight 1, round the mid landing, down flight 2
    xa, xb = x1 - fw / 2, x0 + fw / 2
    pts = [(xa, yt - 0.6), (xa, ym0 + 0.75), (xb, ym0 + 0.75), (xb, y_a - 0.1)]
    S.line(pts, c=INK, lw_mm=0.13, z=4.3)
    S.ax.add_patch(Circle(pts[0], S.m(0.45), fc=INK, ec='none', zorder=4.3))
    S.ax.add_patch(FancyArrow(xb, y_a - 0.1, 0, 0.001, width=0, head_width=S.m(1.4), head_length=S.m(1.6),
                              fc=INK, ec=INK, zorder=4.3))
    S.text(x0 - S.m(1.4), (ym0 + yt) / 2, 'down 2 × 16 × 150/320', mm=1.1, c=INK, rot=90, z=9)
    for (x, y, t) in ((x1 - 0.2, yt - 0.75, '+12.30'), (x1 - 0.2, ym0 + 0.75, '+9.90'), (x0 - 0.2, yt - 0.2, '+7.50')):
        S.text(x, y, t, mm=1.0, c=INK, ha='right', z=9, bg='white')


def draw_roof(S):
    from drawplan import draw_amphi
    from gf import amphitheatre
    draw_amphi(S, amphitheatre())
    for g, fc, lab, lev, at, mk in ROOFS:
        S.poly(g, fc=fc, ec=INK, lw=S.lw(0.35), z=2)
        S.poly(g.buffer(-0.25, join_style=2), fc='none', ec=INK, lw=S.lw(0.1), z=2.1)   # parapet
    # glazing bars of the cube roof
    x0, y0, x1, y1 = BL['K']
    for i in range(1, 6):
        x = x0 + (x1 - x0) * i / 6
        S.line([(x, y0 + 0.25), (x, y1 - 0.25)], c='#7f9cbc', lw_mm=0.1, z=2.2)
    for g in PATHS:
        S.poly(g, fc='#f4f1ea', ec='#a9a49a', lw=S.lw(0.08), z=2.3)
    for g in PLANTERS:
        S.poly(g, fc='#b9cba3', ec='#7d8f6a', lw=S.lw(0.1), z=2.3)
    # meadow texture on the hall roof and the roof garden
    import random
    rnd = random.Random(3)
    for (gx0, gy0, gx1, gy1), n in (((65.8, 0.4, 86.6, 17.0), 260), ((0.4, 0.4, 34.4, 12.2), 300)):
        for i in range(n):
            x, y = rnd.uniform(gx0, gx1), rnd.uniform(gy0, gy1)
            if any(p.contains(Point(x, y)) for p in PATHS) or any(h.buffer(0.3).contains(Point(x, y)) for h, *_ in HEADS):
                continue
            if 31.5 < x < 34.9 and 4.0 < y < 12.3:
                continue
            S.line([(x - 0.15, y - 0.1), (x, y + 0.12), (x + 0.15, y - 0.1)], c='#8da373', lw_mm=0.08, z=2.25)
    # glass railings (blue) on the roofs people walk on
    rail = [[(0.25, 3.6), (0.25, 12.35), (34.55, 12.35)], [(7.7, 0.25), (34.55, 0.25)],
            [(11.15, 12.6), (11.15, 19.35), (34.55, 19.35), (34.55, 13.8)],
            [(43.125, 0.25), (57.95, 0.25), (57.95, 13.55), (35.05, 13.55), (35.05, 12.1)], [(35.05, 10.6), (35.05, 7.0)],
            [(75.25, 17.4), (75.25, 21.0)], [(82.7, 24.35), (86.75, 24.35), (86.75, 17.4)]]
    for r in rail:
        S.line(r, c='#5a7fa6', lw_mm=0.3, z=3.7)
    # head houses
    for g, name, lev, top in HEADS:
        S.poly(g, fc=HEAD, ec=INK, lw=S.lw(0.35), z=5)
        S.poly(g.buffer(-0.2, join_style=2), fc='none', ec=INK, lw=S.lw(0.1), z=5.1)
        c = g.centroid
        S.text(c.x, c.y + S.m(1.0), f'head house {name}', mm=1.15, c=INK, z=9)
        S.text(c.x, c.y - S.m(1.2), f'roof {top}', mm=1.05, c=GREY, z=9)
    for (x, y, ddx, ddy) in EXITS:
        S.arrow(x, y + ddy * 0.15, ddx * S.m(4), ddy * S.m(4), c=RED, width_mm=0.28, head_mm=1.5)
    S.text(2.0, 5.8, 'exit S1', mm=1.05, c=RED, ha='left', z=12) if False else None
    draw_ustair_top(S, USTAIR)
    # drains and falls
    for (x, y) in DRAINS:
        S.ax.add_patch(Circle((x, y), S.m(0.9), fc='white', ec=INK, lw=S.lw(0.13), zorder=6))
        S.ax.add_patch(Circle((x, y), S.m(0.35), fc=INK, ec='none', zorder=6.1))
    for (x, y, ddx, ddy) in FALLS:
        S.arrow(x, y, ddx * S.m(5), ddy * S.m(5), c=INK, width_mm=0.12, head_mm=1.0, z=6)
        S.text(x + S.m(1.2), y + ddy * S.m(2.5), 'i = 2 %', mm=0.95, c=INK, ha='left', z=6)
    # fins (top view) and the two dominant fins
    for f in FINS:
        x0, y0, x1, y1 = fin_rect(f)
        S.poly(R(x0, y0, x1, y1), fc='#8d8b86', z=6.5)
    for f in FINS:
        if f.get('top', 0) >= 20:
            x0, y0, x1, y1 = fin_rect(f)
            S.text((x0 + x1) / 2, y0 - S.m(2.0), f"fin top +{f['top']:.2f}", mm=1.0, c=INK, z=9)
    # labels and levels
    from drawplan import level_mark_plan
    for g, fc, lab, lev, at, mk in ROOFS:
        S.text(at[0], at[1], lab, mm=1.25, c=INK, z=9, bg=None)
        level_mark_plan(S, mk[0], mk[1], lev)
    S.text(78.0, 2.0, '', mm=1)


ROOF_LEGEND = [
    (GARDEN, 'roof garden to walk on (+7.50) – inverted roof, drainage mat, substrate 150–200 mm'),
    (PAVER, 'terraces (+3.90, +12.30) – concrete pavers on pedestals over the waterproofing'),
    (MEADOW, 'extensive green roof (+11.70) – sedum / meadow 120 mm, maintenance only'),
    (GLASS, 'glass roof of the cube (+7.50) – double glazing on steel beams, cleaning walkway'),
    (HEAD, 'head houses of the stairs S1–S4 and the lift'),
    ('#f4f1ea', 'paths of light stone'),
    ('#b9cba3', 'planters'),
]
ROOF_NOTES = [
    'all roofs people walk on: glass railing 1.1 m (blue line); other roofs: parapet 0.6 m + anchor line',
    'roof outlets (circles) with heating cables; falls 2 % (arrows point downhill) to internal drains',
    'the terrace of the peaks (+12.30) has two ways out: S2 + lift and the steel U-stair down to the roof garden',
    'the roof garden (+7.50) is left through S1 or the roof foyer of the three-storey block (+7.50, lift)',
    'the dominant fins of the sound track rise to +25.00 and +21.50 (see the elevations)',
]
