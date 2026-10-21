import sys
from gf import build_gf
from drawplan import plan
from render import Sheet
lv=build_gf()
S=Sheet(-6,-8,93,30,scale=150)
plan(S,lv)
S.save(sys.argv[1],dpi=110)
