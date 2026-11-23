"""Original roof garden, household drying and neighbourhood service fittings."""
import math
import random


def garden(b,rng):
    # Three small brick beds with occupied and freshly cleared rows.
    for bed,y in enumerate([-1.67,.02,1.71]):
        length=rng.uniform(4.7,5.5); half=length/2
        b.box((-.42,y,.166),(length,.73,.33),'soil')
        for course in range(3):
            z=.055+.11*course
            for edge in [-1,1]:
                x=-half
                while x<half-.025:
                    segment=min(.30 if course%2 and x==-half else .53,half-x)
                    b.box((-.42+x+segment*.5,y+edge*.441,z),(segment-.009,.15,.104),rng.choice(['brick','dullbrick','brick']))
                    x+=segment
                b.box((-.42+edge*(half+.068),y,z),(.135,.985,.108),'dullbrick')
        for col in range(13):
            if bed==2 and col%4!=0:continue
            for row in range(2):
                x=-.42-half+.23+(length-.48)*col/12+rng.uniform(-.055,.055)
                cy=y+.19*(2*row-1)+rng.uniform(-.04,.04);r=rng.uniform(.14,.23)
                for leaf in range(8):
                    a=rng.uniform(-.23,.23)+leaf*math.tau/8
                    span=r*rng.uniform(.54,1.4);rise=rng.uniform(.15,.37)
                    side=rng.uniform(.037,.065);vs=[]
                    for k in range(6):
                        t=k/5;wide=side*math.sin(math.pi*t)**.66+.002
                        for lateral in [-1,0,1]:
                            d=span*t**1.35
                            vs.append((x+math.cos(a)*d-math.sin(a)*wide*lateral,
                                       cy+math.sin(a)*d+math.cos(a)*wide*lateral,
                                       .33+rise*(1.4*t-.66*t*t)-abs(lateral)*wide*.48+.018*math.sin(k+leaf)*abs(lateral)))
                    fs=[(k*3+i,k*3+3+i,k*3+4+i,k*3+1+i) for k in range(5) for i in range(2)]
                    b.mesh(vs,fs,rng.choice(['greens','leaf','sage_leaf']),True)
    # Low trellis shades one end; braces and ties follow the upright axes.
    for x in [-3.16,-1.46]:
        for y in [-2.18,2.20]:
            b.box((x,y,.085),(.32,.32,.17),'stone')
            b.cylinder((x,y,.15),(x+.035,y,2.03),.036,'bamboo',12,.027)
            b.cylinder((x+.030,y,1.76),(x+.036,y,1.83),.043,'cord',10)
        b.cylinder((x+.03,-2.36,1.90),(x+.03,2.37,1.92),.041,'bamboo',12)
    for j in range(10):
        y=-2.24+j*.50
        b.cylinder((-3.36,y,1.96),(-1.25,y+.032,1.92),.022,'bamboo',8)
    for y in [-2.18,2.2]:
        b.cylinder((-3.14,y,1.25),(-2.50,y,1.94),.026,'bamboo',9)
    # A working-height potting bench and a shallow stacked earthenware pair.
    for x in [2.62,3.36]:
        for y in [-1.9,-.34]:b.box((x,y,.40),(.065,.065,.80),'iron')
    for j in range(4):b.box((2.67+j*.22,-1.12,.84),(.21,1.75,.08),'timber')
    for i in range(2):
        x=2.90;y=-1.55+.64*i
        b.cylinder((x,y,.88),(x,y,1.15),.128,'terra',20,.199)
        b.cylinder((x,y,1.142),(x,y,1.171),.211,'terra',24)
        b.cylinder((x,y,1.169),(x,y,1.174),.174,'soil',22)


