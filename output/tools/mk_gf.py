import sys
from gf import build_gf
from sheets import compose_plan
lv=build_gf()
compose_plan(lv, sys.argv[1], scale=400, dpi=int(sys.argv[2]) if len(sys.argv)>2 else 300)
