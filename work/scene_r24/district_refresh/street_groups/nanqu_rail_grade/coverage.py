"""Measure across the observed span at both carriageway edges and the centre."""
import argparse
import json
from math import cos, radians, sin
from pathlib import Path


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def sight_limits(origin, heading, outline):
    found=[]
    for a,b in zip(outline,outline[1:]):
        along=[b[0]-a[0],b[1]-a[1]]
        offset=[a[0]-origin[0],a[1]-origin[1]]
        det=cross(heading,along)
        if abs(det)<1e-8: continue
        d=cross(offset,along)/det
        k=cross(offset,heading)/det
        if d>0 and 0<=k<=1: found.append(d)
    assert len(found)==2,found
    return sorted(found)


def generate(guide):
    outline=guide['ways']['1297385297']['en']
    azimuth=radians(110)
    heading=[sin(azimuth),cos(azimuth)]; across=[-cos(azimuth),sin(azimuth)]
    stations=[]
    for index,p in enumerate(guide['pano'],1):
        for edge,offset in (('landside',2.45),('centre',0),('riverside',-2.45)):
            e,n=[a+offset*b for a,b in zip(p['camera_en'],across)]
            near,far=sight_limits((e,n),heading,outline)
            xy=lambda t:[e+t*heading[0],n+t*heading[1]]
            label=f'rail-span-{index}-{edge}'
            values=[xy(near+(far-near)*fraction) for fraction in (.13,.31,.50,.69,.87)]
            guide['samples'][label]=values
            stations.append({'pano':p['pano'],'lateral_offset_m':offset,'position':edge,
                             'sample_key':label,'near_far_en':[xy(near),xy(far)],'near_far_range_m':[near,far]})
    guide['rail_span_intersections']=stations
    return guide


def verify(guide, source, live):
    answer=[]
    for station in guide['rail_span_intersections']:
        key=station['sample_key']
        contents=[]
        for edit,in_game in zip(source['samples'][key],live['samples'][key],strict=True):
            if len(edit['en']) != 2 or any(abs(a-b) > .001 for a,b in zip(edit['en'],in_game['en'],strict=True)):
                raise ValueError(f'Source and runtime probes disagree at {key}')
            owners={v['mesh'].removeprefix('Grade__') for v in edit['meshes']}
            steel='COL_Nanjimen_NorthRailSteelBox' in owners
            hood='Nanjimen_NorthAcousticHood' in owners
            collider=any(hit['body']=='COL_Nanjimen_NorthRailSteelBox' for hit in in_game['up'])
            contents.append({'en':edit['en'],'source_has_box':steel,'source_has_hood':hood,'normal_scene_collision':collider})
        answer.append({**station,'samples':contents})
    all_probes=[x for trial in answer for x in trial['samples']]
    return {'expected':len(all_probes),'steel_mesh_hits':sum(t['source_has_box'] for t in all_probes),
            'hood_mesh_hits':sum(t['source_has_hood'] for t in all_probes),
            'steel_collision_hits':sum(t['normal_scene_collision'] for t in all_probes),
            'every_crossing_has_both_visible_parts':all(
                trial['source_has_box'] and trial['source_has_hood'] and trial['normal_scene_collision']
                for trial in all_probes),'independent_transverse_rays':answer}


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('guide',type=Path); p.add_argument('--source',type=Path); p.add_argument('--live',type=Path); p.add_argument('--output',type=Path); a=p.parse_args()
    g=json.loads(a.guide.read_text())
    if not a.source:
        a.guide.write_text(json.dumps(generate(g),ensure_ascii=False,indent=2)+'\n'); return
    result=verify(g,json.loads(a.source.read_text()),json.loads(a.live.read_text()))
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['expected'],result['steel_mesh_hits'],result['hood_mesh_hits'],result['steel_collision_hits'],result['every_crossing_has_both_visible_parts'])


if __name__=='__main__':
    main()
