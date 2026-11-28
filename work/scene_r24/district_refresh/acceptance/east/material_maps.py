"""Generate the small East material maps and trace their existing scan inputs."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

SIZE=512
ROOT=Path(__file__).resolve().parents[4]/'project/chongqing_godot_v05/assets'


def rescale(a):
    low,high=np.percentile(a,[1.5,98.5])
    return np.clip((a-low)/max(high-low,.01),0,1)


def noise(rng, cells):
    raw=(rng.random((cells,cells))*255).astype(np.uint8)
    border=np.pad(raw,1,mode='wrap')
    target=round(SIZE*(cells+2)/cells)
    enlarged=np.asarray(Image.fromarray(border).resize((target,target),Image.Resampling.BICUBIC),dtype=float)/255
    start=(target-SIZE)//2
    return enlarged[start:start+SIZE,start:start+SIZE]


def save(target,name,pixels):
    a=np.clip(np.rint(pixels*255.),0,255).astype(np.uint8)
    Image.fromarray(a).save(target/name,quality=92,optimize=True)


def normal_map(height,strength):
    x=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*strength
    y=(np.roll(height,1,axis=0)-np.roll(height,-1,axis=0))*strength
    out=np.dstack((-x,-y,np.ones_like(x)))
    out /= np.linalg.norm(out,axis=2)[:,:,None]
    return out*.5+.5


def food(target):
    v,u=np.mgrid[0:1:complex(SIZE),0:1:complex(SIZE)]
    for name,lo,hi,rough,seed in (
        ('mandarin',(.54,.155,.032),(.94,.53,.145),.59,201),
        ('aubergine',(.125,.063,.126),(.395,.230,.36),.44,202),
        ('squash',(.46,.193,.045),(.93,.67,.243),.63,203),
        ('potato',(.38,.235,.123),(.78,.67,.475),.76,204),
    ):
        rng=np.random.default_rng(seed)
        variety=noise(rng,8)
        patches=noise(rng,31)
        micro=noise(rng,112)
        very_fine=rng.random((SIZE,SIZE))
        pores=np.maximum(0.,(.49-micro))*1.4
        if name=='aubergine':
            streaks=np.sin(u*(2*np.pi*9)+patches*3) *.5+.5
            texture=variety*.46+streaks*.26+patches*.18+very_fine*.10
        elif name=='squash':
            ribs=(np.sin(u*2*np.pi*9+.36*np.sin(v*2*np.pi))*.5+.5)
            texture=.41*patches+.25*variety+.29*ribs+.05*very_fine
        else:
            texture=variety*.41+patches*.27+micro*.22+very_fine*.10
        if name=='potato':
            spots=(np.square(np.maximum(0.,patches+micro-1.10))*2.7)
            texture*=1-np.clip(spots,0,.67)
        if name=='mandarin':
            texture*=1-pores*.27
        coeff=rescale(texture)
        rgb=np.asarray(lo)+coeff[...,None]*(np.asarray(hi)-lo)
        height=.45*patches+.29*variety+.26*micro
        save(target,name+'-albedo.jpg',rgb)
        save(target,name+'-normal.jpg',normal_map(height,2.2))
        save(target,name+'-rough.jpg',np.clip(rough+(coeff-.5)*.22,.25,.95))


def planter_ground(target):
    rng=np.random.default_rng(22107)
    grass=rescale(noise(rng,14)*.27+noise(rng,51)*.33+noise(rng,175)*.28+rng.random((SIZE,SIZE))*.12)
    v,u=np.mgrid[0:1:complex(SIZE),0:1:complex(SIZE)]
    stems=(np.sin(u*2*np.pi*93+np.sin(v*2*np.pi*11+grass*3))*.5+.5)
    base=np.clip(.83*grass+.17*stems,0,1)
    color=np.asarray((.16,.26,.060))+base[...,None]*np.asarray((.32,.29,.15))
    save(target,'turf-albedo.jpg',color)
    save(target,'turf-normal.jpg',normal_map(.68*grass+.32*stems,1.55))
    save(target,'turf-rough.jpg',.72+.20*(1-grass))
    sandstone=Image.open(ROOT/'district_r21/terraces_washed_sandstone.jpg').convert('L').resize((SIZE,SIZE))
    height=rescale(np.asarray(sandstone,dtype=float)/255)
    warm=np.asarray((.48,.445,.385))+height[...,None]*np.asarray((.365,.35,.32))
    save(target,'washed-stone-buff-albedo.jpg',warm)
    save(target,'washed-stone-normal.jpg',normal_map(height,1.83))
    save(target,'washed-stone-rough.jpg',.74+.17*(1-height))
    gravel=Image.open(ROOT/'chongqing_district_leaf_scattered_gravel_diff_2k.jpg').convert('L').resize((SIZE,SIZE))
    grain=rescale(np.asarray(gravel,dtype=float)/255)
    sand=np.asarray((.48,.456,.399))+grain[...,None]*np.asarray((.45,.43,.43))
    save(target,'pale-gravel-albedo.jpg',sand)
    shrub=np.asarray(Image.open(ROOT/'chongqing_district_shrub_01_diff_2k.jpg').convert('RGB').resize((SIZE,SIZE)),
                     dtype=float)/255
    veins=np.clip(shrub[...,1]*.68+shrub[...,0]*.27,0,1)
    purple=np.asarray((.165,.035,.100))+veins[...,None]*np.asarray((.39,.155,.26))
    save(target,'purple-leaf-dusk-albedo.jpg',purple)


def ginger_atlas(target):
    scan=ROOT/'connections_r24/ginger'
    sources=[np.asarray(Image.open(scan/('food_ginger_01_'+suffix+'_1k.jpg')).convert('RGB')).copy()
             for suffix in ('diff','nor_gl','rough')]
    mask=sources[0].max(axis=2)>8
    # Extend the atlas islands into their unused gutters before texture
    # compression. At counter distance the sampled mip otherwise mixes the
    # black background into the skin, the normal vectors and the roughness.
    for _ in range(18):
        extended=mask.copy()
        for axis,direction in ((0,-1),(1,1),(0,1),(1,-1)):
            adjacent=np.roll(mask,direction,axis)
            borders=(0 if direction>0 else -1)
            if axis==0:
                adjacent[borders,:]=False
            else:
                adjacent[:,borders]=False
            patch=adjacent & ~extended
            for source in sources:
                source[patch]=np.roll(source,direction,axis)[patch]
            extended|=patch
        mask=extended
    for name, source, neutral in zip(('albedo','normal','rough'),sources,
                                     ((161,132,105),(128,128,255),(199,199,199)),strict=True):
        source[~mask]=neutral
        Image.fromarray(source).save(target/('ginger-scan-'+name+'.jpg'),quality=95,subsampling=0,optimize=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path,nargs='?',default=ROOT/'district_500/acceptance_textures')
    out=parser.parse_args().output
    out.mkdir(exist_ok=True,parents=True)
    food(out)
    planter_ground(out)
    ginger_atlas(out)


if __name__=='__main__':
    main()
