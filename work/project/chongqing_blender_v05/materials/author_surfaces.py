"""Author repeatable PBR data maps from mathematical surface models.

No photographs or supplied reference-image pixels are read by this script.
The seven reused Poly Haven scans are copied byte-for-byte, with their credits.
Run using the regular Python interpreter (NumPy and Pillow required).
"""
from pathlib import Path
import json, shutil, hashlib
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'chongqing_refined/materials'
MANIFEST = {'version': 3, 'surface_revision': 4, 'assets': {}, 'files': [], 'notes': [
    'Reused Poly Haven scans are byte-identical CC0 source assets.',
    'Authored maps are computed from analytic shapes and seeded noise; no street-view, photograph, or reference-image pixels are incorporated.',
    'These materials describe an authored environment, not surveyed surface reproduction.'
]}


def periodic_noise(n, cells, seed):
    rng = np.random.default_rng(seed)
    grid = rng.random((cells, cells), dtype=np.float32)
    # A periodic interpolation grid avoids obvious seams on repeated surfaces.
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    xx *= cells/n; yy *= cells/n
    x0 = np.floor(xx).astype(np.int32); y0 = np.floor(yy).astype(np.int32)
    u = xx-x0; v = yy-y0
    u = u*u*(3-2*u); v = v*v*(3-2*v)
    return ((1-u)*(1-v)*grid[y0 % cells, x0 % cells] +
            u*(1-v)*grid[y0 % cells, (x0+1) % cells] +
            (1-u)*v*grid[(y0+1) % cells, x0 % cells] +
            u*v*grid[(y0+1) % cells, (x0+1) % cells])


def fbm(n, seed, levels=(4, 11, 29, 71, 177), weights=(.35,.26,.18,.13,.08)):
    out = np.zeros((n,n),np.float32)
    for i,(c,w) in enumerate(zip(levels,weights)):
        out += periodic_noise(n,c,seed+101*i)*w
    return out


def normal_from_height(height_m, meters):
    n = len(height_m)
    dx = (np.roll(height_m,-1,axis=1)-np.roll(height_m,1,axis=1))*n/(2*meters)
    dy = (np.roll(height_m,-1,axis=0)-np.roll(height_m,1,axis=0))*n/(2*meters)
    vec = np.stack((-dx,dy,np.ones_like(dx)),axis=-1)
    vec /= np.linalg.norm(vec,axis=-1,keepdims=True)
    return np.round((vec*.5+.5)*255).astype(np.uint8)


def write_surface(key, color, rough, height, meters, description, normal_strength=.65, alpha=None, metallic=0., storage_key=None):
    storage_key=storage_key or key
    folder = HERE/storage_key; folder.mkdir(parents=True,exist_ok=True)
    n = color.shape[0]
    color = np.clip(color,0,1)
    maps={}
    if alpha is not None:
        rgba = np.concatenate((color,np.clip(alpha[...,None],0,1)),axis=-1)
        p=folder/(storage_key+'_diff.png')
        Image.fromarray(np.round(rgba*255).astype(np.uint8),'RGBA').save(p)
    else:
        p=folder/(storage_key+'_diff.jpg')
        Image.fromarray(np.round(color*255).astype(np.uint8),'RGB').save(p,quality=93,subsampling=0)
    maps['diff']=str(p.relative_to(HERE))
    if height is not None:
        p=folder/(storage_key+'_nor_gl.jpg')
        Image.fromarray(normal_from_height(height,meters),'RGB').save(p,quality=95,subsampling=0)
        maps['nor_gl']=str(p.relative_to(HERE))
    if isinstance(rough,np.ndarray):
        p=folder/(storage_key+'_rough.jpg')
        Image.fromarray(np.round(np.clip(rough,0,1)*255).astype(np.uint8),'L').save(p,quality=94)
        maps['rough']=str(p.relative_to(HERE))
        rough_default=.8
    else: rough_default=float(rough)
    MANIFEST['assets'][key]={
        'origin':'Original mathematical material authoring',
        'license':'Project-authored; no third-party source imagery',
        'authors':['Project procedural material authoring'],
        'source_url':'', 'meters':meters, 'resolution_px':[n,n],
        'maps':maps,'normal_strength':normal_strength,
        'roughness':rough_default,'metallic':metallic,
        'alpha':alpha is not None,'description':description
    }


