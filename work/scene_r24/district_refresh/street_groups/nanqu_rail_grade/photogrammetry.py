"""Recompute the white pier-head control from four separately registered lower views."""
import argparse
import json
from math import cos, hypot, radians, sin, tan
from pathlib import Path


def ray(heading, pitch, px, py, w, h, fovy):
    heading,pitch=map(radians,(heading,pitch))
    focal=(h/2)/tan(radians(fovy/2))
    u,v=(px-w/2)/focal,(h/2-py)/focal
    en=[sin(heading)*(cos(pitch)-v*sin(pitch))+u*cos(heading),
        cos(heading)*(cos(pitch)-v*sin(pitch))-u*sin(heading)]
    norm=hypot(*en)
    return [en[0]/norm,en[1]/norm], (sin(pitch)+v*cos(pitch))/norm


def intersection(points, directions):
    offsets=[[-n,e] for e,n in directions]
    a=sum(e*e for e,n in offsets)
    b=sum(e*n for e,n in offsets)
    c=sum(n*n for e,n in offsets)
    x=sum(e*(e*p[0]+n*p[1]) for (e,n),p in zip(offsets,points))
    y=sum(n*(e*p[0]+n*p[1]) for (e,n),p in zip(offsets,points))
    return [(c*x-b*y)/(a*c-b*b),(a*y-b*x)/(a*c-b*b)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('registration','points','grade','output'):
        p.add_argument(name,type=Path)
    a=p.parse_args()
    reg=json.loads(a.registration.read_text())
    ctl=json.loads(a.points.read_text())['photo_triangulation']
    grade=json.loads(a.grade.read_text())
    rows=reg['lower']
    feature=ctl['rail_near_road_pier']
    pairs=[ray(*v,*px,*ctl['view_size_px'],ctl['fovy']) for v,px in zip(feature['heading_pitch_deg'],feature['sample_px'])]
    points=[row['en'] for row in rows]
    fit=intersection(points,[direction for direction,_ in pairs])
    samples=[]
    for (direction,slope),row,angles,pixels in zip(pairs,rows,feature['heading_pitch_deg'],feature['sample_px']):
        e,n=[p-q for p,q in zip(fit,row['en'])]
        along=e*direction[0]+n*direction[1]
        device=row['device_height_m']
        samples.append({'pano':row['pano'],'camera_en':row['en'],'heading_pitch_deg':angles,'feature_px':pixels,
            'vertical_camera_height_m':device,'horizontal_ray_distance_m':along,
            'horizontal_residual_m':abs(e*direction[1]-n*direction[0]),'feature_above_local_road_m':device+along*slope})
    zlower=grade['provider_lower_ref_z']
    upper_z={row['pano']:row['raw_z'] for row in reg['upper']}
    upper=[{'pano':s['pano'],'feature_above_lower_street_m':upper_z[s['pano']]-zlower+s['field_far_relation_m'],
            'ray_feature':'far visible lower steel edge at 04'} for s in grade['six_local_controls']]
    a.output.write_text(json.dumps({'upper_far_edge_above_lower_reference':upper,'lower_pier_head_en_fit':fit,
        'lower_registered_pier_head_rays':samples,'pixel_model':{'size':ctl['view_size_px'],'vertical_fov_deg':ctl['fovy']},
        'scope':'These are different points on the same structure. The low view measures the observed pier head under the steel box and the high view the dark far edge near the crossing. No provider Z values are used as absolute survey heights.'},indent=2)+'\n')


if __name__=='__main__':
    main()
