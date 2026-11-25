"""Repair-shop rain hood, market fabric shades and rolled split-bamboo tea blinds."""
from math import cos,sin,pi
from runpy import run_path
from pathlib import Path
tube=run_path(str(Path(__file__).with_name("occupied_fronts.py")))["tube"]


def shade(p,face,m):
    if not p["name"]:return
    front=-p["depth"]/2; z=p["height"]
    market=p["name"].endswith("市场")
    tea=p["name"].endswith("茶摊")
    for j,(left,right) in enumerate(zip(p["frame"]["u"],p["frame"]["u"][1:])):
        if left-.25<p["door_u"]<right+.25 or right-left<2.4:continue
        a,b=left+.12,right-.12
        if tea:
            # Slats and binding tapes roll back towards the fascia.
            reach=.29 if j%2 else .51
            for n in range(int(reach/.043)):
                h=2.49-n*.044
                face([(a,front-2.17,z+h),(b,front-2.17,z+h),(b,front-2.17,z+h+.032),(a,front-2.17,z+h+.032)],m["wood"])
            for x in (a+.13,b-.13):
                tube(face,(x,front-2.187,z+2.54),(x,front-2.187,z+2.50-reach),.013,m["iron"],6)
            tube(face,(a,front-2.17,z+2.53),(b,front-2.17,z+2.53),.069,m["wood"],10)
            continue
        # Batten attached to the old canopy fascia. Arms return to the posts.
        far=front-(2.91 if market else 2.66)
        for x in (a+.03,b-.03):
            tube(face,(x,front-2.08,z+2.55),(x,far,z+2.28),.022,m["metal"])
            tube(face,(x,front-2.06,z+2.34),(x,far,z+2.28),.019,m["iron"])
        tube(face,(a,far,z+2.28),(b,far,z+2.28),.022,m["metal"])
        stripes=max(8,round((b-a)/.16))
        tone=m["jade"] if market else m["zinc"]
        for n in range(stripes):
            t0,t1=n/stripes,(n+1)/stripes
            x0,x1=a+(b-a)*t0,a+(b-a)*t1
            mat=(m["canvas"] if (n//2)%2==0 else tone) if market else tone
            def section(t):
                h=2.28-.040*sin(pi*t)
                return [(front-2.075,2.57),(front-2.40,2.42-.023*sin(pi*t)),(far,h)]
            s0,s1=section(t0),section(t1)
            for k in range(2):
                face([(x0,s0[k][0],z+s0[k][1]),(x1,s1[k][0],z+s1[k][1]),
                      (x1,s1[k+1][0],z+s1[k+1][1]),(x0,s0[k+1][0],z+s0[k+1][1])],mat)
            if market:
                h0,h1=s0[-1][1],s1[-1][1];mid=(x0+x1)*.5
                face([(x0,far,z+h0),(x1,far,z+h1),(x1,far-.016,z+h1-.105),
                      (mid,far-.021,z+(h0+h1)/2-.154),(x0,far-.016,z+h0-.105)],mat)
