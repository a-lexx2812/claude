"""Sections and elevations generated from the same model as the plans.

Walls, slabs, doors, windows and stairs are taken from the plan levels, so the sections and the
elevations always agree with the plans. View: `look` = unit vector of the direction of view in plan,
u = position to the right of the viewer, z = level. Painter's algorithm (far to near).
"""
import math
import random
from shapely.geometry import box, Polygon, LineString, Point, MultiLineString
from shapely.ops import unary_union
from matplotlib.patches import Polygon as MPoly, Circle, Ellipse
from render import Sheet, INK, GREY, RED, HAND, TITLE
from model import BL, ROOF, R
from fins import FINS, fin_rect
from ll import build_ll
from gf import build_gf, amphitheatre
from ff import build_ff
from f2 import build_2f
from bim import Level, Space

SLAB = 0.35          # floor slab + finish
ROOF_T = 0.60        # roof slab + build-up
HH_T = 0.40          # roof of a head house
PARAPET = 0.30       # parapet upstand above the roof surface
RAIL = 1.10          # glass railing above the roof surface
GROUND = -0.15
WALK_ROOF = {'L': True, 'C': True, 'T': True, 'K': False, 'H': False, 'A': True}

FACADE = '#fbfaf6'
GLASS = '#d3e1ec'
GLASS_E = '#6f8aa6'
DOOR = '#d4a34c'
FINC = '#6e6b65'
FIN_FAR = '#dcdad5'
EARTH = '#ece4d6'
CUT = '#262626'
LIGHT = '#f2f1ed'

HEADS = [  # rect, base, top, interior spaces
    (R(0.0, 0.0, 7.7, 3.6), 7.50, 10.80, [R(0.4, 0.4, 7.3, 3.2)]),
    (R(34.8, 0.0, 43.125, 7.0), 12.30, 15.90, [R(34.925, 0.4, 42.725, 3.2), R(34.925, 3.45, 37.325, 5.25),
                                              R(37.575, 3.45, 42.725, 6.6).union(R(34.925, 5.55, 37.575, 6.6))]),
    (R(65.4, 0.0, 73.1, 3.6), 11.70, 15.00, [R(65.8, 0.4, 72.7, 3.2)]),
    (R(75.0, 21.0, 82.7, 24.6), 3.90, 7.20, [R(75.4, 21.4, 82.3, 24.2)]),
]
# stair cores and the levels each one serves
STAIRS = [
    ('S1', (0.4, 0.4, 7.3, 3.2), 'low', [-3.6, 0.0, 3.9, 7.5]),
    ('S2', (34.925, 0.4, 42.725, 3.2), 'high', [-3.6, 0.0, 3.9, 7.5, 12.3]),
    ('S3', (65.8, 0.4, 72.7, 3.2), 'low', [-3.6, 0.0, 3.9, 7.8, 11.7]),
    ('S4', (75.4, 21.4, 82.3, 24.2), 'high', [0.0, 3.9]),
]
LIFT = R(34.925, 3.45, 37.325, 5.25)
TREAD, RISER, FLIGHT = 0.32, 0.15, 1.35


def head_levels():
    out = []
    for rect, base, top, inner in HEADS[1:3]:
        lv = Level('HH', base, 'head house')
        lv.blocks = [(rect, 0.4)]
        lv.spaces = [Space('', '', 'stair', g) for g in inner]
        out.append(lv)
    return out


def _land(L, n):
    run = (n - 1) * TREAD
    return 1.55 if (L - run) / 2 >= 1.55 else (L - run) / 2


def stair_cores():
    return unary_union([R(*c) for _, c, _, _ in STAIRS])


class Model:
    def __init__(self):
        self.levels = sorted([build_ll(), build_gf(), build_ff(), build_2f()] + head_levels(), key=lambda l: l.z)
        cores = stair_cores().union(LIFT)
        for lv in self.levels:
            fp = unary_union([b for b, _ in lv.blocks])
            sp = unary_union([s.geom for s in lv.spaces]) if lv.spaces else Polygon()
            vd = unary_union([g for g, _ in lv.voids]) if lv.voids else Polygon()
            gl = unary_union(lv.glass) if lv.glass else Polygon()
            ex = unary_union(getattr(lv, 'extra_walls', [])) if getattr(lv, 'extra_walls', []) else Polygon()
            lv._fp = fp
            lv._walls = fp.difference(sp).difference(vd).difference(gl).union(ex.intersection(fp))
            # floor slab: footprint minus voids minus stair wells (floor landing kept) minus the lift shaft
            floor = fp.difference(vd).difference(cores.intersection(fp))
            for name, c, land_at, zs in STAIRS:
                if any(abs(z - lv.z) < 0.35 for z in zs) and fp.contains(Point((c[0] + c[2]) / 2, (c[1] + c[3]) / 2)):
                    zi = min(zs, key=lambda z: abs(z - lv.z))
                    k = zs.index(zi)
                    L = c[2] - c[0]
                    n = round(((zs[k + 1] - zi) if k + 1 < len(zs) else (zi - zs[k - 1])) / RISER / 2)
                    land = _land(L, n)
                    lr = R(c[0], c[1], c[0] + land, c[3]) if land_at == 'low' else R(c[2] - land, c[1], c[2], c[3])
                    floor = floor.union(lr)
            lv._floor = floor
            lv._glass = gl
            lv._voids = vd

    # ceiling (underside of the structure above) at plan point p for level index i
    def ceiling(self, i, p):
        lv = self.levels[i]
        P = Point(p)
        for lv2 in self.levels[i + 1:]:
            if lv2.z <= lv.z + 0.2:
                continue
            if lv2._fp.buffer(0.01).contains(P) and not lv2._voids.contains(P):
                return lv2.z - SLAB
        for rect, base, top, inner in HEADS:
            if rect.buffer(0.01).contains(P) and base >= lv.z - 0.01:
                return top - HH_T
        z = None
        for b, r in BL.items():
            if box(*r).buffer(0.01).contains(P):
                z = max(z or -99, ROOF[b] - ROOF_T)
        return z if z is not None else lv.z + 3.0

    def level_at(self, z):
        return min(self.levels, key=lambda l: abs(l.z - z))


M = None


def model():
    global M
    if M is None:
        M = Model()
    return M


# ------------------------------------------------------------------------------------------------ geometry
class View:
    def __init__(self, look, u_off=0.0, cut=None):
        self.l = look
        self.r = (look[1], -look[0])
        self.u_off = u_off
        self.cut = cut                 # depth of the section plane (None for an elevation)

    def u(self, x, y):
        return self.r[0] * x + self.r[1] * y + self.u_off

    def d(self, x, y):
        return self.l[0] * x + self.l[1] * y

    def urange(self, g):
        x0, y0, x1, y1 = g.bounds if hasattr(g, 'bounds') else g
        us = [self.u(x0, y0), self.u(x1, y1)]
        return min(us), max(us)

    def drange(self, g):
        x0, y0, x1, y1 = g.bounds if hasattr(g, 'bounds') else g
        ds = [self.d(x0, y0), self.d(x1, y1)]
        return min(ds), max(ds)

    def along_x_walls(self):
        """openings of walls that face this view run along x if the view looks along y"""
        return abs(self.l[1]) > 0.5

    def cutline(self, ext=200):
        # plan line of the section plane
        lx, ly = self.l
        if abs(ly) > 0.5:
            y = self.cut / ly
            return LineString([(-ext, y), (ext, y)])
        x = self.cut / lx
        return LineString([(x, -ext), (x, ext)])

    def plan_pt(self, u, depth):
        """inverse: plan point for (u, depth)"""
        uu = u - self.u_off
        return (self.r[0] * uu + self.l[0] * depth, self.r[1] * uu + self.l[1] * depth)


