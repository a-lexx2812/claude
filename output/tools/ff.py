"""First floor +3.90 (learning) of the corrected Dream String model."""
from model import *
from bim import Space as Sp
from fins import FINS, fin_rect


def build_ff():
    lv = Level('FF', 3.90, 'First floor plan +3.90')
    lv.blocks = [(blk('L', 'T', 'K'), EXT), (blk('H'), EXT)]
    S = []
    # ---------------------------------------------- L: 8 practice rooms to the forest, group room 3, WCs, lounge
    S.append(Sp('S1', 'stair S1', 'stair', R(0.4, 0.4, 7.3, 3.2), small=True))
    S.append(Sp('', 'landing hall', 'corridor', R(0.4, 3.45, 7.3, 7.35), show_area=False, label_at=(3.0, 5.0)))
    pr, x = row(7.55, 0.4, 5.4, [(str(40 + i), f'Practice {i + 1}', 'learning', 16) for i in range(8)])
    for p in pr:
        p.small = False
    S += pr
    S.append(Sp('', '', 'tech', R(x, 0.4, 34.675, 5.4), small=True, show_area=False))
    S.append(Sp('', 'learning corridor', 'corridor', R(7.3, 5.55, 34.675, 7.35).union(R(0.4, 5.55, 7.3, 7.35)),
                show_area=False, label_at=(16.0, 6.45)))
    S.append(Sp('57', 'WC girls', 'learning', R(0.4, 7.5, 2.953, 12.2), target=12, small=True))
    S.append(Sp('58', 'WC boys', 'learning', R(3.103, 7.5, 5.656, 12.2), target=12, small=True))
    S.append(Sp('59', 'Accessible WC', 'learning', R(5.806, 7.5, 7.6, 9.73), target=4, small=True))
    S.append(Sp('', '', 'tech', R(5.806, 9.88, 7.6, 12.2), small=True, show_area=False))
    sr, x = row(7.75, 7.5, 12.2, [('54', 'Group room 3', 'learning', 50), ('56', 'Instrument store', 'learning', 20),
                                  ('55', 'Waiting lounge', 'learning', 40)])
    S += sr
    S.append(Sp('', 'way to the terrace', 'corridor', R(x, 7.5, 34.675, 12.2), show_area=False,
                label_at=((x + 34.675) / 2, 9.9)))
    # ---------------------------------------------- T: 4 practice rooms, group rooms 1–2, S2 + lift
    S.append(Sp('S2', 'stair S2', 'stair', R(34.925, 0.4, 42.725, 3.2), small=True))
    S.append(Sp('L', 'lift', 'stair', R(34.925, 3.45, 37.325, 5.25), small=True))
    S.append(Sp('', 'lift lobby', 'corridor', R(37.575, 3.45, 42.725, 5.4), show_area=False, label_at=(40.1, 4.4)))
    p9, x = row(42.975, 0.4, 5.4, [('48', 'Practice 9', 'learning', 16), ('49', 'Practice 10', 'learning', 16),
                                   ('50', 'Practice 11', 'learning', 16), ('51', 'Practice 12', 'learning', 16)])
    p11 = []
    S += p9
    S.append(Sp('', '', 'tech', R(x, 0.4, 57.8, 5.4), small=True, show_area=False))
    S.append(Sp('', 'corridor', 'corridor', R(34.925, 5.55, 57.8, 7.35), show_area=False, label_at=(40.0, 6.45)))
    gr, x = row(34.925, 7.5, 13.4, [('52', 'Group room 1', 'learning', 50), ('53', 'Group room 2', 'learning', 50)])
    S += gr
    S.append(Sp('', 'study corner', 'corridor', R(x, 7.5, 57.8, 13.4), show_area=False,
                label_at=((x + 57.8) / 2, 10.4)))
    # ---------------------------------------------- cube: gallery bridge, void
    S.append(Sp('', 'gallery bridge', 'corridor', R(57.8, 5.55, 65.8, 7.35), show_area=False, label_at=(61.8, 6.45)))
    lv.voids += [(R(58.2, 3.8, 65.4, 5.4), ''), (R(58.2, 7.5, 65.4, 10.6), 'void of the cube')]
    lv.glass += [R(58.2, 3.6, 65.4, 3.8), R(58.2, 10.6, 65.4, 10.8)]
    lv.extra_walls = [R(58.2, 5.4, 65.4, 5.55), R(58.2, 7.35, 65.4, 7.5)]   # bridge parapets (glass)
    # ---------------------------------------------- H: S3, booth, technical balcony, void of the hall
    S.append(Sp('S3', 'stair S3', 'stair', R(65.8, 0.4, 72.7, 3.2), small=True))
    S.append(Sp('39', 'Light + sound booth', 'hall', R(72.95, 0.4, 76.55, 3.2), target=10, small=True))
    S.append(Sp('', 'technical gallery (light rig)', 'hall', R(76.7, 0.4, 86.6, 3.2), show_area=False,
                label_at=(81.6, 1.8)))
    S.append(Sp('', 'balcony', 'corridor', R(65.8, 3.45, 67.6, 7.35).union(R(67.6, 3.45, 76.55, 4.65)),
                show_area=False, label_at=(71.5, 4.05)))
    lv.voids += [(Polygon([(76.7, 3.45), (86.6, 3.45), (86.6, 17.0), (65.8, 17.0), (65.8, 7.5), (67.75, 7.5),
                           (67.75, 4.8), (76.7, 4.8)]), 'void of the transformable hall')]
    # S4 head house on the terrace over the stage
    lv.blocks.append((R(75.0, 21.0, 82.7, 24.6), EXT))
    S.append(Sp('S4', 'stair S4', 'stair', R(75.4, 21.4, 82.3, 24.2), small=True))
    lv.add(*S)
    # ---------------------------------------------- terraces at +3.90
    O = lv.outdoor
    O += [(R(10.9, 12.6, 34.8, 19.6), 'cafe roof terrace +3.90 · planters · glass railing 1.1 m', '#dfe6d4'),
          (R(75.0, 17.4, 87.0, 24.6), 'terrace over the stage +3.90', '#dfe6d4')]
    lv.levels_marks += [(26.0, 6.45, '+3.90'), (46.0, 6.45, '+3.90'), (20.0, 14.0, '+3.90'), (85.0, 18.6, '+3.90')]
    # ---------------------------------------------- doors
    D = lv.doors
    T25, T40 = CORE, EXT
    D += [dx(1.2, 3.325, 1.0, T25, swing=-1)]                       # landing hall -> S1
    for p in pr + p9 + p11:
        x0, y0, x1, y1 = p.geom.bounds
        D.append(dx(x0 + 0.65, 5.475, 0.9, swing=-1, hinge=-1))
    D += [dx(1.7, 7.425, 0.8, swing=1), dx(4.4, 7.425, 0.8, swing=1), dx(6.7, 7.425, 0.9, swing=1)]
    for p in sr:
        x0, y0, x1, y1 = p.geom.bounds
        D.append(dx(x0 + 0.9, 7.425, 1.2 if p.target >= 40 else 0.9, swing=1 if p.target < 40 else -1,
                    double=p.target >= 40))
    D += [Door(32.4, 7.425, 3.0, 'x', INT, opening=True),
          dx(29.0, 12.4, 1.6, T40, swing=1, double=True, label='to the terrace', arrow=1),
          dx(33.6, 12.4, 1.2, T40, swing=1),
          Door(34.8, 6.45, 1.8, 'y', T25, opening=True)]
    for p in gr:
        x0, y0, x1, y1 = p.geom.bounds
        D.append(dx(x0 + 1.2, 7.425, 1.2, swing=-1, double=True))   # >15 people: open outwards
    D += [dx(42.0, 3.325, 1.0, T25, swing=-1), Door(36.1, 5.4, 0.9, 'x', 0.3, opening=True),
          Door(40.1, 5.475, 4.0, 'x', INT, opening=True),
          Door(58.0, 6.45, 1.8, 'y', T40, opening=True), Door(65.6, 6.45, 1.8, 'y', T40, opening=True),
          dx(66.6, 3.325, 1.0, T25, swing=-1),                     # balcony -> S3
          dx(74.6, 3.325, 0.9, T25, swing=1),                      # booth
          dy(76.625, 1.8, 0.9, swing=1),
          dx(81.5, 21.2, 1.0, T40, swing=-1, label='terrace', arrow=-1)]
    # ---------------------------------------------- windows
    W = lv.windows
    W += [wx(2.6, 5.4, 0.2), wy(0.2, 3.9, 7.0), wy(0.2, 8.3, 11.4, sill=1.6)]      # NE end wall: landing hall, WC
    for p in pr + p9 + p11:
        x0, y0, x1, y1 = p.geom.bounds
        W.append(wx(x0 + 0.5, x1 - 0.5, 0.2))
    W += [wx(1.0, 2.4, 12.4, sill=1.6), wx(3.7, 5.1, 12.4, sill=1.6), wx(8.3, 10.3, 12.4), wx(11.3, 17.8, 12.4),
          wx(19.0, 22.0, 12.4), wx(24.0, 27.6, 12.4)]
    W += [wx(35.6, 42.8, 13.6), wx(44.2, 51.4, 13.6), wx(52.8, 57.2, 13.6), wx(37.0, 40.0, 0.2),
          wx(68.4, 71.4, 0.2), wx(73.4, 76.0, 0.2), wy(86.8, 4.4, 8.6), wy(86.8, 11.4, 15.6)]
    W += [Window(72.95, 3.2, 76.55, 3.45, 0.25)]                    # booth window into the hall
    # ---------------------------------------------- stairs, lift, fins
    lv.stairs += [Stair('S1', (0.4, 0.4, 7.3, 3.2), 'x', 'low', up=(24, '+7.50 roof garden'), down=(26, '±0.00')),
                  Stair('S2', (34.925, 0.4, 42.725, 3.2), 'x', 'high', up=(24, '+7.50'), down=(26, '±0.00')),
                  Stair('S3', (65.8, 0.4, 72.7, 3.2), 'x', 'low', up=(26, '+7.80 → roof'), down=(26, '±0.00')),
                  Stair('S4', (75.4, 21.4, 82.3, 24.2), 'x', 'high', down=(26, '±0.00'))]
    lv.railings = [[(10.95, 12.6), (10.95, 19.55), (34.75, 19.55), (34.75, 13.8)],
                   [(75.05, 17.4), (75.05, 21.0)], [(82.7, 24.55), (86.95, 24.55), (86.95, 17.4)]]
    lv.lifts += [(R(34.925, 3.45, 37.325, 5.25), 'lift')]
    for f in FINS:
        if f['top'] > 3.9 + 1.2 and f['bottom'] < 3.9 + 1.2:
            x0, y0, x1, y1 = fin_rect(f)
            lv.fins.append((R(x0, y0, x1, y1), False))
    return lv


if __name__ == '__main__':
    lv = build_ff()
    for s in lv.spaces:
        if s.target:
            print(f"{s.num:>3} {s.name:30s} {s.area:7.1f}  target {s.target:5.0f}  {100*(s.area/s.target-1):+5.1f}%")
