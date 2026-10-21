"""Draw a plan level onto a Sheet."""
import math
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union
from render import (Sheet, draw_door, draw_window, draw_stair, draw_lift, label_space, INK, GREY, RED,
                    HAND, TITLE)
from bim import ZONES, WALL, FIN
from matplotlib.patches import Circle, FancyArrow, Arc, Wedge, Polygon as MPoly


def plan(S, lv, legend=True, labels=True):
    # outdoor surfaces first
    for g, lab, col in lv.outdoor:
        S.poly(g, fc=col, z=0.5)
        if lab:
            c = g.representative_point()
            S.text(c.x, c.y, lab, mm=1.5, c=GREY, z=1)
    fp = unary_union([b for b, _ in lv.blocks])
    S.fp = fp
    S.poly(fp, fc=WALL, z=2)
    for g, lab in lv.voids:
        S.poly(g, fc='white', z=2.5)
        x0, y0, x1, y1 = g.bounds
        S.line([(x0, y0), (x1, y1)], c='#9a9a9a', lw_mm=0.1, z=2.6)
        S.line([(x0, y1), (x1, y0)], c='#9a9a9a', lw_mm=0.1, z=2.6)
        if lab:
            S.text((x0 + x1) / 2, (y0 + y1) / 2, lab, mm=1.6, c=GREY, bg='white', z=8)
    for sp in lv.spaces:
        fc = ZONES[sp.zone][0]
        S.poly(sp.geom, fc=fc, z=2.5)
    for g in getattr(lv, 'extra_walls', []):
        S.poly(g, fc=WALL, z=3.0)
    for g in lv.glass:
        S.poly(g, fc='#e6eef6', ec='#5a7fa6', lw=S.lw(0.13), z=3.1)
    for d in lv.doors:
        draw_door(S, d)
    for w in lv.windows:
        draw_window(S, w)
    for st in lv.stairs:
        draw_stair(S, st, lv.name)
    for g, lab in lv.lifts:
        draw_lift(S, g, lab)
    for f in lv.fins:
        g, hanging = f if isinstance(f, tuple) else (f, False)
        if hanging:
            S.poly(g, fc='none', ec=FIN, lw=S.lw(0.13), z=3.5, ls=(0, (2, 1)))
        else:
            S.poly(g, fc=FIN, z=3.5)
    for r in getattr(lv, 'railings', []):
        S.line(r, c='#5a7fa6', lw_mm=0.25, z=3.7)
    for es in getattr(lv, 'ext_stairs', []):
        draw_ext_stair(S, es)
    for g, acc in getattr(lv, 'stalls', []):
        S.poly(g, fc='#dfe6ef' if acc else 'none', ec='#7d7d7d', lw=S.lw(0.1), z=3.0)
        if acc:
            c = g.centroid
            S.text(c.x, c.y, '♿', mm=2.2, c='#3a5a8a', font='DejaVu Sans', z=9)
    if getattr(lv, 'ramp', None):
        r = lv.ramp
        S.poly(box(r['x0'], r['y0'], r['x1'], r['y1']), fc='#f5efe1', z=3.3)
        xm = (r['x0'] + r['x1']) / 2
        S.arrow(xm, r['y1'] + S.m(10), 0, -S.m(9), c=RED)
        S.text(xm + S.m(2), r['y1'] + S.m(6), r['label'], mm=1.4, c=RED, ha='left', z=12)
    if getattr(lv, 'plotline', None):
        S.line(lv.plotline, c='#8a6d3b', lw_mm=0.25, z=1.2, ls=(0, (6, 2, 1, 2)))
    if getattr(lv, 'amphi', None):
        draw_amphi(S, lv.amphi)
    if getattr(lv, 'seat_rows', False):
        draw_hall_seats(S)
    for (x0, y0, x1, y1) in lv.joints:
        S.line([(x0, y0), (x1, y1)], c='white', lw_mm=0.25, z=3.6, ls=(0, (2, 1.5)))
    if labels:
        for sp in lv.spaces:
            if sp.num or sp.name:
                if sp.zone in ('stair',):
                    continue
                if not sp.num:
                    c = sp.geom.representative_point() if sp.label_at is None else Point(*sp.label_at)
                    S.text(c.x, c.y, sp.name, mm=1.3, c=GREY, z=9)
                    continue
                label_space(S, sp)
    for (x, y, t, mm, c, rot) in lv.notes:
        S.text(x, y, t, mm=mm, c=c, rot=rot, z=10)
    for (x, y, t) in lv.levels_marks:
        level_mark_plan(S, x, y, t)


