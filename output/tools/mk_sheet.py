import sys
from importlib import import_module
from sheets import compose_plan
mod, fn, out = sys.argv[1:4]
dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 300
mode = sys.argv[5] if len(sys.argv) > 5 else 'docx'
lv = getattr(import_module(mod), fn)()
compose_plan(lv, out, scale=400 if mode == 'docx' else 100, dpi=dpi, mode=mode)
