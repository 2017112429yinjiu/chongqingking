from pathlib import Path
import sys,json,bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import here,road,save
district=json.loads((here.parent/'district_age/road_queries.json').read_text())
ax=Vector((.8258,-.4863)).normalized();up=Vector((-ax.y,ax.x));start=Vector((-29.669,86.431))
out=[]
for key in ['sections','ground_grid']:
    for i,row in enumerate(district[key]):
        x,z,h=row[2:5] if key=='sections' else row[:3]
        if h is None:continue
        p=Vector((x,-z))-start
        if not 3.5<p.dot(ax)<17.5 or not -9.0<p.dot(up)<5.5:continue
        floors=road.down(x,-z,h+1.5,3.)
        assert floors,(key,i,row)
        out.append([key,i,x,z,h,floors[0][0],floors[0][1]])
save('north_controls.json',out)
print('NORTH_SOURCE_CONTROLS',len(out),max(abs(r[4]-r[5]) for r in out))
