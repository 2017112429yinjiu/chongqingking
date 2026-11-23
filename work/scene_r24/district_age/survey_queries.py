"""Resolve each sampled public road to its own vertical level at flyovers, preserving map-only tunnels."""
from pathlib import Path
import json,collections
here=Path(__file__).resolve().parent;work=here.parents[1];d=json.loads((here/'survey_after.json').read_text())
geo=json.loads((work/'project/chongqing_blender_v05/source_data/geo_layout.json').read_text('utf8'))
items={str(r['id']):r for r in geo['roads']+geo['paths']}
meta=[];occ=collections.Counter();bridge_under=0;tunnels=0
for key,n,length,width in d['routes']:
 r=items.get(key,{});i=occ[key];occ[key]+=1
 meta.append({'name':key,'part':i,'width':width,'m':length,'tunnel':r.get('tags',{}).get('tunnel')=='yes','bridge':r.get('tags',{}).get('bridge')=='yes','type':r.get('type','local')})
rows=[]
for idx,l,x,y,levels in d['samples']:
 r=meta[idx];key=r['name']
 if r['tunnel']:tunnels+=1;continue
 if not levels:
    rows.append([idx,l,x,-y,None,'']);continue
 preferred=next((v for v in levels if v[1]==f"COL_Road_{key}_{r['part']}_asphalt"),levels[0])
 if key=='734116595' and any(n=='COL_Yard20_CornerSurface' for h,n in levels):preferred=next(v for v in levels if v[1]=='COL_Yard20_CornerSurface')
 if levels[0][0]-preferred[0]>.6:bridge_under+=1
 rows.append([idx,l,x,-y,preferred[0],preferred[1]])
# When two roads share the same XY, continue the approach elevation across any
# clipped junction; the first downward hit can otherwise jump onto the flyover.
from bisect import bisect_left
anchors=collections.defaultdict(list)
for j,row in enumerate(rows):
    idx,l,x,z,h,name=row;r=meta[idx]
    if r['type'] not in ('local','steps','footway') and (name==f"COL_Road_{r['name']}_{r['part']}_asphalt" or name=='COL_Yard20_CornerSurface'):
        anchors[idx,l].append(j)
all_levels={(i,l,x,-y):ls for i,l,x,y,ls in d['samples']}
resolved=0
for j,row in enumerate(rows):
    idx,l,x,z,h,who=row;ix=anchors.get((idx,l),[])
    if len(ix)<2 or h is None or j in ix:continue
    k=bisect_left(ix,j)
    if k==0 or k>=len(ix):continue
    aa,bb=rows[ix[k-1]],rows[ix[k]]
    if (aa[2]-bb[2])**2+(aa[3]-bb[3])**2>170:continue
    s=((x-aa[2])**2+(z-aa[3])**2)**.5;t=((x-bb[2])**2+(z-bb[3])**2)**.5
    target=(aa[4]*t+bb[4]*s)/max(.0001,s+t)
    ls=all_levels[idx,l,x,z];near=min(ls,key=lambda v:abs(v[0]-target))
    if abs(near[0]-target)<abs(h-target)-.6:row[4:6]=near;resolved+=1
grid=[[x,-y,ls[0][0] if ls else None] for x,y,ls in d['grid']]
(here/'road_queries.json').write_text(json.dumps({'routes':meta,'sections':rows,'ground_grid':grid,'underground_alignment_excluded':tunnels,'probes_below_a_higher_surface':bridge_under+resolved},separators=(',',':')),'utf8')
