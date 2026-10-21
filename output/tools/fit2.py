from geo import *
from shapely.geometry import box
from shapely.ops import unary_union, transform
import numpy as np, math, warnings
warnings.filterwarnings('ignore')
free=Polygon([(-54.8,-9.3),(20.0,50.3),(52.0,3.7),(10.6,-47.1),(-33.8,-29.0)])
A=np.array((-54.8,-9.3)); B=np.array((20.0,50.3)); uh=(B-A)/np.linalg.norm(B-A); vh=np.array((uh[1],-uh[0]))
def fp(L=36.0):
    d=L-33.6
    parts=[box(0,0,L,12.6),box(10.9,12.6,L,19.6),box(L,0,L+23.4,13.8),box(L+23.4,3.6,L+30.6,10.8),box(L+30.6,0,L+52.2,17.4),box(L+40.2,17.4,L+52.2,24.6)]
    cx,cy=L+40.2,17.4
    t=np.linspace(0,math.pi/2,40); parts.append(Polygon([(cx,cy)]+[(cx-11*math.cos(a),cy+11*math.sin(a)) for a in t]))
    return unary_union(parts)
def place(g,une,v0,th):
    from shapely import affinity
    g=affinity.rotate(g,th,origin=(0,0))
    return transform(lambda x,y,z=None:(A[0]+(une-x)*uh[0]+(v0+y)*vh[0], A[1]+(une-x)*uh[1]+(v0+y)*vh[1]), g)
for L in (34.8,):
    g=fp(L); best=None
    for th in np.arange(-6,6.1,0.5):
        for une in np.arange(86,96,0.25):
            for v0 in np.arange(0,6,0.25):
                p=place(g,une,v0,th)
                c=free.exterior.distance(p) if free.contains(p) else -p.difference(free).area
                if best is None or c>best[0]: best=(round(c,2),th,une,v0)
    print('L=',L,'best clearance',best)
