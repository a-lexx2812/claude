import sys
from roof import build_roof, draw_roof, ROOF_LEGEND, ROOF_NOTES
from sheets import compose_plan
mode = sys.argv[3] if len(sys.argv) > 3 else 'docx'
compose_plan(build_roof(), sys.argv[1], scale=400 if mode == 'docx' else 100, dpi=int(sys.argv[2]), mode=mode,
             extra=draw_roof, rows=ROOF_LEGEND, notes=ROOF_NOTES,
             subtitle=None)
