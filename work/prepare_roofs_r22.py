"""Build metre-scaled deck surfaces and dyed canvas for the editable R22 layer."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W=Path(__file__).resolve().parent
S=W/'scene_r22'
P=W/'project/chongqing_godot_v05'
T=S/'surfaces'
T.mkdir(parents=True,exist_ok=True)
A=P/'assets/roofs_r22'
A.mkdir(parents=True,exist_ok=True)
V=P/'verification_r22'
V.mkdir(exist_ok=True)
(V/'.gdignore').touch()
survey=json.loads((S/'survey.json').read_text(encoding='utf8'))
source={}
for kind,asset in [('cement','concrete_floor_worn_001_diff_2k.jpg'),('felt','asphalt_02_diff_1k.jpg')]:
    src=P/'assets'/('chongqing_district_'+asset)
    source[kind]=np.asarray(Image.open(src).convert('RGB').resize((768,768)),dtype=np.float32)
palette={'1335306665':('cement',(139,139,128)), '1413081560':('felt',(94,100,99)),
         '809889622':('cement',(143,130,113)), '809889627':('cement',(134,140,133)),
         'A05':('paver',(154,127,106)), 'A07':('felt',(105,108,108)),
         '809889623':('paver',(143,122,105)), '809889624':('cement',(132,131,117)),
         '809889630':('felt',(104,109,108)), 'A03':('cement',(145,143,127))}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def field(rng,shape,cols,rows):
    grid=Image.fromarray(rng.integers(0,256,(max(2,rows),max(2,cols)),dtype=np.uint8))
    return np.asarray(grid.resize(shape,Image.Resampling.BICUBIC),dtype=np.float32)/255.-.5

def roof_texture(key,rec):
    rng=np.random.default_rng(int(hashlib.sha256(key.encode()).hexdigest()[:8],16))
    points=np.asarray(rec['bounds'],dtype=float)
    edges=np.roll(points,-1,axis=0)-points
    u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u=u/np.linalg.norm(u)
    v=np.array([-u[1],u[0]])
    projected=np.stack([points@u,points@v],axis=1)
    low=projected.min(axis=0)-.16;high=projected.max(axis=0)+.16
    extent=high-low
    width,height=[max(256,min(1536,int(math.ceil(x*30/8))*8)) for x in extent]
    yy,xx=np.mgrid[:height,:width]
    x=(xx+.5)*extent[0]/width; y=(height-yy-.5)*extent[1]/height
    kind,tint=palette.get(key,('cement',(135,134,127)))
    sample=source['felt' if kind=='felt' else 'cement']
    grain=sample[((y/3.8*768).astype(int)+173)%768,((x/3.8*768).astype(int)+97)%768]
    value=grain@np.array([.28,.53,.19],dtype=np.float32)
    gray=(value-np.mean(value))*.39
    gray+=field(rng,(width,height),round(extent[0]/4),round(extent[1]/4))*20
    gray+=field(rng,(width,height),round(extent[0]/.7),round(extent[1]/.7))*7
    if kind=='felt':
        # Overlapping bitumen rolls, staggered end laps and occasional repairs.
        band=np.floor(y/.99).astype(int);slip=rng.uniform(0,5,int(band.max())+1)[band]
        ix,iy=(x+slip)%7.6,y%.99
        gray+=rng.uniform(-6,6,int(band.max())+1)[band]
        gray-=18*np.exp(-((iy-.035)/.035)**2)+14*np.exp(-((ix-.045)/.04)**2)
    else:
        sx,sy=(.35,.195) if kind=='paver' else (3.1,2.8)
        row=np.floor(y/sy).astype(int);gx=(x+(row%2)*sx*.50)/sx
        ix=np.minimum(gx%1,1-gx%1)*sx;iy=np.minimum(y%sy,sy-y%sy)
        joint=np.exp(-(np.minimum(ix,iy)/(.010 if kind=='paver' else .017))**2)
        gray-=joint*(24 if kind=='paver' else 17)
        ixcell=gx.astype(int);cells=rng.normal(0,3.4 if kind=='paver' else 1.6,(row.max()+1,ixcell.max()+1))
        gray+=cells[row,ixcell]
    # Runoff is keyed to the actual plan perimeter, including concave corners.
    distance=np.full_like(x,1e5)
    for a,b in zip(projected-low,np.roll(projected,-1,axis=0)-low):
        edge=b-a
        t=np.clip(((x-a[0])*edge[0]+(y-a[1])*edge[1])/max(.00001,edge@edge),0,1)
        distance=np.minimum(distance,np.hypot(x-a[0]-t*edge[0],y-a[1]-t*edge[1]))
    weather=np.exp(-distance/.64)*(.65+field(rng,(width,height),30,26)*.54)
    rgb=np.asarray(tint,dtype=float)+gray[:,:,None]-weather[:,:,None]*[36,28,34]
    # Soil splash and wet feet leave a broad broken stain below the fixtures,
    # with the strongest deposition at the beds, feet and utility outlets.
    for station in json.loads((S/'roof_stations_design.json').read_text()):
        if station['building']!=key:continue
        center=np.asarray(station['anchor'][:2])
        dx=x-(center@u-low[0]);dy=y-(center@v-low[1])
        spread=2.8 if station['kind'] in ['garden','pergola'] else 1.8
        wet=np.exp(-((dx/spread)**2+(dy/2.2)**2)*.56)
        broken=.58+field(rng,(width,height),25,23)*.60
        rgb-=wet[:,:,None]*broken[:,:,None]*[38,31,36]
    if kind=='cement':
        # Fine branching shrinkage, visible in close views and irregularly
        # interrupted at expansion joints. Use a thin, antialiased glaze.
        cracks=Image.new('L',(xx.shape[1],height));pen=ImageDraw.Draw(cracks)
        for _ in range(max(3,int(extent.prod()/48))):
            px,py=rng.random(2)*[xx.shape[1],height];a=rng.uniform(0,math.tau);stroke=[(px,py)]
            for _ in range(rng.integers(8,24)):
                a+=rng.normal(0,.32);l=rng.uniform(2.5,9);px+=math.cos(a)*l;py+=math.sin(a)*l;stroke.append((px,py))
            pen.line(stroke,fill=int(rng.integers(35,95)),width=1)
        rgb-=np.asarray(cracks.filter(ImageFilter.GaussianBlur(.4)),dtype=float)[:,:,None]*.52
    out=Image.fromarray(np.uint8(rgb.clip(0,255)))
    # A few local reseals on accessible flat decks. Keep roof-wide tonal
    # changes continuous under the patch so they don't look like stickers.
    if kind=='felt':
        glaze=Image.new('RGBA',out.size)
        pen=ImageDraw.Draw(glaze)
        for _ in range(9):
            px,py=rng.integers(10,width-10),rng.integers(10,height-10)
            w,h=rng.uniform(.5,2.3)*width/extent[0],rng.uniform(.3,.95)*height/extent[1]
            pen.polygon([(px,py),(px+w,py+1),(px+w-2,py+h),(px+1,py+h+2)],fill=(50,54,53,78))
        out=Image.alpha_composite(out.convert('RGBA'),glaze).convert('RGB')
    out.save(T/(key+'.jpg'),quality=91)
    return {'kind':kind,'u':u.tolist(),'v':v.tolist(),'min':low.tolist(),'span':extent.tolist(),'sha256':sha(T/(key+'.jpg'))}

decks={k:roof_texture(k,b) for k,b in survey['roofs'].items()}
rng=np.random.default_rng(201398)
w,h=1024,512;yy,xx=np.mgrid[:h,:w]
s=xx/w;t=yy/h; weave=np.sin(xx*2.10)*1.8+np.sin(yy*1.90)*2.
tone=field(rng,(w,h),22,9)*13+field(rng,(w,h),78,26)*3+weave+8*t
stripe=s*7%1
cream=np.maximum(np.exp(-((stripe-.08)/.037)**4),np.exp(-((stripe-.16)/.013)**4))
color=np.array([80,103,94])+tone[:,:,None]+cream[:,:,None]*[72,48,37]
Image.fromarray(np.uint8(color.clip(0,255))).save(T/'awning.jpg',quality=94)
(S/'projection.json').write_text(json.dumps(decks,indent=2),encoding='utf8')
baseline=json.loads((P/'assets/render_profile_r21.json').read_text(encoding='utf8'))
baseline['diagnostic_views'].update({
    'r22_breakfast':{'position':[-27.0,12.56,56.2],'target':[-30.48,12.23,61.0],'fov':56,'title':'早餐桌与遮雨棚'},
    'r22_roof_garden':{'position':[3,52,-22],'target':[-14,39.9,-34],'fov':58,'title':'文化室楼顶'},
    'r22_roof_wash':{'position':[-43,49,-47],'target':[-51,43.3,-60],'fov':57,'title':'住户晾晒天台'}})
(V/'base_profile.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf8')
baseline['art_revision']='R22_district_07_internal';baseline['roofs_r22']=True;baseline['river_r22']=True
baseline['surface_import_revision']='R22_surface_import_01'
(P/'assets/render_profile_r22.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf8')
provenance={'new_geometry_and_canvas':'Original project-authored roof dressings, canvas, utensils, kitchen props and vegetation silhouettes.',
 'derived_surfaces':[{'asset':k,'source':'https://polyhaven.com/a/'+k,'license':'CC0-1.0',
 'authors':{'concrete_floor_worn_001':['Dimitrios Savva','Rico Cilliers'],'asphalt_02':['Rob Tuytel']}[k],
 'upstream_local_rgb_sha256':sha(next((P/'assets').glob('chongqing_district_'+k+'_diff*.jpg')))} for k in ['concrete_floor_worn_001','asphalt_02']],
 'attribution_record':'Preserved source authors and original maps in the v05 materials manifest. Per-deck colours, joints, edge weathering and patches authored here.',
 'visual_references':['https://www.cq.gov.cn/ywdt/zwhd/qxdt/202102/t20210218_8899598.html','https://ghzrzyj.cq.gov.cn/zwxx_186/tzgg/202303/P020230322552822130220.pdf'],
 'reference_usage':'Observation only. No photographs from the research articles are ingested.'}
(A/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
