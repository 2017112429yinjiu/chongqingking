"""Shape the slope under the documented footprints and pave the public approaches."""
import numpy as np

def margin(x, y, ring):
    sides = []
    center = ring.mean(axis=0)
    for a,b in zip(ring,np.roll(ring,-1,axis=0)):
        edge = b-a
        normal = np.array([edge[1],-edge[0]]) / np.linalg.norm(edge)
        if (center-a) @ normal > 0:
            normal = -normal
        sides.append((x-a[0])*normal[0]+(y-a[1])*normal[1])
    return np.maximum.reduce(sides)

def door_fraction(key):
    return {"renai_long":2.5/21, "renai_cross":4.5/9, "jinma_classrooms":6.5/13}[key]

def prepare(spec, height, xx, yy, levels, mx, my, rgba):
    grades = {}
    for feature in spec["buildings"]:
        key = feature["id"]
        ring = np.array(feature["points"])
        a,b,c,d = ring
        fraction = door_fraction(key)
        door = a + (b-a)*fraction
        outward = (a-d)/np.linalg.norm(a-d)
        grades[key] = round(height(*(door+outward*.9))+.05,4)
    # The two touching wings have a common floor datum.
    grades["renai_cross"] = grades["renai_long"]
    for feature in spec["buildings"]:
        key=feature["id"]
        ring=np.array(feature["points"])
        distance=margin(xx, yy, ring)
        blend=np.clip(1-np.maximum(distance,0)/.85,0,1)
        levels-=np.maximum(levels-(grades[key]-.16),0)*blend
        edge=margin(mx,my,ring)
        rgba[:,:,1]=np.maximum(rgba[:,:,1], np.clip((1.6-edge)*1.5,0,1))
    school=np.asarray(next(f["points"] for f in spec["buildings"] if f["id"]=="jinma_classrooms"))
    a,b,c,d=school
    rear=(c+d)*.5
    axis=rear-(a+b)*.5
    axis/=np.linalg.norm(axis)
    along=(xx-rear[0])*axis[0]+(yy-rear[1])*axis[1]
    across=np.abs((xx-rear[0])*axis[1]-(yy-rear[1])*axis[0])
    far=height(*(rear+axis*6.2))
    grade=(1-np.clip(along/6.2,0,1))*(grades["jinma_classrooms"]-.08)+np.clip(along/6.2,0,1)*far
    blend=np.clip(2.6-across,0,1)*np.clip(along+1,0,1)*np.clip(7.2-along,0,1)
    levels+=(grade-levels)*blend
    return grades
