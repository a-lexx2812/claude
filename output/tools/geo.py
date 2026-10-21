import json,math
import numpy as np
from shapely.geometry import LineString,Polygon,Point
S='/tmp/claude-0/-home-user-claude/e690d7fc-d415-569f-ba67-842ee1fc8f35/scratchpad/arch'
LAT0,LON0=43.1925,76.9880
kx=111320*math.cos(math.radians(LAT0)); ky=110540
def P(p): return ((p[0]-LON0)*kx,(p[1]-LAT0)*ky)
D=json.load(open(S+'/osm/map1.json'))
def way(i): 
    for w in D['ways']:
        if w['id']==str(i): return [P(p) for p in w['pts']]
M7=np.array(json.load(open(S+'/osm/ov_007.jpg.M.json')))
def px2w(M,pts):
    A=M[:,:2]; t=M[:,2]; Ai=np.linalg.inv(A)
    return [tuple(Ai@(np.array(p)-t)) for p in pts]
KA=LineString(way(551742158)); KA2=LineString(way(1086143001)); ES=LineString(way(238131928)); LINE=LineString(way(1472225044)[3:])
SUB=Polygon(way(1103833382))