def rect_uz(S, u0, u1, z0, z1, **kw):
    S.poly(box(min(u0, u1), z0, max(u0, u1), z1), **kw)


# ------------------------------------------------------------------------------------------------ people & trees
PEOPLE_COLS = ['#3a3a3a', '#3a3a3a', '#a5472f', '#2f5d7c', '#3a3a3a', '#5b7a3a', '#7a4f8a', '#3a3a3a']


def person(S, u, z, h=1.75, col='#3a3a3a', facing=1, kind='walk', z_ord=20):
    """simple but clearly readable silhouette (head, body, legs, arms)"""
    k = h / 1.75
    f = facing
    hr = 0.115 * k
    S.ax.add_patch(Circle((u, z + h - hr), hr, fc=col, ec='none', zorder=z_ord))
    if kind == 'sit':
        body = [(u - 0.17 * k, z + 0.55 * k), (u + 0.17 * k, z + 0.55 * k), (u + 0.15 * k, z + 1.28 * k),
                (u - 0.15 * k, z + 1.28 * k)]
        legs = [(u - 0.16 * k, z + 0.6 * k), (u + 0.34 * k * f, z + 0.6 * k), (u + 0.36 * k * f, z),
                (u + 0.24 * k * f, z), (u + 0.22 * k * f, z + 0.46 * k), (u - 0.16 * k, z + 0.46 * k)]
        S.ax.add_patch(MPoly(body, closed=True, fc=col, ec='none', zorder=z_ord))
        S.ax.add_patch(MPoly(legs, closed=True, fc=col, ec='none', zorder=z_ord))
        return
    sh = z + h * 0.80
    hip = z + h * 0.50
    body = [(u - 0.20 * k, sh), (u + 0.20 * k, sh), (u + 0.15 * k, hip), (u - 0.15 * k, hip)]
    st = 0.13 * k if kind == 'walk' else 0.05 * k
    legs = [(u - 0.15 * k, hip), (u + 0.15 * k, hip), (u + 0.05 * k + st, z), (u + st - 0.06 * k, z),
            (u, hip - 0.2 * k), (u - st + 0.06 * k, z), (u - 0.05 * k - st, z)]
    arms = [(u - 0.20 * k, sh), (u - 0.25 * k - st * 0.6, z + h * 0.47), (u - 0.18 * k - st * 0.6, z + h * 0.46),
            (u - 0.13 * k, sh - 0.12 * k)]
    arms2 = [(u + 0.20 * k, sh), (u + 0.25 * k + st * 0.6, z + h * 0.47), (u + 0.18 * k + st * 0.6, z + h * 0.46),
             (u + 0.13 * k, sh - 0.12 * k)]
    for p in (body, legs, arms, arms2):
        S.ax.add_patch(MPoly(p, closed=True, fc=col, ec='none', zorder=z_ord))


def crowd(S, items, z_ord=20):
    for it in items:
        u, z = it[0], it[1]
        h = it[2] if len(it) > 2 else 1.75
        c = it[3] if len(it) > 3 else '#3a3a3a'
        kind = it[4] if len(it) > 4 else 'walk'
        person(S, u, z, h, c, kind=kind, z_ord=z_ord)


def poplar(S, u, z, h, w, col='#e4e9de', z_ord=0.5):
    S.ax.add_patch(Ellipse((u, z + h * 0.58), w, h * 0.84, fc=col, ec='none', zorder=z_ord))
    S.line([(u, z), (u, z + h * 0.3)], c=col, lw_mm=0.6, z=z_ord)


def deciduous(S, u, z, h, w, col='#e6ebe0', z_ord=0.5):
    S.ax.add_patch(Ellipse((u, z + h * 0.62), w, h * 0.7, fc=col, ec='none', zorder=z_ord))
    S.line([(u, z), (u, z + h * 0.35)], c=col, lw_mm=0.7, z=z_ord)


# ------------------------------------------------------------------------------------------------ annotations
def level_mark(S, u, z, text, side='left', mm=1.4):
    t = S.m(1.6)
    tri = [(u - t / 2, z + t * 0.85), (u + t / 2, z + t * 0.85), (u, z)]
    S.ax.add_patch(MPoly(tri, closed=True, fc='white', ec=INK, lw=S.lw(0.13), zorder=15))
    S.ax.add_patch(MPoly([(u - t / 2, z + t * 0.85), (u, z + t * 0.85), (u, z)], closed=True, fc=INK, ec='none',
                         zorder=15))
    L = S.m(9)
    if side == 'left':
        S.line([(u - L, z + t * 0.85), (u + t / 2, z + t * 0.85)], c=INK, lw_mm=0.1, z=15)
        S.text(u - L, z + t * 0.85 + S.m(1.3), text, mm=mm, c=INK, ha='left', z=15, font='Poppins')
    else:
        S.line([(u - t / 2, z + t * 0.85), (u + L, z + t * 0.85)], c=INK, lw_mm=0.1, z=15)
        S.text(u + L, z + t * 0.85 + S.m(1.3), text, mm=mm, c=INK, ha='right', z=15, font='Poppins')


def dim_z(S, u, zs, mm=1.25):
    tick = S.m(1.2)
    S.line([(u, zs[0] - tick), (u, zs[-1] + tick)], c=INK, lw_mm=0.1, z=15)
    for z in zs:
        S.line([(u - tick / 2, z - tick / 2), (u + tick / 2, z + tick / 2)], c=INK, lw_mm=0.25, z=15)
        S.line([(u - tick, z), (u + tick * 0.4, z)], c=INK, lw_mm=0.1, z=15)
    for a, b in zip(zs[:-1], zs[1:]):
        if b - a < 0.2:
            continue
        S.text(u - S.m(1.4), (a + b) / 2, f"{(b - a) * 1000:.0f}", mm=mm, c=INK, rot=90, z=15, font='Poppins',
               bg='white')


def axis_row(S, us, labels, z, mm=1.9):
    from drawplan import axis_bubble
    for u, t in zip(us, labels):
        S.line([(u, z + S.m(2.5)), (u, GROUND)], c='#8a8a8a', lw_mm=0.1, z=1.5, ls=(0, (12, 3, 2, 3)))
        axis_bubble(S, u, z, t, mm=mm)


def scale_bar(S, x, y, mm=1.2):
    from drawplan import scale_bar as sb
    sb(S, x, y, length_m=10, step=2, mm=mm)


# ------------------------------------------------------------------------------------------------ openings
def door_rect(d):
    if d.axis == 'x':
        return box(d.x - d.w / 2, d.y - d.t / 2, d.x + d.w / 2, d.y + d.t / 2)
    return box(d.x - d.t / 2, d.y - d.w / 2, d.x + d.t / 2, d.y + d.w / 2)


EXTRA_OPENINGS = [  # doors of the head houses on the roofs: (rect, orientation, z0, z1, kind)
    (box(39.5, 6.6, 40.7, 7.0), 'x', 12.30, 14.70, 'door'),
    (box(66.1, 3.2, 67.1, 3.6), 'x', 11.70, 13.90, 'door'),
]


