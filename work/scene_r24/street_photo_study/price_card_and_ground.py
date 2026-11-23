# Executed inside the source authoring script, before flushing the per-site geometry.
group='Workday12_PriceCard'
x,y=-24.27,-75.70
h=anchor('card stake',x,y,9.1)
rod((x,y,h+.050),(x-.018,y+.035,h+.61),.014,'split_bamboo',7)
# Card has its own UV surface. Worn corners and the fold are part of the outline.
cx,cy,cz=x-.018,y-.023,h+.486
shape=[(-.181,-.117),(.128,-.120),(.182,-.098),(.183,.098),(.159,.121),(-.174,.115)]
verts=[(cx+u,cy+v*.106+u*.28,cz+v+u*.033) for u,v in shape]
cardmesh=bpy.data.meshes.new(group);cardmesh.from_pydata(verts,[],[tuple(range(6))]);cardmesh.update()
uv=cardmesh.uv_layers.new()
for lp in cardmesh.loops:
    u,v=shape[lp.vertex_index];uv.data[lp.index].uv=((u+.185)/.37,(v+.125)/.25)
cardmat=bpy.data.materials.new('Reclaimed_carton_local_prices');cardmat.use_nodes=True;nt=cardmat.node_tree
pic=nt.nodes.new('ShaderNodeTexImage');pic.image=bpy.data.images.load(str(root/'greengrocer_card.jpg'));pic.image.pack()
nt.links.new(pic.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color']);nt.nodes['Principled BSDF'].inputs['Roughness'].default_value=.93
cardmesh.materials.append(cardmat);card_object=bpy.data.objects.new('Workday12_PencilledPrices',cardmesh)
# A local, bilinearly sampled ground field keeps old plaster staining at the actual base along rising streets.
import struct,zlib
dim=161; rows=[]
for j in range(dim):
    data=bytearray()
    for i in range(dim):
        xx=(i+.5)*200/dim-100; zz=(j+.5)*200/dim-100
        try:gh=support(xx,-zz)[0]
        except RuntimeError:gh=-8
        data.extend(struct.pack('>H',round(max(0,min(1,(gh+8)/56))*65535)))
    rows.append(b'\x00'+data)
def chunk(tag,dat):return struct.pack('>I',len(dat))+tag+dat+struct.pack('>I',zlib.crc32(tag+dat)&0xffffffff)
heightmap=project/'assets/street_use_r24/support_heights.png'
heightmap.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',dim,dim,16,0,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b''))