def write_credits():
    lines=['重庆街区 v03 材质来源','',
           '采用的 Poly Haven 原始扫描贴图文件保持未修改，许可 CC0 1.0。',
           '许可：https://polyhaven.com/license','']
    seen=set()
    for key,spec in MANIFEST['assets'].items():
        asset=spec.get('asset')
        if not asset or asset in seen:continue
        seen.add(asset)
        lines.extend([f"{key}: {asset} — {', '.join(spec['authors'])}",spec['source_url'],''])
    lines.extend([
        'brick_dark 使用 Brick Wall 08 原始漫反射贴图与设定粗糙度，未混用不匹配的法线贴图。',
        '原创 ceramic/plaster/stone/roof/rust/timber/soil/grime/court 材质由本项目数学表面模型和确定性噪声生成，不读取街景或参考照片像素。',
        '球场贴图按照场景 palette 的线性色转换到 sRGB，保留既有配色；细纹与小面积磨损由原创数学模型生成。',
        '瓷砖 v4 经真实引擎对照修正：移除原程序材质的大尺度云状污色，保留逐片釉色微差、细砖缝、小缺角与稀疏细渗水。',
        '逐图文件校验、实际采用通道、来源与物理 UV 比例见 material_provenance.json。',''])
    (HERE/'CREDITS_zh.txt').write_text('\n'.join(lines),encoding='utf-8')


def ceramic(key,base,seed):
    n=2048; meters=2.4
    yy,xx=np.mgrid[0:n,0:n].astype(np.float32)
    u=xx/n*16; v=yy/n*32
    ix=np.floor(u).astype(int); iy=np.floor(v).astype(int)
    fx=u-ix; fy=v-iy
    edge=np.minimum(np.minimum(fx,1-fx),np.minimum(fy,1-fy)*.5)
    rng=np.random.default_rng(seed)
    variation=rng.uniform(-.024,.024,(32,16))[iy,ix]
    fine=fbm(n,seed+2,(43,137,359,739),(.12,.20,.32,.36))
    grain=rng.normal(0,.12,(n,n)).astype(np.float32)
    # Real-engine inspection exposed repeated metre-scale cloud stains in the
    # former base color. Keep age variation local to glaze, grout and tiny
    # chips. Large damp bands belong to separately placed facade overlays.
    mortar = edge < (.011 + .004*(fine-.5))
    bevel = np.clip((edge-.010)/.016,0,1)
    color=np.array(base)[None,None,:]+variation[...,None]+(fine-.5)[...,None]*.035+grain[...,None]*.022
    # Sparse, narrow gravity-aligned seepage, at low contrast. No macro cloud
    # term is used in either diffuse or roughness maps.
    seep=np.zeros((n,n),np.float32)
    for _ in range(10):
        start_x=float(rng.uniform(0,n));start_y=float(rng.uniform(0,n))
        width=float(rng.uniform(1.2,3.8));length=float(rng.uniform(.07,.26)*n)
        dx=np.abs(xx-start_x);dx=np.minimum(dx,n-dx)
        dy=(yy-start_y)%n
        line=np.exp(-(dx/width)**2)*np.clip(1-dy/length,0,1)**1.5
        seep+=line*(.45+.55*fine)
    color-=np.minimum(seep,.8)[...,None]*.032
    grout=np.array([.285,.295,.275])[None,None,:]+(fine-.5)[...,None]*.075
    color=np.where(mortar[...,None],grout,color)
    chip_tile=(rng.random((32,16))<.12)[iy,ix]
    chip_x=rng.uniform(.12,.88,(32,16))[iy,ix]
    chip_top=(rng.random((32,16))>.5)[iy,ix]
    chip_depth=np.where(chip_top,1-fy,fy)
    chips=chip_tile&(np.abs(fx-chip_x)<.035+.035*fine)&(chip_depth<.045+.018*fine)
    color=np.where(chips[...,None],np.array([.39,.40,.37])+(fine-.5)[...,None]*.04,color)
    height=.0012*bevel + (fine-.5)*.00008+grain*.00002
    height[mortar]-=.00035
    height[chips]-=.00035
    rough=.60+.08*fine+variation*.5+seep*.02
    rough[mortar]=.9
    rough[chips]=.84
    write_surface(key,color,rough,height,meters,'Aged 150 x 75 mm ceramic cladding; restrained tile-wise glaze differences, 3 mm joints, sparse small edge chips and faint thin seepage. Metre-scale dark cloud masks removed after real-engine review.',.55,storage_key=key+'_v4')


