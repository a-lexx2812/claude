"""Plan renderer (matplotlib) for the Dream String model."""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Circle, Arc, FancyArrow, Rectangle
from shapely.geometry import Polygon, MultiPolygon, box, LineString
from shapely.ops import unary_union
from bim import ZONES, WALL, FIN, FONT_DIR

for f in ['ArchitectsDaughter-Regular.ttf', 'CaveatBrush-Regular.ttf', 'Poppins-Regular.ttf',
          'Poppins-Medium.ttf', 'Poppins-SemiBold.ttf']:
    fm.fontManager.addfont(FONT_DIR + f)
HAND = 'Architects Daughter'
TITLE = 'Caveat Brush'
INK = '#2f2f2f'
GREY = '#6b6b6b'
RED = '#a8322d'


class Sheet:
    """A drawing sheet in world metres at a given paper scale."""

    def __init__(self, xmin, ymin, xmax, ymax, scale=200, mm=None):
        self.scale = scale
        self.k = 1000.0 / scale          # paper mm per world metre
        self.mm = mm or {}
        w_in = (xmax - xmin) * self.k / 25.4
        h_in = (ymax - ymin) * self.k / 25.4
        self.fig = plt.figure(figsize=(w_in, h_in))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(xmin, xmax)
        self.ax.set_ylim(ymin, ymax)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ext = (xmin, ymin, xmax, ymax)

    # sizes ---------------------------------------------------------------
    def pt(self, mm):
        """text size in points for a text height of `mm` millimetres on paper."""
        return mm / 0.3528 * 1.35        # cap height ~0.74 of the em

    def lw(self, mm):
        return mm / 0.3528

    def m(self, paper_mm):
        """world metres that correspond to `paper_mm` on paper"""
        return paper_mm / self.k

    # primitives ------------------------------------------------------------
    def poly(self, g, fc='none', ec='none', lw=0.0, z=1, alpha=1.0, ls='-', hatch=None):
        if g is None or g.is_empty:
            return
        geoms = [g] if isinstance(g, Polygon) else list(getattr(g, 'geoms', []))
        for p in geoms:
            if not isinstance(p, Polygon) or p.is_empty:
                continue
            path_pts = list(p.exterior.coords)
            patch = MPoly(path_pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha,
                          ls=ls, hatch=hatch, joinstyle='miter')
            self.ax.add_patch(patch)
            for hole in p.interiors:
                self.ax.add_patch(MPoly(list(hole.coords), closed=True, fc='white' if fc != 'none' else 'none',
                                        ec=ec, lw=lw, zorder=z + 0.01))

    def line(self, pts, c=INK, lw_mm=0.18, z=5, ls='-', alpha=1.0, cap='butt'):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=c, lw=self.lw(lw_mm), zorder=z, ls=ls, alpha=alpha,
                     solid_capstyle=cap, dash_capstyle=cap)

    def text(self, x, y, s, mm=2.0, c=INK, font=HAND, ha='center', va='center', rot=0, z=9,
             weight='normal', bg=None, style='normal'):
        kw = {}
        if bg:
            kw['bbox'] = dict(boxstyle='round,pad=0.25', fc=bg, ec='none', alpha=0.9)
        fam = [font, 'DejaVu Sans'] if font != 'DejaVu Sans' else font
        self.ax.text(x, y, s, fontsize=self.pt(mm), color=c, family=fam, ha=ha, va=va,
                     rotation=rot, zorder=z, weight=weight, style=style, **kw)

    def circle_num(self, x, y, s, mm=2.0, c=INK, fc='white', z=9):
        r = self.m(mm * 0.95)
        self.ax.add_patch(Circle((x, y), r, fc=fc, ec=c, lw=self.lw(0.13), zorder=z))
        self.text(x, y - self.m(0.05 * mm), s, mm=mm * 0.78, c=c, z=z + 0.1, font='Poppins')

    def arrow(self, x, y, dx, dy, c=RED, width_mm=0.35, head_mm=2.2, z=12):
        L = math.hypot(dx, dy)
        self.ax.add_patch(FancyArrow(x, y, dx, dy, width=self.m(width_mm), head_width=self.m(head_mm),
                                     head_length=self.m(head_mm * 1.2), length_includes_head=True,
                                     fc=c, ec=c, zorder=z))

    def save(self, path, dpi=200):
        self.fig.savefig(path, dpi=dpi, facecolor='white')
        plt.close(self.fig)


