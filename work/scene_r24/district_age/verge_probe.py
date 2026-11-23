from pathlib import Path
import sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
def mark(x,y):
 h=road.down(x,y,16,12)
 if not h:return '-'
 n=h[0][1];return 'S' if n.startswith('COL_D18') else 'R' if 'asphalt' in n else 'C' if 'curb' in n.lower() else 'P' if 'pavement' in n else '+'
for y in [-78.5-i*.12 for i in range(39)]:print('VERGE',round(y,2),''.join(mark(22+i*.2,y) for i in range(56)))
for x in range(12,41):
 p=[y*.02 for y in range(-4250,-3850) if mark(x,y*.02)=='-']
 if p:print('SLOT',x,min(p),max(p))