def openings():
    """all openings of all levels: dict(g, ori, z0, z1, kind, lv)"""
    m = model()
    out = []
    for i, lv in enumerate(m.levels):
        for w in lv.windows:
            g = box(min(w.x1, w.x2), min(w.y1, w.y2), max(w.x1, w.x2), max(w.y1, w.y2))
            ori = 'x' if abs(w.x2 - w.x1) > abs(w.y2 - w.y1) else 'y'
            head = w.head
            if lv.name == '2F' and 47.5 < (w.x1 + w.x2) / 2 < 58.0:
                head = 3.6                                   # movement hall: tall windows
            out.append(dict(g=g, ori=ori, z0=lv.z + w.sill, z1=lv.z + head, kind='window', lv=i))
        for d in lv.doors:
            g = door_rect(d)
            if d.sliding or d.folding:
                out.append(dict(g=g, ori=d.axis, z0=lv.z, z1=lv.z + 3.0, kind='glasswall', lv=i))
                continue
            h = 2.4 if (d.double or d.w >= 1.4) else 2.1
            if d.opening:
                h = 2.7 if d.w > 1.0 else 2.1
            out.append(dict(g=g, ori=d.axis, z0=lv.z, z1=lv.z + h, kind='opening' if d.opening else 'door',
                            double=d.double, lv=i, w=d.w))
        for gq in lv.glass:
            x0, y0, x1, y1 = gq.bounds
            ori = 'x' if (x1 - x0) > (y1 - y0) else 'y'
            c = gq.centroid
            out.append(dict(g=gq, ori=ori, z0=lv.z, z1=m.ceiling(i, (c.x, c.y)), kind='glass', lv=i))
    for g, ori, z0, z1, kind in EXTRA_OPENINGS:
        out.append(dict(g=g, ori=ori, z0=z0, z1=z1, kind=kind, double=False, lv=None, w=1.0))
    return out


def draw_opening(S, V, o, far=False):
    u0, u1 = V.urange(o['g'])
    z0, z1 = o['z0'], o['z1']
    lw = 0.1 if far else 0.15
    if o['kind'] == 'window':
        rect_uz(S, u0, u1, z0, z1, fc=GLASS if not far else '#e6edf3', ec=GLASS_E, lw=S.lw(lw), z=S._z + 0.01)
        if u1 - u0 > 1.6:
            n = max(1, int(round((u1 - u0) / 1.5)))
            for k in range(1, n):
                uu = u0 + (u1 - u0) * k / n
                S.line([(uu, z0), (uu, z1)], c=GLASS_E, lw_mm=0.08, z=S._z + 0.02)
        S.line([(u0 - 0.05, z0), (u1 + 0.05, z0)], c=INK, lw_mm=0.18, z=S._z + 0.02)
    elif o['kind'] in ('glass', 'glasswall'):
        rect_uz(S, u0, u1, z0, z1, fc=GLASS if not far else '#e6edf3', ec=GLASS_E, lw=S.lw(lw), z=S._z + 0.01)
        n = max(1, int(round((u1 - u0) / 1.2)))
        for k in range(1, n):
            uu = u0 + (u1 - u0) * k / n
            S.line([(uu, z0), (uu, z1)], c=GLASS_E, lw_mm=0.08, z=S._z + 0.02)
        if o['kind'] == 'glasswall':
            S.line([(u0, z0 + 2.6), (u1, z0 + 2.6)], c=GLASS_E, lw_mm=0.08, z=S._z + 0.02)
    elif o['kind'] == 'door':
        rect_uz(S, u0, u1, z0, z1, fc=DOOR if not far else '#efe4cc', ec=INK, lw=S.lw(lw), z=S._z + 0.01)
        if o.get('double'):
            S.line([((u0 + u1) / 2, z0), ((u0 + u1) / 2, z1)], c=INK, lw_mm=0.08, z=S._z + 0.02)
    else:
        rect_uz(S, u0, u1, z0, z1, fc='none', ec=GREY, lw=S.lw(0.08), z=S._z + 0.01)


# ------------------------------------------------------------------------------------------------ elevation
def solids():
    out = []
    for b, r in BL.items():
        out.append(dict(kind='block', name=b, g=box(*r), z0=GROUND, z1=ROOF[b] + PARAPET, roof=ROOF[b]))
    for rect, base, top, inner in HEADS:
        out.append(dict(kind='head', g=rect, z0=base, z1=top + 0.2, roof=top))
    for f in FINS:
        out.append(dict(kind='fin', g=box(*fin_rect(f)), z0=max(GROUND, f['bottom']), z1=f['top'], main=f['main']))
    return out


def face_openings(V, sol, ops):
    """openings that sit in the near face of a solid"""
    dn = V.drange(sol['g'])[0]
    u0, u1 = V.urange(sol['g'])
    want = 'x' if V.along_x_walls() else 'y'
    res = []
    for o in ops:
        if o['ori'] != want:
            continue
        c = o['g'].centroid
        dc = V.d(c.x, c.y)
        if not (dn - 0.05 <= dc <= dn + 0.5):
            continue
        ou0, ou1 = V.urange(o['g'])
        if ou0 < u0 - 0.1 or ou1 > u1 + 0.1:
            continue
        if o['z1'] < sol['z0'] or o['z0'] > sol['z1']:
            continue
        res.append(o)
    return res


def draw_solid(S, V, sol, ops, far=False, clip=None):
    g = sol['g'] if clip is None else sol['g'].intersection(clip)
    if g.is_empty:
        return
    u0, u1 = V.urange(g)
    z0, z1 = sol['z0'], sol['z1']
    if sol['kind'] == 'fin':
        rect_uz(S, u0, u1, z0, z1, fc=FIN_FAR if far else FINC, ec='none', z=S._z)
        return
    fc = LIGHT if far else FACADE
    if sol['kind'] == 'block' and sol['name'] == 'K':
        fc = '#e9f0f5' if far else GLASS
    rect_uz(S, u0, u1, z0, z1, fc=fc, ec=GREY if far else INK, lw=S.lw(0.1 if far else 0.25), z=S._z)
    if sol['kind'] == 'block':
        r = sol['roof']
        S.line([(u0, r), (u1, r)], c=GREY if far else INK, lw_mm=0.08, z=S._z + 0.01)
        if WALK_ROOF[sol['name']]:
            rect_uz(S, u0, u1, r + PARAPET, r + RAIL, fc='#dfeaf3', ec='none', z=S._z + 0.005, alpha=0.7)
            S.line([(u0, r + RAIL), (u1, r + RAIL)], c=GLASS_E, lw_mm=0.13, z=S._z + 0.01)
            for uu in [u0 + k * 1.5 for k in range(int((u1 - u0) / 1.5) + 1)]:
                S.line([(uu, r + PARAPET), (uu, r + RAIL)], c=GLASS_E, lw_mm=0.05, z=S._z + 0.01)
        if sol['name'] == 'K' and not far:
            n = int(round((u1 - u0) / 1.2))
            for k in range(1, n):
                uu = u0 + (u1 - u0) * k / n
                S.line([(uu, z0), (uu, r)], c=GLASS_E, lw_mm=0.08, z=S._z + 0.01)
            for zz in (3.55, 3.9):
                S.line([(u0, zz), (u1, zz)], c=GLASS_E, lw_mm=0.1, z=S._z + 0.01)
    if clip is None:
        order = {'glass': 0, 'glasswall': 1, 'window': 2, 'opening': 3, 'door': 4}
        for o in sorted(face_openings(V, sol, ops), key=lambda o: order[o['kind']]):
            draw_opening(S, V, o, far=far)


