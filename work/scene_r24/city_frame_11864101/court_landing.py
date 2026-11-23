"""Join the east court entrance to one full central tread and the surveyed court slab."""
import bpy
from mathutils import Vector

def rebuild(scene):
    from trim_paving import footprints
    step=scene.objects['COL_Court_east_entry_steps_step_concrete']
    rail=scene.objects['Court_entry_rails_frame']
    central=scene.objects['COL_Walk_Central_stair_lane_step_concrete']
    floor=scene.objects['COL_Community_court_pavement']
    c,ring=next((c,r) for c,r in footprints(central) if -1<c.y<0 and abs(c.x+18)<.05)
    start=min(p.x for p in ring)
    ylo=min(p.y for p in ring)+.02
    yhi=max(p.y for p in ring)-.02
    court=[floor.matrix_world@v.co for v in floor.data.vertices]
    end=max(v.x for v in court)
    h=max(v.z for v in court)
    assert 1.95<start-end<2.2 and .64<h-c.z<.71
    rows=[(0.,ylo,yhi,c.z),(.30,ylo,yhi,c.z)]
    for i in range(1,5):
        f=i/4
        rows.append((.30+(start-end-.30)*f,ylo+(-1.35-ylo)*f,yhi+(1.35-yhi)*f,c.z+(h-c.z)*f))
    vs=[];fs=[]
    def face(points):
        idx=len(vs);vs.extend(points);fs.append(tuple(range(idx,idx+len(points))))
    # A continuous top with a closed riser between adjacent levels. Butt joins at both ends.
    for idx in range(len(rows)-1):
        s,lo,hi,oldz=rows[idx];u,ulo,uhi,z=rows[idx+1]
        x=start-s;xx=start-u;base=c.z-.72
        face([(x,lo,z),(x,hi,z),(xx,uhi,z),(xx,ulo,z)])
        if idx:face([(x,lo,oldz),(x,hi,oldz),(x,hi,z),(x,lo,z)])
        face([(xx,ulo,base),(x,lo,base),(x,lo,z),(xx,ulo,z)])
        face([(x,hi,base),(xx,uhi,base),(xx,uhi,z),(x,hi,z)])
    def replace(ob,vertices,faces,uv):
        data=bpy.data.meshes.new(ob.name+"_joined")
        mat=ob.data.materials[0]
        data.from_pydata([ob.matrix_world.inverted()@Vector(v) for v in vertices],[],faces);data.materials.append(mat);data.update()
        if uv:
            coords=data.uv_layers.new(name='Paving metres')
            for f in data.polygons:
                for i in f.loop_indices:
                    x,y,z=vertices[data.loops[i].vertex_index]
                    coords.data[i].uv=(x*.55,y*.55) if f.normal.z>.5 else ((x+y)*.55,z*.55)
        ob.data=data
    replace(step,vs,fs,True)
    # A single handrail faces the lower slope. The other side opens onto the court.
    import math
    vs=[];fs=[]
    def rod(a,b,r):
        a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.orthogonal().normalized();v=axis.cross(u);n=8;j=len(vs)
        vs.extend([p+r*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n)) for p in [a,b] for k in range(n)])
        fs.extend([tuple(j+k for k in reversed(range(n))),tuple(j+n+k for k in range(n))]+[(j+k,j+(k+1)%n,j+n+(k+1)%n,j+n+k) for k in range(n)])
    line=[]
    for s in [.14,1.08,start-end-.12]:
        f=max(0.,(s-.30)/(start-end-.30));y=ylo-.015+(-1.35-ylo)*f+.075
        top=c.z+.90+(h-c.z)*f;z=next(row[3] for row in rows[1:] if row[0]>=s)
        rod((start-s,y,z-.015),(start-s,y,top),.024);line.append((start-s,y,top))
    for a,b in zip(line,line[1:]):rod(a,b,.029)
    replace(rail,vs,fs,False)
    return dict(start_x=start,end_x=end,central_z=c.z,court_z=h,mouth_width=yhi-ylo,risers=4,
                rise=(h-c.z)/4,lower_landing=.30,stones=[step.name,rail.name])

