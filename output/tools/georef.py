import json,math,sys
import numpy as np
from PIL import Image,ImageDraw
LAT0,LON0=43.1925,76.9880
kx=111320*math.cos(math.radians(LAT0)); ky=110540
def P(p): return ((p[0]-LON0)*kx,(p[1]-LAT0)*ky)
def fit(pairs):
    # pairs: [(px,py,X,Y)] -> affine world->pixel
    A=[];b=[]
    for px,py,X,Y in pairs:
        A.append([X,Y,1,0,0,0]);b.append(px)
        A.append([0,0,0,X,Y,1]);b.append(py)
    sol,res,_,_=np.linalg.lstsq(np.array(A),np.array(b),rcond=None)
    M=sol.reshape(2,3)
    err=[ (np.hypot(*(M@[X,Y,1]-[px,py]))) for px,py,X,Y in pairs]
    return M,err
def overlay(img,M,d,out):
    im=Image.open(img).convert('RGB'); dr=ImageDraw.Draw(im)
    for w in d['ways']:
        t=w['tags']
        if t.get('waterway')=='river' or t.get('power') or t.get('highway')=='secondary':
            pts=[tuple(M@[*P(p),1]) for p in w['pts']]
            col=(0,0,255) if 'waterway' in t else (255,0,0) if t.get('power') else (0,160,0)
            dr.line(pts,fill=col,width=2)
    im.save(out,quality=90)
if __name__=='__main__':
    d=json.load(open(sys.argv[1]))
    pairs=json.loads(sys.argv[4])
    M,err=fit(pairs)
    print('M=',M.tolist()); print('err px',[round(e,1) for e in err])
    sc=math.sqrt(abs(np.linalg.det(M[:,:2]))); print('px per m',sc)
    overlay(sys.argv[2],M,d,sys.argv[3])
    json.dump(M.tolist(),open(sys.argv[3]+'.M.json','w'))
