"""Re-register both panorama sequences using the unchanged project control."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'north_edges'))
from register_panoramas import bd_mercator, bd_to_gcj, digest, line_hit, project, to_wgs84

LOWER = ['090292001223051416'+suffix+'AU' for suffix in ('3419600','3420960','3422320','3423679')]


def register(path, transform, ways, source=None):
    row = json.loads(path.read_bytes())['content'][0]
    xy = [row['X'],row['Y']]
    bd = bd_mercator(xy[0]/100,xy[1]/100)
    gcj = bd_to_gcj(*bd)
    wgs, residual = to_wgs84(*gcj)
    en = project(wgs, transform)
    nearest = sorted((line_hit(en, data['en']), ident) for ident, data in ways.items() if 'highway' in data['tags'])
    return {'pano':path.stem,'date':row['Date'],'source_sha256':digest(path),'raw_mc_cm':xy,'raw_z':row['Z'],
            'provider':row.get('Provider'),'device_height_m':row.get('DeviceHeight'),'road_name':row.get('Rname'),
            'capture_pitch_deg':row.get('Pitch'),'capture_roll_deg':row.get('Roll'),'vehicle_heading_deg':row.get('MoveDir'),
            'current_provider_routes':[{'id':road.get('ID'),'count':len(road.get('Panos') or []),'order':next((item['Order'] for item in road.get('Panos') or [] if item['PID']==path.stem),None)} for road in row.get('Roads',[]) if road.get('IsCurrent')],'bd09':bd,'gcj02':gcj,'wgs84':wgs,'roundtrip_deg':residual,
            'en':en,'legacy_bridge_park_en':source,
            'roads':[{'id':ident,'distance_m':h[0],'projection':h[1],'tags':ways[ident]['tags']} for h,ident in nearest[:6]]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('top','lower','guide','old_bridge_field','result'):
        p.add_argument(name,type=Path)
    a=p.parse_args()
    guide=json.loads(a.guide.read_text())
    bridge=json.loads(a.old_bridge_field.read_text())
    legacy={s.get('pano',s.get('panoid')):s['camera_game_east_north'] for s in bridge['street_view'].values()}
    upper=[register(a.top/(r['pano']+'.json'),guide['map_registration'],guide['ways']) for r in guide['pano']]
    lower=[register(a.lower/(pid+'.json'),guide['map_registration'],guide['ways'],legacy.get(pid)) for pid in LOWER]
    values=[u['raw_z']-v['raw_z'] for u in upper for v in lower]
    a.result.write_text(json.dumps({'upper':upper,'lower':lower,'raw_cross_layer_ranges_m':[min(values),max(values)],
        'raw_range_note':'Extrema over the two independently driven camera routes. Z is used only as relative corroboration. All selected records give DeviceHeight 2.32 m and provider 9. The absolute vertical datum and a per-day bias are unresolved.'},indent=2,ensure_ascii=False)+'\n')


if __name__=='__main__':
    main()
