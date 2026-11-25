"""Reopen the outer source and compare each plinth underside with the finished terrain."""
import bpy,json,os
from pathlib import Path
from math import sin,cos,ceil
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent;game=here.parents[1]/"project/chongqing_godot_v05"
plots=json.loads((game/"assets/district_500/layout.json").read_text(encoding="utf-8"))["plots"]
def surface(items):
    verts=[];faces=[]
    for obj in items:
        base=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(base+i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(verts,faces)
ground=surface([ob for ob in bpy.context.scene.objects if ob.name.startswith("COL_Outer500_Surface_")])
base=surface([bpy.data.objects["COL_Outer500_Building_envelopes"]])
rows=[];gaps=[];n=0;missing=[]
for p in plots:
    c,s=cos(p["bearing"]),sin(p["bearing"]);x0,y0=p["east_north"];w,d=p["width"]*.5-.022,p["depth"]*.5-.022
    corners=[(-w,-d),(w,-d),(w,d),(-w,d)]
    samples=[]
    for (ax,ay),(bx,by) in zip(corners,corners[1:]+corners[:1]):
        steps=ceil(max(abs(bx-ax),abs(by-ay))/.40)
        for j in range(steps):
            t=j/steps;u=ax+(bx-ax)*t;v=ay+(by-ay)*t
            x=x0+c*u-s*v;y=y0+s*u+c*v
            terrain=ground.ray_cast((x,y,p["roof"]+10),(0,0,-1))[0]
            bottom=base.ray_cast((x,y,-120),(0,0,1))[0]
            if terrain is None or bottom is None:missing.append([p["plot_id"],x,y]);continue
            delta=bottom.z-terrain.z;n+=1;samples.append(delta)
            if delta>.025:gaps.append([p["plot_id"],round(u,3),round(v,3),round(delta,3)])
    rows.append({"plot":p["plot_id"],"max_separation_m":round(max(samples),4) if samples else None})
result={"blender":bpy.app.version_string,"samples":n,"plots":rows,"positive_gaps_over_25mm":gaps,"missing":missing}
out=Path(os.environ["CQ_QA_DIR"]);(out/"plinths.json").write_text(json.dumps(result,indent=2)+"\n")
print("STREET_PLINTHS",n,len(gaps),len(missing),max(r["max_separation_m"] for r in rows))
