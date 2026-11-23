"""Derive the game-space river, road axes and distant building plans from OSM."""
from pathlib import Path
import hashlib,json,math
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

W=Path(__file__).resolve().parent; S=W/'scene_r22'; src=W/'assets_incoming/r22_city'
dest=W/'project/chongqing_godot_v05/source_data/river_r22';dest.mkdir(parents=True,exist_ok=True)
urls={'osm_southwest.osm':'https://api.openstreetmap.org/api/0.6/map?bbox=106.5554,29.5471,106.5633,29.5546',
      'osm_southbank.osm':'https://api.openstreetmap.org/api/0.6/map?bbox=106.5500,29.5365,106.5690,29.5460',
      'osm_river.osm':'https://api.openstreetmap.org/api/0.6/relation/9087399/full'}
license={'credit':'© OpenStreetMap contributors','license':'ODbL-1.0','license_url':'https://opendatacommons.org/licenses/odbl/1-0/',
         'copyright_url':'https://www.openstreetmap.org/copyright','sources':[],'derived_database':'river_plan.json',
         'modifications':'Local east/north projection, shoreline clipping, island mask and selection of closed building footprints and two bridge road axes. Vertical art and traffic are fictional.'}
nodes={};ways={};relations={}
for name,url in urls.items():
    file=src/name;root=ET.parse(file).getroot()
    license['sources'].append({'file':name,'url':url,'downloaded_local_date':'2026-11-21','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    for n in root.findall('node'):nodes[n.get('id')]=(float(n.get('lon')),float(n.get('lat')))
    for w in root.findall('way'):ways[w.get('id')]=w
    for r in root.findall('relation'):relations[r.get('id')]=r
(src/'PROVENANCE.json').write_text(json.dumps(license,ensure_ascii=False,indent=2),encoding='utf8')
(dest/'LICENSE.json').write_text(json.dumps(license,ensure_ascii=False,indent=2),encoding='utf8')
area=(-1650.,-1690.,1260.,475.)
lon0,lat0=map(math.radians,(106.56445,29.55325))
def xyz(lon,lat):
    n=6378137/math.sqrt(1-.0066943799901413165*math.sin(lat)**2)
    return np.array([n*math.cos(lat)*math.cos(lon),n*math.cos(lat)*math.sin(lon),n*(1-.0066943799901413165)*math.sin(lat)])
origin=xyz(lon0,lat0);east=np.array([-math.sin(lon0),math.cos(lon0),0])
north=np.array([-math.sin(lat0)*math.cos(lon0),-math.sin(lat0)*math.sin(lon0),math.cos(lat0)])
def line(w):
    pts=[]
    for item in w.findall('nd'):
        lon,lat=nodes[item.get('ref')];d=xyz(math.radians(lon),math.radians(lat))-origin
        pts.append([round(float(d@east),3),round(float(d@north),3)])
    return pts
def clip(points):
    for axis,limit,sign in [(0,area[0],1),(1,area[1],1),(0,area[2],-1),(1,area[3],-1)]:
        if not points:break
        out=[]
        for a,b in zip(points,points[1:]+points[:1]):
            ai=(a[axis]-limit)*sign>=0;bi=(b[axis]-limit)*sign>=0
            if ai!=bi:
                f=(limit-a[axis])/(b[axis]-a[axis]);out.append([round(a[k]+f*(b[k]-a[k]),3) for k in [0,1]])
            if bi:out.append(b)
        points=out
    return points
rings=[]
for member in relations['9087399'].findall('member'):
    if member.get('type')!='way':continue
    p=clip(line(ways[member.get('ref')])[:-1])
    if len(p)>2:rings.append({'id':member.get('ref'),'role':member.get('role'),'points':p})
assert sum(p['role']=='outer' for p in rings)==1
axes=[{'id':i,'points':line(ways[i])} for i in ['49182292','49182296']]
blocks=[]
for i,w in ways.items():
    tags={t.get('k'):t.get('v') for t in w.findall('tag')}
    if 'building' not in tags or tags['building'] in ['roof','no','construction']:continue
    p=line(w)
    if len(p)<4 or p[0]!=p[-1]:continue
    p=p[:-1];c=np.mean(p,axis=0);r=np.linalg.norm(c)
    if not 330<r<1550 or c[1]>160:continue
    size=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
    if not 65<size<9500:continue
    blocks.append({'osm_id':i,'points':p,'area':round(size,1),'height_tag':tags.get('height'),'levels_tag':tags.get('building:levels'),'building':tags['building']})
plan={'source_license':'ODbL-1.0','attribution':'© OpenStreetMap contributors','origin_wgs84':[106.56445,29.55325],
      'bounds':area,'river_relation':'9087399','rings':rings,'axes':axes,'buildings':blocks}
(dest/'river_plan.json').write_text(json.dumps(plan,ensure_ascii=False,separators=(',',':')),encoding='utf8')
res=2.;w=math.ceil((area[2]-area[0])/res);h=math.ceil((area[3]-area[1])/res)
def pix(q):return ((q[0]-area[0])/res,(q[1]-area[1])/res)
water=Image.new('L',(w,h));islands=Image.new('L',(w,h));land=ImageDraw.Draw(water);sand=ImageDraw.Draw(islands)
for ring in sorted(rings,key=lambda it:it['role']!='outer'):
    pts=[pix(q) for q in ring['points']]
    land.polygon(pts,fill=255 if ring['role']=='outer' else 0)
    if ring['role']=='inner':sand.polygon(pts,fill=255)
fields=np.stack([np.asarray(im) for im in [water,water.filter(ImageFilter.GaussianBlur(13)),islands.filter(ImageFilter.GaussianBlur(4)),water.filter(ImageFilter.GaussianBlur(52))]],axis=2)
np.save(S/'river_fields.npy',fields)
Image.fromarray(fields[:,:,:3]).resize((665,495)).save(S/'river_study.png')
asset=W/'project/chongqing_godot_v05/assets/river_r22';asset.mkdir(exist_ok=True)
Image.fromarray(fields[:,:,[1,2,3]]).save(asset/'shore_masks.png')
print('Clipped rings',len(rings),'buildings',len(blocks),'axes',len(axes))