def pergola(b,rng):
    for x in [-2.76,2.76]:
        for y in [-1.61,1.61]:
            b.box((x,y,.10),(.42,.42,.20),'stone')
            b.box((x,y,1.22),(.105,.105,2.11),'timber')
        b.box((x,0,2.32),(.135,3.53,.19),'timber')
    for y in [-1.61,1.61]:b.box((0,y,2.40),(5.93,.13,.17),'timber')
    for i in range(19):
        x=-2.93+i*.328
        b.box((x,0,2.52),(.084,3.73,.13),'timber')
    for y in [-1.21,1.21]:
        for x in [-1.65,1.65]:
            b.box((x,y,.217),(.27,.41,.435),'dullbrick')
        for j in range(3):b.box((0,y+(j-1)*.134,.47),(4.04,.124,.078),'timber')
    # Leaves cluster unevenly around two climbing stems, not over the whole roof.
    for y in [-1.50,1.46]:
        b.pipe([(-2.66,y,.02),(-2.78,y+.03,.7),(-2.66,y-.08,1.4),(-2.68,y+.06,2.40)],.026,'bamboo',8)
        for j in range(14):
            x=-2.79+j*.217;cy=y*(.77+.19*math.sin(j*.55))
            b.cylinder((x,cy,2.54),(x+.28,cy+.11*math.sin(j*.5),2.57),.013,'bamboo',7)
            for k in range(12):
                px=x+rng.uniform(-.26,.26);py=cy+rng.uniform(-.43,.43);z=2.56+rng.uniform(-.09,.14)
                r=rng.uniform(.075,.16);a=rng.uniform(0,math.tau)
                b.mesh([(px,py,z),(px+.6*r*math.cos(a)-.57*r*math.sin(a),py+.6*r*math.sin(a)+.57*r*math.cos(a),z+.04),
                        (px+r*1.8*math.cos(a),py+r*1.8*math.sin(a),z-.035),
                        (px+.6*r*math.cos(a)+.57*r*math.sin(a),py+.6*r*math.sin(a)-.57*r*math.cos(a),z+.008)],
                       [(0,1,2),(0,2,3)],rng.choice(['greens','leaf','sage_leaf']),True)


def drying(b,rng):
    for x in [-2.40,2.40]:
        for y in [-.80,.80]:
            b.box((x,y,.075),(.39,.39,.15),'stone')
            b.cylinder((x,y,.11),(x,y,1.87),.023,'iron',12)
            b.cylinder((x,y,.20),(x+.31*(-1 if x>0 else 1),y,.03),.018,'iron',10)
        b.cylinder((x,-.94,1.86),(x,.94,1.86),.023,'zinc',12)
    for y in [-.64,.64]:
        def line(x):return 1.85-.112*(1-(x/2.40)**2)
        b.pipe([(x,y,line(x)) for x in [-2.4+i*.20 for i in range(25)]],.007,'cord',7)
        for j,(center,width,drop) in enumerate([(-1.29,1.44,1.02),(.47,1.32,.86),(1.64,.52,.67)]):
            if y>0 and j==1:continue
            tone=rng.choice(['indigo','faded','linen']);phase=rng.random()*5
            def fabric(s,t,back=False):
                x=center+(s-.5)*width
                depth=.012+(.016+.042*t)*math.sin(17*s+phase+.40*t)+.034*t*t
                return (x+.019*t*math.sin(4*s),y+(-depth-.016 if back else depth),
                        line(x)+.008-(.20 if back else drop)*t+.025*t*math.sin(s*9+phase))
            for back in [True,False]:
                for k in range(20):
                    for l in range(10):
                        mat='linen' if tone=='indigo' and l==8 else tone
                        b.quad(fabric(k/20,l/10,back),fabric((k+1)/20,l/10,back),
                               fabric((k+1)/20,(l+1)/10,back),fabric(k/20,(l+1)/10,back),mat)
            for s in [.09,.90]:
                x=center+(s-.5)*width;b.box((x,y,line(x)+.02),(.031,.055,.078),'bamboo')


def service(b,rng):
    # Vented roof enclosure with real lapped corrugation and metal frame.
    for x in [-1.70,1.70]:
        for y in [-1.04,1.04]:
            b.box((x,y,.08),(.30,.30,.16),'stone')
            b.box((x,y,.80),(.07,.07,1.45),'iron')
    for y in [-1.04,1.04]:
        b.box((0,y,1.50),(3.6,.075,.085),'iron')
    for x in [-1.70,1.70]:
        for j in range(11):b.box((x,0,.32+j*.108),(.058,2.10,.076),'zinc')
    previous=None
    for j in range(201):
        x=-1.89+3.78*j/200;wave=.023*math.cos(2*math.pi*j/5)
        row=[(x,-1.23,1.72+wave),(x,1.23,1.52+wave),(x,1.23,1.48+wave)]
        if previous:
            b.quad(previous[0],row[0],row[1],previous[1],'tin')
            b.quad(previous[1],row[1],row[2],previous[2],'tin')
        previous=row
    for side in [-1,1]:
        x=side*1.14;b.cylinder((x,0,.04),(x,0,.25),.37,'stone',24)
        b.cylinder((x,0,.25),(x,0,1.48),.27,'zinc',24)