def ground_band(S, u0, u1):
    S.poly(box(u0, -1.4, u1, GROUND), fc='#efe9de', z=0.8)
    S.line([(u0, GROUND), (u1, GROUND)], c=INK, lw_mm=0.4, z=30)


# ------------------------------------------------------------------------------------------------ elevation sheets
P = PEOPLE_COLS
ELEV = {
    'NW': dict(look=(0, 1), u_off=0.0, title='North-west elevation',
               sub='towards the forest walk and Autumn Dream',
               axes=('x',),
               people=[  # plan x, plan y, z, height, colour, kind
                   (3.2, -2.6, GROUND, 1.75, P[0]), (8.6, -3.0, GROUND, 1.30, P[2]), (9.3, -3.1, GROUND, 1.78, P[1]),
                   (19.5, -2.4, GROUND, 1.70, P[3]), (20.4, -2.6, GROUND, 1.15, P[5]), (31.0, -2.8, GROUND, 1.80, P[0]),
                   (41.0, -2.3, GROUND, 1.72, P[6]), (47.6, -3.2, GROUND, 1.36, P[2]), (48.3, -3.2, GROUND, 1.25, P[3]),
                   (55.0, -2.5, GROUND, 1.78, P[0]), (60.4, -1.6, GROUND, 1.70, P[1]), (61.2, -1.7, GROUND, 1.20, P[5]),
                   (63.6, -2.0, GROUND, 1.76, P[3]), (64.3, -2.1, GROUND, 1.40, P[2]), (71.0, -2.7, GROUND, 1.80, P[0]),
                   (79.5, -3.0, GROUND, 1.68, P[6]), (85.0, -2.5, GROUND, 1.74, P[0]),
                   (14.0, 1.6, 7.50, 1.74, P[0]), (15.0, 1.7, 7.50, 1.25, P[2]), (27.5, 1.6, 7.50, 1.70, P[3]),
                   (46.0, 1.5, 12.30, 1.76, P[0]), (47.0, 1.6, 12.30, 1.32, P[5]), (53.5, 1.5, 12.30, 1.72, P[3])],
               trees=[(-6, 30, 'p', 27), (6, 34, 'd', 15), (17, 36, 'p', 29), (29, 32, 'd', 14), (38, 40, 'p', 26),
                      (50, 35, 'd', 16), (60, 42, 'p', 30), (74, 38, 'd', 14), (93, 30, 'p', 27), (89, 40, 'd', 15)]),
    'SE': dict(look=(0, -1), u_off=87.0, title='South-east elevation', sub='towards the park and the Esentai',
               axes=('x',),
               people=[
                   (15.0, 22.4, -0.15, 1.75, P[0]), (16.0, 22.6, -0.15, 1.25, P[2]), (21.5, 21.8, -0.15, 1.72, P[3]),
                   (24.0, 23.0, -0.15, 1.30, P[5], 'sit'), (28.0, 22.2, -0.15, 1.78, P[1]),
                   (31.5, 23.0, -0.15, 1.68, P[6]), (40.0, 16.5, GROUND, 1.74, P[0]), (52.0, 17.5, GROUND, 1.38, P[2]),
                   (52.8, 17.6, GROUND, 1.78, P[3]), (62.3, 13.6, GROUND, 1.72, P[0]), (63.3, 13.8, GROUND, 1.25, P[5]),
                   (68.0, 28.0, 2.25, 1.74, P[3]), (72.0, 29.0, 2.25, 1.30, P[2]), (74.0, 29.2, 2.25, 1.76, P[0]),
                   (84.0, 26.0, GROUND, 1.78, P[1]), (20.0, 18.0, 3.90, 1.70, P[0]), (21.0, 18.2, 3.90, 1.22, P[2]),
                   (30.0, 18.0, 3.90, 1.75, P[3]), (45.0, 12.6, 12.30, 1.74, P[0]), (51.0, 12.6, 12.30, 1.70, P[6]),
                   (84.5, 20.0, 3.90, 1.72, P[0]), (85.6, 20.1, 3.90, 1.36, P[5]), (6.0, 15.0, GROUND, 1.80, P[0])],
               trees=[(-4, -16, 'd', 15), (8, -22, 'p', 28), (22, -18, 'd', 16), (33, -25, 'p', 27), (46, -20, 'd', 15),
                      (58, -26, 'p', 30), (70, -18, 'd', 16), (80, -24, 'p', 27), (92, -16, 'd', 14)]),
    'NE': dict(look=(1, 0), u_off=24.6, title='North-east elevation', sub='towards the square and the new bridge',
               axes=('y',),
               people=[(-2.4, 5.0, GROUND, 1.76, P[0]), (-2.6, 8.4, GROUND, 1.72, P[3]), (-3.0, 10.0, GROUND, 1.30, P[2]),
                       (-2.0, 1.5, GROUND, 1.78, P[1]), (-3.2, 14.8, GROUND, 1.75, P[6]), (-2.2, -2.6, GROUND, 1.70, P[0]),
                       (1.6, 6.5, 7.50, 1.74, P[0]), (1.8, 9.0, 7.50, 1.25, P[5]), (12.0, 22.0, -0.15, 1.72, P[3]),
                       (12.4, 23.2, -0.15, 1.22, P[2])],
               trees=[(60, -12, 'p', 28), (60, 32, 'd', 15), (60, -4, 'd', 14), (70, 36, 'p', 27)]),
    'SW': dict(look=(-1, 0), u_off=0.0, title='South-west elevation', sub='towards the amphitheatre and the 110 kV corridor',
               axes=('y',),
               people=[(89.5, 9.0, GROUND, 1.76, P[0]), (89.6, 11.2, GROUND, 1.30, P[2]), (89.2, 22.0, GROUND, 1.78, P[3]),
                       (88.5, -2.6, GROUND, 1.72, P[1]), (86.0, 19.0, 3.90, 1.74, P[0]), (86.2, 20.4, 3.90, 1.25, P[5]),
                       (78.0, 27.5, 2.25, 1.70, P[6]), (77.0, 26.0, 1.80, 1.20, P[2], 'sit')],
               trees=[(20, -10, 'p', 28), (30, 30, 'd', 16), (10, 12, 'p', 27), (40, -2, 'd', 14)]),
}
LEVELS_ELEV = [(-0.15, '−0.15', 'R'), (0.0, '±0.00 = 1,155.00', 'L'), (3.90, '+3.90', 'B'), (7.50, '+7.50', 'B'),
               (11.70, '+11.70', 'R'), (12.30, '+12.30', 'L'), (25.0, '+25.00 top of the fins', 'B')]


def amphi_solid():
    """berm + top walkway of the amphitheatre as a solid (for the elevations)"""
    from model import AMPHI_C
    cx, cy = AMPHI_C
    pts = [(cx, cy)] + [(cx + 11.2 * math.cos(math.radians(90 + 90 * i / 40)),
                         cy + 11.2 * math.sin(math.radians(90 + 90 * i / 40))) for i in range(41)]
    return dict(kind='amphi', g=Polygon(pts), z0=GROUND, z1=2.25)


