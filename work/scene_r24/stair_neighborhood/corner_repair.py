import bmesh
# Two source material batches split a twisted one-metre cell along its near-level diagonal.
# Reconstruct the cell through its four measured boundary heights, welded on each edge.
orig_names=['COL_Terrain_200m_pavement','COL_Terrain_200m_stone']
corner_z={};old_faces=[]
for label in orig_names:
    ob=scene.objects[label];mesh=ob.data;bm=bmesh.new();bm.from_mesh(mesh);remove=[]
    for face in bm.faces:
        coords=[ob.matrix_world@v.co for v in face.verts]
        if all(-22.0001<=v.x<=-20.9999 and -16.0001<=v.y<=-14.9999 for v in coords):
            for v in coords:corner_z[round(v.x),round(v.y)]=v.z
            remove.append(face);old_faces.append([label,[list(v) for v in coords]])
    if remove:bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(mesh);mesh.update()
    bm.free()
assert len(old_faces)==2 and len(corner_z)==4,(old_faces,corner_z)
pts=[];f=[];sub=5
for j in range(sub+1):
    v=j/sub
    for i in range(sub+1):
        u=i/sub
        z=(1-u)*(1-v)*corner_z[-22,-16]+u*(1-v)*corner_z[-21,-16]+u*v*corner_z[-21,-15]+(1-u)*v*corner_z[-22,-15]
        pts.append((-22+u,-16+v,z))
for j in range(sub):
    for i in range(sub):
        k=j*(sub+1)+i;f.extend([(k,k+1,k+sub+2),(k,k+sub+2,k+sub+1)])
add('COL_N13_CourtCornerMasonry',pts,f,'cement')

