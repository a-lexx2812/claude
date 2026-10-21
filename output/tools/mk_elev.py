import sys
from elev import elevation
elevation(sys.argv[1], sys.argv[2], dpi=int(sys.argv[3]) if len(sys.argv) > 3 else 250)
