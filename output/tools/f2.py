"""Second floor +7.50 (movement) of the corrected Dream String model."""
from model import *
from bim import Space as Sp
from fins import FINS, fin_rect


def build_2f():
    lv = Level('2F', 7.50, 'Second floor plan +7.50')
    lv.blocks = [(blk('T'), EXT), (blk('H'), EXT), (R(0.0, 0.0, 7.7, 3.6), EXT)]
    S = []
    S.append(Sp('S1', 'stair S1', 'stair', R(0.4, 0.4, 7.3, 3.2), small=True))
    S.append(Sp('S2', 'stair S2', 'stair', R(34.925, 0.4, 42.725, 3.2), small=True))
    S.append(Sp('L', 'lift', 'stair', R(34.925, 3.45, 37.325, 5.25), small=True))
    S.append(Sp('', 'lift lobby', 'corridor', R(37.575, 3.45, 42.725, 5.4), show_area=False, label_at=(40.1, 4.4)))
    S.append(Sp('64', 'Accessible WC', 'movement', R(34.925, 11.6, 37.125, 13.4), target=4, small=True))
    foy = R(34.925, 5.55, 42.725, 13.4).difference(R(34.925, 11.45, 37.275, 13.4))
    S.append(Sp('', 'roof foyer', 'corridor', foy, show_area=False, label_at=(39.8, 9.3)))
    S.append(Sp('61', 'Changing women + shower', 'movement', R(42.975, 0.4, 47.65, 4.678), target=20))
    S.append(Sp('62', 'Changing men + shower', 'movement', R(42.975, 4.828, 47.65, 9.106), target=20))
    S.append(Sp('', 'passage', 'corridor', R(42.975, 9.256, 47.65, 11.111), show_area=False, label_at=(45.3, 10.2)))
    S.append(Sp('63', 'Equipment store', 'movement', R(42.975, 11.261, 47.65, 13.4), target=10, small=True))
    S.append(Sp('60', 'Movement hall (dance, yoga)', 'movement', R(47.8, 0.4, 57.8, 13.4), target=130,
                label_at=(52.8, 7.4)))
    # hall block at this level: walls and the void, S3 between +7.80 and the roof
    S.append(Sp('S3', 'stair S3', 'stair', R(65.8, 0.4, 72.7, 3.2), small=True))
    S.append(Sp('', 'lighting catwalk +7.80 (grating, railing 1.1 m)', 'tech', R(65.8, 3.45, 86.6, 4.65),
                show_area=False, label_at=(78.0, 4.05)))
    lv.voids += [(R(72.95, 0.4, 86.6, 3.45).union(R(65.8, 4.65, 86.6, 17.0)), 'void of the hall')]
    lv.add(*S)
    # roofs around at +7.50 and below
    O = lv.outdoor
    O += [(R(0.0, 0.0, 34.8, 12.6), 'roof garden +7.50 · meadow, paths of stone pavers · glass railing 1.1 m',
           '#dfe6d4'),
          (R(58.2, 3.6, 65.4, 10.8), 'glass roof of the cube +7.50', '#e6eef6'),
          (R(10.9, 12.6, 34.8, 19.6), 'cafe roof terrace +3.90 (below)', '#eef1ea'),
          (R(75.0, 17.4, 87.0, 24.6), 'terrace over the stage +3.90 (below)', '#eef1ea')]
    lv.levels_marks += [(39.5, 12.2, '+7.50'), (52.8, 4.6, '+7.50'), (20.0, 2.4, '+7.50'), (60.2, 9.6, '+7.50')]
    # doors
    D = lv.doors
    T25, T40 = CORE, EXT
    D += [dx(42.0, 3.325, 1.0, T25, swing=-1), Door(36.1, 5.4, 0.9, 'x', 0.3, opening=True),
          Door(40.1, 5.475, 4.0, 'x', INT, opening=True),
          dy(42.85, 4.06, 0.9, swing=1), dy(47.725, 2.6, 0.9, swing=1),
          dy(42.85, 7.0, 0.9, swing=1), dy(47.725, 7.0, 0.9, swing=1),
          dy(42.85, 10.2, 1.6, swing=1, double=True), dy(47.725, 10.2, 1.6, swing=-1, double=True),
          dy(47.725, 12.3, 1.2, swing=1),
          dx(36.0, 11.525, 0.9, swing=-1),
          dy(34.8, 7.6, 1.8, T25, swing=-1, double=True, arrow=-1, label='roof garden', lab_off=(-2.4, 2.4)),
          dy(34.8, 10.2, 1.2, T25, swing=-1),
          dx(66.6, 3.325, 1.0, T25, swing=1)]                     # S3 landing +7.80 -> lighting catwalk
    W = lv.windows
    W += [wx(37.0, 40.0, 0.2), wx(43.6, 46.9, 0.2, sill=1.8), wx(48.6, 51.4, 0.2), wx(52.4, 57.0, 0.2),
          wx(35.6, 42.3, 13.6), wx(48.4, 57.2, 13.6), wy(58.0, 1.0, 3.2), wy(58.0, 5.0, 9.4), wy(58.0, 11.0, 13.0),
          wx(68.4, 71.4, 0.2), wy(86.8, 4.4, 8.6), wy(86.8, 11.4, 15.6)]
    D += [dx(1.2, 3.4, 1.0, T40, swing=1)]
    lv.notes += [(4.6, 4.5, '↑ door to the roof garden', 1.15, '#a8322d', 0)]
    lv.stairs += [Stair('S1', (0.4, 0.4, 7.3, 3.2), 'x', 'low', down=(24, '+3.90')),
                  Stair('S2', (34.925, 0.4, 42.725, 3.2), 'x', 'high', up=(32, '+12.30 terrace'), down=(24, '+3.90')),
                  Stair('S3', (65.8, 0.4, 72.7, 3.2), 'x', 'low', up=(26, '+11.70 roof'), down=(26, '+3.90'))]
    lv.lifts += [(R(34.925, 3.45, 37.325, 5.25), 'lift')]
    lv.railings = [[(7.7, 0.2), (34.6, 0.2)], [(0.2, 3.6), (0.2, 12.4)], [(0.2, 12.4), (34.6, 12.4)]]
    for f in FINS:
        if f['top'] > 7.5 + 1.2 and f['bottom'] < 7.5 + 1.2:
            x0, y0, x1, y1 = fin_rect(f)
            lv.fins.append((R(x0, y0, x1, y1), False))
    return lv


if __name__ == '__main__':
    lv = build_2f()
    for s in lv.spaces:
        if s.target:
            print(f"{s.num:>3} {s.name:30s} {s.area:7.1f}  target {s.target:5.0f}  {100*(s.area/s.target-1):+5.1f}%")
