"""One smooth-shaded market batch of squash, aubergines and mandarins in their real trays."""
from math import cos,sin,pi
from random import Random
import bpy


def create(p,frame,materials,material):
    rng=Random(814);vertices=[];faces=[];ids=[]
    palettes=[((.48,.21,.045),(.40,.17,.035),(.49,.26,.074)),((.19,.075,.18),(.145,.056,.135),(.23,.105,.19)),
              ((.66,.24,.036),(.58,.19,.020),(.68,.28,.052))]
    palette=[material("Market skin %d %d"%(i,j),color) for i,row in enumerate(palettes) for j,color in enumerate(row)]
    leaf=material("Market stalks",(.10,.16,.054)); palette.append(leaf)
    def poly(verts,mat):faces.append(verts);ids.append(mat)
    def goods(x,y,z,rad,kind):
        angle=rng.random()*pi; lean=rng.uniform(-.14,.14);n=20
        profile=([(0,.37),(.16,.79),(.49,1),(.74,.88),(.84,.58),(.78,.20)]
                 if kind==0 else [(0,.19),(.18,.42),(.53,.60),(.97,.46),(1.40,.27),(1.53,.12)]
                 if kind==1 else [(0,.26),(.15,.72),(.48,.98),(.83,.84),(1.02,.46),(.98,.16)])
        rings=[]
        for height,r in profile:
            row=[]
            for j in range(n):
                a=j*2*pi/n
                rr=rad*r*(1+(.095 if kind==0 else .018)*cos(a*(7 if kind==0 else 3)+angle))
                dx,dy=rr*cos(a),rr*sin(a)
                if kind==1:dx+=rad*height*.66;dy*=.78
                row.append(len(vertices))
                vertices.append(frame(x+dx*cos(angle)-dy*sin(angle),y+dx*sin(angle)+dy*cos(angle),z+rad*(height+lean*r*sin(a))))
            rings.append(row)
        base=kind*3+rng.randrange(3)
        poly(rings[0][::-1],base)
        for lo,hi in zip(rings,rings[1:]):
            for j in range(n):poly((lo[j],lo[(j+1)%n],hi[(j+1)%n],hi[j]),base)
        poly(rings[-1],base)
        h=profile[-1][0];shift=rad*h*.66 if kind==1 else 0
        cx,cy=x+shift*cos(angle),y+shift*sin(angle)
        stem=[]
        for dz,r in ((0,.021),(.034,.010)):
            row=[]
            for j in range(6):
                a=j*pi/3;row.append(len(vertices))
                vertices.append(frame(cx+r*cos(a)+.26*dz,cy+r*sin(a),z+h*rad+dz))
            stem.append(row)
        for j in range(6):poly((stem[0][j],stem[0][(j+1)%6],stem[1][(j+1)%6],stem[1][j]),9)
        poly(stem[1],9)
    w=p["width"]/2;d=p["depth"]/2;z=p["height"]
    for group,(u,v) in enumerate(((-w+2,-d+2.4),(-w+2,-d+5.25),(2.85,-d+3.6),(w-2,-d+2.5))):
        for j in range(3):
            cx=u-.75+j*.75;kind=(group+j)%3
            for i in range(4):
                for k in range(3):
                    goods(cx+(k-1)*.184+rng.uniform(-.012,.012),v+(i-1.5)*.19+rng.uniform(-.014,.014),z+.881,
                          rng.uniform(.075,.098),kind)
    for group,u in enumerate((-2.6,1.1,5.9)):
        for tray in range(3):
            for i in range(3):
                for j in range(3):
                    goods(u-.73+tray*.56+(j-1)*.15+rng.uniform(-.01,.01),-d-1.42+i*.15,z+.872,
                          rng.uniform(.063,.083),(tray+group)%3)
    mesh=bpy.data.meshes.new("Outer500_MarketProduce")
    mesh.from_pydata(vertices,[],faces);mesh.update()
    for mat in palette:mesh.materials.append(materials[mat])
    for f,slot in zip(mesh.polygons,ids):
        f.material_index=slot; f.use_smooth=True
    obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj)
