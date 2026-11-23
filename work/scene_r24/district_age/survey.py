"""Public road sections, terrain coverage and old residential walls in the editable district."""
import json, math, sys
from pathlib import Path
from collections import Counter
import bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
work=here.parents[1]
sys.path[:0]=[str(here.parent/'stair_neighborhood'),str(work/'project/chongqing_blender_v05')]
from site_neighborhood import scene, Surfaces, extent, visible_ground
from district_layout import DATA,SUPPLEMENTAL,road_width,clip_line
def dump(file,data):
    (here/file).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),'utf8')
def surface(o):
    if o.type!='MESH' or o.hide_render or not len(o.data.polygons):return False
    name=o.name
    return visible_ground(o) or name.startswith(('COL_R24_Median_R24_median_', 'COL_R24_Verge','COL_Yard20_CornerSurface','COL_East17_','COL_N13_StairFoundations','COL_D18_NanquShoulder','COL_D18_','COL_R17_Stair','COL_Stairs','COL_Stair_','COL_R24_Approach','COL_Circulation')) and not any(s in name.lower() for s in ('rail','door','kitchen','shelf','room','window','hook','banister'))
road_objects=[o for o in scene.objects if surface(o)]
road=Surfaces(road_objects)
def run():
    roofs={}
    houses={}
    for o in scene.objects:
        if o.type!='MESH' or o.hide_render:continue
        name=o.name
        if name.startswith(('COL_B_','COLH_B_')) or any(s in name.lower() for s in ('bicycl','bike_shed','cycleframe','cycle_frame','bikerack','cycle_rack','unit_door','entrance_door')):
            houses[name]=extent(o)
    dump('inventory.json',{'residences':houses,'ground':{o.name:extent(o) for o in road_objects}})
    routes=[];samples=[];alerts=[];used=Counter()
    specs=[(str(item['id']),seg,road_width(item)) for item in DATA['roads']+DATA['paths'] for seg in clip_line(item['points'])]
    routes_local=list(SUPPLEMENTAL)
    if phase=='after':
        way=json.loads((work/'project/chongqing_godot_v05/assets/district_age/west_passage.json').read_text())
        eastern=json.loads((work/'project/chongqing_godot_v05/assets/district_age/east_passage.json').read_text())
        bend=json.loads((work/'project/chongqing_godot_v05/assets/district_age/blue_block_bend.json').read_text())
        for i,(key,line,width) in enumerate(specs):
            if key=='1328811309':specs[i]=(key,json.loads((work/'project/chongqing_godot_v05/assets/district_age/wall_side_passage.json').read_text())+line[2:],width)
            if key=='734116595':specs[i]=(key,line[:-1]+bend+[line[-1]],width)
        for idx,(name,line,width) in enumerate(routes_local):
            if name=='East photo alley':routes_local[idx]=(name,line[:3]+eastern+line[-1:],width)
            if name=='West residential link':routes_local[idx]=(name,line[:4]+way+line[4:-1]+json.loads((work/'project/chongqing_godot_v05/assets/district_age/west_north_end.json').read_text()),width)
    specs+=routes_local
    for index,(key,line,width) in enumerate(specs):
        first=len(samples);last={}
        for a,b in zip(line,line[1:]):
            run=math.dist(a,b)
            if run<.02:continue
            nx=-(b[1]-a[1])/run;ny=(b[0]-a[0])/run
            intervals=math.ceil(run/.45)
            for i in range(intervals+1):
                t=i/intervals
                for lane,offset in enumerate((-.43*width,0,.43*width)):
                    x=a[0]+t*(b[0]-a[0])+nx*offset;y=a[1]+t*(b[1]-a[1])+ny*offset
                    if abs(x)>100 or abs(y)>100:continue
                    hits=road.down(x,y,75,90)
                    # Retain every distinct support elevation. This preserves bridges and underpasses.
                    levels=[[round(h,4),n] for h,n,_ in hits]
                    z=levels[0][0] if levels else None
                    samples.append([index,lane,round(x,3),round(y,3),levels])
                    if levels:used[levels[0][1]]+=1
                    if lane in last and z is not None and last[lane][2] is not None:
                        px,py,pz=last[lane];d=math.hypot(x-px,y-py)
                        if .03<d<.55 and abs(z-pz)>.25:alerts.append([index,lane,round(x,2),round(y,2),round(z-pz,3),levels[0][1]])
                    if z is None:alerts.append([index,lane,x,y,None,'no source floor'])
                    last[lane]=(x,y,z)
        routes.append([key,len(samples)-first,round(sum(math.dist(a,b) for a,b in zip(line,line[1:])),2),width])
    grid=[]
    for y in range(-99,100,2):
        for x in range(-99,100,2):
            rows=road.down(x,y,75,95)
            grid.append([x,y,[[round(h,3),n] for h,n,_ in rows]])
    dump('survey_'+phase+'.json',{'routes':routes,'samples':samples,'grid':grid,'step_candidates':alerts,'sampled_surfaces':used})
    print('SURVEY',phase,len(routes),len(samples),len(grid),len(alerts),len(road_objects),flush=True)
phase='after' if '--after' in sys.argv or bpy.context.scene.get('street_revision','').startswith('R24 residential') else 'before'
if __name__=='__main__':run()
