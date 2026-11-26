"""Probe saved and linked school meshes from both sides of the finish boundary."""
from mathutils import Vector
import bpy

def audit(xy,z0,length,depth):
    shell="COL_Court_jinma_classrooms"
    partition="COL_Court_Structure_jinma_classrooms"
    deck="Court_Jinma_Story_Exposed_Deck"
    def p(x,y,h):return Vector((*xy(x,y),z0+h))
    def material(name,start,end):
        obj=bpy.data.objects[name]
        ray=p(*end)-p(*start)
        hit,point,normal,index=obj.ray_cast(p(*start),ray.normalized(),distance=ray.length)
        if not hit:return None
        return obj.data.materials[obj.data.polygons[index].material_index].name
    side=depth*.32
    records={}
    sites=[
        ("floor",shell,(20,2,.25),(20,2,-.02),"Jinma warm worn school floor"),
        ("case_wall",partition,(21,side-.30,.6),(21,side,.6),"Jinma ivory limewash"),
        ("passage_low",partition,(21,side+.40,.65),(21,side,.65),"Jinma aged teal passage paint"),
        ("passage_high",partition,(21,side+.40,1.36),(21,side,1.36),"Jinma ivory limewash"),
        ("window_pier",shell,(8*length/13,1,1.6),(8*length/13,.10,1.6),"Jinma ivory limewash"),
        ("outer_pier",shell,(8*length/13,-.25,1.6),(8*length/13,.10,1.6),"Weathered school limewash"),
        ("upstairs_floor",shell,(22,2,3.62),(22,2,3.39),"Dark oiled timber"),
        ("ceiling_board",deck,(20.53,1.77,3.13),(20.53,1.77,3.42),"Jinma exposed floorboards"),
        ("joist",deck,(25*length/39,2.13,3.12),(25*length/39,2.13,3.42),"Jinma old fir joists"),
        ("open_stairwell",deck,(22,depth*.54,3.05),(22,depth*.54,3.44),None)]
    for label,mesh,start,end,target in sites:
        found=material(mesh,start,end)
        assert found==target,(label,found,target)
        records[label]=found
    return records