def level_mark_plan(S, x, y, t):
    r = S.m(1.2)
    S.ax.add_patch(Wedge((x, y), r, 0, 90, fc=INK, ec=INK, lw=0.3, zorder=11))
    S.ax.add_patch(Wedge((x, y), r, 180, 270, fc=INK, ec=INK, lw=0.3, zorder=11))
    S.ax.add_patch(Circle((x, y), r, fc='none', ec=INK, lw=S.lw(0.13), zorder=11))
    S.text(x + r * 1.3, y + r * 0.2, t, mm=1.5, c=INK, ha='left', z=11)


def axis_bubble(S, x, y, t, mm=2.0):
    r = S.m(mm * 1.25)
    S.ax.add_patch(Circle((x, y), r, fc='white', ec=INK, lw=S.lw(0.15), zorder=12))
    S.text(x, y - S.m(0.1), t, mm=mm * 0.9, c=INK, font='Poppins', z=12.1)


def axes(S, xs, ys, xlab, ylab, ext):
    xmin, ymin, xmax, ymax = ext
    for x, t in zip(xs, xlab):
        S.line([(x, ymin), (x, ymax)], c='#8a8a8a', lw_mm=0.1, z=1.5, ls=(0, (12, 3, 2, 3)))
        axis_bubble(S, x, ymin - S.m(4.5), t)
        axis_bubble(S, x, ymax + S.m(4.5), t)
    for y, t in zip(ys, ylab):
        S.line([(xmin, y), (xmax, y)], c='#8a8a8a', lw_mm=0.1, z=1.5, ls=(0, (12, 3, 2, 3)))
        axis_bubble(S, xmin - S.m(4.5), y, t)
        axis_bubble(S, xmax + S.m(4.5), y, t)


def dim_chain(S, pts, y, label_mm=1.6, above=True, z=12, fmt=None, axis='x', c=INK):
    """Dimension chain along x at height y (or along y at x if axis == 'y')."""
    tick = S.m(1.2)
    for i, p in enumerate(pts):
        if axis == 'x':
            S.line([(p - tick / 2, y - tick / 2), (p + tick / 2, y + tick / 2)], c=c, lw_mm=0.25, z=z)
            S.line([(p, y - tick * 0.9), (p, y + tick * 0.9)], c=c, lw_mm=0.1, z=z)
        else:
            S.line([(y - tick / 2, p - tick / 2), (y + tick / 2, p + tick / 2)], c=c, lw_mm=0.25, z=z)
            S.line([(y - tick * 0.9, p), (y + tick * 0.9, p)], c=c, lw_mm=0.1, z=z)
    if axis == 'x':
        S.line([(pts[0] - tick, y), (pts[-1] + tick, y)], c=c, lw_mm=0.1, z=z)
    else:
        S.line([(y, pts[0] - tick), (y, pts[-1] + tick)], c=c, lw_mm=0.1, z=z)
    for a, b in zip(pts[:-1], pts[1:]):
        v = b - a
        if v < 0.05:
            continue
        s = fmt(v) if fmt else (f"{v:.2f}".rstrip('0').rstrip('.') if v < 10 else f"{v:.1f}".rstrip('0').rstrip('.'))
        s = f"{v*1000:.0f}"
        off = S.m(1.3) * (1 if above else -1)
        if axis == 'x':
            S.text((a + b) / 2, y + off, s, mm=label_mm, c=c, font='Poppins', z=15, bg='white')
        else:
            S.text(y - off, (a + b) / 2, s, mm=label_mm, c=c, font='Poppins', rot=90, z=15, bg='white')


def north_arrow(S, x, y, ang_deg, r_mm=7):
    """ang_deg: direction of north on the sheet, degrees from +x counterclockwise."""
    r = S.m(r_mm)
    S.ax.add_patch(Circle((x, y), r, fc='white', ec=INK, lw=S.lw(0.2), zorder=13))
    a = math.radians(ang_deg)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    tip = (x + dx * r * 0.95, y + dy * r * 0.95)
    base = (x + dx * r * 0.25, y + dy * r * 0.25)
    w = r * 0.28
    S.line([(x - dx * r * 0.95, y - dy * r * 0.95), base], c=INK, lw_mm=0.3, z=13.1)
    S.ax.add_patch(MPoly([tip, (base[0] + px * w, base[1] + py * w), (base[0] - px * w, base[1] - py * w)],
                         closed=True, fc=INK, ec=INK, zorder=13.1))
    S.text(x + dx * r * 1.4, y + dy * r * 1.4, 'N', mm=2.0, c=INK, font='Poppins', z=13)


def scale_bar(S, x, y, length_m=10, step=2, mm=1.4):
    h = S.m(1.2)
    n = int(length_m / step)
    for i in range(n):
        S.poly(box(x + i * step, y, x + (i + 1) * step, y + h), fc=INK if i % 2 == 0 else 'white', ec=INK,
               lw=S.lw(0.13), z=13)
        S.text(x + i * step, y - S.m(2.0), f"{i*step}", mm=mm, c=INK, font='Poppins', z=13)
    S.text(x + length_m, y - S.m(2.0), f"{length_m} m", mm=mm, c=INK, font='Poppins', z=13)


