from pathlib import Path
import bpy,bmesh
s=bpy.context.scene
for o in s.objects:
    if not o.name.startswith('B_A04_courtyard_home_details_') or o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);todo=set(bm.verts);rows=[]
    while todo:
        vs=[todo.pop()]
        for v in vs:
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in todo:todo.remove(w);vs.append(w)
        lo=[min(v.co[i] for v in vs) for i in range(3)]
        hi=[max(v.co[i] for v in vs) for i in range(3)]
        if -67<lo[0]<-60 and hi[0]<-59.8 and lo[1]>-9.5 and hi[1]>-8.75 and lo[2]<20.7 and hi[2]>18.65:
            rows.append([*[round(q,2) for q in lo],*[round(q,2) for q in hi]])
    if rows:print('FRONTAGE',o.name,rows,flush=True)
    bm.free()
