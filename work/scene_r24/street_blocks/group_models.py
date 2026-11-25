"""Four registered one-storey footprints at the northwest Shancheng Lane bend."""
from math import ceil
import numpy as np

def frontage(ring,ways):
    edges=np.roll(ring,-1,axis=0)-ring
    lens=np.linalg.norm(edges,axis=1)
    def distance_to_way(q):
        a,b=ways[:-1],ways[1:];seg=b-a
        f=np.clip(np.sum((q-a)*seg,axis=1)/np.sum(seg*seg,axis=1),0,1)
        return np.linalg.norm(q-a-f[:,None]*seg,axis=1).min()
    i=min((i for i in range(4) if lens[i]>.86*lens.max()),key=lambda i:distance_to_way(ring[i]+edges[i]*.5))
    return [ring[(i+k)%4] for k in range(4)]

def build(group,ways,z,material,mats,Batch,grades):
    def slot(name,color,file):
        mats.append(material(name,color,file))
        return len(mats)-1
    plaster=slot("North lane rubbed lime plaster",(.66,.64,.55),"plastered_wall_04_diff_1k.jpg")
    brick=slot("North lane weathered brick",(.55,.48,.41),"brick_wall_08_diff_2k.jpg")
    roof=slot("North lane grey tile",(.37,.41,.40),"roof_tiles_diff.jpg")
    wood=6
    sash=5
    glazing=slot("Dark recessed courtyard glazing",(.040,.051,.049),None)
    notes=[]
    for p in group["buildings"]:
        ring=np.array(p["points"])
        # Pick the long facade nearest the mapped public lane. All dimensions below
        # are distances along the actual quadrilateral, preserving deviations from a rectangle.
        a,b,c,d=frontage(ring,ways)
        w=float(np.linalg.norm(b-a));dep=float(np.linalg.norm(d-a))
        def q(u,v):return (a+(b-a)*u/w)*(1-v/dep)+(d+(c-d)*u/w)*v/dep
        def pos(u,v,h):return [*q(u,v),h]
        base=grades[p["osm"]]
        batch=Batch();detail=Batch()
        def block(dest,x0,y0,h0,x1,y1,h1,mat):
            verts=[pos(x,y,h) for h in (h0,h1) for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
            # A clockwise captured ring needs reversed normals on every authored face.
            clockwise=np.linalg.det(np.stack([b-a,d-a]))<0
            for face in ((3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
                dest.face([verts[j] for j in (face[::-1] if clockwise else face)],mat)
        def box(*dims):block(batch,*dims)
        def fit(*dims):block(detail,*dims)
        bottom=min(z(pt) for pt in ring)-.28
        box(0,0,bottom,w,dep,base,4)
        height=3.05;top=base+height
        bays=max(3,round(w/3.85));bay=w/bays;door=bays//2
        for j in range(bays):
            l,r=j*bay,(j+1)*bay;u=(l+r)/2
            span=.78 if j==door else min(.88,bay*.28)
            wall=plaster
            for x0,x1 in ((l,u-span),(u+span,r)):box(x0,0,base,x1,.21,top,wall)
            box(u-span,0,base+2.24,u+span,.21,top,wall)
            if j!=door:
                box(u-span,0,base,u+span,.21,base+.88,brick)
                fit(u-span-.07,-.09,base+.83,u+span+.07,.24,base+.92,4)
                fit(u-span,.135,base+.92,u+span,.16,base+2.24,glazing)
                for mu in (u-span,u,u+span):fit(mu-.031,.075,base+.92,mu+.031,.13,base+2.24,wood)
                fit(u-span,.06,base+1.83,u+span,.14,base+1.88,wood)
            else:
                for mu in (u-span,u+span):fit(mu-.042,-.02,base,mu+.042,.25,base+2.30,wood)
                # Open leaf inside the reveal and sill directly supported on the stone plinth.
                fit(u+span-.09,.23,base+.04,u+span,.89,base+2.21,wood)
                level=z(q(u,-.55))
                num=max(1,ceil((base-level)/.17))
                for step in range(num):
                    v=-.31*(step+1)
                    box(u-.82,v,min(z(q(u,v))-.1,base-.2),u+.82,v+.31,base-(base-level)*(step+.25)/num,4)
        box(0,.21,base,.23,dep,top,plaster);box(w-.23,.21,base,w,dep,top,plaster)
        # Small rear lights sit above the uphill sill. Their reveals, lintels and
        # stepped brick footing remain visible from the opposite side of the lane.
        for j in range(bays):
            lo=max(.23,j*bay);hi=min(w-.23,(j+1)*bay)
            u=(lo+hi)*.5;half=min(.53,bay*.21)
            if j%2:
                box(lo,dep-.21,base,hi,dep,top,plaster)
            else:
                for x0,x1 in ((lo,u-half),(u+half,hi)):box(x0,dep-.21,base,x1,dep,top,plaster)
                box(u-half,dep-.21,base,u+half,dep,base+1.42,plaster)
                box(u-half,dep-.21,base+2.19,u+half,dep,top,plaster)
                fit(u-half,dep-.15,base+1.43,u+half,dep-.12,base+2.18,glazing)
                for mx in (u-half,u,u+half):fit(mx-.037,dep-.12,base+1.42,mx+.037,dep-.05,base+2.19,wood)
                fit(u-half-.07,dep-.22,base+1.36,u+half+.07,dep+.09,base+1.43,4)
            fit(lo,dep-.03,base,hi,dep+.025,base+.38,brick)
        # End purlins and the lengths of individual rafters articulate the eaves at walking height.
        for u in np.arange(.18,w-.05,.46):
            for near,far in ((-.43,.16),(dep-.16,dep+.43)):
                fit(u-.043,near,top-.085,u+.043,far,top+.02,wood)
        for v in np.linspace(.22,dep-.22,5):
            h=top+.04+min(v,dep-v)*.34
            for lo,hi in ((-.27,.01),(w-.01,w+.27)):fit(lo,v-.073,h-.12,hi,v+.073,h+.015,wood)
        for u in np.linspace(.18,w-.18,bays+1):
            fit(u-.09,-.28,top-.16,u+.09,dep+.28,top+.04,wood)
            box(u-.078,dep*.56-.08,base,u+.078,dep*.56+.08,top,wood)
        ridge=top+dep*.17
        for side,hh in ((-.30,top+.04),(dep+.30,top+.04)):
            quad=[pos(-.23,side,hh),pos(w+.23,side,hh),pos(w+.23,dep*.5,ridge),pos(-.23,dep*.5,ridge)]
            if np.cross(np.subtract(quad[1],quad[0]),np.subtract(quad[2],quad[0]))[2]<0:quad.reverse()
            batch.face(quad,roof)
            fit(-.23,side-.032,hh-.13,w+.23,side+.032,hh,wood)
        fit(-.25,dep*.5-.095,ridge-.03,w+.25,dep*.5+.095,ridge+.085,roof)
        for u in (0,w):
            tri=[pos(u,0,top),pos(u,dep,top),pos(u,dep*.5,ridge)]
            detail.face(tri,plaster);detail.face(tri[::-1],plaster)
        name=p["osm"].split("@")[0][1:]
        batch.make("COL_Shancheng_OSM_"+name)
        detail.make("Shancheng_Joinery_"+name)
        notes.append({"osm":p["osm"],"gers":p["gers"],"source_storeys":p["levels"],"wall_base_corners":ring.tolist(),"door":[*q(w*(door+.5)/bays,0),base],"floor_z":base,"eaves_m":height,"bays":bays})
    return notes