# ---------------------------------------------------------------------------
def draw_door(S, d, floor_fc='white'):
    w, t = d.w, d.t
    if d.axis == 'x':
        op = box(d.x - w / 2, d.y - t / 2, d.x + w / 2, d.y + t / 2)
    else:
        op = box(d.x - t / 2, d.y - w / 2, d.x + t / 2, d.y + w / 2)
    S.poly(op, fc=floor_fc, z=3.2)
    lw = 0.13
    if d.opening:
        return
    if d.sliding or d.folding:
        # sliding / folding glass wall: thin double line + zig-zag
        if d.axis == 'x':
            S.line([(d.x - w / 2, d.y - 0.05), (d.x + w / 2, d.y - 0.05)], c='#5a7fa6', lw_mm=0.18, z=6)
            S.line([(d.x - w / 2, d.y + 0.05), (d.x + w / 2, d.y + 0.05)], c='#5a7fa6', lw_mm=0.18, z=6)
            if d.folding:
                n = max(2, int(round(w / 1.2)))
                pts = []
                for i in range(n + 1):
                    pts.append((d.x - w / 2 + w * i / n, d.y + (0.25 if i % 2 else 0) * d.swing))
                S.line(pts, c='#5a7fa6', lw_mm=0.13, z=6)
        else:
            S.line([(d.x - 0.05, d.y - w / 2), (d.x - 0.05, d.y + w / 2)], c='#5a7fa6', lw_mm=0.18, z=6)
            S.line([(d.x + 0.05, d.y - w / 2), (d.x + 0.05, d.y + w / 2)], c='#5a7fa6', lw_mm=0.18, z=6)
            if d.folding:
                n = max(2, int(round(w / 1.2)))
                pts = []
                for i in range(n + 1):
                    pts.append((d.x + (0.25 if i % 2 else 0) * d.swing, d.y - w / 2 + w * i / n))
                S.line(pts, c='#5a7fa6', lw_mm=0.13, z=6)
        return
    leaves = [(-1, w / 2), (1, w / 2)] if d.double else [(d.hinge, w)]
    for hside, lw_ in leaves:
        if d.axis == 'x':
            hx = d.x + hside * w / 2
            hy = d.y + d.swing * t / 2
            ex, ey = hx, hy + d.swing * lw_
            S.line([(hx, hy), (ex, ey)], c=INK, lw_mm=0.18, z=6)
            # arc from leaf end to the closed position
            cx_close = hx - hside * lw_
            a0 = math.degrees(math.atan2(ey - hy, ex - hx))
            a1 = math.degrees(math.atan2(0, cx_close - hx))
        else:
            hx = d.x + d.swing * t / 2
            hy = d.y + d.hinge * w / 2 if not d.double else d.y + hside * w / 2
            ex, ey = hx + d.swing * lw_, hy
            S.line([(hx, hy), (ex, ey)], c=INK, lw_mm=0.18, z=6)
            cy_close = hy - (d.hinge if not d.double else hside) * lw_
            a0 = math.degrees(math.atan2(ey - hy, ex - hx))
            a1 = math.degrees(math.atan2(cy_close - hy, 0))
        lo, hi = sorted([a0, a1])
        if hi - lo > 180:
            lo, hi = hi, lo + 360
        S.ax.add_patch(Arc((hx, hy), 2 * lw_, 2 * lw_, theta1=lo, theta2=hi, color=GREY,
                           lw=S.lw(0.1), zorder=6))
    if d.arrow:
        L = S.m(5.0)
        gap = S.m(0.8)
        fp = getattr(S, 'fp', None)
        ox, oy = (d.lab_off or (0, 0))[:2]
        ha_force = (d.lab_off[2] if d.lab_off and len(d.lab_off) > 2 else None)
        # entrance: arrow outside pointing in; exit: arrow outside pointing out
        n0 = -d.arrow * (t / 2 + gap + L)          # tail of an entrance arrow (relative to the wall centre)
        out_variant = False
        if fp is not None:
            from shapely.geometry import Point as _P
            tail = _P(d.x, d.y + n0) if d.axis == 'x' else _P(d.x + n0, d.y)
            if fp.buffer(-0.01).contains(tail):
                out_variant = True
        if out_variant:
            s0 = d.arrow * (t / 2 + gap)
        else:
            s0 = n0
        if d.axis == 'x':
            S.arrow(d.x, d.y + s0, 0, d.arrow * L, width_mm=0.28, head_mm=1.5)
            if d.label:
                ym = d.y + s0 + d.arrow * L * 0.45
                S.text(d.x + S.m(1.2 + ox) * (1 if ox >= 0 else 1), ym + S.m(oy), d.label, mm=1.15, c=RED,
                       ha=ha_force or ('left' if ox >= 0 else 'right'), z=12)
        else:
            S.arrow(d.x + s0, d.y, d.arrow * L, 0, width_mm=0.28, head_mm=1.5)
            if d.label:
                xm = d.x + s0 + d.arrow * L * 0.5
                S.text(xm + S.m(ox), d.y + S.m(1.6 + oy), d.label, mm=1.15, c=RED, ha=ha_force or 'center', z=12)


