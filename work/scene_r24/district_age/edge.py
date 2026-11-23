from pathlib import Path
import sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
obs=[o for o in road_objects if not o.name.startswith('COL_D18_')]
surf=Surfaces(obs)
seen=[]
for x in [46.99,47.001,47.05,47.2,47.6,48.5,50,55,59]:
    print('X',x)
    for y in [-78,-77,-76.8,-76.6,-76.2,-76,-75.6,-75.2,-74.8,-74.4,-74,-73.6,-73.2,-72.8,-72.4,-72,-71.6,-71.2,-70.8,-70,-69.3,-68.8]:
        rows=surf.down(x,y,15,9);seen.append([x,y,[[round(k,3),n] for k,n,_ in rows]])
dump('edge.json',seen)