def plaster(key,base,seed):
    n=2048; meters=4.
    # Primary scene review found the earlier large dark clouds too obvious.
    # Keep broad pigment variation low and place texture in the aggregate.
    cloud=periodic_noise(n,7,seed)*.30+periodic_noise(n,19,seed+1)*.70
    aggregate=fbm(n,seed+2,(31,79,173,353,700),(.15,.18,.24,.23,.20))
    rng=np.random.default_rng(seed+7)
    grain=rng.normal(0,.18,(n,n)).astype(np.float32)
    chipmask=(periodic_noise(n,53,seed+4)>.74)&(periodic_noise(n,211,seed+5)>.67)
    pores=rng.random((n,n))<.0045
    color=np.array(base)[None,None,:]+(cloud-.5)[...,None]*.065+(aggregate-.5)[...,None]*.13+grain[...,None]*.045
    under=np.array([.405,.405,.375])[None,None,:]+(aggregate-.5)[...,None]*.14
    color=np.where(chipmask[...,None],under,color)
    color[pores]*=.73
    height=(aggregate-.5)*.0015+grain*.0004-chipmask*.00065-pores*.00035
    rough=.80+.14*aggregate+.02*grain
    write_surface(key,color,rough,height,meters,'Fine mineral plaster with subtle pigment variation, millimetre aggregate, sparse chipped paint and tiny pores; reduced large soot clouds after scene review.',.5)


def dark_brick():
    n=2048; meters=2.4
    yy,xx=np.mgrid[0:n,0:n].astype(np.float32)
    v=yy/n*24; row=np.floor(v).astype(int); fy=v-row
    u=xx/n*9+(row%2)*.5; col=np.floor(u).astype(int)%9; fx=u-np.floor(u)
    noise=fbm(n,720)
    edge=np.minimum(np.minimum(fx,1-fx)*.27,np.minimum(fy,1-fy)*.10)
    mortar=edge<.004+(noise-.5)*.0015
    rng=np.random.default_rng(927)
    var=rng.uniform(-.07,.07,(24,9))[row,col]
    color=np.stack([.32+var,.335+var,.315+var],axis=-1)+(noise-.5)[...,None]*.13
    color=np.where(mortar[...,None],np.array([.22,.225,.215]),color)
    height=np.clip((edge-.0035)/.005,0,1)*.003+(noise-.5)*.0007
    write_surface('brick_dark',color,.78+noise*.16,height,meters,'Smoke-grey heritage brick, staggered courses and weathered recessed mortar.',.65)


def stone():
    n=2048; meters=1.5
    yy,xx=np.mgrid[0:n,0:n].astype(np.float32)
    row=np.floor(yy/n*8).astype(int); fy=yy/n*8-row
    row_offsets=np.array([0.,.43,.12,.57,.02,.35,.16,.61],np.float32)
    ux=xx/n*5+row_offsets[row]
    col=np.floor(ux).astype(int)%5; fx=ux-np.floor(ux)
    noise=fbm(n,1324,(17,43,97,211,512),(.20,.25,.23,.20,.12)); fine=periodic_noise(n,700,283)
    edge=np.minimum(np.minimum(fx,1-fx)*.30,np.minimum(fy,1-fy)*.1875)
    edge += (noise-.5)*.008
    rng=np.random.default_rng(1134)
    var=rng.uniform(-.035,.035,(8,5))[row,col]
    dark=np.clip((periodic_noise(n,11,1427)-.63)*.75,0,.12)
    color=np.stack([.43+var,.435+var,.405+var],axis=-1)+(noise-.5)[...,None]*.24+(fine-.5)[...,None]*.055
    color*=1-dark[...,None]
    mortar=edge<.0045
    color=np.where(mortar[...,None],np.array([.28,.29,.265])+(noise-.5)[...,None]*.12,color)
    height=np.clip((edge-.003)/.008,0,1)*.0045+(noise-.5)*.002+(fine-.5)*.0005
    write_surface('stone',color,.84+noise*.12,height,meters,'Small weathered retaining blocks, about300 x188mm; staggered irregular joints, broken edges and granular stone. Scale reduced after full-scene review.',.6)


