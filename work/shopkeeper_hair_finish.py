"""Paint a regional salt-and-pepper variation onto the existing CC0 hair UVs."""
import bpy
import numpy as np
from math import exp


def finish(hair, out):
    mesh=hair.data
    material=mesh.materials[0]
    nodes=material.node_tree.nodes
    source=nodes.get('DiffuseTexture').image
    w,h=source.size
    rgba=np.empty(w*h*4,dtype=np.float32)
    source.pixels.foreach_get(rgba)
    rgba=rgba.reshape(h,w,4)
    temple=np.zeros((h,w),dtype=np.float32)
    mesh.calc_loop_triangles()
    uv=mesh.uv_layers.active.data
    for tri in mesh.loop_triangles:
        points=np.array([uv[k].uv[:] for k in tri.loops])*[w,h]
        points-=.5
        a,b,c=points
        x0,y0=np.maximum(0,np.floor(points.min(axis=0)).astype(int))
        x1,y1=np.minimum([w-1,h-1],np.ceil(points.max(axis=0)).astype(int))
        denom=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denom)<1e-8 or x1<x0 or y1<y0:continue
        yy,xx=np.ogrid[y0:y1+1,x0:x1+1]
        s=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/denom
        t=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/denom
        u=1-s-t
        v=[mesh.vertices[k].co for k in tri.vertices]
        coverage=[exp(-((abs(p.x)-.072)/.028)**2-((p.y+.059)/.090)**2-((p.z-1.52)/.088)**2) for p in v]
        region=temple[y0:y1+1,x0:x1+1]
        np.maximum(region,np.where((s>=0)&(t>=0)&(u>=0),s*coverage[0]+t*coverage[1]+u*coverage[2],0),out=region)
    # Reuse the source's real painted strand directions. Fine ridges from the
    # difference against the neighbouring locks carry most silver pigment.
    light=rgba[:,:,:3].mean(axis=2)
    surround=sum(np.roll(light,d,axis=axis) for axis in [0,1] for d in [-4,4])*.25
    ridges=np.clip((light-surround)*47+.15,0,1)**1.65
    amount=(.065+.66*temple)*ridges
    for channel,pigment in enumerate([.21,.193,.168]):
        rgba[:,:,channel]=rgba[:,:,channel]*(1-amount)+amount*pigment
    # Preserve fractional edge coverage in the original strand texture.
    image=bpy.data.images.new('CQ_TempleHair',width=w,height=h,alpha=True)
    image.alpha_mode='STRAIGHT'
    image.pixels.foreach_set(rgba.ravel())
    image.filepath_raw=str(out/'temple_hair.png')
    image.file_format='PNG'
    image.save()
    image.pack()
    tex=nodes.get('DiffuseTexture')
    tex.image=image
    bs=nodes.get('Principled BSDF')
    material.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
    bs.inputs['Roughness'].default_value=.68
    for vertex in mesh.vertices:
        p=vertex.co
        front=exp(-((p.y+.117)/.029)**2-((p.z-1.585)/.023)**2)
        hairline=front*(.004*exp(-((abs(p.x)-.044)/.018)**2)-.0026*exp(-((p.x+.012)/.022)**2))
        p.z+=hairline
        p.y+=hairline*.68
    mesh.update()
