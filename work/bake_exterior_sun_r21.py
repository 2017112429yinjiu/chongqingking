"""Project the existing scanned canopy silhouettes onto the distant district."""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def bake(layout, profile, canopy_folder, output, size=1536, radius=360):
    # Coordinates are Blender plan X/Y. Altitude is projected onto a horizontal
    # receiver; the resulting field drapes over the authored surrounding hills.
    elevation, azimuth, _ = profile['lighting']['sun_rotation_deg']
    heading = math.radians(azimuth)
    shadow = np.array([-math.sin(heading), math.cos(heading)])
    cross = np.array([math.cos(heading), math.sin(heading)])
    tangent = math.tan(math.radians(abs(elevation)))
    exposure = np.ones((size, size), dtype=np.float32)
    root_contact = np.zeros_like(exposure)
    scale = size / (2 * radius)
    templates = {}
    for kind in range(2):
        for face in range(4):
            with Image.open(canopy_folder / f'{kind}_{face}.png') as tile:
                alpha = tile.getchannel('A').resize((112,112), Image.Resampling.BOX)
                templates[kind,face] = np.asarray(alpha, dtype=np.float32)/255

    for tree in layout['outer_canopy']:
        x, _, z = tree['position']
        y = -z
        kind = tree['kind']
        species = ['tree_small_02', 'island_tree_01'][kind]
        width = tree['height'] * layout['canopy_pivots'][species]['frame_width_over_height']
        reach = (tree['height']/tangent + width/2 + 2) * scale
        u, v = (x+radius)*scale, (y+radius)*scale
        x0,x1 = max(0,int(u-reach)), min(size,math.ceil(u+reach))
        y0,y1 = max(0,int(v-reach)), min(size,math.ceil(v+reach))
        yy,xx = np.mgrid[y0:y1,x0:x1]
        dx,dy = (xx+.5-u)/scale, (yy+.5-v)/scale
        across = (dx*cross[0]+dy*cross[1])/width
        along = (dx*shadow[0]+dy*shadow[1])*tangent/width
        # Match the horizontal handedness of the Blender orthographic bake.
        tx = np.floor((.5+across)*112).astype(int)
        ty = np.floor((.98-along)*112).astype(int)
        inside = (tx>=0)&(tx<112)&(ty>=0)&(ty<112)
        face = math.floor((heading-tree['yaw'])/(math.pi/2)+.5)%4
        opacity = np.where(inside,templates[kind,face][ty.clip(0,111),tx.clip(0,111)],0)
        exposure[y0:y1,x0:x1] *= 1-opacity*.92
        root_radius = max(.60,tree['height']*.12)
        root = np.exp(-(dx*dx+dy*dy)/(2*root_radius*root_radius))
        np.maximum(root_contact[y0:y1,x0:x1], root, out=root_contact[y0:y1,x0:x1])

    def channel(values, blur):
        return Image.fromarray(np.uint8(np.clip(values,0,1)*255)).filter(ImageFilter.GaussianBlur(blur))
    # Separate ground receiver shadow, diffuse root contact and broad shade.
    out = Image.merge('RGB', (channel(1-exposure,1.45),channel(root_contact,.52),channel(1-exposure,6.5)))
    out.save(output)
    return {'tree_sites':len(layout['outer_canopy']),'size':size,'extent_m':radius*2,
            'sun_yaw_deg':azimuth,'elevation_deg':abs(elevation),
            'method':'Four photographed tree directions projected onto a planar receiver then sampled on existing outer terrain. Fixed daylight.'}


if __name__ == '__main__':
    work = Path(__file__).resolve().parent
    assets = work / 'project/chongqing_godot_v05/assets'
    district = assets / 'district_r21'
    read = lambda path:json.loads(path.read_text(encoding='utf8'))
    metadata = bake(read(district/'layout.json'),read(assets/'render_profile_r21.json'),
                    work/'scene_r21/canopy',district/'exterior_sun_mask.png')
    (work/'scene_r21/exterior_sun_bake.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