def roof():
    n=2048; meters=3.2
    yy,xx=np.mgrid[0:n,0:n].astype(np.float32)
    u=xx/n*20; v=yy/n*12
    row=np.floor(v).astype(int); col=np.floor(u).astype(int)
    fx=u-col; fy=v-row
    noise=fbm(n,8293)
    arc=np.sqrt(np.clip(1-((fx-.5)*2)**2,0,1))
    height=arc*.008+fy*.0018+(noise-.5)*.0007
    joints=(fy<.035)|(fx<.035)|(fx>.965)
    height[joints]-=.0012
    rng=np.random.default_rng(834)
    var=rng.uniform(-.04,.04,(12,20))[row,col]
    shade=.285+var+(noise-.5)*.13
    color=np.stack((shade*.97,shade,shade*.97),axis=-1)
    color[joints]*=.68
    write_surface('roof_tiles',color,.77+noise*.16,height,meters,'Dark grey fired-clay barrel tiles, 160 mm spacing; tile-wise age variation and fine grit.',.7)


def rust():
    n=1024; meters=1.2
    noise=fbm(n,8373)
    pitting=periodic_noise(n,221,127)
    rust=np.clip((noise-.4)*4,0,1)
    oldpaint=np.array([.26,.29,.26])[None,None,:]
    oxidized=np.stack((.30+noise*.16,.13+noise*.10,.065+noise*.065),axis=-1)
    color=oldpaint*(1-rust[...,None])+oxidized*rust[...,None]
    color+=(pitting-.5)[...,None]*.08
    height=(noise-.5)*.0007-(pitting>.83)*.0005
    write_surface('rust_texture',color,.56+.35*rust,height,meters,'Pitted metal with irregular oxidized patches and surviving dark green paint.',.65,metallic=.34)


def timber():
    n=2048; meters=2.
    yy,xx=np.mgrid[0:n,0:n].astype(np.float32)
    cloud=fbm(n,8345)
    fine=periodic_noise(n,711,986)
    u=xx/n*180 + 2.7*np.sin(yy/n*15) + cloud*5
    grain=(np.sin(u*2*np.pi)*.5+.5)
    knots=(np.sin(xx/n*13+np.sin(yy/n*11)*1.2)*.5+.5)*.06
    shade=.27+.095*cloud-.065*grain+knots
    color=np.stack((shade*1.1,shade*.78,shade*.52),axis=-1)
    color+=(fine-.5)[...,None]*.035
    height=grain*.00055+(fine-.5)*.00015
    write_surface('timber',color,.65+.26*cloud,height,meters,'Worn dark timber grain with restrained amber color; suitable for beams, doors and balcony frames.',.65)


