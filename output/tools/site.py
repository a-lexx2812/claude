"""General plan 1:500 and site plan 1:1000 for the corrected Dream String model (old map style)."""
import sys, math, random
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union, transform
from shapely import affinity
from geo import D, P, KA, KA2, ES, LINE, SUB
from fit2 import free, A, uh, vh
from render import Sheet, INK, GREY, RED, TITLE
from model import BL, ROOF, AMPHI_C
from fins import FINS, fin_rect
from matplotlib.patches import Circle, Polygon as MP
from drawplan import north_arrow, scale_bar

UNE, V0 = 92.75, 2.0
def W(g):          # model -> world (east, north)
    return transform(lambda x, y, z=None: (A[0] + (UNE - x) * uh[0] + (V0 + y) * vh[0],
                                           A[1] + (UNE - x) * uh[1] + (V0 + y) * vh[1]), g)
def Wp(x, y):
    return (A[0] + (UNE - x) * uh[0] + (V0 + y) * vh[0], A[1] + (UNE - x) * uh[1] + (V0 + y) * vh[1])

ROOFC = {'L': '#cfdcbd', 'C': '#e6e2d8', 'T': '#e6e2d8', 'K': '#d6e4ef', 'H': '#cfdcbd', 'A': '#e6e2d8'}
RW = {'secondary': 14, 'tertiary': 10, 'residential': 8, 'service': 5, 'track': 3.5, 'unclassified': 6}
PW = {'footway': 2.5, 'path': 2.0, 'steps': 2.0, 'pedestrian': 4}

def ways(fn):
    for w in D['ways']:
        if fn(w['tags']):
            yield w['tags'], [P(p) for p in w['pts']]

def amphi():
    cx, cy = AMPHI_C
    return Polygon([(cx, cy)] + [(cx + 11.2 * math.cos(math.radians(90 + 90 * i / 40)),
                                  cy + 11.2 * math.sin(math.radians(90 + 90 * i / 40))) for i in range(41)])

# ------------------------------------------------------------------ new site elements (model coordinates)
SQUARE = Polygon([(-6, -6), (-36, -6), (-40, 6), (-40, 30), (-24, 38), (-6, 34)])
LOOP_C = (-24.0, 16.0)
FOREST_WALK = box(-6, -4.5, 87.0, 0.0)
SERVICE = box(-6, 12.6, 10.9, 16.2)
CAFE_T = box(13.5, 19.6, 34.8, 24.5)
RAMP = LineString([(4.2, 18.3), (4.2, 23.0), (2.6, 26.6), (-1.0, 28.2), (-15.0, 28.2)])
PARK_PATH = LineString([(24.0, 24.5), (30.0, 40.0), (52.0, 62.0)])
ALLEY = LineString([(63.0, 10.8), (63.0, 16.0), (58.0, 30.0), (50.0, 48.0)])

def bldg():
    return unary_union([box(*r) for r in BL.values()])

