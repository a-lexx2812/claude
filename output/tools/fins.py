"""The 'sound track': fibre-concrete fins in front of the facades.

Every fin: facade side, position along the facade (centre, m), width along the
facade, depth, bottom and top level. Fins keep at least 1.0 m clear of every
exterior door (they never stand in front of a door) and stay off the glass cube.
"""
import random
from model import BL, ROOF

MAIN_W, MAIN_D = 0.60, 0.40
LOW_W, LOW_D = 0.35, 0.35
GAP = 0.35            # gap between the wall and the fin

# facades that carry fins: (side, block, x0, x1, wall line y, outward normal sign)
FACADES = [
    ('NW', 'L', 0.6, 34.3, 0.0, -1),
    ('NW', 'T', 35.3, 57.7, 0.0, -1),
    ('NW', 'H', 65.9, 86.5, 0.0, -1),
    ('SE', 'C', 11.4, 34.3, 19.6, +1),
    ('SE', 'L', 0.6, 10.4, 12.6, +1),
    ('SE', 'T', 35.3, 57.7, 13.8, +1),
    ('SE', 'H', 65.9, 66.6, 17.4, +1),
]

# exterior doors at ground level (x range) per facade – fins keep 1.0 m away
DOORS_NW = [(41.4, 42.6), (66.0, 67.2), (61.1, 62.9)]
DOORS_SE = [(1.1, 2.7), (3.9, 4.9), (19.1, 20.9), (29.4, 30.6), (62.1, 63.9), (65.9, 67.1)]

# special fins: (side, x, top, bottom, main)
SPECIAL = [
    ('NW', 57.95, 25.00, 0.0, True),    # the dominant fin at the main entrance (+25.00)
    ('NW', 65.65, 21.50, 0.0, True),    # second fin on the hall corner (+21.50)
    ('NW', 59.3, 9.6, 4.2, False),      # hanging 'sound bars' over the entrance
    ('NW', 60.2, 9.2, 5.0, False),
    ('NW', 63.8, 9.4, 4.6, False),
    ('NW', 64.6, 8.8, 5.4, False),
]


def _ok(x, w, doors, clear=1.0):
    for a, b in doors:
        if x + w / 2 > a - clear and x - w / 2 < b + clear:
            return False
    return True


def make_fins(seed=7):
    rnd = random.Random(seed)
    fins = []
    n_main = {('NW', 'L'): 5, ('NW', 'T'): 4, ('NW', 'H'): 4, ('SE', 'C'): 3, ('SE', 'T'): 3,
              ('SE', 'L'): 1, ('SE', 'H'): 1}
    for side, b, x0, x1, yw, sgn in FACADES:
        doors = DOORS_NW if side == 'NW' else DOORS_SE
        roof = ROOF[b]
        xs = []
        x = x0
        while x < x1:
            if _ok(x, MAIN_W, doors):
                xs.append(round(x, 2))
            x += rnd.choice([0.7, 0.9, 1.1, 1.3, 1.6, 2.0, 2.4]) * (1.0 if b != 'C' else 1.3)
        k = min(n_main.get((side, b), 0), len(xs))
        mains = set(rnd.sample(range(len(xs)), k)) if k else set()
        for i, x in enumerate(xs):
            is_main = i in mains
            w = MAIN_W if is_main else LOW_W
            d = MAIN_D if is_main else LOW_D
            if is_main:
                top = round(rnd.uniform(10.5, 18.5), 2)
                bottom = 0.0
            else:
                top = round(roof + rnd.uniform(0.6, 3.6), 2)
                bottom = 0.0 if rnd.random() < 0.72 else round(rnd.uniform(2.7, 4.2), 2)
                if b == 'C':
                    top = round(roof + rnd.uniform(0.8, 4.5), 2)
                    bottom = 0.0 if rnd.random() < 0.8 else round(rnd.uniform(2.6, 3.0), 2)
            fins.append(dict(side=side, block=b, x=x, w=w, d=d, y_wall=yw, sgn=sgn,
                             bottom=bottom, top=top, main=is_main))
    for side, x, top, bottom, main in SPECIAL:
        w = MAIN_W if main else LOW_W
        d = MAIN_D if main else LOW_D
        yw = 3.6 if (side == 'NW' and 58.3 < x < 65.3) else 0.0
        fins.append(dict(side=side, block='K', x=x, w=w, d=d, y_wall=yw, sgn=-1, bottom=bottom, top=top,
                         main=main))
    return fins


FINS = make_fins()


def fin_rect(f):
    """plan rectangle (x0, y0, x1, y1) of a fin"""
    if f['sgn'] < 0:
        y1 = f['y_wall'] - GAP
        y0 = y1 - f['d']
    else:
        y0 = f['y_wall'] + GAP
        y1 = y0 + f['d']
    return (f['x'] - f['w'] / 2, y0, f['x'] + f['w'] / 2, y1)


if __name__ == '__main__':
    m = [f for f in FINS if f['main']]
    print(len(FINS), 'fins,', len(m), 'main')
    for f in sorted(m, key=lambda f: -f['top'])[:6]:
        print(f['side'], f['block'], f['x'], f['top'])
