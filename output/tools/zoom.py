import sys
from importlib import import_module
from drawplan import plan
from render import Sheet
mod,fn,out,x0,y0,x1,y1=sys.argv[1],sys.argv[2],sys.argv[3],*map(float,sys.argv[4:8])
lv=getattr(import_module(mod),fn)()
S=Sheet(x0,y0,x1,y1,scale=float(sys.argv[8]) if len(sys.argv)>8 else 60)
plan(S,lv)
S.save(out,dpi=110)
