"""Surface finishes inside the former school, in the window, doorway and stair views."""
from math import ceil, floor
from pathlib import Path
from runpy import run_path
import bpy
import numpy as np

here=Path(__file__).resolve().parent
assets=here.parents[3]/"work/project/chongqing_godot_v05/assets"

def materials(mats):
    def load(path,scalar=False):
        image=bpy.data.images.load(str(path),check_existing=True)
        if scalar:image.colorspace_settings.name="Non-Color"
        if not image.packed_file:image.pack()
        return image
    def surface(name,colour,scan,scale,tint=(1,1,1)):
        mat=bpy.data.materials.new("Jinma "+name)
        mat.use_nodes=True
        nodes=mat.node_tree.nodes
        link=mat.node_tree.links.new
        bsdf=nodes.get("Principled BSDF")
        def texture(image):
            t=nodes.new("ShaderNodeTexImage")
            t.image=image
            return t.outputs["Color"]
        rgb=texture(load(here/(colour+".jpg")))
        if tint!=(1,1,1):
            mix=nodes.new("ShaderNodeMix")
            mix.data_type="RGBA";mix.blend_type="MULTIPLY";mix.inputs[0].default_value=1.
            mix.inputs[7].default_value=(*tint,1.)
            link(rgb,mix.inputs[6]);rgb=mix.outputs[2]
        link(rgb,bsdf.inputs["Base Color"])
        prefix="chongqing_district_"+scan
        size="1k" if scan=="plastered_wall_04" else "2k"
        normal=nodes.new("ShaderNodeNormalMap")
        normal.inputs["Strength"].default_value=scale
        link(texture(load(assets/(prefix+"_nor_gl_"+size+".jpg"),True)),normal.inputs["Color"])
        link(normal.outputs["Normal"],bsdf.inputs["Normal"])
        # The existing game scans store roughness in G; R and B are solid white.
        channels=nodes.new("ShaderNodeSeparateColor")
        link(texture(load(assets/(prefix+"_rough_"+size+".png"),True)),channels.inputs["Color"])
        link(channels.outputs["Green"],bsdf.inputs["Roughness"])
        mats.append(mat)
        return len(mats)-1
    lime=surface("ivory limewash","school_lime","plastered_wall_04",.19)
    skirt=surface("aged teal passage paint","school_passage","plastered_wall_04",.24)
    floor_mat=surface("warm worn school floor","school_screed","concrete_floor_worn_001",.18)
    plank=surface("exposed floorboards","school_pine","wood_table_worn",.27)
    joist=surface("old fir joists","school_pine","wood_table_worn",.31,(.75,.72,.69))
    case=surface("amber shellac shelving","school_pine","wood_table_worn",.24,(.78,.43,.28))
    return dict(lime=lime,skirt=skirt,floor=floor_mat,plank=plank,joist=joist,case=case)

def coat(mesh,start,p0,p1,upper,lower=None,cut=None):
    # Retain the collision boundary. Split only the existing inward-facing
    # polygon at the actual paint line, including the faces below the sills.
    a,b=np.asarray(p0)[:2],np.asarray(p1)[:2]
    v=b-a
    normal=np.array([-v[1],v[0]])/np.linalg.norm(v)
    def clipped(points,above):
        result=[]
        for p,q in zip(points,points[1:]+points[:1]):
            if (p[2]>=cut if above else p[2]<=cut):result.append(p)
            if min(p[2],q[2])<cut<max(p[2],q[2]):
                result.append(p+(q-p)*((cut-p[2])/(q[2]-p[2])))
        return result
    for i in range(start,len(mesh.faces)):
        points=[np.array(mesh.vertices[k]) for k in mesh.faces[i]]
        if not all(abs((p[:2]-a)@normal)<.0001 for p in points):continue
        mesh.slots[i]=upper
        if lower is None:continue
        heights=[p[2] for p in points]
        if max(heights)<=cut:mesh.slots[i]=lower
        elif min(heights)<cut:
            high=clipped(points,True)
            mesh.faces[i]=tuple(range(len(mesh.vertices),len(mesh.vertices)+len(high)))
            mesh.vertices.extend(tuple(p) for p in high)
            mesh.face(clipped(points,False),lower)

def underside(point,rectangles,span,storey,mats,slots):
    """Run boards and joists across existing floor panels. Leave the stairwell open."""
    Batch=run_path(str(here/"mesh.py"))["Batch"]
    deck=Batch("Court_Jinma_Story_Exposed_Deck",point)
    # The joists bear on the existing longitudinal beams; board ends fall on joists.
    spacing=span/39
    z=storey-.115
    for left,right,front,back in rectangles:
        for row in range(floor(front/.205),ceil(back/.205)):
            y0=max(front,row*.205)+.0014;y1=min(back,(row+1)*.205)-.0014
            if y1-y0<.008:continue
            offset=row%4
            for j in range(floor((left/spacing-offset)/5),ceil((right/spacing-offset)/5)):
                x0=max(left,(j*5+offset)*spacing)+.0015
                x1=min(right,((j+1)*5+offset)*spacing)-.0015
                if x1-x0<.009:continue
                shift=((row*17+j*31)%89)/89
                def face(points):
                    deck.face(points,mats[slots["plank"]],[(x*.45+shift,row*.331+(y-y0)*1.04) for x,y,h in points])
                # A narrow chamfer catches grazing light at each board edge.
                face([(x0,y0+.0018,z-.012),(x0,y1-.0018,z-.012),
                      (x1,y1-.0018,z-.012),(x1,y0+.0018,z-.012)])
                face([(x0,y0,z-.009),(x0,y0+.0018,z-.012),(x1,y0+.0018,z-.012),(x1,y0,z-.009)])
                face([(x0,y1-.0018,z-.012),(x0,y1,z-.009),(x1,y1,z-.009),(x1,y1-.0018,z-.012)])
        for j in range(ceil(left/spacing),ceil(right/spacing)):
            if j%6==0:continue  # Existing primary crossbeams at every second window bay.
            x=j*spacing
            if x-.042<left or x+.042>right:continue
            deck.board(x,(back+front)/2,z-.145,.084,back-front,.133,mats[slots["joist"]],.005)
    return deck.save()

def daylight(point,span):
    # Local diffuse bounce from the window row; falloff is limited to the classroom.
    for i,x in enumerate((7.7*span/13,9.1*span/13),1):
        light=bpy.data.lights.new("Story window bounce %d"%i,"POINT")
        light.energy=22
        light.color=(1.,.955,.88)
        light.shadow_soft_size=.57
        light.use_custom_distance=True
        light.cutoff_distance=5.8
        obj=bpy.data.objects.new(light.name,light)
        bpy.context.collection.objects.link(obj)
        obj.location=point(x,1.30,2.18)
