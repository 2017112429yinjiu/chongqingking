"""The desks, cabinets and bench proportions visible in the two on-site room views."""
from math import sin,cos
from random import Random

def front(g,x,y,z,w,h,tile,m,lean=0):
    g.print([(x-w/2,y,z),(x+w/2,y,z),(x+w/2,y+lean,z+h),(x-w/2,y+lean,z+h)],tile,m['print'])

def sheet(g,x,y,z,w,d,tile,m,angle=0,thick=.004):
    c,s=cos(angle),sin(angle)
    pts=[(x+a*c-b*s,y+a*s+b*c,z+thick) for a,b in ((-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2))]
    g.face([(u,v,z) for u,v,_ in pts[::-1]],m['paper'])
    for p,q in zip(pts,pts[1:]+pts[:1]):
        g.face([(p[0],p[1],z),(q[0],q[1],z),q,p],m['paper'])
    g.print(pts,tile,m['print'])

def desk(g,x,y,w,d,h,m,drawer=False,top='lacquer'):
    # Dark lacquer on four joined top boards. Exposed frame and feet use the worn scan.
    for j in range(4):
        g.board(x,y-d/2+(j+.5)*d/4,h-.034,w,d/4-.001,.034,m[top],.003)
    for side in (-1,1):
        u=x+side*(w/2-.068)
        for v in (y-d/2+.057,y+d/2-.057):
            g.board(u,v,0,.070,.068,h-.03,m['walnut'],.005,(.048,.05))
            g.tube((u,v-.036,h-.09),(u,v-.039,h-.09),.004,m['peg'],sides=8)
        g.board(u,y,h-.168,.045,d-.086,.136,m['walnut'])
    for side in (-1,1):
        g.board(x,y+side*(d/2-.060),h-.145,w-.12,.035,.113,m['walnut'])
    if drawer:
        for j in range(2):
            xx=x+(j-.5)*(w-.18)*.5
            g.board(xx,y-d/2+.024,h-.156,(w-.19)/2,.028,.106,m['wood'])
            for off in (-.045,.045):g.tube((xx+off,y-d/2+.009,h-.099),(xx+off,y-d/2-.013,h-.099),.006,m['brass'])
            g.tube((xx-.045,y-d/2-.013,h-.099),(xx+.045,y-d/2-.013,h-.099),.006,m['brass'])

def bench(g,x,y,w,m):
    g.board(x,y,.391,w,.182,.038,m['wood'],.009)
    for sign in (-1,1):
        u=x+sign*(w/2-.15)
        for s in (-1,1):
            g.tube((u+sign*.057,y+s*.112,.003),(u,y+s*.051,.393),.030,m['walnut'],.035,6)
        g.board(u,y,.272,.046,.155,.048,m['wood'])
    g.board(x,y,.205,w-.20,.030,.051,m['walnut'])
    for u in (-w/2+.15,w/2-.15):
        g.tube((x+u,y,.428),(x+u,y,.430),.009,m['peg'],sides=10)

def plaque(g,x,y,z,w,h,tile,m):
    # Glazed artwork and paper backing within a mitred timber surround.
    g.board(x,y,z,w,.032,h,m['walnut'])
    border=.026 if w>.65 else .012
    front(g,x,y-.018,z+border,w-2*border,h-2*border,tile,m)

def booklet(g,x,y,z,w,h,tile,m,lean=.048):
    t=.012
    a=(x-w/2,y,z);b=(x+w/2,y,z)
    c=(x+w/2,y+lean,z+h);d=(x-w/2,y+lean,z+h)
    g.print([a,b,c,d],tile,m['print'])
    for p,q in ((b,c),(c,d),(d,a)):
        g.face([p,q,(q[0],q[1]+t,q[2]),(p[0],p[1]+t,p[2])],m['paper'])