def draw_amphi_solid(S, V, sol):
    u0, u1 = V.urange(sol['g'])
    S.poly(box(u0, GROUND, u1, 2.25), fc='#cfdcbd', ec=INK, lw=S.lw(0.15), z=S._z)
    for k in range(1, 5):
        S.line([(u0, GROUND + 0.48 * k), (u1, GROUND + 0.48 * k)], c='#9fb08c', lw_mm=0.06, z=S._z + 0.01)
    S.line([(u0, 2.25 + 1.1), (u1, 2.25 + 1.1)], c=INK, lw_mm=0.12, z=S._z + 0.01)
    for uu in [u0 + k * 1.2 for k in range(int((u1 - u0) / 1.2) + 1)]:
        S.line([(uu, 2.25), (uu, 3.35)], c=INK, lw_mm=0.06, z=S._z + 0.01)


def elevation(name, out, scale=400, dpi=300, big=False):
    cfg = ELEV[name]
    V = View(cfg['look'], cfg['u_off'])
    sols = solids() + [amphi_solid()]
    ops = openings()
    us = []
    for s in sols:
        us += list(V.urange(s['g']))
    umin, umax = min(us), max(us)
    xmin, xmax = umin - 14, umax + 10
    zmin, zmax = -9.0, 33.0
    S = Sheet(xmin, zmin, xmax, zmax, scale=scale)
    items = []
    for s in sols:
        dn = V.drange(s['g'])[0]
        pri = {'block': 0, 'head': 1, 'amphi': 2, 'fin': 3}[s['kind']]
        items.append((dn, pri, 'solid', s))
    for pp in cfg['people']:
        x, y, z, h, c = pp[:5]
        kind = pp[5] if len(pp) > 5 else 'walk'
        items.append((V.d(x, y), 9, 'person', (V.u(x, y), z, h, c, kind)))
    for (a, b, kind, h) in cfg['trees']:
        # trees given as (plan x, plan y) for NW/SE, as (depth, u) otherwise
        x, y = (a, b)
        items.append((V.d(x, y), -1, 'tree', (V.u(x, y), kind, h)))
    items.sort(key=lambda t: (-t[0], t[1]))
    S._z = 2.0
    ground_band(S, xmin + 4, xmax - 4)
    for dn, pri, kind, obj in items:
        S._z += 0.05
        if kind == 'solid':
            if obj['kind'] == 'amphi':
                draw_amphi_solid(S, V, obj)
            else:
                draw_solid(S, V, obj, ops)
        elif kind == 'person':
            u, z, h, c, k = obj
            person(S, u, z, h, c, kind=k, z_ord=S._z)
        else:
            u, k, h = obj
            (poplar if k == 'p' else deciduous)(S, u, GROUND, h, 4.2 if k == 'p' else 8.5, z_ord=1.0)
    annotate(S, V, cfg, xmin, xmax, zmin, zmax, big)
    S.text(xmin + S.m(8), zmax - S.m(6), cfg['title'], mm=7.0 if big else 4.4, c=INK, font=TITLE, ha='left', z=60)
    S.text(xmin + S.m(8), zmax - S.m(11.5), f"{cfg['sub']} · scale 1:{scale}", mm=2.6 if big else 1.6, c=GREY,
           ha='left', z=60)
    S.save(out, dpi=dpi)


def annotate(S, V, cfg, xmin, xmax, zmin, zmax, big, levels=None):
    from sheets import XAX, XLAB, YAX, YLAB
    lv = levels or LEVELS_ELEV
    uL, uR = xmin + S.m(30), xmax - S.m(22)
    for z, t, side in lv:
        if side in 'LB':
            level_mark(S, uL, z, t, side='left', mm=1.25)
        if side in 'RB':
            level_mark(S, uR, z, t.split(' ')[0], side='right', mm=1.25)
    dim_z(S, uL - S.m(12), sorted(set([0.0, 3.9, 7.5, 11.7, 12.3])), mm=1.15)
    if cfg['axes'][0] == 'x':
        us = [V.u(x, 0) for x in XAX]
        axis_row(S, us, XLAB, -7.2 if V.cut is not None else -4.2)
    else:
        us = [V.u(0, y) for y in YAX]
        axis_row(S, us, YLAB, -7.2 if V.cut is not None else -4.2)
    scale_bar(S, xmax - S.m(60), zmin + S.m(8))
    S.text(xmax - S.m(8), zmin + S.m(3), 'Dream String · music leisure centre · Eva Kulikovskaya · Arch3-26-2r',
           mm=1.1, c=GREY, ha='right', z=60)


# ------------------------------------------------------------------------------------------------ sections
def segs(geom, line):
    """list of (p0, p1) plan segments of line ∩ geom"""
    g = geom.intersection(line)
    out = []
    if g.is_empty:
        return out
    parts = getattr(g, 'geoms', [g])
    for p in parts:
        if p.geom_type == 'LineString' and p.length > 0.005:
            c = list(p.coords)
            out.append((c[0], c[-1]))
    return out


def useg(V, s):
    a, b = V.u(*s[0]), V.u(*s[1])
    return (min(a, b), max(a, b))


def car_rear(S, u, z, col='#9aa5b1'):
    S.poly(box(u - 0.9, z + 0.25, u + 0.9, z + 0.95), fc=col, ec=INK, lw=S.lw(0.08), z=S._z)
    S.poly(Polygon([(u - 0.75, z + 0.95), (u + 0.75, z + 0.95), (u + 0.6, z + 1.45), (u - 0.6, z + 1.45)]),
           fc='#c9d3dc', ec=INK, lw=S.lw(0.08), z=S._z)
    for du in (-0.6, 0.6):
        S.poly(box(u + du - 0.18, z, u + du + 0.18, z + 0.3), fc=INK, z=S._z)


def car_side(S, u, z, facing=1, col='#9aa5b1'):
    f = facing
    pts = [(-2.25, 0.3), (2.25, 0.3), (2.25, 0.85), (1.2, 0.95), (0.6, 1.45), (-1.3, 1.45), (-1.9, 0.95),
           (-2.25, 0.85)]
    S.poly(Polygon([(u + f * x, z + y) for x, y in pts]), fc=col, ec=INK, lw=S.lw(0.08), z=S._z)
    for dx_ in (-1.45, 1.45):
        S.ax.add_patch(Circle((u + f * dx_, z + 0.32), 0.32, fc=INK, ec='none', zorder=S._z + 0.01))


def stair_flights(name, core, land_at, zs):
    """flights of a U-stair: list of dict(side, a0, a1, z0, z1, n) along the core (a from core x0)
    and mid landings dict(a0, a1, z)"""
    L = core[2] - core[0]
    fl, ml = [], []
    for za, zb in zip(zs[:-1], zs[1:]):
        N = int(round((zb - za) / RISER))
        n1 = N // 2
        n2 = N - n1
        land = _land(L, n1)
        e1 = (n1 - 1) * TREAD
        zm = za + n1 * RISER
        if land_at == 'low':
            a_s, a_m = land, land + e1
            ml.append(dict(a0=a_m, a1=L, z=zm))
        else:
            a_s, a_m = L - land, L - land - e1
            ml.append(dict(a0=0.0, a1=a_m, z=zm))
        fl.append(dict(side=0, a0=a_s, a1=a_m, z0=za, z1=zm, n=n1))
        fl.append(dict(side=1, a0=a_m, a1=a_s + (a_m - a_s) * 0.0 + (0 if True else 0), z0=zm, z1=zb, n=n2))
        # flight 2 returns to the floor-landing edge
        fl[-1]['a1'] = a_m - (a_m - a_s) / max(1, (n1 - 1)) * (n2 - 1) if n1 > 1 else a_s
    return fl, ml


