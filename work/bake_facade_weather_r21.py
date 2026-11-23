"""Paint rain tracks under actual sills and damp bands at the street base."""
from pathlib import Path
from PIL import Image
import numpy as np,json,math
W=Path(__file__).resolve().parent
src=W/'project/chongqing_blender_v05/architecture_manifest.json'
A=W/'project/chongqing_godot_v05/assets/district_r21'
B=json.loads(src.read_text(encoding='utf8'))['buildings']
tw,th,cols=384,192,8;rows=math.ceil(len(B)*4/cols)
atlas=np.zeros((rows*th,cols*tw,3),dtype=np.uint8)
records={};rng=np.random.default_rng(68041)
for k,b in enumerate(B):
    pts=np.array(b['points'])
    low=pts.min(axis=0)-.3;high=pts.max(axis=0)+.3
    z0=b['base_m']-3;z1=b['base_m']+b['height_m']+1.
    walls=[np.zeros((th,tw,3),np.float32) for n in range(4)]
    profile=[np.full(tw,np.nan,dtype=np.float32) for n in range(4)]
    count=0
    for e in b['facade_openings']:
        a=np.array(e['a']);d=np.array(e['b'])-a;d/=np.linalg.norm(d)
        nx,ny=d[1],-d[0]
        card=(0 if nx>0 else 1) if abs(nx)>abs(ny) else (2 if ny>0 else 3)
        axis=1 if card<2 else 0
        x=np.linspace(low[axis],high[axis],tw)
        z=np.linspace(z1,z0,th)[:,None]
        wall=walls[card]
        s0,s1=sorted([a[axis],np.array(e['b'])[axis]])
        profile[card][(x>=s0)&(x<=s1)]=b['base_m']
        for l,r,bottom,top in e['holes']:
            if bottom<.48:continue
            count+=1
            for u in [l-.04,r+.04]:
                if rng.random()<.24:continue
                sill=b['base_m']+bottom-.065
                down=sill-z
                age=rng.uniform(.4,1.);reach=rng.uniform(.34,1.60);width=rng.uniform(.047,.17)
                at=(a+d*u)[axis]
                drift=rng.uniform(-.058,.058)*np.clip(down,0,reach)
                dx=x[None,:]-at-drift
                strength=np.exp(-.5*(dx/width)**2)*np.exp(-np.maximum(0,down)/(reach*.49))
                strength*=np.clip((down+.075)/.10,0,1)*np.clip((reach-down)/.19,0,1)*age
                pigment=0 if rng.random()<.76 else 1
                np.maximum(wall[:,:,pigment],strength, out=wall[:,:,pigment])
                wide=.24*np.exp(-.5*(dx/(width*2.55))**2)*np.exp(-np.maximum(0,down)/.49)*np.clip(down/.1,0,1)
                np.maximum(wall[:,:,0],wide,out=wall[:,:,0])
    for card,wall in enumerate(walls):
        axis=1 if card<2 else 0
        x=np.linspace(low[axis],high[axis],tw)
        z=np.linspace(z1,z0,th)[:,None]
        # Intermittent mineral splash/wicking along the plinth, varying by wall.
        height=b['base_m']+.29+.17*np.sin(x*1.54)+.079*np.cos(x*4.6)
        damp=np.clip((height[None,:]-z)/.25+.28,0,1)*np.clip((z-(b['base_m']-.61))/.3,0,1)
        wall[:,:,2]=damp*(.59+.18*np.sin(x*.74))[None,:]*np.isfinite(profile[card])[None,:]
        i=k*4+card;yy=i//cols*th;xx=i%cols*tw
        atlas[yy:yy+th,xx:xx+tw]=(np.clip(wall,0,1)*255).astype('uint8')
    records[str(b['id'])]={'first_tile':k*4,'min':[float(low[0]),float(low[1]),z0],'span':[float(high[0]-low[0]),float(high[1]-low[1]),z1-z0],'window_or_sill_openings':count}
Image.fromarray(atlas).save(A/'wall_runoff.png')
(A/'wall_fields.json').write_text(json.dumps({'atlas_grid':[cols,rows],'tile_px':[tw,th],'buildings':records,'method':'Four facade orientations per building. Edge projections of measured apertures, rain-wash, lime and damp plinth; a designed weathering field, not a moisture simulation.'},indent=2),encoding='utf8')
