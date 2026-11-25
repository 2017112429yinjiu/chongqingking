"""Three retained footprint buildings: shaded window returns and recessed loggias at fixed roof height."""
def elevation(spec,floor,h,storey,length,frame,batch,solid,box,wall,m):
    def face(points,mat,physical=False):
        (solid if physical else batch).face([frame(*p) for p in points],mat,[(u/2.1,z/2.1) for u,v,z in points])
    def strip(a,b,lo,hi):
        if b>a:face([(a,0,lo),(b,0,lo),(b,0,hi),(a,0,hi)],wall,True)
    bays=max(1,int(length/3.15));cursor=0
    for bay in range(bays):
        if length<1.6 or (floor==0 and (bay+spec["id"])%3!=0):continue
        u=(bay+.5)*length/bays;span=min(.89,length/bays*.33)
        a,b=u-span,u+span
        lo,hi=h+storey*.285,h+storey*.746
        strip(cursor,a,h,h+storey);strip(a,b,h,lo);strip(a,b,hi,h+storey)
        deep=(bay+spec["id"])%4==0 and floor>0
        depth=.72 if deep else .19
        tint=m["panes"][(spec["id"]+floor*3+bay)%4]
        for x in (a,b):
            face([(x,0,lo),(x,depth,lo),(x,depth,hi),(x,0,hi)],m["stone"],True)
        for z in (lo,hi):
            face([(a,0,z),(b,0,z),(b,depth,z),(a,depth,z)],m["stone"],True)
        face([(a,depth,lo),(b,depth,lo),(b,depth,hi),(a,depth,hi)],tint,True)
        for x in (a+.025,u,b-.025):
            box(batch,frame,x-.018,depth-.042,lo,x+.018,depth-.005,hi,m["trim"])
        box(batch,frame,a,depth-.046,hi-.32,b,depth-.007,hi-.286,m["trim"])
        if deep:
            box(batch,frame,a,-.10,lo-.05,b,.18,lo+.09,m["stone"])
            for x in (a+.08,u,b-.08):
                box(batch,frame,x-.019,-.035,lo+.07,x+.019,.003,lo+.58,m["iron"])
            for z in (lo+.24,lo+.58):
                box(batch,frame,a,-.058,z,b,.010,z+.031,m["metal"])
        cursor=b
    strip(cursor,length,h,h+storey)
