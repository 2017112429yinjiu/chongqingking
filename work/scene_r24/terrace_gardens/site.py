from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,extent,save,road
if __name__=='__main__':
    area={}
    for o in scene.objects:
        if o.type!='MESH' or o.hide_render:continue
        a,b=extent(o);n=o.name
        if b[0]<16 or a[0]>83 or a[1]>-15 or b[1]<-85:continue
        if max(b[0]-a[0],b[1]-a[1])>85:continue
        area[n]=[a,b]
    save('site_objects.json',area)
    for x in [26,34,38,40,43,46,47.01,49,52,55,58,61,64,68,72,78]:
        last=None
        for i in range(150):
            y=-87+i*.2
            rows=road.down(x,y,14.5,10)
            key=rows[0][1] if rows else ''
            if key!=last:print('SECTION',x,round(y,1),key,round(rows[0][0],2) if rows else None);last=key
    print('SITE',len(area))