def draw_common(S, scale, detail):
    ext = box(*S.ext[:2], *S.ext[2:])
    # land use
    for t, pts in ways(lambda t: t.get('natural') == 'wood' or t.get('leisure') == 'park'):
        if len(pts) > 2:
            S.poly(Polygon(pts).buffer(0), fc='#eef2e8', z=0.3)
    for t, pts in ways(lambda t: t.get('landuse') == 'residential'):
        if len(pts) > 2:
            S.poly(Polygon(pts).buffer(0), fc='#f4f1ec', z=0.2)
    for t, pts in ways(lambda t: t.get('landuse') == 'construction'):
        if len(pts) > 2:
            S.poly(Polygon(pts).buffer(0), fc='#f1ece4', ec='#b9a88d', lw=S.lw(0.1), z=0.25, hatch='///')
    # water strips 35 m and rivers
    rivers = [KA, KA2, ES]
    for r in rivers:
        S.poly(r.buffer(35 + 4), fc='#e6eff6', z=0.4)
    for t, pts in ways(lambda t: t.get('waterway') == 'river'):
        S.poly(LineString(pts).buffer(4.0), fc='#a9c6dc', z=0.6)
    # 110 kV line + zone 20 m from the outer wires (wires ±4 m from the axis)
    S.poly(LINE.buffer(24.0), fc='none', ec=RED, lw=S.lw(0.15), z=0.7, hatch='////', alpha=0.45)
    S.line(list(LINE.coords), c=RED, lw_mm=0.3, z=0.8, ls=(0, (8, 3)))
    S.poly(SUB, fc='#e3c9c4', ec=INK, lw=S.lw(0.15), z=1.0)
    # roads and paths
    for t, pts in ways(lambda t: t.get('highway') in RW):
        S.poly(LineString(pts).buffer(RW[t['highway']] / 2, cap_style=2), fc='#d8d3ca', ec='#b8b2a6',
               lw=S.lw(0.08), z=0.9)
    for t, pts in ways(lambda t: t.get('highway') in PW):
        S.poly(LineString(pts).buffer(PW[t['highway']] / 2), fc='#efe9dd', z=0.85)
    # existing buildings
    for t, pts in ways(lambda t: 'building' in t):
        if len(pts) > 2:
            g = Polygon(pts).buffer(0)
            S.poly(affinity.translate(g, 1.2, -1.2), fc='#cfccc6', z=1.05)
            S.poly(g, fc='#dcd8d1', ec=INK, lw=S.lw(0.12), z=1.1)
    # free land
    S.line(list(free.exterior.coords), c='#4f7d4a', lw_mm=0.3, z=1.2, ls=(0, (4, 2)))

def draw_project(S, detail):
    b = bldg()
    paved = unary_union([W(SQUARE), W(FOREST_WALK), W(SERVICE), W(CAFE_T)])
    S.poly(paved, fc='#efe9dd', ec='#b8b2a6', lw=S.lw(0.08), z=2.0)
    S.poly(W(Point(LOOP_C).buffer(9.0)), fc='#d8d3ca', z=2.1)
    S.poly(W(Point(LOOP_C).buffer(4.5)), fc='#cfdcbd', ec=INK, lw=S.lw(0.08), z=2.2)
    S.poly(W(RAMP.buffer(1.9, cap_style=2)), fc='#d8d3ca', ec=INK, lw=S.lw(0.1), z=2.15, ls=(0, (3, 2)))
    S.poly(W(PARK_PATH.buffer(1.5)), fc='#efe9dd', z=1.95)
    S.poly(W(ALLEY.buffer(1.5)), fc='#efe9dd', z=1.95)
    # access road + new bridge from the nearest street over the river
    sq = W(SQUARE)
    roads = unary_union([LineString(p) for t, p in ways(lambda t: t.get('highway') in ('secondary', 'residential', 'tertiary'))])
    c = sq.centroid
    from shapely.ops import nearest_points
    q = nearest_points(c, roads)[1]
    acc = LineString([nearest_points(q, sq.exterior)[1], q])
    S.poly(acc.buffer(3.5, cap_style=2), fc='#d8d3ca', ec='#b8b2a6', lw=S.lw(0.08), z=2.05)
    riv = unary_union([LineString(p).buffer(6.0) for t, p in ways(lambda t: t.get('waterway') == 'river')])
    br = acc.buffer(4.2, cap_style=2).intersection(riv)
    S.poly(br, fc='#c9c2b5', ec=INK, lw=S.lw(0.18), z=2.3)
    # amphitheatre
    S.poly(W(amphi()), fc='#d8d8d3', ec=INK, lw=S.lw(0.1), z=2.4)
    S.poly(W(Point(AMPHI_C).buffer(4.5).intersection(amphi())), fc='#e9dfcf', ec=INK, lw=S.lw(0.08), z=2.45)
    # building with roofs, shadow
    S.poly(affinity.translate(W(b), 2.5, -2.5), fc='#c9c6bf', z=2.5)
    for k, r in BL.items():
        S.poly(W(box(*r)), fc=ROOFC[k], ec=INK, lw=S.lw(0.25), z=2.6)
    if detail:
        for f in FINS:
            S.poly(W(box(*fin_rect(f))), fc='#6e6b65', z=2.7)
        for k, r in BL.items():
            c = W(box(*r)).centroid
            lab = {'L': 'roof garden +7.50', 'C': 'cafe terrace +3.90', 'T': '3 fl. +12.30', 'K': 'cube',
                   'H': 'hall +11.70', 'A': '+3.90'}[k]
            S.text(c.x, c.y, lab, mm=1.4, c=INK, z=9, rot=math.degrees(math.atan2(uh[1], uh[0])) + 180 - 180)
    return acc, br

