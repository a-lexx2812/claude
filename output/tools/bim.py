"""Tiny building model + plan renderer for the Dream String drawings.

Coordinates in metres. Plan x runs along the building from the north-east end
(x = 0) to the south-west end; plan y runs from the north-west facade (y = 0)
towards the south-east. On the drawings x is to the right and y is up, so the
south-east (park) side is at the top, as in the original sheets.
"""
import math
from dataclasses import dataclass, field
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union

FONT_DIR = '/tmp/claude-0/-home-user-claude/e690d7fc-d415-569f-ba67-842ee1fc8f35/scratchpad/arch/fonts/'

# zone colours (taken from the original sheets)
ZONES = {
    'entrance':  ('#f2d9a6', 'entrance, foyer'),
    'admin':     ('#d3dbea', 'administration'),
    'cafe':      ('#ebcdb8', 'cafe and kitchen'),
    'club':      ('#f4e7a4', "children's club"),
    'hall':      ('#cfd7e7', 'hall, stage'),
    'learning':  ('#d5e5c9', 'learning'),
    'movement':  ('#c6e3dc', 'movement'),
    'loud':      ('#f1c9c1', 'loud rooms'),
    'tech':      ('#dedede', 'technical'),
    'corridor':  ('#f5efe1', 'corridor, lounge'),
    'stair':     ('#ffffff', 'stair, lift'),
    'garage':    ('#eceeea', 'garage'),
    'outdoor':   ('#ecebe6', 'terrace, walk'),
}
WALL = '#2b2b2b'
FIN = '#8d8b86'


@dataclass
class Space:
    num: str
    name: str
    zone: str
    geom: Polygon
    target: float = None      # programme area, m2
    label_at: tuple = None
    show_area: bool = True
    small: bool = False       # label with number only
    prog: str = None          # programme key (for the area check)

    @property
    def area(self):
        return self.geom.area


@dataclass
class Door:
    x: float
    y: float
    w: float
    axis: str           # 'x' if the wall runs along x (door in a horizontal wall)
    t: float = 0.4      # wall thickness
    swing: int = 1      # +1 opens to +normal side, -1 to -normal side
    hinge: int = -1     # -1 hinge at the low end, +1 at the high end
    double: bool = False
    ext: bool = False   # entrance / exit (red arrow)
    arrow: int = 0      # +1/-1 arrow direction along the normal (into the building)
    sliding: bool = False
    folding: bool = False
    label: str = None
    opening: bool = False
    lab_off: tuple = None   # label offset on paper (dx_mm, dy_mm)


@dataclass
class Window:
    x1: float
    y1: float
    x2: float
    y2: float
    t: float = 0.4
    sill: float = 0.9
    head: float = 3.0


@dataclass
class Stair:
    """U-stair (two flights + landings) inside a rectangular core.

    core: inner rectangle (x0, y0, x1, y1). along: 'x' or 'y' = direction of the flights.
    land_at: 'low' or 'high' = end of the floor landing.
    runs: list of (risers, label) for the flight pair that starts at this level (or None for top floor).
    """
    name: str
    core: tuple
    along: str
    land_at: str
    up: tuple = None        # (risers_total, 'to +3.90')
    down: tuple = None      # (risers_total, 'to -3.60')
    flight_w: float = 1.35
    tread: float = 0.32
    riser: float = 0.15
    first_flight: int = 0   # 0 = the flight at the low side of the cross axis goes up first


class Level:
    def __init__(self, name, z, title):
        self.name, self.z, self.title = name, z, title
        self.blocks = []        # (Polygon, wall thickness)
        self.spaces = []
        self.doors = []
        self.windows = []
        self.stairs = []
        self.lifts = []
        self.voids = []         # (Polygon, label)
        self.outdoor = []       # (Polygon, label, colour)
        self.notes = []         # (x, y, text, size, colour, rot)
        self.arrows = []        # (x, y, dx, dy, text)
        self.glass = []         # glass walls (Polygon)
        self.joints = []        # seismic joints (x0,y0,x1,y1)
        self.fins = []          # (Polygon)
        self.levels_marks = []  # (x, y, text)

    def footprint(self):
        return unary_union([b for b, _ in self.blocks])

    def add(self, *spaces):
        self.spaces.extend(spaces)


def R(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
