"""Lower level −3.60: garage, loud rooms, technical rooms."""
from model import *
from bim import Space as Sp


GARAGE = R(0.0, 0.0, 42.95, 18.3).union(R(42.95, 5.65, 45.45, 18.3))


def build_ll():
    lv = Level('LL', -3.60, 'Lower level plan −3.60')
    lv.blocks = [(GARAGE.union(R(42.95, 3.05, 65.4, 5.65)).union(blk('H')), EXT)]
    S = []
    # ---------------------------------------------- garage for 24 cars
    S.append(Sp('S1', 'stair S1', 'stair', R(0.4, 0.4, 7.3, 3.2), small=True))
    S.append(Sp('', 'fire lobby', 'corridor', R(0.4, 3.45, 7.3, 5.75), show_area=False, label_at=(3.8, 4.6)))
    S.append(Sp('S2', 'stair S2', 'stair', R(34.925, 0.4, 42.725, 3.2), small=True))
    S.append(Sp('L', 'lift', 'stair', R(34.925, 3.45, 37.325, 5.25), small=True))
    S.append(Sp('', 'lift lobby', 'corridor', R(37.575, 3.45, 42.725, 5.75), show_area=False, label_at=(40.1, 4.6)))
    gar = R(0.4, 0.4, 45.05, 17.9).difference(R(0.0, 0.0, 7.55, 5.9)).difference(R(34.675, 0.0, 45.45, 5.9))
    S.append(Sp('G', 'Garage · 24 places (3 accessible)', 'garage', gar, show_area=True, label_at=(19.0, 8.9)))
    # ---------------------------------------------- corridor to the hall
    S.append(Sp('', 'corridor', 'corridor', R(42.95, 3.45, 65.8, 5.25).union(R(65.8, 3.45, 86.6, 5.25)),
                show_area=False, label_at=(52.0, 4.35)))
    # ---------------------------------------------- under the hall: loud rooms + technical
    S.append(Sp('S3', 'stair S3', 'stair', R(65.8, 0.4, 72.7, 3.2), small=True))
    t, x = row(72.95, 0.4, 3.2, [('71', 'Electrical room', 'tech', 10), ('72', 'Cleaning', 'tech', None, 1.5),
                                 ('73', 'Cleaning', 'tech', None, 1.5)])
    t[1].target = 4; t[2].target = 4
    for k in t:
        k.small = True
    S += t
    S.append(Sp('', 'shaft / risers', 'tech', R(x, 0.4, 86.6, 3.2), show_area=False, label_at=((x + 86.6) / 2, 1.8)))
    S.append(Sp('70', 'Plant room (ventilation, heating)', 'tech', R(65.8, 5.55, 71.0, 17.0), target=60,
                label_at=(68.4, 11.0)))
    S.append(Sp('65', 'Band room', 'loud', R(71.3, 9.95, 76.974, 17.0), target=40))
    S.append(Sp('66', 'Drum room', 'loud', R(77.274, 9.95, 80.678, 17.0), target=24))
    S.append(Sp('67', 'Recording – live room', 'loud', R(80.978, 9.95, 85.233, 17.0), target=30))
    S.append(Sp('', '', 'tech', R(85.533, 9.95, 86.6, 17.0), show_area=False, small=True))
    S.append(Sp('68', 'Control room', 'loud', R(82.94, 5.55, 86.6, 9.65), target=15, small=True))
    S.append(Sp('69', 'Accessible WC', 'loud', R(71.3, 5.55, 73.5, 7.35), target=4, small=True))
    S.append(Sp('', 'sound lock · lobby', 'corridor', R(71.3, 7.5, 82.79, 9.65).union(R(73.65, 5.55, 82.79, 7.5)),
                show_area=False, label_at=(78.2, 6.6)))
    lv.add(*S)
    # ---------------------------------------------- parking stalls (2.5 × 5.5, accessible 3.6 × 5.5)
    st = []
    x = 7.55
    for i in range(10):                       # NW row 10 × 2.5 × 5.5
        st.append((R(x, 0.4, x + 2.5, 5.9), False)); x += 2.5
    x = 6.1
    for i in range(11):                       # SE row 11 × 2.5 × 6.0
        st.append((R(x, 11.9, x + 2.5, 17.9), False)); x += 2.5
    x = 34.25
    for i in range(3):                        # 3 wide places 3.6 × 6.0 next to the lift (SP RK 3.06-101, 8.8.6)
        st.append((R(x, 11.9, x + 3.6, 17.9), True)); x += 3.6
    lv.stalls = st
    lv.notes += [(19.0, 7.0, 'aisle 6.0 m · clear height 2.6 m · places 2.5 × 5.5 / 2.5 × 6.0, wide places 3.6 × 6.0', 1.3, '#6b6b6b', 0)]
    # ramp portal in the SE wall
    lv.ramp = dict(x0=2.3, x1=6.1, y0=17.9, y1=18.3, label='covered heated ramp ≤ 15 % · 3.8 m lane → square (see general plan)')
    lv.levels_marks += [(19.0, 10.4, '−3.60'), (58.0, 4.35, '−3.60')]
    D = lv.doors
    T25, T40 = CORE, EXT
    D += [dx(1.2, 3.325, 1.0, T25, swing=1), dx(5.0, 5.825, 1.0, INT, swing=1),
          dx(42.0, 3.325, 1.0, T25, swing=1), Door(36.1, 5.4, 0.9, 'x', 0.3, opening=True),
          dx(40.1, 5.825, 1.2, INT, swing=1),
          dy(42.84, 4.35, 1.2, 0.225, swing=1),
          dx(66.6, 3.325, 1.0, T25, swing=1),
          dx(74.8, 3.325, 0.9, T25, swing=-1), dx(76.9, 3.325, 0.8, T25, swing=-1), dx(78.55, 3.325, 0.8, T25, swing=-1),
          dx(68.4, 5.4, 1.6, 0.3, swing=1, double=True),
          dx(78.0, 5.4, 1.2, 0.3, swing=1),
          dx(72.4, 7.425, 0.9, 0.15, swing=1),
          dx(74.0, 9.8, 1.0, 0.3, swing=1), dx(79.0, 9.8, 1.0, 0.3, swing=1), dx(81.9, 9.8, 1.0, 0.3, swing=1),
          dy(82.865, 8.6, 0.9, 0.15, swing=1)]
    lv.windows += [Window(82.94, 9.65, 85.233, 9.95, 0.3)]          # control room -> live room
    lv.stairs += [Stair('S1', (0.4, 0.4, 7.3, 3.2), 'x', 'low', up=(24, '±0.00')),
                  Stair('S2', (34.925, 0.4, 42.725, 3.2), 'x', 'high', up=(24, '±0.00')),
                  Stair('S3', (65.8, 0.4, 72.7, 3.2), 'x', 'low', up=(24, '±0.00'))]
    lv.lifts += [(R(34.925, 3.45, 37.325, 5.25), 'lift')]
    return lv


if __name__ == '__main__':
    lv = build_ll()
    for s in lv.spaces:
        if s.target:
            print(f"{s.num:>3} {s.name:30s} {s.area:7.1f}  target {s.target:5.0f}  {100*(s.area/s.target-1):+5.1f}%")
        elif s.num == 'G':
            print('garage', round(s.area, 1))
    print('stalls', len(lv.stalls), 'accessible', sum(1 for _, a in lv.stalls if a))