def trees(S, avoid, n=900, seed=5):
    rnd = random.Random(seed)
    wood = unary_union([Polygon(p).buffer(0) for t, p in ways(lambda t: t.get('natural') == 'wood' or t.get('leisure') == 'park') if len(p) > 2])
    x0, y0, x1, y1 = S.ext
    for i in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        p = Point(x, y)
        if wood.contains(p) and not avoid.contains(p):
            r = rnd.uniform(2.6, 4.2)
            S.ax.add_patch(Circle((x, y), r, fc='#dfe8d3', ec='#93a582', lw=S.lw(0.08), zorder=1.6, alpha=0.95))

def legend(S, x, y, mm, rows):
    for i, (fc, t, h) in enumerate(rows):
        yy = y - S.m(mm * 2.2) * i
        S.poly(box(x, yy - S.m(mm * 0.6), x + S.m(mm * 2.2), yy + S.m(mm * 0.6)), fc=fc, ec=INK, lw=S.lw(0.08), z=20,
               hatch=h)
        S.text(x + S.m(mm * 3.0), yy, t, mm=mm, c=INK, ha='left', z=20)

ROWS = [('#cfdcbd', 'building – green roofs to walk on, terraces', None), ('#6e6b65', 'fins – the sound track', None),
        ('#d8d3ca', 'roads, drop-off loop, ramp to the garage (dashed – covered)', None),
        ('#efe9dd', 'square, forest walk, terraces, paths', None), ('#dfe8d3', 'existing trees kept', None),
        ('#a9c6dc', 'rivers', None), ('#e6eff6', 'water-protection strips 35 m – no building', None),
        ('white', '110 kV line, zone 20 m from the outer wires – no building', '////'),
        ('white', 'free land between the restrictions (dashed green)', None)]

def genplan(out, dpi=250):
    c = W(box(-40, -20, 95, 45)).centroid
    S = Sheet(c.x - 95, c.y - 78, c.x + 95, c.y + 70, scale=500)
    draw_common(S, 500, True)
    acc, br = draw_project(S, True)
    avoid = unary_union([W(box(-42, -8, 89, 40)), W(amphi()).buffer(2), acc.buffer(5)])
    trees(S, avoid, 1400)
    # labels
    q = Wp(-24, 16); S.text(*q, 'square · drop-off', mm=1.5, c=INK, z=9)
    q = Wp(-15, 31); S.text(*q, 'ramp portal → garage −3.60, 24 places', mm=1.3, c=RED, z=9, ha='left')
    q = Wp(40, -2.6); S.text(*q, 'forest walk 4.5 m', mm=1.3, c=INK, z=9)
    q = Wp(62.0, -6.5); S.text(*q, 'main entrance ↑', mm=1.4, c=RED, z=9)
    q = Wp(4.0, 14.4); S.text(*q, 'service bay', mm=1.2, c=INK, z=9)
    q = Wp(24, 22.5); S.text(*q, 'cafe terrace', mm=1.2, c=INK, z=9)
    q = Wp(70, 25); S.text(*q, 'amphitheatre 90 seats', mm=1.2, c=INK, z=9)
    bc = br.centroid if not br.is_empty else None
    if bc:
        S.text(bc.x + 8, bc.y, 'new bridge', mm=1.4, c=INK, z=9, ha='left')
    x0, y0, x1, y1 = S.ext
    S.text(x0 + S.m(8), y1 - S.m(8), 'General plan', mm=4.4, c=INK, font=TITLE, ha='left', z=30)
    S.text(x0 + S.m(8), y1 - S.m(13), 'scale 1:500 · new bridge and access road, square with drop-off, covered ramp to the garage, '
           'forest walk, cafe terrace, amphitheatre · the building 87.0 × 24.6 m stands inside the free land',
           mm=1.5, c=GREY, ha='left', z=30)
    north_arrow(S, x1 - S.m(14), y1 - S.m(14), 90, r_mm=6)
    scale_bar(S, x1 - S.m(110), y0 + S.m(10), length_m=40, step=10, mm=1.2)
    S.poly(box(x0 + S.m(4), y0 + S.m(4), x0 + S.m(95), y0 + S.m(48)), fc='white', ec=INK, lw=S.lw(0.1), z=19.5)
    legend(S, x0 + S.m(8), y0 + S.m(43), 1.3, ROWS)
    S.save(out, dpi=dpi)

