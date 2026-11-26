"""Tabletop objects from the window and foreground photographs."""
from math import sin,cos,tau
from runpy import run_path
from pathlib import Path
parts=run_path(str(Path(__file__).with_name("furniture.py")))
front,sheet=parts["front"],parts["sheet"]

def radio(g,x,y,z,m):
    g.board(x,y,z,.492,.155,.238,m['honey'],.013)
    for side in (-1,1):
        u=x+side*.159
        for r,v,material in ((.076,-.080,'brass'),(.070,-.084,'black')):
            g.tube((u,y+v+.004,z+.115),(u,y+v,z+.115),r,m[material],sides=36)
        ring=[]
        for j in range(36):
            a=tau*j/36
            ring.append((u+.064*cos(a),y-.086,z+.115+.064*sin(a)))
        # Map a perforated weave inside the circular lip, following the physical grille.
        uv=[((.5+.47*cos(tau*j/36))/4,(.5+.47*sin(tau*j/36))/4) for j in range(36)]
        g.face(ring,m['print'],uv)
        g.board(x+side*.194,y+.027,z+.237,.023,.025,.060,m['black'])
    g.board(x,y+.027,z+.285,.409,.029,.019,m['black'],.006)
    front(g,x,y-.081,z+.135,.161,.077,13,m)
    g.board(x,y-.076,z+.032,.152,.022,.09,m['black'])
    g.board(x,y-.087,z+.048,.113,.005,.046,m['steel'])
    for off in (-.027,.027):g.tube((x+off,y-.092,z+.073),(x+off,y-.095,z+.073),.012,m['black'],sides=15)
    for j in range(6):g.board(x+(j-2.5)*.028,y-.042,z+.237,.023,.036,.008,m['steel'],.002)
    g.tube((x-.194,y+.056,z+.246),(x+.178,y+.060,z+.262),.004,m['steel'])

def record_player(g,x,y,z,m):
    g.board(x,y,z,.385,.312,.096,m['black'],.012)
    g.board(x,y-.004,z+.087,.362,.285,.018,m['honey'])
    # Open lid tilts away from the visitor, with its lining inset in the turned lip.
    for yoff,mat in ((.018,'black'),(0,'lining')):
        w=.375 if yoff else .342
        h=.268 if yoff else .246
        g.face([(x-w/2,y+.139+yoff,z+.098),(x+w/2,y+.139+yoff,z+.098),
                (x+w/2,y+.224+yoff,z+.098+h),(x-w/2,y+.224+yoff,z+.098+h)],m[mat])
    for u in (-.178,.178):g.tube((x+u,y+.14,z+.102),(x+u,y+.226,z+.365),.009,m['black'])
    g.tube((x-.178,y+.226,z+.365),(x+.178,y+.226,z+.365),.009,m['black'])
    g.turn(x-.033,y,z+.105,[(0,.110),(.008,.113),(.010,.105)],m['steel'])
    g.turn(x-.033,y,z+.114,[(0,.103),(.003,.106)],m['black'])
    for rad in (.073,.084,.095):
        for j in range(28):
            a=tau*j/28;b=tau*(j+1)/28
            g.face([(x-.033+(rad+dr)*cos(t),y+(rad+dr)*sin(t),z+.118) for dr,t in ((0,a),(.0007,a),(.0007,b),(0,b))],m['steel'])
    g.turn(x-.033,y,z+.117,[(0,.029),(.002,.029)],m['label'])
    g.tube((x-.033,y,z+.12),(x-.033,y,z+.127),.002,m['steel'])
    g.turn(x+.123,y+.077,z+.105,[(0,.020),(.032,.018)],m['steel'])
    g.tube((x+.123,y+.077,z+.137),(x+.085,y-.072,z+.128),.006,m['steel'])
    g.board(x+.079,y-.075,z+.120,.024,.039,.014,m['black'])
    for u in (-.141,.141):g.board(x+u,y-.157,z+.055,.022,.008,.031,m['brass'])

