"""Reuse packed CC0 household scans from the editable v05 donor library."""
from math import cos,sin,pi
from mathutils import Matrix, Vector
import bpy


def place(library,plots,world,basket_library):
    keys={"plant":"potted_plant_02","chair":"plastic_monobloc_chair_01",
          "crate":"plastic_crate_01","table":"chinese_tea_table","armchair":"chinese_armchair"}
    with bpy.data.libraries.load(str(library),link=False) as (source,draft):
        draft.objects=[n for n in source.objects if any(n.startswith("PH_"+value+"_base_") for value in keys.values())]
    donors={k:[o for o in draft.objects if o.name.startswith("PH_"+value+"_base_")] for k,value in keys.items()}
    existing=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(basket_library))
    imported=set(bpy.data.objects)-existing
    basket=next(o for o in imported if o.name=="Court14_BackBasket")
    greens=next(o for o in imported if o.name=="Court14_BasketGreens")
    verts=[basket.matrix_world @ vertex.co for vertex in basket.data.vertices]
    center=Vector(((min(v.x for v in verts)+max(v.x for v in verts))/2,
                   (min(v.y for v in verts)+max(v.y for v in verts))/2,min(v.z for v in verts)))
    basket_origin=Matrix.Translation(-center)
    donors["basket"]=[basket,greens]
    keys["basket"]="Court14_BackBasket_and_greens"
    records=[]
    def item(p,key,u,v,h,yaw=0,scale=1.0):
        x,y=world(p,u,v); z=p["height"]+h
        matrix=Matrix.Translation((x,y,z)) @ Matrix.Rotation(p["bearing"]+yaw,4,"Z") @ Matrix.Scale(scale,4)
        index=len(records)
        for j,source in enumerate(donors[key]):
            obj=bpy.data.objects.new("Outer500_Household_%03d_%s_%d"%(index,key,j),source.data)
            bpy.context.scene.collection.objects.link(obj)
            local=basket_origin @ source.matrix_world if key=="basket" else source.matrix_world
            obj.matrix_world=matrix @ local
        records.append({"asset":keys[key],"origin":[x,y,z],"plot":p["plot_id"],"scale":scale,"yaw":p["bearing"]+yaw})
    for p in plots:
        back=p["depth"]/2; front=-back
        if p.get("room"):
            r=p["room"];side=1 if p["door_u"]<0 else -1
            if p["kind"]%2==0:
                item(p,"chair",r["inside_u"]+side*.35,back-1.90,.035,p["bearing"]*.13+.48,.89)
            else:
                item(p,"crate",r["inside_u"]+side*.64,back-1.22,.035,.10,1.2)
        if p.get("court"):
            c=p["court"]; k=c["stair_side"]; center=c["center_u"]; w=c["half_width"]
            for lo,hi in ((-w+.28,.30),(.30,w-.22)):
                item(p,"basket",center+k*(hi-.59),back+9.38,c["upper_m"],-.76,1.16)
                item(p,"armchair",center+k*(hi-1.32),back+9.31,c["upper_m"],(-1 if k>0 else 1)*.67,.86)
            item(p,"plant",center+k*(-w+1.30),back+4.49,.09,1.20,1.18)
            item(p,"plant",center+k*(-w+.70),back+5.90,.68,-.77,.69)
            item(p,"plant",center+k*(-w+1.46),c["landing_v"]+.22,c["upper_m"],.26,.82)
            item(p,"chair",center+k*(-w+1.64),back+6.08,.09,k*.80,.97)
            if p["name"]:
                item(p,"crate",center+k*1.95,back+7.45,.09,.11,1.26)
                item(p,"plant",center+k*2.85,back+7.32,.09,-.53,.89)
        if p["name"].endswith("茶摊"):
            for x,y,turn in ((1.12,front+1.92,.12),(-4.30,front+5.60,-.32)):
                item(p,"table",x,y,.035,turn,1.08)
                item(p,"armchair",x-.85,y+.15,.035,turn-pi/2,.92)
                item(p,"chair",x+.83,y+.12,.035,turn+pi/2,1.0)
        if p["name"].endswith("市场"):
            for u,v in ((p["door_u"]-2.38,-.94),(p["door_u"]-2.38,.03),(p["door_u"]-2.38,1.00)):
                item(p,"basket",u,v,.76,v*.76,1.48)
            for x,y in ((-4.22,front+.82),(-4.48,front+1.48),(4.78,front+.75),(5.20,front+.66)):
                item(p,"crate",x,y,.035,-.21,1.55)
            item(p,"crate",-4.48,front+1.48,.035+.264*1.55,-.21,1.50)
            item(p,"chair",3.62,front+2.29,.035,.38,.91)
        if p["name"].endswith("修理铺"):
            item(p,"chair",-2.15,front+.95,.035,-.7)
            for j in range(3):
                item(p,"crate",4.15+j*.64,front+1.25,.035,j*.1,1.35)
    for obj in imported | set(draft.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    return records