def draw_window(S, w):
    g = box(min(w.x1, w.x2), min(w.y1, w.y2), max(w.x1, w.x2), max(w.y1, w.y2))
    S.poly(g, fc='white', ec=INK, lw=S.lw(0.08), z=3.3)
    if abs(w.y2 - w.y1) < abs(w.x2 - w.x1):     # wall along x
        ym = (w.y1 + w.y2) / 2
        S.line([(w.x1, ym), (w.x2, ym)], c='#6f8fb3', lw_mm=0.15, z=3.4)
    else:
        xm = (w.x1 + w.x2) / 2
        S.line([(xm, w.y1), (xm, w.y2)], c='#6f8fb3', lw_mm=0.15, z=3.4)


def draw_stair(S, st, level_name):
    x0, y0, x1, y1 = st.core
    S.poly(box(x0, y0, x1, y1), fc='white', z=2.6)
    fw, tr = st.flight_w, st.tread
    along_x = st.along == 'x'
    L = (x1 - x0) if along_x else (y1 - y0)
    Wc = (y1 - y0) if along_x else (x1 - x0)
    gap = Wc - 2 * fw

    def P(a, b):  # a along, b across  -> world
        return (x0 + a, y0 + b) if along_x else (x0 + b, y0 + a)

    # number of risers per flight for the flight pair drawn at this level
    n_up = st.up[0] // 2 if st.up else None
    n_dn = st.down[0] // 2 if st.down else None
    n = n_up or n_dn
    run = (n - 1) * tr
    land = 1.55 if (L - run) / 2 >= 1.55 else (L - run) / 2
    if st.land_at == 'low':
        a_start = land            # flights start after the floor landing
        a_end = a_start + run
    else:
        a_end = L - land
        a_start = a_end - run
    lw = 0.1
    # two flights: low side (b in [0, fw]) and high side (b in [fw+gap, Wc])
    sides = [(0, fw), (fw + gap, Wc)]
    up_side = st.first_flight
    for si, (b0, b1) in enumerate(sides):
        is_up = (si == up_side)
        nn = (n_up if is_up else n_dn)
        if nn is None:
            continue
        rr = (nn - 1) * tr
        if st.land_at == 'low':
            aa0, aa1 = land, land + rr
        else:
            aa0, aa1 = L - land - rr, L - land
        for i in range(nn):
            a = aa0 + i * tr
            if a > aa1 + 1e-6:
                break
            S.line([P(a, b0), P(a, b1)], c='#7a7a7a', lw_mm=lw, z=3)
        S.line([P(aa0, b0), P(aa1, b0)], c='#7a7a7a', lw_mm=lw, z=3)
        S.line([P(aa0, b1), P(aa1, b1)], c='#7a7a7a', lw_mm=lw, z=3)
        # walking line with arrow
        bm = (b0 + b1) / 2
        if st.land_at == 'low':
            start, end = (aa0 - 0.35, aa1 + 0.25) if is_up else (aa1 + 0.25, aa0 - 0.35)
        else:
            start, end = (aa1 + 0.35, aa0 - 0.25) if is_up else (aa0 - 0.25, aa1 + 0.35)
        if not is_up:
            start, end = end, start
        p0, p1 = P(start, bm), P(end, bm)
        S.line([p0, p1], c=INK, lw_mm=0.13, z=4)
        S.ax.add_patch(FancyArrow(p1[0], p1[1], (p1[0] - p0[0]) * 0.001, (p1[1] - p0[1]) * 0.001,
                                  width=0, head_width=S.m(1.6), head_length=S.m(1.9),
                                  length_includes_head=False, fc=INK, ec=INK, zorder=4))
        # dot at the start
        S.ax.add_patch(Circle(p0, S.m(0.45), fc=INK, ec='none', zorder=4))
        lab = (st.up if is_up else st.down)
        txt = ('up ' if is_up else 'down ') + f"{lab[0]}×150/320"
        am = (aa0 + aa1) / 2
        pt = P(am, bm)
        rot = 0 if along_x else 90
        S.text(pt[0], pt[1], txt, mm=1.25, c=INK, rot=rot, z=8, bg='white')
    # gap line between the flights (or the well)
    S.line([P(0.0 if st.land_at == 'high' else land, fw + gap / 2),
            P(L - (land if st.land_at == 'high' else 0.0), fw + gap / 2)], c='#9a9a9a', lw_mm=0.25, z=3)
    S.text(*P(L / 2, -0.0 - S.m(0.0) + Wc + S.m(1.6)), st.name, mm=1.5, c=GREY, z=8) if False else None


