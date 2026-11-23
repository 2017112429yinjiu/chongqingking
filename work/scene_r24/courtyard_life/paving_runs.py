"""Trace straight, mixed-material tile runs only when four surrounding edges agree."""
def trace(cells):
    def solid(key):
        v=cells.get(key,[])
        return v[0] if len(v)==2 and v[0]==v[1] else None
    found=[]
    for axis in [0,1]:
        def world(c,t): return (c,t) if axis==0 else (t,c)
        starts={}
        for x,z in cells:
            if not (-87<=x<=5 and -14<=z<=48): continue
            c,t=(x,z) if axis==0 else (z,x)
            if set(cells[(x,z)])!={'pavement','yard_concrete'} or len(cells[(x,z)])!=2:continue
            low=solid(world(c-1,t));high=solid(world(c+1,t))
            if low and high and low!=high: starts[(c,t)]=(low,high)
        for (c,t),sides in sorted(starts.items()):
            if starts.get((c,t-1))==sides:continue
            end=t+1
            while starts.get((c,end))==sides:end+=1
            if end-t<2:continue
            entry=solid(world(c,t-1));leave=solid(world(c,end))
            if entry not in sides or leave not in sides or entry==leave:continue
            a=c+(entry==sides[0]);b=c+(leave==sides[0])
            found.append(dict(axis=axis,c=c,start=t,end=end,a=a,b=b,low=sides[0],high=sides[1]))
    return found
