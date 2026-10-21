import json,math,sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.load(open(sys.argv[1]))
LAT0,LON0=43.1925,76.9880
kx=111320*math.cos(math.radians(LAT0)); ky=110540
def P(p): return ((p[0]-LON0)*kx,(p[1]-LAT0)*ky)
fig,ax=plt.subplots(figsize=(14,14))
for w in d['ways']:
    tg=w['tags']; pts=[P(p) for p in w['pts']]
    if not pts: continue
    xs,ys=zip(*pts)
    if 'waterway' in tg and tg['waterway']=='river': ax.plot(xs,ys,'b-',lw=2); ax.text(xs[len(xs)//2],ys[len(ys)//2],tg.get('name','')+' '+w['id'],color='b',fontsize=7,clip_on=True)
    elif tg.get('power')=='line': ax.plot(xs,ys,'r-.',lw=2); [ax.plot(x,y,'rs') for x,y in pts]
    elif tg.get('power')=='substation': ax.fill(xs,ys,color='salmon',alpha=.6)
    elif 'building' in tg: ax.fill(xs,ys,color='tan')
    elif tg.get('natural')=='wood': ax.fill(xs,ys,color='green',alpha=.15)
    elif 'highway' in tg:
        lw={'secondary':3,'residential':1.5}.get(tg['highway'],0.7); ax.plot(xs,ys,'k-',lw=lw,alpha=.7)
        if tg.get('bridge'): ax.plot(xs,ys,'m-',lw=3)
    elif tg.get('landuse') or tg.get('leisure'): ax.plot(xs,ys,'g--',lw=.8); ax.text(xs[0],ys[0],tg.get('landuse',tg.get('leisure')),fontsize=6,clip_on=True)
for k,(p,v) in d['ntags'].items():
    if v.get('highway')=='bus_stop' or v.get('public_transport'):
        x,y=P(p); ax.plot(x,y,'ko'); ax.text(x,y,v.get('name',''),fontsize=7,clip_on=True)
ax.set_aspect('equal'); ax.grid(True,alpha=.3)
ax.set_xlim(float(sys.argv[3]),float(sys.argv[4])); ax.set_ylim(float(sys.argv[5]),float(sys.argv[6]))
plt.savefig(sys.argv[2],dpi=80,bbox_inches='tight')
