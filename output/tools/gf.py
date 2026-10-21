"""Ground floor ±0.00 of the corrected Dream String model."""
import math
from model import *
from bim import Space as Sp
from shapely.geometry import Polygon, box
from fins import FINS, fin_rect


def amphitheatre():
    """outdoor stage + 5 rows + passages + panel walls, centred at the corner hall / artists' block.
    The fan opens from the NE (angle 180°) to the SE (angle 90°) around AMPHI_C."""
    cx, cy = AMPHI_C
    parts = {}
    def ring(r0, r1, a0, a1, n=40):
        pts = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        pts += [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
                 cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
        return Polygon(pts)
    stage = Polygon([(cx, cy)] + [(cx + 4.5 * math.cos(math.radians(90 + 90 * i / 30)),
                                   cy + 4.5 * math.sin(math.radians(90 + 90 * i / 30))) for i in range(31)])
    parts['stage'] = stage
    parts['orchestra'] = ring(4.5, 5.5, 90, 180)
    # sectors: 4 sectors, 2 through passages (stepped aisles 1.2 m) and one panel wall in the middle
    # angles measured on the 7.5 m radius
    rows = []
    edges = [(90, 108.5), (113.8, 133.0), (137.0, 156.2), (161.5, 180)]
    for k in range(5):
        r0 = 5.5 + 0.9 * k
        for a0, a1 in edges:
            rows.append((k, ring(r0, r0 + 0.9, a0, a1)))
    parts['rows'] = rows
    parts['passages'] = [ring(5.5, 10.0, 108.5, 113.8), ring(5.5, 10.0, 156.2, 161.5)]
    parts['wall'] = ring(5.5, 11.2, 133.0, 137.0)
    parts['top'] = ring(10.0, 11.2, 90, 180)
    # seats: 0.5 m per seat on the middle line of every row
    seats = 0
    for k in range(5):
        rm = 5.5 + 0.9 * k + 0.45
        for a0, a1 in edges:
            seats += int(math.radians(a1 - a0) * rm / 0.5)
    parts['seats'] = seats
    return parts


def build_gf():
    lv = Level('GF', 0.0, 'Ground floor plan ±0.00')
    lv.blocks = [(blk('L', 'C', 'T', 'K'), EXT), (blk('H', 'A'), EXT)]
    S = []
    # ================================================= learning block L: administration + kitchen back rooms
    S.append(Sp('S1', 'stair S1', 'stair', R(0.4, 0.4, 7.3, 3.2), small=True))
    S.append(Sp('18', 'Wardrobe', 'admin', R(4.15, 3.45, 6.2, 5.4), target=4, small=True))
    S.append(Sp('', '', 'tech', R(6.35, 3.45, 7.3, 5.4), small=True, show_area=False))
    S.append(Sp('', 'staff hall', 'corridor', R(0.4, 3.45, 4.0, 7.35), show_area=False, label_at=(2.2, 6.7)))
    adm, x = row(7.55, 0.4, 5.4, [('10', 'Director', 'admin', 18), ('9', 'Secretary', 'admin', 10),
                                  ('11', 'Deputy', 'admin', 12), ('12', 'Accountant', 'admin', 18),
                                  ('13', 'Meeting room', 'admin', 18), ('14', "Teachers' room", 'admin', 30),
                                  ('15', 'Staff rest room', 'admin', 18)])
    S += adm
    S.append(Sp('16', 'Archive', 'admin', R(x, 0.4, 34.675, 5.4), target=6, small=True))
    S.append(Sp('', 'staff corridor', 'corridor', R(4.0, 5.55, 34.675, 7.35), show_area=False, label_at=(18.0, 6.45)))
    S.append(Sp('', 'kitchen passage', 'corridor', R(0.4, 7.5, 21.557, 8.7), show_area=False, label_at=(13.0, 8.1)))
    kit, x = row(0.4, 8.85, 12.2, [('29', 'Delivery', 'cafe', 10), ('30', 'Waste', 'cafe', 6),
                                   ('23', 'Dry store', 'cafe', 6), ('24', 'Cold store', 'cafe', 6),
                                   ('25', 'Veg. store', 'cafe', 4), ('26', 'Prep: meat, fish', 'cafe', 8),
                                   ('27', 'Prep: vegetables', 'cafe', 6), ('31', 'Kitchen staff changing', 'cafe', 8),
                                   ('32', 'Staff WC + shower', 'cafe', None, 1.3), ('28', 'Dishwashing', 'cafe', 8)])
    for k in kit:
        if k.num == '32':
            k.target = 4
        k.small = k.num not in ('29',)
    S += kit
    sv, x2 = row(21.707, 7.5, 9.25, [('19', 'Staff WC', 'admin', 6), ('20', 'Staff WC', 'admin', 6),
                                     ('17', 'Cleaning', 'admin', 4)])
    for v in sv:
        v.small = True
    S += sv
    gal = R(21.707, 9.4, 34.675, 12.2).union(R(x2, 7.5, 34.675, 9.4))
    S.append(Sp('', "children's gallery", 'entrance', gal, show_area=False, label_at=(28.0, 10.9)))
    # ================================================= cafe block C
    S.append(Sp('22', 'Hot kitchen', 'cafe', R(11.3, 12.6, 14.95, 19.2), target=24))
    S.append(Sp('21', 'Cafe, 40 seats', 'cafe', R(15.1, 12.6, 24.95, 19.2), target=65, label_at=(20.0, 16.6)))
    S.append(Sp('33', 'Club / playroom', 'club', R(25.1, 12.6, 34.4, 19.2), target=62, label_at=(29.7, 16.6)))
    # ================================================= three-storey block T
    S.append(Sp('S2', 'stair S2', 'stair', R(34.925, 0.4, 42.725, 3.2), small=True))
    S.append(Sp('L', 'lift', 'stair', R(34.925, 3.45, 37.325, 5.25), small=True))
    S.append(Sp('5', 'WC men', 'entrance', R(42.975, 0.4, 46.575, 5.4), target=18))
    S.append(Sp('4', 'WC women', 'entrance', R(46.725, 0.4, 50.325, 5.4), target=18))
    S.append(Sp('3', 'Cloakroom', 'entrance', R(50.575, 0.4, 56.575, 5.4), target=30))
    S.append(Sp('34', 'Library + homework', 'club', R(34.925, 9.55, 47.9, 13.4), target=50))
    rec = R(55.4, 8.4, 57.8, 10.9)
    sec = R(54.0, 11.05, 57.8, 13.4)
    S.append(Sp('7', 'Reception', 'admin', rec, target=6, small=True))
    S.append(Sp('8', 'Security', 'admin', sec, target=9, small=True))
    foy = R(34.925, 5.55, 57.8, 9.4).union(R(37.575, 3.45, 42.725, 5.4)).union(R(56.725, 0.4, 57.8, 5.4)) \
        .union(R(48.05, 9.4, 53.85, 13.4)).union(R(53.85, 9.4, 55.25, 10.9))
    foy = foy.difference(rec.buffer(0.15, join_style=2)).difference(sec.buffer(0.15, join_style=2))
    S.append(Sp('2', "Foyer + children's gallery", 'entrance', foy, target=120, label_at=(48.5, 7.7)))
    # ================================================= glass cube K
    S.append(Sp('1', 'Entrance lobby + tambour', 'entrance', R(58.2, 3.8, 65.4, 6.3), target=18,
                label_at=(64.0, 5.3)))
    S.append(Sp('6', 'Accessible WC', 'entrance', R(58.2, 8.4, 60.2, 10.6), target=4, small=True))
    S.append(Sp('', 'foyer · way to the hall', 'entrance', R(58.2, 6.45, 65.4, 8.25).union(R(60.35, 8.25, 65.4, 10.6)),
                show_area=False, label_at=(62.9, 9.3)))
    # ================================================= hall H + artists' block A
    S.append(Sp('S3', 'stair S3', 'stair', R(65.8, 0.4, 72.7, 3.2), small=True))
    S.append(Sp('36', 'Chair + stage store', 'hall', R(72.95, 0.4, 86.6, 3.2), target=40))
    S.append(Sp('35', 'Transformable hall, 150–200 seats', 'hall', R(65.8, 3.45, 86.6, 17.0), target=280,
                label_at=(76.2, 5.6)))
    S.append(Sp('37', 'Backstage 1', 'hall', R(75.4, 17.4, 79.55, 21.0), target=15))
    S.append(Sp('38', 'Backstage 2', 'hall', R(79.7, 17.4, 83.85, 21.0), target=15))
    S.append(Sp('S4', 'stair S4', 'stair', R(75.4, 21.4, 82.3, 24.2), small=True))
    S.append(Sp('', 'service hall', 'corridor', R(84.0, 17.4, 86.6, 21.15).union(R(82.55, 21.15, 86.6, 24.2)),
                show_area=False, label_at=(85.2, 22.7)))
    lv.add(*S)

    # ================================================= glass
    lv.glass += [R(58.2, 3.6, 65.4, 3.8), R(58.2, 10.6, 65.4, 10.8),       # cube
                 R(24.95, 13.6, 25.1, 18.2),                                # cafe | club glass wall
                 R(58.2, 6.3, 65.4, 6.45)]                                  # tambour glass screen
    lv.extra_walls = [R(60.2, 8.25, 60.35, 10.6), R(58.2, 8.25, 60.35, 8.4)]  # accessible WC box
    # ================================================= doors
    D = lv.doors
    T25, T40 = CORE, EXT
    # L – staff side
    D += [dy(0.2, 1.8, 1.2, T40, swing=-1, hinge=1, arrow=-1, label='exit'),          # S1 to outside
          dx(1.2, 3.325, 1.0, T25, swing=-1),                                         # staff hall -> S1
          dy(0.2, 5.4, 1.2, T40, swing=-1, hinge=-1, arrow=1, label='staff\nentrance', lab_off=(4.6, -1.6, 'left')),
          dx(5.2, 5.475, 0.8, swing=-1),                                              # wardrobe
          dy(11.225, 4.4, 0.9, swing=-1, hinge=1),                                     # secretary -> director
          dx(12.6, 5.475, 0.9, swing=-1), dx(14.9, 5.475, 0.9, swing=-1),
          dx(18.8, 5.475, 0.9, swing=-1), dx(22.4, 5.475, 1.0, swing=-1),
          dx(26.5, 5.475, 1.0, swing=-1), dx(32.2, 5.475, 0.9, swing=-1),
          dx(34.04, 5.475, 0.8, swing=-1),
          dx(23.4, 7.425, 0.8, swing=1), dx(27.0, 7.425, 0.8, swing=1), dx(30.0, 7.425, 0.8, swing=1),
          dx(32.9, 7.425, 1.2, swing=1, label='staff door'),
          ]
    # L – kitchen
    D += [dy(0.2, 8.1, 1.0, T40, swing=-1, arrow=1, label='kitchen staff', lab_off=(4.6, -1.6, 'left')),
          dx(1.9, 12.4, 1.6, T40, swing=1, double=True, arrow=-1, label='delivery', lab_off=(-2.6, 0)),
          dx(1.9, 8.775, 1.2, swing=-1, double=True),
          dx(4.43, 12.4, 1.0, T40, swing=1),
          dx(4.43, 8.775, 0.9, swing=-1),
          dx(6.37, 8.775, 0.9, swing=1), dx(8.31, 8.775, 0.9, swing=1), dx(9.95, 8.775, 0.8, swing=1),
          dx(11.9, 8.775, 0.9, swing=1), dx(14.13, 8.775, 0.9, swing=1), dx(16.37, 8.775, 0.9, swing=1),
          dy(17.644, 10.6, 0.7, swing=1),                                             # changing -> WC/shower
          dx(20.36, 8.775, 1.0, swing=1),
          dx(12.2, 12.4, 0.9, T40, swing=1), dx(14.1, 12.4, 0.9, T40, swing=1),         # prep -> hot kitchen
          dy(15.025, 13.6, 0.9, swing=1),                                              # hot kitchen -> cafe
          dx(20.4, 12.4, 0.9, T40, swing=-1),                                          # cafe -> dishwashing
          ]
    # cafe + club + gallery
    D += [dx(23.4, 12.4, 1.6, T40, swing=1, double=True),                             # gallery -> cafe
          dx(30.0, 12.4, 1.6, T40, swing=1, double=True),                             # gallery -> club
          dy(25.025, 18.7, 0.9, swing=1, hinge=1),                                     # cafe <-> club
          dx(20.0, 19.4, 1.8, T40, swing=1, double=True, arrow=1, label='terrace'),
          dx(30.0, 19.4, 1.2, T40, swing=1, arrow=1, label='exit'),
          Door(34.8, 8.4, 1.7, 'y', CORE, opening=True),                              # gallery opening
          ]
    # T
    D += [dx(44.8, 5.475, 1.0, swing=-1), dx(48.5, 5.475, 1.0, swing=-1),
          dx(42.0, 3.325, 1.0, T25, swing=-1),                                        # foyer -> S2
          dx(42.0, 0.2, 1.2, T40, swing=-1, arrow=-1, label='exit'),                   # S2 -> outside
          dx(51.4, 5.475, 0.9, swing=1),                                               # cloakroom staff door
          dx(41.4, 9.475, 1.6, swing=1, double=True),                                  # library
          Door(36.1, 5.4, 0.9, 'x', 0.3, opening=True),                                # lift door
          dy(55.325, 10.2, 0.8, swing=-1),                                             # reception
          dy(53.925, 12.2, 0.9, swing=1),                                              # security
          ]
    lv.notes += [(53.6, 5.2, 'counter', 1.25, GREYC, 0), (56.6, 8.0, 'counter', 1.25, GREYC, 0)]
    # openings foyer <-> cube <-> hall
    D += [Door(58.0, 7.35, 1.8, 'y', T40, opening=True),                              # T foyer -> cube
          dx(62.0, 3.7, 1.8, 0.2, swing=-1, double=True, arrow=1, label='main\nentrance', lab_off=(-2.6, 0)),
          dx(62.0, 6.375, 1.8, 0.15, swing=1, double=True),                           # inner tambour door
          dy(60.275, 9.5, 0.9, swing=1),                                               # accessible WC (outwards)
          dx(63.0, 10.7, 1.8, 0.2, swing=1, double=True, arrow=-1, label='entrance\nfrom the park', lab_off=(-1.2, 4.5, 'center')),
          dy(65.6, 5.0, 1.6, T40, swing=-1, double=True),                             # hall doors to the foyer
          dy(65.6, 9.2, 1.6, T40, swing=-1, double=True),
          ]
    # H
    D += [dx(66.6, 0.2, 1.2, T40, swing=-1, arrow=-1, label='exit'),                   # S3 -> outside
          dx(66.6, 3.325, 1.2, T25, swing=-1),                                         # hall -> S3
          dx(76.0, 3.325, 2.0, T25, swing=1, double=True), dx(83.5, 3.325, 2.0, T25, swing=1, double=True),
          dy(86.8, 10.0, 1.6, T40, swing=1, double=True, arrow=1, label='exit'),
          dx(66.5, 17.2, 1.2, T40, swing=1, arrow=1, label='exit'),
          Door(71.0, 17.2, 7.2, 'x', T40, folding=True, swing=1),                     # folding glass wall
          dx(77.5, 17.2, 1.2, T40, swing=-1), dx(81.8, 17.2, 1.2, T40, swing=-1),     # backstage -> hall
          ]
    # A
    D += [dy(75.2, 19.2, 1.4, T40, swing=-1, double=True, label=None),                # backstage 1 -> stage
          dy(79.625, 19.6, 0.9, swing=1), dy(83.925, 19.6, 1.0, swing=1),
          dy(82.425, 22.8, 1.0, T25, swing=1),
          dx(81.5, 24.4, 1.2, T40, swing=1, arrow=1, label='exit'),
          dy(86.8, 22.6, 1.6, T40, swing=-1, double=True, arrow=-1, label='artists, equipment'),
          ]
    # ================================================= windows
    W = lv.windows
    W += [wx(2.6, 5.4, 0.2)]                                             # S1
    for (a, b) in [(8.0, 10.7), (11.6, 13.0), (13.9, 15.4), (16.5, 19.1), (20.2, 22.9), (24.0, 26.2),
                   (26.8, 29.0), (30.1, 32.8)]:
        W.append(wx(a, b, 0.2))
    W += [wx(11.8, 14.4, 19.4), wx(15.6, 19.0, 19.4), wx(21.0, 24.5, 19.4), wx(25.6, 29.0, 19.4),
          wx(31.0, 33.9, 19.4), wy(11.1, 14.0, 17.6), wy(34.6, 14.4, 18.6),
          wy(0.2, 9.6, 11.6, sill=1.2), wy(0.2, 3.7, 4.4, sill=1.2)]                 # NE end wall
    W += [wx(37.0, 40.0, 0.2), wx(35.5, 39.0, 13.6), wx(40.0, 43.5, 13.6), wx(44.5, 47.4, 13.6),
          wx(48.5, 53.4, 13.6), wx(54.6, 57.3, 13.6)]
    W += [wx(68.4, 71.4, 0.2), wy(86.8, 4.4, 8.6), wy(86.8, 11.4, 15.6), wx(84.2, 86.2, 24.4),
          wy(86.8, 18.0, 20.6)]
    # ================================================= stairs + lift
    lv.stairs += [Stair('S1', (0.4, 0.4, 7.3, 3.2), 'x', 'low', up=(26, '+3.90'), down=(24, '−3.60')),
                  Stair('S2', (34.925, 0.4, 42.725, 3.2), 'x', 'high', up=(26, '+3.90'), down=(24, '−3.60')),
                  Stair('S3', (65.8, 0.4, 72.7, 3.2), 'x', 'low', up=(26, '+3.90'), down=(24, '−3.60')),
                  Stair('S4', (75.4, 21.4, 82.3, 24.2), 'x', 'high', up=(26, '+3.90 roof'))]
    lv.lifts += [(R(34.925, 3.45, 37.325, 5.25), 'lift')]
    # ================================================= fins (ground level cut 1.2 m)
    for f in FINS:
        x0, y0, x1, y1 = fin_rect(f)
        lv.fins.append((R(x0, y0, x1, y1), f['bottom'] > 1.2))
    # ================================================= outdoor
    amp = amphitheatre()
    lv.amphi = amp
    O = lv.outdoor
    PAVE = '#ecebe6'
    O += [(R(-3.0, -4.5, 87.0, 0.0), 'forest walk 4.5 m · fire-engine access · shared with Autumn Dream', PAVE),
          (R(87.0, -4.5, 90.6, 26.0), '', PAVE),
          (R(-3.0, -4.5, 0.0, 16.0), '', PAVE),
          (R(0.0, 12.6, 10.9, 16.2), 'service bay', '#e4e1da'),
          (R(13.5, 19.6, 34.8, 24.5), 'cafe terrace −0.15', PAVE),
          (R(34.8, 13.8, 58.2, 16.0), '', PAVE),
          (R(58.2, 10.8, 65.4, 16.0), '', PAVE),
          (R(65.4, 17.4, 70.0, 19.4), '', PAVE)]
    lv.plotline = [(-3.0, -2.0), (90.6, -2.0)]
    lv.levels_marks += [(39.6, 8.8, '±0.00'), (31.0, 22.8, '−0.15'), (30.0, -3.4, '−0.10'), (84.0, 12.6, '±0.00')]
    lv.seat_rows = True
    return lv


GREYC = '#6b6b6b'

if __name__ == '__main__':
    lv = build_gf()
    tot = 0
    for s in lv.spaces:
        if s.target:
            tot += s.target
            print(f"{s.num:>3} {s.name:34s} {s.area:7.1f}  target {s.target:5.0f}  {100*(s.area/s.target-1):+5.1f}%")
    print('programme GF', tot, 'seats in the amphitheatre', lv.amphi['seats'])
