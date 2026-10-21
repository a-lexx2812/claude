"""Compose finished plan sheets (title, axes, dimensions, legend, north, scale, sections)."""
import math
from shapely.geometry import box, Point
from render import Sheet, INK, GREY, RED, HAND, TITLE
from drawplan import plan, axes, dim_chain, north_arrow, scale_bar, section_mark, level_mark_plan
from bim import ZONES
from model import NORTH_DEG, BL

XAX = [0, 5.8, 11.6, 17.4, 23.2, 29.0, 34.8, 40.65, 46.5, 52.35, 58.2, 65.4, 72.6, 79.8, 87.0]
XLAB = [str(i + 1) for i in range(len(XAX))]
YAX = [0.0, 6.3, 12.6, 17.4, 24.6]
YLAB = ['A', 'B', 'C', 'D', 'E']
SECTIONS = {
    'A': dict(p0=(-9.6, 9.0), p1=(96.6, 9.0), look=(0, 1)),
    'B': dict(p0=(72.0, -15.2), p1=(72.0, 33.0), look=(1, 0)),
    'C': dict(p0=(20.5, -15.2), p1=(20.5, 33.0), look=(-1, 0)),
    'D': dict(p0=(-9.6, 1.1), p1=(96.6, 1.1), look=(0, 1)),
}


def text_w(s, mm):
    return len(s) * 0.66 * mm


def smart_labels(S, lv, mm_num, mm_name):
    from render import label_space
    for sp in lv.spaces:
        if sp.zone == 'stair' or not sp.num:
            if not sp.num and sp.name and sp.zone != 'stair':
                c = sp.label_at or (sp.geom.representative_point().x, sp.geom.representative_point().y)
                minx, miny, maxx, maxy = sp.geom.bounds
                if (maxx - minx) * S.k > text_w(sp.name, mm_name * 0.85) + 2:
                    S.text(c[0], c[1], sp.name, mm=mm_name * 0.85, c=GREY, z=9)
            continue
        minx, miny, maxx, maxy = sp.geom.bounds
        wmm, hmm = (maxx - minx) * S.k, (maxy - miny) * S.k
        x, y = sp.label_at or (sp.geom.representative_point().x, sp.geom.representative_point().y)
        if sp.num == 'G':
            S.text(x, y, sp.name, mm=mm_name * 1.1, c=INK, z=9)
            S.text(x, y - S.m(mm_name * 1.8), f"{sp.area:.0f} m²", mm=mm_name, c=GREY, z=9)
            continue
        full = (not sp.small) and wmm > text_w(sp.name, mm_name) + 1.5 and hmm > mm_num * 2 + mm_name * 3.2
        if full:
            S.circle_num(x, y + S.m(mm_num * 1.15), sp.num, mm=mm_num)
            S.text(x, y - S.m(mm_name * 0.55), sp.name, mm=mm_name, c=INK, z=9)
            S.text(x, y - S.m(mm_name * 2.0), f"{sp.area:.1f} m²", mm=mm_name * 0.92, c=GREY, z=9)
        else:
            S.circle_num(x, y, sp.num, mm=mm_num)


def stair_labels(S, lv, mm):
    for st in lv.stairs:
        x0, y0, x1, y1 = st.core
        S.text((x0 + x1) / 2, y1 + S.m(mm * 0.2) - (y1 - y0) * 0.0, '', mm=mm)
        # name tag outside the flights, on the landing side
        lx = x0 + 0.75 if st.land_at == 'low' else x1 - 0.75
        S.text(lx, (y0 + y1) / 2, st.name, mm=mm * 1.05, c=RED, font='Poppins', weight='bold', z=10, rot=90)


def legend(S, lv, x0, y0, mm, cols=4, title='Rooms of this level – area as drawn / room programme 2.4, m²'):
    rooms = [s for s in lv.spaces if s.num and s.zone not in ('stair',) and s.num != 'G']
    rooms.sort(key=lambda s: int(s.num) if s.num.isdigit() else 999)
    S.text(x0, y0, title, mm=mm * 1.1, c=INK, ha='left', z=12)
    lh = S.m(mm * 1.9)
    per = math.ceil(len(rooms) / cols)
    colw = S.m(62 if mm >= 1.8 else 52)
    for i, s in enumerate(rooms):
        c, r = divmod(i, per)
        x = x0 + c * colw
        y = y0 - lh * (r + 1.3)
        S.poly(box(x, y - S.m(mm * 0.55), x + S.m(mm * 1.1), y + S.m(mm * 0.55)), fc=ZONES[s.zone][0], ec=INK,
               lw=S.lw(0.08), z=12)
        tgt = f" / {s.target:.0f}" if s.target else ''
        S.text(x + S.m(mm * 1.7), y, f"{s.num}  {s.name} – {s.area:.1f}{tgt}", mm=mm, c=INK, ha='left', z=12)
    # zones
    zx = x0 + cols * colw
    zs = []
    for s in lv.spaces:
        if s.zone not in zs and s.zone not in ('stair',):
            zs.append(s.zone)
    S.text(zx, y0, 'Zones as in the functional diagram 2.5', mm=mm * 1.1, c=INK, ha='left', z=12)
    for i, z in enumerate(zs):
        y = y0 - lh * (i + 1.3)
        S.poly(box(zx, y - S.m(mm * 0.55), zx + S.m(mm * 1.1), y + S.m(mm * 0.55)), fc=ZONES[z][0], ec=INK,
               lw=S.lw(0.08), z=12)
        S.text(zx + S.m(mm * 1.7), y, ZONES[z][1], mm=mm, c=INK, ha='left', z=12)
    return per