def siteplan(out, dpi=220):
    c = W(box(-40, -20, 95, 45)).centroid
    S = Sheet(c.x - 210, c.y - 150, c.x + 210, c.y + 150, scale=1000)
    draw_common(S, 1000, False)
    acc, br = draw_project(S, False)
    trees(S, unary_union([W(box(-42, -8, 89, 40)), acc.buffer(5)]), 2600)
    # street / river names and bus stops
    for t, pts in ways(lambda t: t.get('highway') in ('secondary', 'residential') and 'name' in t):
        ls = LineString(pts)
        m_ = ls.interpolate(0.5, normalized=True)
        S.text(m_.x, m_.y, t.get('name:en', t['name']), mm=1.4, c=INK, z=9, bg='white')
    for k, v in D['ntags'].items():
        p, tg = v
        if tg.get('highway') == 'bus_stop' or tg.get('public_transport') == 'platform':
            q = P(p)
            S.ax.add_patch(Circle(q, S.m(1.4), fc='#2f5d7c', ec='white', lw=0.5, zorder=12))
            S.text(q[0] + S.m(2.2), q[1], tg.get('name', 'bus stop'), mm=1.2, c='#2f5d7c', ha='left', z=12)
    cc = W(bldg()).centroid
    S.text(cc.x, cc.y - 22, 'Dream String', mm=2.0, c=INK, z=12, weight='bold')
    x0, y0, x1, y1 = S.ext
    S.text(x0 + S.m(8), y1 - S.m(8), 'Site plan', mm=4.4, c=INK, font=TITLE, ha='left', z=30)
    S.text(x0 + S.m(8), y1 - S.m(13), 'scale 1:1000 · rivers and 35 m water-protection strips, 110 kV line and its 20 m zone, '
           'substation, streets and stops · data © OpenStreetMap contributors', mm=1.5, c=GREY, ha='left', z=30)
    north_arrow(S, x1 - S.m(14), y1 - S.m(14), 90, r_mm=6)
    scale_bar(S, x1 - S.m(130), y0 + S.m(10), length_m=100, step=20, mm=1.2)
    S.poly(box(x0 + S.m(4), y0 + S.m(4), x0 + S.m(95), y0 + S.m(48)), fc='white', ec=INK, lw=S.lw(0.1), z=19.5)
    legend(S, x0 + S.m(8), y0 + S.m(43), 1.3, ROWS)
    S.save(out, dpi=dpi)

if __name__ == '__main__':
    genplan('../out/genplan_new.png')
    siteplan('../out/siteplan_new.png')
    # check: building inside the free land, outside the zones
    b = W(unary_union([bldg(), amphi()]))
    print('inside free land:', free.contains(b), 'clearance', round(free.exterior.distance(b), 2))
    print('to 110 kV axis', round(b.distance(LINE), 1), 'to rivers', [round(b.distance(r), 1) for r in (KA, KA2, ES)])
    print('ramp portal to nearest window wall', round(Point(-15, 28.2).distance(box(0, 0, 10.9, 19.6)), 1))
