"""Reopen the scene and measure surfaces carrying the photographed collection."""
from pathlib import Path
from hashlib import sha256
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

def audit(school):
    a,b,c,d=np.asarray(school["ring"])
    length=np.linalg.norm(b-a)
    depth=(np.linalg.norm(d-a)+np.linalg.norm(c-b))/2
    floor=school["floor"]
    def xy(x,y):
        u,v=x/length,y/depth
        return ((1-u)*a+u*b)*(1-v)+((1-u)*d+u*c)*v
    deps=bpy.context.evaluated_depsgraph_get()
    def tree(name):
        return BVHTree.FromObject(bpy.data.objects[name],deps)
    def height(surface,x,y,start):
        pt=surface.ray_cast((*xy(x,y),floor+start),(0,0,-1),2)[0]
        assert pt is not None,(x,y,start)
        return float(pt.z-floor)
    frame=tree("COL_Court_Jinma_Story_Furniture")
    glazing=tree("Court_Jinma_Story_Glass")
    pavement=tree("COL_Court_jinma_classrooms")
    heights={}
    for name,surface,x,y,h in (
            ("joined_desk_1",frame,19.22,2.46,.769),("joined_desk_2",frame,21.45,2.40,.769),
            ("bench_1",frame,19.75,3.115,.429),("bench_2",frame,21.41,3.115,.429),
            ("window_desk",frame,21.8,.62,.776),("fare_box_stand",frame,8*length/13,.693,.933),
            ("window_case_glass",glazing,23.40,.735,1.192)):
        z=height(surface,x,y,h+.10)
        assert abs(z-h)<.006,(name,z,h)
        heights[name]=round(z,4)
    feet=[]
    for x in (19.85,21.41):
        for end in (-1,1):
            for side in (-1,1):
                u,v=x+end*(1.556/2-.068),2.44+side*(.77/2-.057)
                p=frame.ray_cast((*xy(u,v),floor-.016),(0,0,1),.04)[0]
                assert p is not None,(u,v)
                gap=p.z-floor-height(pavement,u,v,.06)
                assert abs(gap)<.004,gap
                feet.append(round(gap,4))
    # Probe all four case posts at the supporting desktop, below the case base.
    corners=[height(frame,23.40+u,.735+v,.789) for u in (-.251,.251) for v in (-.179,.179)]
    assert all(abs(z-.776)<.004 for z in corners),corners
    detail=bpy.data.objects["Court_Jinma_Story_Collection"]
    mat=next(m for m in detail.data.materials if m.name.startswith("Story hall Original printed"))
    image=next(n.image for n in mat.node_tree.nodes if n.type=="TEX_IMAGE")
    atlas=Path(__file__).with_name("printwork.jpg").read_bytes()
    assert image.packed_file and sha256(image.packed_file.data).digest()==sha256(atlas).digest()
    tiles=set()
    for obj in (detail,bpy.data.objects["COL_Court_Jinma_Story_Furniture"]):
        mesh=obj.data
        slot=mesh.materials.find(mat.name)
        uv=mesh.uv_layers.active.data
        for face in mesh.polygons:
            if face.material_index!=slot:continue
            u,v=np.mean([uv[i].uv[:] for i in face.loop_indices],axis=0)
            tiles.add(int(4*u)+(3-int(4*v))*4)
    assert tiles==set(range(16)),tiles
    return {"heights_above_floor_m":heights,"desk_foot_gaps_m":feet,
            "support_below_four_glass_case_posts_m":[round(z,4) for z in corners],
            "original_print_tiles_used":sorted(tiles),"packed_printwork_sha256":sha256(atlas).hexdigest()}
