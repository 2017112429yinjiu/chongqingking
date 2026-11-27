"""Fit the exposed wall to the 2015 pipe sightlines and the game ground."""
from math import cos, pi, sin
from random import Random

from mathutils import Vector


def wall(common, ground, fit, mats):
    Mesh = common["Mesh"]
    axis = common["Edge"]([(0.,0.),(1.,0.)], ground)
    center = Vector(fit["en"])
    direction = Vector((-.50,.8660254))
    outward = Vector((direction.y,-direction.x))
    core = Mesh("COL_Western33_SurveyedWall")
    blocks = Mesh("Western33_RoughStoneCoursesAndDamp")
    vegetation = Mesh("Western33_ClimbingIvy")
    pipe = Mesh("Western33_LocatedPipeAndClamps")
    rng = Random(20150907)

    def en(s,t):
        return center+direction*s+outward*t

    def at(s,t,y):
        return (*en(s,t),y)

    def grade(s):
        return axis.ground_y(en(s,.14))+.06

    def course(mesh,a,b,c,d,low,top,material):
        xy = [(a,c),(a,d),(b,d),(b,c)]
        mesh.solid([at(s,t,grade(s)+low) for s,t in xy],[at(s,t,grade(s)+top) for s,t in xy],material)

    # Both lower eyes have the stone face next to the camera, well before the pipe.
    a,b = -10.85,2.5
    course(core,a,b,-.48,-.166,-.26,2.64,mats["ashlar"])
    course(blocks,a-.045,b+.035,-.48,-.09,2.62,2.71,mats["border"])
    z = -.14
    for row in range(6):
        h = (.38,.48,.37,.49,.44,.49)[row]
        s = a
        while s < b-.10:
            next_s = min(b,s+rng.uniform(.59,1.22))
            lip = -.152+rng.uniform(.009,.043)
            chosen = rng.choice(("ashlar","grey","grey","warm")) if row else rng.choice(("ashlar","wet","wet"))
            course(blocks,s+.012,next_s-.008,-.176,lip,z+.016,z+h-.008,mats[chosen])
            if row > 1 and rng.random()<.55:
                here = s+(next_s-s)*rng.uniform(.18,.34)
                pos = at(here,lip+.003,grade(here)+z+h*.41)
                blocks.face([pos,at(here+.20,lip+.005,pos[2]+rng.uniform(.032,.079)),
                             at(here+.17,lip+.006,pos[2]+.041)],mats["cut"])
            s = next_s
        z += h

    for patch,spread in ((-9.10,.96),(-5.34,.60),(-2.84,.78),(1.27,1.08)):
        for _ in range(180):
            y = rng.uniform(.11,2.61)
            s = patch+rng.uniform(-1.,1.)*spread*(.5+.23*y)
            v = rng.uniform(-.076,.011)+.05*sin(y*3.1+s)
            if not a+.09 < s < b-.10 or abs(s)<.14:
                continue
            level = grade(s)+y
            w = rng.uniform(.035,.117)
            tilt = rng.uniform(-.13,.16)
            vegetation.face([at(s-w,v+.013,level+tilt),
                             at(s,v+.056,level+.06),at(s+w*.82,v,level-.022),
                             at(s+.015,v+.026,level-.054)],rng.choice((mats["leaf"],mats["ivy_young"],mats["ivy_shade"])))

    base = grade(0.)-.052

    def tube(radius, start, stop, material):
        mesh_points = [(center.x+radius*cos(i*pi/7.),center.y+radius*sin(i*pi/7.)) for i in range(14)]
        pipe.solid([(*p,start) for p in mesh_points],[(*p,stop) for p in mesh_points],material)

    tube(.048,base,base+2.62,mats["pipe"])
    for h in (.23,.91,1.63,2.31):
        y = base+h
        tube(.058,y,y+.031,mats["pipe_dark"])
        a0,b0 = -.029,.029
        bracket = [at(s,t,y) for s,t in ((a0,-.18),(a0,-.034),(b0,-.034),(b0,-.18))]
        pipe.solid(bracket,[(x,n,z+.032) for x,n,z in bracket],mats["pipe_dark"])
    return [m.save() for m in (core,blocks,vegetation,pipe)]