def notes_box(S, x, y, lines, mm):
    S.text(x, y, 'Notes', mm=mm * 1.1, c=INK, ha='left', z=12)
    for i, l in enumerate(lines):
        S.text(x, y - S.m(mm * 1.9) * (i + 1.3), '· ' + l, mm=mm, c=INK, ha='left', z=12)


COMMON_NOTES = [
    'red arrows – entrances and exits; doors of rooms for more than 15 people open outwards',
    'stairs S1–S4: risers 150 mm, treads 320 mm (2h + b = 620 mm), flights 1.35 m, landings ≥ 1.50 m',
    'no door opens onto a flight; every stair has a door straight outside or into the foyer',
    'S1–S3: at ±0.00 the flights to −3.60 are closed off by a fire partition EI 45 with a self-closing door',
    'walls: exterior 400 mm, stair and lift cores 250 mm, partitions 150 mm, loud rooms 300 mm (box in box)',
    'grey squares – fins of the sound track (GRC 350 / 600 mm), dashed – fins hanging above the ground',
    'seismic joints between Section I, the glass cube and Section II (SP RK 2.03-30-2017)',
]


def legend_rows(S, rows, x0, y0, mm, title='Legend'):
    S.text(x0, y0, title, mm=mm * 1.1, c=INK, ha='left', z=12)
    lh = S.m(mm * 1.9)
    for i, (fc, t) in enumerate(rows):
        y = y0 - lh * (i + 1.3)
        S.poly(box(x0, y - S.m(mm * 0.55), x0 + S.m(mm * 1.1), y + S.m(mm * 0.55)), fc=fc, ec=INK, lw=S.lw(0.08), z=12)
        S.text(x0 + S.m(mm * 1.7), y, t, mm=mm, c=INK, ha='left', z=12)
    return len(rows)


def compose_plan(lv, out, scale=400, dpi=300, mode='docx', subtitle=None, sections=('A', 'B', 'C', 'D'),
                 extra=None, legend_cols=4, notes=None, ext=None, rows=None):
    big = mode != 'docx'
    mm_num, mm_name = (2.6, 2.2) if big else (1.55, 1.25)
    mm_leg = 2.2 if big else 1.25
    xmin, ymin, xmax, ymax = ext or (-13.0, -44.0, 100.0, 39.0)
    S = Sheet(xmin, ymin, xmax, ymax, scale=scale)
    plan(S, lv, labels=False)
    smart_labels(S, lv, mm_num, mm_name)
    stair_labels(S, lv, mm_num * 0.85)
    if extra:
        extra(S)
    # axes
    axes(S, XAX, YAX, XLAB, YLAB, (-5.0, -10.8, 92.0, 28.2))
    # dimension chains
    dim_chain(S, XAX, -5.8, label_mm=mm_name * 0.95)
    dim_chain(S, [0, 34.8, 58.2, 65.4, 87.0], -7.8, label_mm=mm_name * 0.95)
    dim_chain(S, [0, 87.0], -9.8, label_mm=mm_name * 0.95)
    dim_chain(S, [0, 12.6, 19.6], -3.6, label_mm=mm_name * 0.95, axis='y', above=True)
    dim_chain(S, [0, 19.6], -1.9 - 3.6, label_mm=mm_name * 0.95, axis='y', above=True)
    dim_chain(S, [0, 13.8], 60.0, label_mm=mm_name * 0.9, axis='y', above=False) if False else None
    dim_chain(S, [0, 17.4, 24.6], 90.8, label_mm=mm_name * 0.95, axis='y', above=False)
    for k in sections:
        sc = SECTIONS[k]
        section_mark(S, *sc['p0'], *sc['p1'], k, look=sc['look'])
    # title block
    ty = ymax - S.m(6)
    S.text(xmin + S.m(8), ty, lv.title, mm=7.0 if big else 4.4, c=INK, font=TITLE, ha='left', z=14)
    S.text(xmin + S.m(8), ty - S.m(7.5 if big else 5.2), subtitle or f'scale 1:{100 if big else scale} · ±0.00 = 1,155.00',
           mm=2.6 if big else 1.6, c=GREY, ha='left', z=14)
    north_arrow(S, xmax - S.m(16), ymax - S.m(16), NORTH_DEG, r_mm=9 if big else 6)
    scale_bar(S, xmax - S.m(70 if big else 50) - 10, ymin + S.m(14), length_m=10, step=2, mm=2.0 if big else 1.2)
    ly = -19.0
    if rows:
        per = legend_rows(S, rows, xmin + S.m(8), ly, mm_leg)
    else:
        per = legend(S, lv, xmin + S.m(8), ly, mm_leg, cols=legend_cols)
    nl = notes or COMMON_NOTES
    notes_box(S, xmin + S.m(8), ly - S.m(mm_leg * 1.9) * (per + 2.6), nl, mm_leg)
    S.text(xmax - S.m(8), ymin + S.m(5), 'Dream String · music leisure centre · Eva Kulikovskaya · Arch3-26-2r',
           mm=1.8 if big else 1.1, c=GREY, ha='right', z=14)
    S.save(out, dpi=dpi)
