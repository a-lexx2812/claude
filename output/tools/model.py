"""Dream String – corrected building model (all levels)."""
from bim import Level, Space, Door, Window, Stair, R
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
import math

# ---------------------------------------------------------------- blocks
BL = {
    'L': (0.0, 0.0, 34.8, 12.6),    # learning block, 2 storeys + lower level (garage)
    'C': (10.9, 12.6, 34.8, 19.6),  # cafe, hot kitchen and club, 1 storey, roof terrace +3.90
    'T': (34.8, 0.0, 58.2, 13.8),   # three-storey block, roof +12.30
    'K': (58.2, 3.6, 65.4, 10.8),   # glass cube, 2 storeys high, roof +7.50
    'H': (65.4, 0.0, 87.0, 17.4),   # transformable hall, roof +11.70, loud rooms below
    'A': (75.0, 17.4, 87.0, 24.6),  # artists' block, 1 storey, terrace over the stage +3.90
}
ROOF = {'L': 7.50, 'C': 3.90, 'T': 12.30, 'K': 7.50, 'H': 11.70, 'A': 3.90}
AMPHI_C = (75.0, 17.4)          # centre of the amphitheatre (corner hall / artists' block)
EXT = 0.40                      # exterior wall
INT = 0.15                      # partition
CORE = 0.25                     # stair / lift walls


def blk(*names):
    return unary_union([box(*BL[n]) for n in names])


def row(x0, y0, y1, items, gap=INT, xdir=1):
    """Place rooms side by side along x between y0 and y1 so that each has its area.
    items: (num, name, zone, area) or (num, name, zone, None, width). Returns spaces, x_end."""
    out = []
    d = y1 - y0
    x = x0
    for it in items:
        num, name, zone, area = it[:4]
        w = it[4] if len(it) > 4 and it[4] else area / d
        if xdir > 0:
            g = R(x, y0, x + w, y1)
            x = x + w + gap
        else:
            g = R(x - w, y0, x, y1)
            x = x - w - gap
        out.append(Space(num, name, zone, g, target=area))
    return out, x


def col(y0, x0, x1, items, gap=INT, ydir=1):
    out = []
    d = x1 - x0
    y = y0
    for it in items:
        num, name, zone, area = it[:4]
        h = it[4] if len(it) > 4 and it[4] else area / d
        if ydir > 0:
            g = R(x0, y, x1, y + h)
            y = y + h + gap
        else:
            g = R(x0, y - h, x1, y)
            y = y - h - gap
        out.append(Space(num, name, zone, g, target=area))
    return out, y


# ---------------------------------------------------------------- helpers for openings
def dx(x, y, w, t=INT, swing=1, hinge=-1, **kw):
    """door in a wall that runs along x (centre line y)"""
    return Door(x, y, w, 'x', t, swing, hinge, **kw)


def dy(x, y, w, t=INT, swing=1, hinge=-1, **kw):
    """door in a wall that runs along y (centre line x)"""
    return Door(x, y, w, 'y', t, swing, hinge, **kw)


def wx(x1, x2, y, t=EXT, sill=0.9, head=3.0):
    return Window(x1, y - t / 2, x2, y + t / 2, t, sill, head)


def wy(x, y1, y2, t=EXT, sill=0.9, head=3.0):
    return Window(x - t / 2, y1, x + t / 2, y2, t, sill, head)


# north on the sheet (plan x -> SW, plan y -> SE): degrees from +x, counter-clockwise
NORTH_DEG = -128.5
# room numbers of the whole programme (73 rooms)