def soil():
    n=2048; meters=3.2
    cloud=periodic_noise(n,6,1926)
    noise=fbm(n,1947,(31,79,173,353,700),(.16,.20,.24,.22,.18))
    rng=np.random.default_rng(1355)
    fine=rng.normal(0,.18,(n,n)).astype(np.float32)
    moss=np.clip((cloud-.46)*1.4,0,.26)
    color=np.array([.305,.30,.255])[None,None,:]+(noise-.5)[...,None]*.15+(cloud-.5)[...,None]*.055+fine[...,None]*.06
    color=color*(1-moss[...,None])+np.array([.235,.27,.19])[None,None,:]*moss[...,None]
    height=(noise-.5)*.0023+(cloud-.5)*.002+fine*.00045
    # Uneven mineral flecks provide genuine spatial structure at centimetre
    # scale instead of a single brown cloud field across the whole terrain.
    for _ in range(7800):
        cx=int(rng.integers(6,n-6));cy=int(rng.integers(6,n-6))
        rx=float(rng.uniform(.65,4.8));ry=rx*float(rng.uniform(.45,1.35))
        rad=int(np.ceil(max(rx,ry)))+1
        x0=max(0,cx-rad);x1=min(n,cx+rad+1);y0=max(0,cy-rad);y1=min(n,cy+rad+1)
        yy,xx=np.mgrid[y0:y1,x0:x1]
        shape=((xx-cx)/rx)**2+((yy-cy)/ry)**2
        mask=shape<1
        value=float(rng.uniform(.26,.46))
        pebble=np.array([value*1.02,value,value*.93])
        region=color[y0:y1,x0:x1]
        region[mask]=pebble+(1-shape[mask,None])*.025
        height[y0:y1,x0:x1][mask]+=np.sqrt(1-shape[mask])*.0017
    write_surface('ground_dirt',color,.85+noise*.12,height,meters,'Damp neutral earth, sparse small gravel grains and restrained olive moss patches; granular close-up detail added after street review.',.45)


def court_surface(key, linear_base, seed):
    """Mineral-filled sports paint; keep the scene palette's linear color.

    These maps are authored mathematical material data. Tiny aggregate,
    pores and sparse scuffs add close detail without a repeating cloud mask.
    """
    n=2048;meters=5.
    base=np.array(linear_base,np.float32)
    # Blender's solid-color palette uses linear values; image nodes use sRGB.
    base=np.where(base<=.0031308,base*12.92,1.055*base**(1/2.4)-.055)
    rng=np.random.default_rng(seed)
    grain=rng.normal(0,.22,(n,n)).astype(np.float32)
    aggregate=fbm(n,seed+4,(149,367,887),(.16,.31,.53))
    paint=periodic_noise(n,37,seed+9)
    pores=rng.random((n,n))<.004
    color=base[None,None,:]+(aggregate-.5)[...,None]*.09+grain[...,None]*.055+(paint-.5)[...,None]*.012
    height=(aggregate-.5)*.00085+grain*.00032-pores*.00025
    rough=.925+(aggregate-.5)*.055+grain*.015
    color[pores]*=.88
    # A few centimetre-sized, gently feathered scuffs expose a little darker
    # mineral. No painted court lines are baked into this repeatable material.
    for _ in range(34):
        cx=int(rng.integers(42,n-42));cy=int(rng.integers(24,n-24))
        rx=float(rng.uniform(8,34));ry=float(rng.uniform(2.5,9.5))
        radx=int(np.ceil(rx))+1;rady=int(np.ceil(ry))+1
        x0=cx-radx;x1=cx+radx+1;y0=cy-rady;y1=cy+rady+1
        yy,xx=np.mgrid[y0:y1,x0:x1]
        dist=((xx-cx)/rx)**2+((yy-cy)/ry)**2
        scuff=np.clip(1-dist,0,1)*.15
        scuff*=.45+.55*rng.random(scuff.shape)
        color[y0:y1,x0:x1]*=(1-scuff[...,None])
        height[y0:y1,x0:x1]-=scuff*.00045
        rough[y0:y1,x0:x1]-=scuff*.12
    write_surface(key,color,rough,height,meters,'Fine-grained matte sports-court coating; original seeded aggregate, tiny pores and sparse centimetre-sized worn scuffs. Color matches the scene palette in linear space.',.42)
    MANIFEST['assets'][key]['scene_palette_linear']=list(linear_base)