def flight_poly(V, core, f, waist=0.22):
    """profile polygon (u, z) of one flight for views looking along y"""
    x0 = core[0]
    n = f['n']
    d = 1 if f['a1'] >= f['a0'] else -1
    pts = []
    a, z = f['a0'], f['z0']
    for i in range(n):
        pts.append((a, z))
        z += RISER
        pts.append((a, z))
        if i < n - 1:
            a += d * TREAD
    # pts end at (a1, z1)
    a_end, z_end = pts[-1]
    pitch = RISER / TREAD
    soff = waist * math.sqrt(1 + pitch * pitch)
    pts += [(a_end, z_end - soff - RISER * 0.5), (f['a0'], f['z0'] - soff + RISER * 0.5 - RISER)]
    return [(V.u(x0 + a, 0) if abs(V.l[1]) > 0.5 else 0, zz) for a, zz in pts]


def draw_stairs_section(S, V):
    line = V.cutline()
    for name, core, land_at, zs in STAIRS:
        cr = R(*core)
        if line.intersection(cr).is_empty:
            continue
        fl, ml = stair_flights(name, core, land_at, zs)
        if abs(V.l[1]) > 0.5:                              # profile: flights along x, view along y
            yc = V.cut / V.l[1]
            side_cut = 0 if yc <= core[1] + FLIGHT + 0.05 else (1 if yc >= core[3] - FLIGHT - 0.05 else None)
            beyond_side = {0: 1, 1: 0}.get(side_cut) if V.l[1] > 0 and side_cut == 0 else (0 if side_cut == 1 and V.l[1] < 0 else None)
            if side_cut is None:
                beyond_side = 1 if V.l[1] > 0 else 0
            for f in fl:
                poly = flight_poly(V, core, f)
                if f['side'] == side_cut:
                    S.poly(Polygon(poly), fc=CUT, ec=CUT, lw=S.lw(0.05), z=S._z + 0.3)
                elif f['side'] == beyond_side:
                    S.poly(Polygon(poly), fc='#f4f3ef', ec=INK, lw=S.lw(0.1), z=S._z + 0.1)
                    # handrail 0.9 m above the nosings
                    ua, ub = V.u(core[0] + f['a0'], 0), V.u(core[0] + f['a1'], 0)
                    S.line([(ua, f['z0'] + 0.9 + RISER), (ub, f['z1'] + 0.9)], c=INK, lw_mm=0.1, z=S._z + 0.12)
            for m_ in ml:
                ua, ub = sorted([V.u(core[0] + m_['a0'], 0), V.u(core[0] + m_['a1'], 0)])
                S.poly(box(ua, m_['z'] - 0.25, ub, m_['z']), fc=CUT, z=S._z + 0.3)
        else:                                              # cut across the flights
            xc = V.cut / V.l[0]
            a = xc - core[0]
            u_side = [V.urange((core[0], core[1], core[2], core[1] + FLIGHT)),
                      V.urange((core[0], core[3] - FLIGHT, core[2], core[3]))]
            for f in fl:
                lo, hi = sorted([f['a0'], f['a1']])
                if lo <= a <= hi:
                    t = abs(a - f['a0']) / TREAD
                    z = f['z0'] + (math.floor(t) + 1) * RISER
                    ua, ub = u_side[f['side']]
                    S.poly(box(ua, z - 0.3, ub, z), fc=CUT, z=S._z + 0.3)
            for m_ in ml:
                if m_['a0'] <= a <= m_['a1']:
                    ua, ub = V.urange(core)
                    S.poly(box(ua, m_['z'] - 0.25, ub, m_['z']), fc=CUT, z=S._z + 0.3)


def terrain_z(x, y):
    from model import AMPHI_C
    cx, cy = AMPHI_C
    r = math.hypot(x - cx, y - cy)
    th = math.degrees(math.atan2(y - cy, x - cx))
    if 89.9 <= th <= 180.1 and y >= cy:
        if r < 5.5:
            return 0.0
        if r < 10.0:
            return 0.45 * (int((r - 5.5) / 0.9) + 1)
        if r < 11.2:
            return 2.25
        if r < 14.2:
            return 2.25 - (r - 11.2) / 3.0 * (2.25 - GROUND)
    return GROUND


def visible_openings(S, V, m, i, lv, ops):
    line = V.cutline()
    want = 'x' if V.along_x_walls() else 'y'
    walls = lv._walls.buffer(-0.02)
    for o in ops:
        if o['lv'] != i or o['ori'] != want:
            continue
        c = o['g'].centroid
        dc = V.d(c.x, c.y)
        if dc <= V.cut + 0.15 or dc > V.cut + 30:
            continue
        uc = V.u(c.x, c.y)
        p0 = V.plan_pt(uc, V.cut + 0.03)
        if not lv._fp.contains(Point(p0)):
            continue
        p1 = V.plan_pt(uc, dc - 0.25)
        if LineString([p0, p1]).intersects(walls):
            continue
        draw_opening(S, V, o, far=True)


