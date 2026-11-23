"""Give adjoining OSM road ribbons a common cross section at their shared node."""
from mathutils import Vector

def join(scene,change,first,second):
    obs=[scene.objects['COL_Road_%d_0_asphalt'%way] for way in (first,second)]
    ends=[]
    for ob in obs:
        points=[ob.matrix_world@v.co for v in ob.data.vertices]
        ends.append([([0,1],(points[0]+points[1])/2,points[2:4]),([-2,-1],(points[-2]+points[-1])/2,points[-4:-2])])
    a,b=min(((a,b) for a in ends[0] for b in ends[1]),key=lambda pair:(pair[0][1]-pair[1][1]).length)
    assert (a[1]-b[1]).length<.08,(first,second,a[1],b[1])
    center=(a[1]+b[1])*.5;normals=[]
    for ob,(ids,mid,_) in zip(obs,(a,b)):
        v=[ob.matrix_world@ob.data.vertices[i].co for i in ids]
        normals.append((v[1]-v[0]).to_2d().normalized())
    if normals[0].dot(normals[1])<0:normals[1].negate()
    n=(normals[0]+normals[1]).normalized()
    width=(obs[0].matrix_world@obs[0].data.vertices[a[0][0]].co-a[1]).to_2d().length
    offset=n*(width/n.dot(normals[0]))
    for ob,(ids,_,_) in zip(obs,(a,b)):
        change(ob)
        inverse=ob.matrix_world.inverted()
        for vid in ids:
            old=ob.matrix_world@ob.data.vertices[vid].co
            sign=1 if (old-center).to_2d().dot(offset)>0 else -1
            ob.data.vertices[vid].co=inverse@(center+Vector((sign*offset.x,sign*offset.y,0)))
        ob.data.update()
    return dict(ways=[first,second],center=list(center),deck_width=width*2)

