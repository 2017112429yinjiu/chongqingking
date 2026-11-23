from pathlib import Path
import sys,json,math,bpy
here=Path(__file__).resolve().parent
work=here.parents[1]
game=work/'project/chongqing_godot_v05'
sys.path.insert(0,str(here.parent/'district_age'))
from survey import scene,road,road_objects,Surfaces,extent
def save(name,value): (here/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),'utf8')
def sample(x,y):
    hits=road.down(x,y,32,33)
    return hits[0][0] if hits else None