def fare_box(g,x,y,z,m):
    # Open pressed-metal shell with a pale inner lid, spring fingers and loose fare slips.
    w,d,h=.232,.155,.080
    g.board(x,y,z,w,d,.008,m['red'],.003)
    for s in (-1,1):
        g.board(x+s*(w/2-.003),y,z+.006,.006,d,h,m['red'],.002)
        g.board(x,y+s*(d/2-.003),z+.006,w-.009,.006,h,m['red'],.002)
    pts=[(x-w/2,y+d/2,z+h),(x+w/2,y+d/2,z+h),(x+w/2,y+d/2+.045,z+h+.142),(x-w/2,y+d/2+.045,z+h+.142)]
    g.face(pts,m['red']);g.face(pts[::-1],m['red'])
    ww=w-.015
    g.face([(x-ww/2,y+d/2+.001,z+h+.010),(x+ww/2,y+d/2+.001,z+h+.010),
            (x+ww/2,y+d/2+.039,z+h+.133),(x-ww/2,y+d/2+.039,z+h+.133)],m['steel'])
    for i in range(3):
        u=x+(i-1)*.060
        v=y+d/2
        g.print([(u-.023,v-.001,z+h+.028),(u+.023,v-.001,z+h+.028),(u+.023,v+.022,z+h+.104),(u-.023,v+.022,z+h+.104)],3,m["print"])
        for off in (-.013,.013):
            g.tube((u+off,v+.002,z+h+.032),(u+off,v+.017,z+h+.087),.0017,m["steel"])
        g.tube((u,y+d/2+.001,z+h+.015),(u,y+d/2+.017,z+h+.103),.0027,m['brass'])
    for j in range(11):
        colour=(2,3,8,2,3)[j%5]
        sheet(g,x+.039*sin(j*2.7),y+.027*cos(j*.9),z+.009+.004*j,.108,.054,colour,m,.25*sin(j),.003)
    # Rolled enamel lip, hinge barrels and the fold-down metal carrying handle.
    for s in (-1,1):
        g.tube((x+s*w/2,y-d/2+.003,z+h+.005),(x+s*w/2,y+d/2-.003,z+h+.005),.003,m['red'])
        g.tube((x-w/2+.003,y+s*d/2,z+h+.005),(x+w/2-.003,y+s*d/2,z+h+.005),.003,m['red'])
        u=x+s*.072
        g.tube((u-.012,y+d/2,z+h+.003),(u+.012,y+d/2,z+h+.003),.004,m['steel'])
        u=x+s*.032
        g.tube((u,y-d/2+.001,z+.047),(u,y-d/2-.009,z+.047),.006,m['steel'])
        g.tube((u,y-d/2-.009,z+.047),(u,y-d/2-.014,z+.029),.003,m['black'])
    g.tube((x-.032,y-d/2-.014,z+.029),(x+.032,y-d/2-.014,z+.029),.004,m['black'])
    g.board(x,y-d/2-.004,z+.067,.013,.004,.020,m['steel'],.001)


def stamp_tray(g,x,y,z,m):
    for i in range(2):
        u=x+(i-.5)*.32
        g.board(u,y,z,.31,.21,.012,m['wood'])
        for sign in (-1,1):
            g.board(u+sign*.152,y,z+.01,.008,.21,.035,m['wood'])
            g.board(u,y+sign*.101,z+.01,.30,.008,.035,m['wood'])
        for j in range(6):
            px=u+(j%3-1)*.083;py=y+(j//3-.5)*.085
            g.board(px,py,z+.014,.052,.049,.014,m['peg'])
            g.turn(px,py,z+.028,[(0,.014),(.023,.010),(.040,.017),(.052,.022),(.062,.015)],m['steel'])
    g.board(x-.43,y+.043,z,.085,.071,.033,m['red'],.005)