def overlay(key,seed,moss=False):
    n=1024; yy,xx=np.mgrid[0:n,0:n].astype(np.float32); y=yy/n
    cloud=fbm(n,seed)
    noise=periodic_noise(n,100,seed+5)
    if moss:
        alpha=np.clip((cloud-.48)*3.6,0,.60)
        alpha*=np.clip((1-y)*1.5,0,1)
        color=np.stack((.13+cloud*.07,.17+cloud*.09,.075+cloud*.05),axis=-1)
    else:
        rng=np.random.default_rng(seed)
        streak=np.zeros((n,n),np.float32)
        for _ in range(38):
            x0=rng.uniform(0,n);width=rng.uniform(1.5,9);length=rng.uniform(.12,.95)
            horizontal=np.exp(-((xx-x0)/width)**2)
            vertical=np.clip((length-y)/length,0,1)**.6
            streak+=horizontal*vertical*rng.uniform(.1,.42)
        alpha=np.clip(streak*(.65+cloud*.7)+np.clip(cloud-.57,0,1)*.25,0,.55)
        color=np.stack((.15+cloud*.045,.145+cloud*.045,.12+cloud*.04),axis=-1)
    # Fade texture edges; each quad has soft, unobtrusive boundaries.
    edge=np.minimum(np.minimum(xx/n,1-xx/n),np.minimum(yy/n,1-yy/n))
    alpha*=np.clip(edge*30,0,1)
    write_surface(key,color,.96,None,4.,'Subtle transparent '+('moss residue at masonry base' if moss else 'rain streaks below eaves and drain fixtures')+'; authored mask, no photo pixels.',alpha=alpha)


def main():
    src=json.loads((SOURCE/'material_provenance.json').read_text())
    for key,spec in src['assets'].items():
        new=dict(spec); new.update({'origin':'Poly Haven scan, reused unchanged','license':'CC0-1.0','license_url':'https://polyhaven.com/license'})
        new['maps']={}
        for role in ('diff','rough','nor_gl'):
            rel=f"{key}/{spec['asset']}_{role}_{spec['resolution']}.jpg"
            (HERE/key).mkdir(parents=True,exist_ok=True)
            shutil.copy2(SOURCE/rel,HERE/rel)
            new['maps'][role]=rel
        if key=='tile':new['meters']=2.0
        new['normal_strength']=.62 if key in ('concrete','bark') else .55
        MANIFEST['assets'][key]=new
    ceramic('tile_blue',(.56,.61,.60),391)
    ceramic('tile_cream',(.68,.65,.56),782)
    plaster('plaster_ochre',(.64,.605,.52),122)
    plaster('plaster_grey',(.57,.575,.54),427)
    dark_brick(); stone(); roof(); rust(); timber(); soil()
    court_surface('court_green',(.12,.20,.18),5121)
    court_surface('court_red',(.26,.12,.087),5122)
    overlay('grime_streak',414); overlay('moss_grime',173,True)
    wet=dict(MANIFEST['assets']['pavement'])
    wet['maps']={k:v for k,v in wet['maps'].items() if k!='rough'}
    wet['roughness']=.30
    wet['description']='Original pavement maps with a lower authored roughness value; use sparingly on damp pavement patches.'
    MANIFEST['assets']['wet_pavement']=wet
    if (HERE/'scan_overrides.json').exists():
        overrides=json.loads((HERE/'scan_overrides.json').read_text())
        MANIFEST['assets'].update(overrides['assets'])
        MANIFEST['notes'][0]='Reused and additional Poly Haven assets are unmodified CC0 sources. Additional original analytic maps provide ceramic/plaster variation and weathering masks. See each material map list for channels actually supplied.'
    seen=set()
    for key,spec in MANIFEST['assets'].items():
        for role,rel in spec['maps'].items():
            if rel in seen:continue
            seen.add(rel);path=HERE/rel
            with Image.open(path) as im:
                im.verify()
            MANIFEST['files'].append({'local_path':rel,'role':role,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (HERE/'material_provenance.json').write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2)+'\n')
    write_credits()
    print(json.dumps({'materials':len(MANIFEST['assets']),'image_files':len(MANIFEST['files']),'bytes':sum(x['bytes'] for x in MANIFEST['files']),'keys':list(MANIFEST['assets'])}))


if __name__=='__main__':main()
