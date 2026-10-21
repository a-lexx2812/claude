from geo import *
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import affinity
import numpy as np, math, itertools
free=Polygon([(-54.8,-9.3),(20.0,50.3),(52.0,3.7),(10.6,-47.1),(-33.8,-29.0)])
def footprint(art_inline=True):
    parts=[box(0,0,33.6,11.4),box(15.6,11.4,33.6,16.8),box(33.6,3.0,57.0,16.8),box(57.0,5.4,64.2,12.6),box(64.2,0.6,85.8,18.0)]
    if art_inline:
        parts.append(box(85.8,0.6,97.8,7.8))
        t=np.linspace(0,math.pi/2,30); parts.append(Polygon([(85.8,7.8)]+[(85.8+12*math.cos(a),7.8+12*math.sin(a)) for a in t]))
    return unary_union(parts)
A=np.array((-54.8,-9.3)); B=np.array((20.0,50.3)); uh=(B-A)/np.linalg.norm(B-A); vh=np.array((uh[1],-uh[0]))
def place(fp,une,v0,th):
    # plan x -> -u, plan y -> +v ; rotate by th (deg) about NE corner
    g=affinity.rotate(fp,th,origin=(0,0))
    def tr(x,y,z=None):
        u=une-x; v=v0+y
        P=A+u*uh+v*vh
        return P
    from shapely.ops import transform
    return transform(lambda x,y,z=None:(A[0]+(une-x)*uh[0]+(v0+y)*vh[0], A[1]+(une-x)*uh[1]+(v0+y)*vh[1]), g)
def clearance(g):
    if not free.contains(g): 
        return -g.difference(free).area
    return free.exterior.distance(g)
for inline in (True,False):
    fp=footprint(inline); best=None
    for th in np.arange(-12,12.1,1):
        for une in np.arange(85,100,0.5):
            for v0 in np.arange(0,20,0.5):
                c=clearance(place(fp,une,v0,th))
                if best is None or c>best[0]: best=(c,th,une,v0)
    print('inline' if inline else 'no artists',best)