def section_mark(S, x0, y0, x1, y1, lab, look=(0, 1)):
    """Section line from (x0,y0) to (x1,y1); `look` = direction of view (unit vector)."""
    S.line([(x0, y0), (x1, y1)], c=RED, lw_mm=0.25, z=14, ls=(0, (9, 2.5, 1.5, 2.5)))
    for (x, y) in ((x0, y0), (x1, y1)):
        r = S.m(2.2)
        S.ax.add_patch(Circle((x, y), r, fc='white', ec=RED, lw=S.lw(0.25), zorder=14))
        S.text(x, y, lab, mm=1.9, c=RED, font='Poppins', z=14.1, weight='semibold')
        ax, ay = look
        S.arrow(x + ax * r, y + ay * r, ax * S.m(3.2), ay * S.m(3.2), c=RED, width_mm=0.3, head_mm=1.6, z=14)


def draw_amphi(S, a):
    S.poly(a['stage'], fc='#e9dfcf', ec=INK, lw=S.lw(0.13), z=1.0)
    S.poly(a['orchestra'], fc='#f1ede6', ec='#9a9a9a', lw=S.lw(0.08), z=1.0)
    shades = ['#d9d9d6', '#d0d0cc', '#c7c7c3', '#bebeb9', '#b5b5b0']
    for k, g in a['rows']:
        S.poly(g, fc=shades[k], ec='#8a8a85', lw=S.lw(0.08), z=1.0)
    for g in a['passages']:
        S.poly(g, fc='#efece6', ec='#8a8a85', lw=S.lw(0.08), z=1.0)
    S.poly(a['wall'], fc='#7d7b76', z=1.1)
    S.poly(a['top'], fc='#ecebe6', ec='#9a9a9a', lw=S.lw(0.08), z=1.0)


def draw_hall_seats(S):
    """concert layout: 200 chairs in rows facing the stage platforms at the south-east wall"""
    y = 13.6
    n = 0
    while y > 6.2 and n < 200:
        x = 66.8
        while x < 85.6 and n < 200:
            if not (74.6 < x < 76.0):          # central aisle 1.4 m
                S.poly(box(x, y, x + 0.42, y + 0.42), fc='none', ec='#7f8fae', lw=S.lw(0.06), z=3.0)
                n += 1
            x += 0.5
        y -= 0.95
    S.poly(box(68.0, 14.6, 83.0, 16.9), fc='#e9dfcf', ec='#7f8fae', lw=S.lw(0.1), z=3.0)
    S.text(75.5, 15.75, 'stage platforms (from the store) · 200 chairs on trolleys', mm=1.15, c='#4f5f7e', z=9)


def draw_ext_stair(S, es):
    x0, x1, y0, y1, n = es['x0'], es['x1'], es['y0'], es['y1'], es['n']
    S.poly(box(x0, y0, x1, y1), fc='white', ec=INK, lw=S.lw(0.13), z=4)
    if es['along'] == 'y':
        for i in range(n):
            y = y0 + (y1 - y0) * i / (n - 1) if n > 1 else y0
            S.line([(x0, y), (x1, y)], c='#7a7a7a', lw_mm=0.1, z=4.1)
        xm = (x0 + x1) / 2
        S.line([(xm, y0 + 0.2), (xm, y1 - 0.3)], c=INK, lw_mm=0.13, z=4.2)
        S.ax.add_patch(FancyArrow(xm, y1 - 0.3, 0, 0.001, width=0, head_width=S.m(1.4), head_length=S.m(1.6),
                                  fc=INK, ec=INK, zorder=4.2))
        S.text(x0 - S.m(1.0), (y0 + y1) / 2, es['label'], mm=1.1, c=INK, rot=90, z=9)
    else:
        for i in range(n):
            x = x0 + (x1 - x0) * i / (n - 1) if n > 1 else x0
            S.line([(x, y0), (x, y1)], c='#7a7a7a', lw_mm=0.1, z=4.1)
        ym = (y0 + y1) / 2
        S.line([(x0 + 0.2, ym), (x1 - 0.3, ym)], c=INK, lw_mm=0.13, z=4.2)
        S.ax.add_patch(FancyArrow(x1 - 0.3, ym, 0.001, 0, width=0, head_width=S.m(1.4), head_length=S.m(1.6),
                                  fc=INK, ec=INK, zorder=4.2))
        S.text((x0 + x1) / 2, y0 - S.m(1.2), es['label'], mm=1.1, c=INK, z=9)
