"""Build the gutter, battered retaining face and crossing between the existing two walks."""
from mathutils import Vector
from grade_junction_r24 import Edge,sections,ease
from terrain_strip_r24 import cut_strip

def outline(obj):
    return [[obj.matrix_world@obj.data.vertices[i].co for i in poly.vertices] for poly in obj.data.polygons if poly.normal.z>.5]

def slice_at(loops,x):
    points=[]
    for loop in loops:
        for a,b in zip(loop,loop[1:]+loop[:1]):
            if a.x<=x<b.x or b.x<=x<a.x:points.append(a.lerp(b,(x-a.x)/(b.x-a.x)))
    return points

def build(scene,change,surface,box,rod,mat):
    upper=outline(scene.objects['COL_Walk_OSM_734116598_0_pavement'])
    branch=outline(scene.objects['COL_Road_176034707_0_pavement'])+outline(scene.objects['COL_Road_176034707_0_asphalt'])
    primary=Edge([b for a,b in sections(scene,(1189963547,49182408))])
    points=[]
    for i in range(97):
        x=23.65+.24*i
        walk=min(slice_at(upper,x),key=lambda q:q.y)
        street=max([primary.sample(x)]+[q for q in slice_at(branch,x) if q.y<walk.y],key=lambda q:q.y)
        if walk.y-street.y>.34:points.append((street,walk))
    low=Edge([a for a,b in points]);high=Edge([b for a,b in points])
    old=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('COL_Terrain_200m') or o.name=='COL_R23_PathFoundations')]
    removed=cut_strip(old,low,high,change)
    wall=mat('corner_stone',(.275,.248,.207));cap=mat('corner_cap',(.291,.283,.254))
    cement=mat('corner_paving',(.25,.248,.23));gravel=mat('corner_grit',(.184,.172,.134))
    iron=mat('corner_iron',(.083,.089,.082),.74,.39)
    rows=[];ramp_width=0.
    for a,b in points:
        x=a.x;t=ease(35.9,38.4,x)*(1.-ease(42.8,45.35,x))
        end=ease(low.x[0],low.x[0]+.9,x)*(1.-ease(high.x[-1]-.9,high.x[-1],x))
        t=1.-(1.-t)*end
        if 38.4<x<42.8:ramp_width+=.24
        row=[]
        for u,h in [(0.,0.),(.09,.006),(.28,.035),(.41,.92),(.52,.97),(1.,1.)]:
            p=a.lerp(b,u);p.z=a.z+(b.z-a.z)*(t*u+(1.-t)*h)+.006;row.append(p)
        rows.append((row,t))
    for (a,t),(b,u) in zip(rows,rows[1:]):
        for j in range(5):
            m=cement if max(t,u)>.92 else [cement,gravel,wall,cap,cement][j]
            surface('COL_R24_CloseTerrace',m,[a[j],b[j],b[j+1],a[j+1]],[(0,1,2,3)])
    # Under the two transition edges close the area to the uncut original slope.
    for row,reverse in [(rows[0][0],False),(rows[-1][0],True)]:
        for a,b in zip(row,row[1:]):
            ps=[a-Vector((0,0,1.3)),b-Vector((0,0,1.3)),b,a]
            surface('COL_R24_CloseTerrace',wall,ps,[(0,1,2,3) if reverse else (3,2,1,0)])
    # Grates sit flush in the bed of the gutter and are narrow enough to leave the crossing clear.
    for i in [25,80]:
        row,t=rows[i];p=row[0].lerp(row[1],.70);p.z+=.012
        box('R24_StreetDrain',iron,p,(.44,.105,.018))
        for k in range(7):box('R24_StreetDrain',cap,(p.x-.177+k*.059,p.y,p.z+.014),(.016,.088,.012))
    return dict(length=high.x[-1]-low.x[0],open_crossing_m=ramp_width,old_faces_removed=removed)