def section(name, out, scale=200, dpi=300, big=False):
    cfg = SECT[name]
    m = model()
    V = View(cfg['look'], cfg['u_off'], cut=cfg['cut'])
    line = V.cutline()
    sols = solids() + [amphi_solid()]
    ops = openings()
    xmin, xmax = cfg['urange']
    zmin, zmax = -9.0, 33.0
    S = Sheet(xmin, zmin, xmax, zmax, scale=scale)
    S._z = 2.0
    # earth with the terrain profile along the cut
    us = [xmin + 3 + k * 0.05 for k in range(int((xmax - xmin - 6) / 0.05))]
    top = [terrain_z(*V.plan_pt(u, V.cut)) for u in us]
    S.poly(Polygon([(us[0], -6.0)] + list(zip(us, top)) + [(us[-1], -6.0)]), fc=EARTH, z=1.0)
    S.line(list(zip(us, top)), c=INK, lw_mm=0.35, z=40)
    # amphitheatre steps (cut) where the line crosses the rows
    am = [(u, t) for u, t in zip(us, top) if t > GROUND + 0.01 or terrain_z(*V.plan_pt(u, V.cut)) == 0.0]
    # ---------------------------------------------------------------- beyond (light)
    clip = None
    lx, ly = V.l
    big_ = 400
    if abs(ly) > 0.5:
        yc = V.cut / ly
        clip = box(-big_, yc, big_, big_) if ly > 0 else box(-big_, -big_, big_, yc)
    else:
        xc = V.cut / lx
        clip = box(xc, -big_, big_, big_) if lx > 0 else box(-big_, -big_, xc, big_)
    items = []
    for s_ in sols:
        g = s_['g'].intersection(clip)
        if g.is_empty or g.area < 1e-4:
            continue
        dn = V.drange(g)[0]
        pri = {'block': 0, 'head': 1, 'amphi': 2, 'fin': 3}[s_['kind']]
        items.append((dn, pri, s_, g))
    items.sort(key=lambda t: (-t[0], t[1]))
    for dn, pri, s_, g in items:
        S._z += 0.02
        if s_['kind'] == 'amphi':
            continue
        whole = g.equals(s_['g']) or abs(g.area - s_['g'].area) < 1e-3
        if whole:
            draw_solid(S, V, s_, ops, far=True)
        else:
            draw_solid(S, V, s_, ops, far=True, clip=clip)
    for (x, y, kind, h) in cfg.get('trees', []):
        (poplar if kind == 'p' else deciduous)(S, V.u(x, y), GROUND, h, 4.2 if kind == 'p' else 8.5, z_ord=1.5)
    S._z = 10.0
    # ---------------------------------------------------------------- cut, level by level
    for i, lv in enumerate(m.levels):
        # interior (white) between the floor and the ceiling
        for sg in segs(lv._fp, line):
            u0, u1 = useg(V, sg)
            k = max(2, int((u1 - u0) / 0.1))
            prev = None
            start = u0
            for j in range(k + 1):
                u = u0 + (u1 - u0) * j / k
                c = m.ceiling(i, V.plan_pt(u, V.cut))
                if prev is not None and abs(c - prev) > 0.01:
                    S.poly(box(start, lv.z, u, prev), fc='white', z=10.1)
                    start = u
                prev = c
            S.poly(box(start, lv.z, u1, prev), fc='white', z=10.1)
    S._z = 10.5
    for i, lv in enumerate(m.levels):
        visible_openings(S, V, m, i, lv, ops)
    # hall: stage platforms beyond, trusses
    hall_extras(S, V)
    S._z = 12.0
    for i, lv in enumerate(m.levels):
        for sg in segs(lv._walls, line):
            u0, u1 = useg(V, sg)
            cs = [m.ceiling(i, V.plan_pt(u0 + (u1 - u0) * t, V.cut)) for t in (0.02, 0.5, 0.98)]
            ztop = max(cs)
            S.poly(box(u0, lv.z, u1, ztop), fc=CUT, z=12.0)
            for o in ops:
                if o['lv'] != i:
                    continue
                if not o['g'].intersects(LineString(sg)):
                    continue
                ov = o['g'].intersection(LineString(sg))
                if ov.is_empty or ov.length < 0.05:
                    continue
                cc = list(ov.coords)
                a, b = sorted([V.u(*cc[0]), V.u(*cc[-1])])
                if o['kind'] in ('door', 'opening'):
                    S.poly(box(a, lv.z, b, o['z1']), fc='white', z=12.1)
                elif o['kind'] == 'window':
                    S.poly(box(a, o['z0'], b, o['z1']), fc='white', z=12.1)
                    for f in (0.35, 0.65):
                        S.line([(a + (b - a) * f, o['z0']), (a + (b - a) * f, o['z1'])], c=GLASS_E, lw_mm=0.13, z=12.2)
                elif o['kind'] == 'glasswall':
                    S.poly(box(a, o['z0'], b, o['z1']), fc='white', z=12.1)
                    S.line([((a + b) / 2, o['z0']), ((a + b) / 2, o['z1'])], c=GLASS_E, lw_mm=0.2, z=12.2)
        for sg in segs(lv._glass, line):
            u0, u1 = useg(V, sg)
            c = m.ceiling(i, V.plan_pt((u0 + u1) / 2, V.cut))
            S.poly(box(u0, lv.z, u1, c), fc='#dbe7f1', z=12.0)
            S.line([((u0 + u1) / 2, lv.z), ((u0 + u1) / 2, c)], c=GLASS_E, lw_mm=0.2, z=12.1)
        for sg in segs(lv._floor, line):
            u0, u1 = useg(V, sg)
            t = 0.6 if lv.z < -1 else SLAB
            S.poly(box(u0 - 0.2, lv.z - t, u1 + 0.2, lv.z), fc=CUT, z=12.0)
        if lv.name == 'GF':
            # footings under the ground floor walls where there is no lower level
            ll = m.levels[0]
            for sg in segs(lv._walls, line):
                u0, u1 = useg(V, sg)
                um = (u0 + u1) / 2
                if not ll._fp.contains(Point(V.plan_pt(um, V.cut))) and u1 - u0 > 0.3:
                    S.poly(box(u0 - 0.15, -1.6, u1 + 0.15, -0.35), fc=CUT, z=12.0)
    # roofs
    heads_u = unary_union([h[0] for h in HEADS])
    holes = stair_cores().union(LIFT)
    for b, r in BL.items():
        rg = box(*r).difference(heads_u).difference(holes)
        rz = ROOF[b]
        for sg in segs(rg, line):
            u0, u1 = useg(V, sg)
            S.poly(box(u0, rz - ROOF_T, u1, rz - 0.35), fc=CUT, z=12.3)
            col = {'L': '#a9bd92', 'H': '#a9bd92', 'K': '#cfe0ee'}.get(b, '#cbc5ba')
            S.poly(box(u0, rz - 0.35, u1, rz), fc=col, ec=INK, lw=S.lw(0.06), z=12.3)
        for sg in segs(box(*r), line):
            u0, u1 = useg(V, sg)
            for ue, sgn in ((u0, 1), (u1, -1)):
                pout = V.plan_pt(ue - sgn * 0.3, V.cut)
                higher = any(box(*r2).contains(Point(pout)) and ROOF[b2] >= rz for b2, r2 in BL.items() if b2 != b)
                if higher:
                    continue
                S.poly(box(min(ue, ue + sgn * 0.4), rz - ROOF_T, max(ue, ue + sgn * 0.4), rz + PARAPET), fc=CUT, z=12.4)
                if WALK_ROOF[b]:
                    ur = ue + sgn * 0.3
                    S.line([(ur, rz + PARAPET), (ur, rz + RAIL)], c=GLASS_E, lw_mm=0.35, z=12.4)
                    S.line([(ur - 0.15, rz + RAIL), (ur + 0.15, rz + RAIL)], c=INK, lw_mm=0.3, z=12.4)
    for rect, base, topz, inner in HEADS:
        for sg in segs(rect, line):
            u0, u1 = useg(V, sg)
            S.poly(box(u0, topz - HH_T, u1, topz + 0.2), fc=CUT, z=12.4)
    S._z = 13.0
    draw_stairs_section(S, V)
    amphi_section(S, V, us, top)
    # people, cars, labels
    S._z = 20.0
    for pp in cfg.get('people', []):
        u, z, h, c = pp[:4]
        kind = pp[4] if len(pp) > 4 else 'walk'
        person(S, u, z, h, c, kind=kind, z_ord=20)
    for cu, kind in cfg.get('cars', []):
        S._z = 19.0
        (car_rear if kind == 'rear' else car_side)(S, cu, -3.60) if kind == 'rear' else car_side(S, cu, -3.60, 1 if kind == 'side' else -1)
    room_labels(S, V, m, line, cfg.get('skip_labels', ()))
    annotate(S, V, cfg, xmin, xmax, zmin, zmax, big, levels=cfg.get('levels'))
    S.text(xmin + S.m(8), zmax - S.m(6), cfg['title'], mm=7.0 if big else 4.4, c=INK, font=TITLE, ha='left', z=60)
    S.text(xmin + S.m(8), zmax - S.m(11.5), f"{cfg['sub']} · scale 1:{scale}", mm=2.6 if big else 1.6, c=GREY,
           ha='left', z=60)
    for t_ in cfg.get('notes', []):
        S.text(*t_[:2], t_[2], mm=t_[3] if len(t_) > 3 else 1.2, c=t_[4] if len(t_) > 4 else INK, ha='left', z=60)
    S.save(out, dpi=dpi)


