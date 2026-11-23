"""Fair the vertical profile of the existing east ramp across both surface streets."""
import numpy as np
from mathutils import Vector

def fair(scene,change):
    asphalt=scene.objects['COL_Road_59146775_1_asphalt']
    pts=[asphalt.matrix_world@v.co for v in asphalt.data.vertices]
    c=np.asarray([tuple((a+b)*.5) for a,b in zip(pts[::2],pts[1::2])],dtype=float)
    steps=np.linalg.norm(np.diff(c[:,:2],axis=0),axis=1)
    station=np.r_[0.,np.cumsum(steps)];end=station[-1]
    # Monotone Hermite grade between the surveyed ends. A broad rise allows the two
    # surface lanes to pass underneath; the original cross section stays level.
    t=station/end
    h0,h1=c[0,2],c[-1,2]
    y=h0*(2*t**3-3*t**2+1)+h1*(-2*t**3+3*t**2)+end*(.064*(t**3-2*t**2+t)+.076*(t**3-t**2))
    lift=y-c[:,2];delta=c[1:,:2]-c[:-1,:2];len2=(delta*delta).sum(axis=1)
    def offset(xy):
        d=xy-c[:-1,:2];f=np.clip((d*delta).sum(axis=1)/len2,0,1)
        idx=np.argmin(((d-f[:,None]*delta)**2).sum(axis=1))
        return lift[idx]*(1.-f[idx])+lift[idx+1]*f[idx]
    names=['COL_Road_59146775_1_asphalt','COL_Road_59146775_1_curb_painted_metal','Road_paint_59146775_line_white.001']
    for name in names:
        ob=scene.objects[name];change(ob);world=ob.matrix_world;inv=world.inverted()
        for v in ob.data.vertices:
            p=world@v.co
            dz=lift[v.index//2] if name==names[0] else offset(np.array([p.x,p.y]))
            p.z+=float(dz);v.co=inv@p
        ob.data.update()
    return {'length_m':float(end),'original_max_grade':float(np.max(np.abs(np.diff(c[:,2])/steps))),'new_max_grade':float(np.max(np.abs(np.diff(y)/steps))),'max_height_change_m':float(max(abs(lift)))}