def back_shelves(g,items,m):
    # Looking towards the plaque: square cubbies left, tiered face-out rack right.
    rng=Random(133)
    for x,w,d,cols,rows in ((-.93,1.47,.32,4,3),(.69,1.68,.34,1,4)):
        top=.745
        desk(g,x,0,w+.08,.52,top,m,True)
        bottom=top+.026
        height=1.105
        g.board(x,.140,bottom,w,.029,height,m['wood'])
        for j in range(cols+1):
            u=x-w/2+j*w/cols
            g.board(u,0,bottom,.026,d,height+.035,m['wood'])
        for j in range(rows+1):
            z=bottom+j*height/rows
            g.board(x,-.014,z,w,d+.024,.022,m['wood'])
            if cols==1 and j<rows:g.board(x,-.184,z+.018,w,.018,.041,m['walnut'])
        for k in range(rows):
            z=bottom+k*height/rows+.022
            if cols==1:
                for j in range(7):
                    u=x+(j-3)*.223
                    booklet(items,u,-.158,z,.177+rng.uniform(-.012,.012),.205+rng.uniform(-.013,.013),4+(j+3*k)%8,m,.065)
            else:
                for j in range(cols):
                    u=x+(j+.5-cols/2)*w/cols
                    if (j+k)%3==0:
                        for q in range(7):
                            sheet(items,u,-.012,z+.014*q,.247,.158,4+(j+k+q)%8,m,.018*sin(q),.014)
                    elif (j+k)%3==1:
                        for q in range(5):
                            # Printed fore-edges of separately bound pamphlets.
                            xx=u+(q-2)*.040
                            items.board(xx,.02,z,.034,.171,.25-.012*(q%3),m['paper'],.0015)
                            front(items,xx,-.067,z+.002,.034,.246-.012*(q%3),4+(k+q)%8,m)
                    else:booklet(items,u,-.101,z,.194,.236,4+(j+k)%8,m,.07)
        crown=bottom+height+.037
        if cols>1:
            plaque(items,x-.28,-.014,crown,.51,.32,15,m)
            # Folded pale canvas bags across the cubby tops, beside the printed sign.
            for n in range(4):
                u=x+.40+.012*sin(n*2)
                z=crown+n*.014
                pts=[(u-.19,-.130,z+.003),(u-.13,-.154,z+.008),(u+.16,-.143,z),
                     (u+.203,-.083,z+.005),(u+.188,.110,z+.01),(u-.177,.122,z+.006)]
                items.face(pts,m['paper'])
                for a,b in zip(pts,pts[1:]+pts[:1]):
                    items.face([a,b,(b[0],b[1],b[2]+.009),(a[0],a[1],a[2]+.009)],m['paper'])
                items.face([(a,b,c+.009) for a,b,c in pts],m['paper'])
            for offset in (-.08,.08):
                items.tube((x+.39+offset,-.12,crown+.055),(x+.39+offset,-.18,crown+.029),.003,m['label'])
            items.tube((x+.31,-.18,crown+.029),(x+.47,-.18,crown+.029),.003,m['label'])
        else:
            booklet(items,x+.46,.055,crown,.254,.35,7,m,.078)
            items.tube((x-.16,.028,crown+.115),(x-.16,.032,crown+.115),.116,m['enamel'],sides=36)
            for j in range(8):
                u=x-.49;v=.024
                items.tube((u+(j-4)*.008,v,crown+.006),(u+(j-4)*.017,v+.027,crown+.155-.012*abs(j-4)),.003,m['honey'])

    plaque(g,-.10,.180,2.23,1.33,.40,0,m)

def tall_case(g,glass,items,x,y,w,m,edition):
    # Freestanding, glazed upper cabinet; panelled base, overlapping doors and brass pulls.
    g.board(x,y,.015,w-.08,.38,.075,m['walnut'])
    g.board(x,y,.085,w,.405,.42,m['wood'])
    for k in (-1,1):
        u=x+k*w*.244
        g.board(u,y-.206,.128,w*.46,.023,.321,m['walnut'])
        g.board(u,y-.220,.155,w*.46-.051,.012,.267,m['wood'])
    g.board(x,y+.187,.51,w,.026,1.34,m['walnut'])
    for sign in (-1,1):g.board(x+sign*(w/2-.017),y,.48,.034,.42,1.40,m['wood'])
    g.board(x,y,1.85,w+.032,.45,.048,m['wood'])
    for row in range(4):
        z=.51+row*.33
        g.board(x,y,z,w-.04,.395,.023,m['wood'])
        for col in range(4):
            u=x+(col-1.5)*w*.21
            if (col+row)%3==0:booklet(items,u,y-.11,z+.023,.16,.216,4+(col+row+edition)%8,m)
            elif (col+row)%3==1:
                items.turn(u,y-.02,z+.023,[(0,.045),(.018,.059),(.095,.066),(.105,.054)],m['enamel'])
            else:
                for n in range(3):sheet(items,u,y-.025,z+.023+n*.010,.15,.16,4+(row+n)%8,m,.05*sin(col),.010)
    for j in (-1,1):
        u=x+j*w*.244
        for side in (-1,1):g.board(u+side*w*.231,y-.207,.505,.021,.033,1.335,m['wood'])
        for h in (.505,1.807):g.board(u,y-.207,h,w*.466,.033,.033,m['wood'])
        glass.face([(u-w*.22,y-.205,.536),(u+w*.22,y-.205,.536),(u+w*.22,y-.205,1.807),(u-w*.22,y-.205,1.807)],m['glass'])
        g.tube((u-j*w*.18,y-.224,.98),(u-j*w*.18,y-.245,.98),.015,m['brass'])
