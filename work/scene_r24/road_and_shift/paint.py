"""Bake the Blender-projected wear mask into the two existing terrain materials."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFilter
here=Path(__file__).resolve().parent
out=here.parents[1]/'project/chongqing_godot_v05/assets/courtyard_grade/footwear.png'
image=Image.new('L',(1024,512))
drawing=ImageDraw.Draw(image)
for ring in json.loads((here/'paint_polygons.json').read_text('utf8')):
    drawing.polygon([((x+78)*16,(z-5)*16) for x,z in ring],fill=255)
image.filter(ImageFilter.GaussianBlur(1.2)).save(out)
