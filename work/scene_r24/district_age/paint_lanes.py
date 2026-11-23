import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
here=Path(__file__).resolve().parent
tiles=Image.new('L',(2048,2048));brush=ImageDraw.Draw(tiles)
for ring in json.loads((here/'wear.json').read_text()):
    brush.polygon([((x+100)*10.24,(z+100)*10.24) for x,z in ring],fill=235)
from PIL import ImageChops
route=json.loads((here.parents[1]/'project/chongqing_godot_v05/assets/district_age/west_passage.json').read_text())
points=[((x+100)*10.24,(100-y)*10.24) for x,y in route]
brush.line(points,fill=235,width=26,joint='curve')
east=json.loads((here.parents[1]/'project/chongqing_godot_v05/assets/district_age/east_passage.json').read_text())
brush.line([((x+100)*10.24,(100-y)*10.24) for x,y in east],fill=235,width=24,joint='curve')
tail=json.loads((here.parents[1]/'project/chongqing_godot_v05/assets/district_age/west_north_end.json').read_text())
brush.line([((x+100)*10.24,(100-y)*10.24) for x,y in tail],fill=220,width=24,joint='curve')
yard=json.loads((here.parents[1]/'project/chongqing_godot_v05/assets/district_age/wall_side_passage.json').read_text())
brush.line([((x+100)*10.24,(100-y)*10.24) for x,y in yard],fill=225,width=20,joint='curve')
for x,y in points:brush.ellipse((x-13,y-13,x+13,y+13),fill=235)
tiles.filter(ImageFilter.GaussianBlur(2.7)).save(here.parents[1]/'project/chongqing_godot_v05/assets/district_age/footpaths.png')
