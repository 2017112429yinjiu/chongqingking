"""Joined timber bookcases; millimetre edge breaks and grain following each board."""
from math import hypot
from random import Random
import bpy

TIERS=6
PITCH=.355
DECK=.033

def build(index,start,end,y,bays,storey,point,material):
    verts,faces,coords=[],[],[]
    rng=Random(511+index)
    def board(axis,lo,hi,a,b,c,d,edge):
        # For horizontal boards the section is (depth,height); for stiles (width,depth).
        section=[(a+edge,c),(b-edge,c),(b,c+edge),(b,d-edge),
                 (b-edge,d),(a+edge,d),(a,d-edge),(a,c+edge)]
        def at(along,s,t):
            x,v,z=(along,s,t) if axis=="x" else (s,t,along)
            return point(x,y+v,storey+z)
        offset=len(verts)
        shift=(rng.random(),rng.random())
        for along in (lo,hi):
            verts.extend(at(along,s,t) for s,t in section)
        def face(ids,uv):
            faces.append(tuple(i+offset for i in ids))
            coords.extend((shift[0]+u*.83,shift[1]+v*.83) for u,v in uv)
        for cap,k in ((0,range(7,-1,-1)),(8,range(8))):
            face([cap+i for i in k],[(section[i][0]-a,section[i][1]-c) for i in k])
        across=0.
        for i,(s,t) in enumerate(section):
            j=(i+1)%8
            width=hypot(section[j][0]-s,section[j][1]-t)
            face([i,j,8+j,8+i],[(0,across),(0,across+width),(hi-lo,across+width),(hi-lo,across)])
            across+=width
    sign=1 if index==2 else -1
    cap=.16+TIERS*PITCH+DECK
    unit=(end-start)/bays
    board("x",start-.024,end+.024,-.226,.226,cap,cap+.037,.007)
    board("x",start+.009,end-.009,-.158,.158,.006,.16,.004)
    for j in range(bays+1):
        x=start+j*unit
        board("z",.008,cap,x-.034,x+.034,-.209,.209,.005)
        a,b=sorted((sign*.190,sign*.227))
        board("z",.040,cap,x-.043,x+.043,a,b,.006)
    for j in range(bays):
        left=start+j*unit+.034
        right=start+(j+1)*unit-.034
        a,b=sorted((-sign*.178,-sign*.195))
        for n in range(4):
            x=left+(right-left)*n/4
            board("z",.15,cap,x,x+(right-left)/4-.001,a,b,.001)
        for k in range(TIERS+1):
            z=.16+k*PITCH
            board("x",left,right,-.201,.201,z,z+DECK,.002)
            a,b=sorted((sign*.192,sign*.219))
            board("x",left,right,a,b,z-.007,z+DECK,.004)
    mesh=bpy.data.meshes.new("Bookcase joinery")
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(material)
    uv=mesh.uv_layers.new(name="Board grain")
    uv.data.foreach_set("uv",[v for pair in coords for v in pair])
    mesh.update()
    obj=bpy.data.objects.new("COL_Court_Jinma_Casework_%d"%(index+1),mesh)
    bpy.context.collection.objects.link(obj)
    return obj
