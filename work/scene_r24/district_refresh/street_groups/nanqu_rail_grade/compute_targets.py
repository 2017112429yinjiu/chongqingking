"""Anchor the prototype upper road to the lower game street through two camera runs."""
import argparse
import json
from pathlib import Path
from statistics import median


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('cameras','ties','extra','game','source','guide','result'):
        parser.add_argument(name,type=Path)
    a=parser.parse_args()
    c, ties, extra, game, source, guide = [json.loads(path.read_text()) for path in (a.cameras,a.ties,a.extra,a.game,a.source,a.guide)]
    lower=[next(x['top'] for x in station['meshes'] if x['mesh'].startswith('COL_Outer500_Surface_')) for station in source['samples']['pano-low']]
    lower_datum, lower_original = median(lower), median(row['raw_z'] for row in c['lower'])
    peers={row['pano']:row for row in (*c['upper'],*ties,*extra)}
    target=[]
    for row in peers.values():
        road=row['roads'][0]
        if road['id'] not in ('176034685','59146775','176968735') or road['distance_m']>4.1:
            continue
        if abs(float(row['device_height_m'])-2.32)>.001:
            raise ValueError(f"Different camera mounting height at {row['pano']}")
        e=road['projection'][0]
        target.append([e,lower_datum+row['raw_z']-lower_original,row['pano']])
    # Interpolate the matched hidden tunnel/bridge deck crossings only from the known drive,
    # so a near-coincident -1 road cannot overrule a confirmed upper-road membership.
    for row in c['upper']:
        if row['pano'] in {t[2] for t in target}:
            continue
        road=next(v for v in row['roads'] if v['id']=='59146775')
        target.append([road['projection'][0],lower_datum+row['raw_z']-lower_original,row['pano']])
    target.sort()
    road_by_name={entry[2]:entry for entry in target}
    top_names={'COL_Nanqu_RaisedWestApproach','COL_R24_LinkDeck_R24_link_asphalt'}
    stations=[]
    for camera,old_road,old_beam in zip(guide['pano'],game['samples']['pano-top'],source['samples']['pano-far-edge']):
        y_road=next(v['at'][2] for v in old_road['down'] if v['body'] in top_names)
        y_beam=next(v['soffit'] for v in old_beam['meshes'] if v['mesh']=='COL_Nanjimen_NorthRailSteelBox')
        fit_y=road_by_name[camera['pano']][1]+camera['far_edge_height_over_road_m']
        stations.append({'pano':camera['pano'],'en':camera['camera_en'],'far_edge_en':old_beam['en'],
            'old_road_game_y':y_road,'old_far_soffit_game_y':y_beam,'candidate_road_game_y':road_by_name[camera['pano']][1],
            'field_far_relation_m':camera['far_edge_height_over_road_m'],'patient_fit_far_game_y':fit_y,
            'candidate_far_shift_needed_m':fit_y-y_beam})
    shift=median(row['candidate_far_shift_needed_m'] for row in stations)
    elevation_ties=[row[:2] for row in target]
    elevation_ties.insert(0,[-289.,elevation_ties[0][1]+.65])
    elevation_ties.append([215.,elevation_ties[-1][1]+.75])
    west=[(p['en'][0],next(h['at'][2] for h in p['down'] if 'Surface_' in h['body'])) for p in game['samples']['176034685']]
    rail=[[-1200,0],[-178,0],[-166,-.08],[-150,-.31],[-128,-.77],[-108,shift*.74],[-92,shift],[-78,shift-.16],[-47,shift-.58],[0,shift-.60]]
    a.result.write_text(json.dumps({'registered_game_ref_y':lower_datum,'provider_lower_ref_z':lower_original,
        'road_target_by_east':elevation_ties,'road_measurement_ties':target,'west_terrain_by_east':west,
        'rail_shift_by_north':rail,'six_local_controls':stations,
        'scope':'Values are a reproducible fit in game ENU. Independent road-chain ties drive the road. The north soffit correction is small and is constrained by the registered relative height of the observed far flange.'},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
