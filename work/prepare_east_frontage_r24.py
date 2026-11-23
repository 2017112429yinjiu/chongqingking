"""Project closed OSM buildings into the district's R22 local east/north frame."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, hashlib, math
import numpy as np

W=Path(__file__).resolve().parent
raw=W/'assets_incoming/r24_stall/osm_east.osm'
source=ET.parse(raw).getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in source.findall('node')}
def ecef(lon,lat):
    lon,lat=map(math.radians,(lon,lat))
    n=6378137/math.sqrt(1-.0066943799901413165*math.sin(lat)**2)
    return np.array([n*math.cos(lat)*math.cos(lon),n*math.cos(lat)*math.sin(lon),n*(1-.0066943799901413165)*math.sin(lat)])
lon,lat=map(math.radians,(106.56445,29.55325));origin=ecef(106.56445,29.55325)
axes=np.array([[-math.sin(lon),math.cos(lon),0.],[-math.sin(lat)*math.cos(lon),-math.sin(lat)*math.sin(lon),math.cos(lat)]])
blocks=[]
for way in source.findall('way'):
    tags={t.get('k'):t.get('v') for t in way.findall('tag')}
    if tags.get('building','no') in ['no','roof','construction']:continue
    refs=[n.get('ref') for n in way.findall('nd')]
    if len(refs)<4 or refs[0]!=refs[-1]:continue
    poly=[(axes@(ecef(*nodes[n])-origin)).round(3).tolist() for n in refs[:-1]]
    x,y=np.mean(poly,axis=0)
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))*.5
    if 125<x<890 and -365<y<270 and abs(y+72)<.98*(x+38) and 105<area<7400:
        blocks.append(dict(osm_id=way.get('id'),points=poly,levels=tags.get('building:levels'),height=tags.get('height'),area=round(area,2)))
target=W/'scene_r24/playtest/source_data/east_r24'
target.mkdir(exist_ok=True)
(target/'footprints.json').write_text(json.dumps(blocks,separators=(',',':')))
(target/'LICENSE.json').write_text(json.dumps(dict(credit='© OpenStreetMap contributors',license='ODbL-1.0',copyright_url='https://www.openstreetmap.org/copyright',license_url='https://opendatacommons.org/licenses/odbl/1-0/',source='https://api.openstreetmap.org/api/0.6/map?bbox=106.5656,29.5501,106.5740,29.5555',source_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),source_osm_timestamp=source.find('meta').get('osm_base') if source.find('meta') is not None else None,derived_database='footprints.json',modifications='Subset of closed footprints in local east and north metres with available height tags. Facades, inferred heights and rooftops are scene art.'),indent=2,ensure_ascii=False),encoding='utf8')
print(len(blocks),'mapped candidate footprints')

