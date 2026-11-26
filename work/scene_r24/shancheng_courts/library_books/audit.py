"""Inspect saved book meshes, UV plates and packed materials in the reopened Blender source."""
from hashlib import sha256
from pathlib import Path
import bpy
import numpy as np

def audit():
    folder=Path(__file__).resolve().parent
    result={}
    for name in ["Case_1","Case_2","Case_3","DisplayTables"]:
        obj=bpy.data.objects["Court_Jinma_Books_"+name]
        geo=obj.data
        num=int(obj["volumes"])
        expected=[("jackets.jpg","Base Color"),("cut_paper.png","Base Color")]
        if name=="DisplayTables":expected.append(("reading_spread.jpg","Base Color"))
        for i,(filename,socket) in enumerate(expected):
            shader=geo.materials[i].node_tree.nodes.get("Principled BSDF")
            image=shader.inputs[socket].links[0].from_node.image
            assert image.packed_file and sha256(image.packed_file.data).digest()==sha256((folder/filename).read_bytes()).digest()
        rough=geo.materials[0].node_tree.nodes.get("Principled BSDF").inputs["Roughness"].links[0].from_node.image
        assert rough.packed_file and rough.colorspace_settings.name=="Non-Color"
        assert sha256(rough.packed_file.data).digest()==sha256((folder/"binding_roughness.png").read_bytes()).digest()
        coords=np.empty(len(geo.loops)*2,dtype=np.float32)
        geo.uv_layers.active.data.foreach_get("uv",coords)
        uv=coords.reshape((-1,2))
        polys=np.asarray([list(poly.loop_indices) for poly in geo.polygons])
        slots=np.array([p.material_index for p in geo.polygons])
        wrap=uv[polys[slots==0]]
        tiles=np.floor(np.column_stack([wrap[:,:,0].mean(axis=1),1-wrap[:,:,1].mean(axis=1)])*8).astype(int)
        unique=len(np.unique(tiles,axis=0))
        assert np.isfinite(uv).all() and (uv>=0).all() and (uv<=1).all()
        quad_span=wrap.max(axis=1)-wrap.min(axis=1)
        # A full-height printed cover, four continuous spine strips and three
        # exposed paper cuts must survive the source save. The reading spread is audited separately.
        closed=num-(name=="DisplayTables")
        full_cover=(quad_span[:,0]>.045)&(quad_span[:,1]>.11)
        spine=(quad_span[:,0]>.0035)&(quad_span[:,0]<.0038)&(quad_span[:,1]>.115)
        assert full_cover.sum()>=closed*2 and spine.sum()==4*closed and (slots==1).sum()>=closed*3
        if name.startswith("Case"):
            assert unique==64 and num>0
        else:
            assert (slots==2).sum()==10
        result[name]={"volumes":num,"printed_plate_cells":unique,"full_cover_faces":int(full_cover.sum()),
                      "rounded_spine_strips":int(spine.sum()),"paper_faces":int((slots==1).sum())}
    return result