def amphi_section(S, V, us, top):
    prof = [(u, t) for u, t in zip(us, top)]
    run = []
    for u, t in prof:
        p = V.plan_pt(u, V.cut)
        from model import AMPHI_C
        r = math.hypot(p[0] - AMPHI_C[0], p[1] - AMPHI_C[1])
        if p[1] >= AMPHI_C[1] and 4.5 <= r <= 11.2 and 89.9 <= math.degrees(math.atan2(p[1] - AMPHI_C[1], p[0] - AMPHI_C[0])) <= 180.1:
            run.append((u, t))
    if len(run) < 3:
        return
    # concrete steps 150 mm on the earth berm
    upper = run
    lower = [(u, t - 0.18) for u, t in reversed(run)]
    S.poly(Polygon(upper + lower), fc=CUT, z=13.5)
    ua, ub = run[0][0], run[-1][0]
    rail_u = ub if abs(ub - V.u(*AMPHI_C_pt())) > abs(ua - V.u(*AMPHI_C_pt())) else ua
    S.line([(rail_u, 2.25), (rail_u, 3.35)], c=INK, lw_mm=0.2, z=13.6)


def AMPHI_C_pt():
    from model import AMPHI_C
    return AMPHI_C


def hall_extras(S, V):
    """trusses of the hall roof (span 17.4 m along y, at axes 12 and 13) and the stage platforms"""
    ztop, zbot = ROOF['H'] - ROOF_T, ROOF['H'] - ROOF_T - 1.5
    trusses = [72.6, 79.8]
    if abs(V.l[1]) > 0.5:          # looking along y: trusses are cut / seen end-on
        if 0.4 < V.cut / V.l[1] < 17.0:
            for x in trusses:
                u = V.u(x, 0)
                S.poly(box(u - 0.2, zbot, u + 0.2, ztop), fc=CUT, z=12.5)
            # stage platforms beyond (y 14.6–16.9) when looking towards the SE
            if V.l[1] > 0 and V.cut / V.l[1] < 14.6:
                S.poly(box(V.u(68.0, 0), 0.0, V.u(83.0, 0), 0.6), fc='#e9dfcf', ec=INK, lw=S.lw(0.08), z=10.8)
    else:
        xc = V.cut / V.l[0]
        nxt = [x for x in trusses if (x - xc) * V.l[0] > 0]
        if 65.4 < xc < 87.0 and nxt:
            x = min(nxt, key=lambda t: abs(t - xc))
            u0, u1 = sorted([V.u(x, 0.4), V.u(x, 17.0)])
            S.line([(u0, ztop - 0.1), (u1, ztop - 0.1)], c=INK, lw_mm=0.25, z=10.9)
            S.line([(u0, zbot), (u1, zbot)], c=INK, lw_mm=0.25, z=10.9)
            n = 10
            for k in range(n + 1):
                uu = u0 + (u1 - u0) * k / n
                S.line([(uu, zbot), (uu, ztop - 0.1)], c=INK, lw_mm=0.1, z=10.9)
                if k < n:
                    uu2 = u0 + (u1 - u0) * (k + 1) / n
                    S.line([(uu, zbot) if k % 2 == 0 else (uu, ztop - 0.1), (uu2, ztop - 0.1) if k % 2 == 0 else (uu2, zbot)],
                           c=INK, lw_mm=0.1, z=10.9)
            S.text((u0 + u1) / 2, zbot - 0.55, 'steel truss 1.5 m · span 17.4 m', mm=1.1, c=GREY, z=11)


def room_labels(S, V, m, line, skip=()):
    for i, lv in enumerate(m.levels):
        if lv.name == 'HH':
            continue
        for sp in lv.spaces:
            if sp.zone == 'stair' or not (sp.num or sp.name):
                continue
            for sg in segs(sp.geom, line):
                u0, u1 = useg(V, sg)
                w = u1 - u0
                name = sp.name
                if sp.num and sp.num in skip:
                    continue
                t = name if len(name) * 0.66 * 1.1 / S.k < w - 0.4 else (sp.num if sp.num else '')
                if not t:
                    continue
                z = lv.z + (2.55 if lv.z > -1 else 2.35)
                if sp.num == '35':
                    z = lv.z + 6.0
                S.text((u0 + u1) / 2, z, t, mm=1.1, c=INK if sp.num else GREY, z=21)


SECT = {
    'A': dict(look=(0, 1), u_off=0.0, cut=9.0, urange=(-16, 100), axes=('x',), title='Section A–A',
              sub='along the building: kitchen, foyer, glass cube, transformable hall, garage and loud rooms',
              people=[(5.0, 0.0, 1.75, P[0]), (14.0, 0.0, 1.72, P[1]), (44.0, 0.0, 1.76, P[3]), (45.0, 0.0, 1.25, P[2]),
                      (51.0, 0.0, 1.70, P[6]), (61.0, 0.0, 1.74, P[0]), (62.0, 0.0, 1.30, P[5]),
                      (70.0, 0.0, 1.2, P[0], 'sit'), (71.0, 0.0, 1.2, P[3], 'sit'), (72.5, 0.0, 1.2, P[2], 'sit'),
                      (77.5, 0.0, 1.2, P[0], 'sit'), (79.0, 0.0, 1.2, P[6], 'sit'), (81.0, 0.0, 1.2, P[1], 'sit'),
                      (75.5, 0.6, 1.78, P[2]), (11.0, 3.9, 1.70, P[0]), (12.0, 3.9, 1.30, P[5]), (38.0, 3.9, 1.74, P[3]),
                      (39.0, 3.9, 1.35, P[2]), (49.0, 3.9, 1.25, P[5]), (20.0, 7.5, 1.74, P[0]), (21.0, 7.5, 1.22, P[2]),
                      (50.0, 7.5, 1.70, P[6]), (53.0, 7.5, 1.68, P[3]), (46.0, 12.3, 1.76, P[0]), (47.0, 12.3, 1.30, P[5]),
                      (74.0, -3.6, 1.75, P[3]), (78.0, -3.6, 1.72, P[0])],
              cars=[(8.0, 'rear'), (13.0, 'rear'), (18.0, 'rear'), (24.0, 'rear'), (29.0, 'rear'), (36.0, 'rear')]),
    'B': dict(look=(1, 0), u_off=31.0, cut=72.0, urange=(-14, 45), axes=('y',), title='Section B–B',
              sub='across the hall, the stair S3, the loud rooms and the amphitheatre',
              people=[(31.0 - 6.0, 0.0, 1.2, P[0], 'sit'), (31.0 - 7.0, 0.0, 1.2, P[3], 'sit'), (31.0 - 9.0, 0.0, 1.2, P[2], 'sit'),
                      (31.0 - 11.0, 0.0, 1.2, P[6], 'sit'), (31.0 - 13.0, 0.0, 1.2, P[0], 'sit'), (31.0 - 15.5, 0.6, 1.78, P[2]),
                      (31.0 - 19.0, 0.0, 1.75, P[3]), (31.0 - 23.5, 0.90, 1.2, P[0], 'sit'), (31.0 - 24.5, 1.35, 1.2, P[5], 'sit'),
                      (31.0 - 25.4, 1.80, 1.2, P[2], 'sit'), (31.0 - 27.6, 2.25, 1.74, P[0]), (31.0 - 13.0, -3.6, 1.75, P[3]),
                      (31.0 - 7.0, -3.6, 1.70, P[0]), (31.0 - 4.0, 7.5, 1.72, P[1])]),
}
SECT['A']['levels'] = [(-3.6, '−3.60', 'B'), (0.0, '±0.00 = 1,155.00', 'L'), (3.9, '+3.90', 'B'), (7.5, '+7.50', 'B'),
                       (11.7, '+11.70', 'R'), (12.3, '+12.30', 'L')]
SECT['B']['levels'] = SECT['A']['levels'][:-1] + [(11.7, '+11.70', 'B')]