def draw_lift(S, g, label='lift'):
    x0, y0, x1, y1 = g.bounds
    S.poly(g, fc='white', z=2.6)
    S.line([(x0 + 0.15, y0 + 0.15), (x1 - 0.15, y1 - 0.15)], c='#8a8a8a', lw_mm=0.1, z=3)
    S.line([(x0 + 0.15, y1 - 0.15), (x1 - 0.15, y0 + 0.15)], c='#8a8a8a', lw_mm=0.1, z=3)
    S.poly(box(x0 + 0.15, y0 + 0.15, x1 - 0.15, y1 - 0.15), ec='#8a8a8a', lw=S.lw(0.1), z=3)
    S.text((x0 + x1) / 2, (y0 + y1) / 2, label, mm=1.4, c=INK, bg='white')


def label_space(S, sp, mm_num=1.9, mm_name=1.45):
    c = sp.geom.representative_point() if sp.label_at is None else None
    x, y = (sp.label_at if sp.label_at else (c.x, c.y))
    minx, miny, maxx, maxy = sp.geom.bounds
    w, h = maxx - minx, maxy - miny
    if sp.small or (min(w, h) < 2.4 and sp.area < 9):
        S.circle_num(x, y, sp.num, mm=mm_num)
        return
    S.circle_num(x, y + S.m(2.0), sp.num, mm=mm_num)
    name = sp.name
    S.text(x, y - S.m(0.9), name, mm=mm_name, c=INK, z=9)
    if sp.show_area:
        S.text(x, y - S.m(3.0), f"{sp.area:.1f} m²", mm=mm_name * 0.95, c=GREY, z=9)
