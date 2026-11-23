"""Place prepared CC0 Poly Haven models without duplicating mesh/texture data.
Blender Z up, metres. Run prepare_scanned_assets.py once to create the library.
Templates are unlinked; only placed instances enter the caller's scene.
"""
from pathlib import Path
import json,math,random
import bpy
from mathutils import Matrix,Vector

_CACHE={}
_MANIFEST=None
_ROOT=Path(__file__).resolve().parent/'scanned_assets'

def setup(root_path=None):
    global _ROOT,_MANIFEST,_CACHE
    if root_path:
        root=Path(root_path)
        for p in [root/'scanned_assets',root/'source/scanned_assets',root]:
            if (p/'prepared_assets.blend').is_file():_ROOT=p;break
    if _MANIFEST is not None and _CACHE:return _MANIFEST
    path=_ROOT/'prepared_assets.blend'
    if not path.is_file():raise FileNotFoundError('Prepared asset library missing: '+str(path))
    _MANIFEST=json.loads((_ROOT/'manifest.json').read_text())
    required={n for a in _MANIFEST['prepared_assets'].values() for level in a['variants'].values() for n in level['objects']}
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):
        dst.objects=[n for n in src.objects if n in required]
    _CACHE={o.name:o for o in dst.objects if o is not None}
    for o in _CACHE.values():
        for c in list(o.users_collection):c.objects.unlink(o)
    return _MANIFEST

def _collection(c):
    if c is None:return bpy.context.scene.collection
    if isinstance(c,str):
        col=bpy.data.collections.get(c)
        if col is None:col=bpy.data.collections.new(c);bpy.context.scene.collection.children.link(col)
        return col
    return c

def make_prop(asset_key,name,location,height=None,width=None,yaw=0.,scale=1.,collection=None,lod='base',part_lods=None):
    """Instantiate one normalized asset; requested height/width is metres.
    Source's ground/root sits at location. Returns a list of Mesh objects.
    """
    setup();record=_MANIFEST['prepared_assets'][asset_key]
    if lod not in record['variants']:lod=next(iter(record['variants']))
    factor=float(scale)
    if height is not None:factor*=float(height)/record['source_height_m']
    elif width is not None:factor*=float(width)/record['source_width_m']
    transform=Matrix.Translation(Vector(location))@Matrix.Rotation(float(yaw),4,'Z')@Matrix.Scale(factor,4)
    col=_collection(collection);result=[]
    for i,template_name in enumerate(record['variants'][lod]['objects']):
        part_lod=(part_lods or {}).get(i,lod)
        if part_lod!=lod:
            replacement=record['variants'][part_lod]['objects']
            if len(replacement)!=len(record['variants'][lod]['objects']):
                raise ValueError('Prepared asset part ordering differs between variants: '+asset_key)
            template_name=replacement[i]
        template=_CACHE[template_name];ob=template.copy();ob.data=template.data
        ob.name=f'{name}_{i:02d}';ob.use_fake_user=False;col.objects.link(ob);ob.matrix_world=transform
        ob['scanned_asset']=True;ob['asset_origin']='Poly Haven CC0 model, optimized locally';ob['source']=record['source_page'];ob['license']='CC0 1.0';ob['placed_height_m']=record['source_height_m']*factor
        ob['prepared_asset_key']=asset_key;ob['prepared_variant']=part_lod;ob['prepared_template']=template_name
        result.append(ob)
    return result

def make_tree(name,location,height=8.,seed=0,collection=None,hero=False,lod=None,species=None):
    """Two real tree forms; low≈30k, medium≈80k, hero≈250k tris.
    No implied local-species/photogrammetric survey of Chongqing.
    """
    rng=random.Random(seed)
    key=species or ('island_tree_01' if seed%3==0 else 'tree_small_02')
    level=lod or ('hero' if hero else 'low')
    # Medium island foliage collapses most separate leaves to one triangle.
    # All large, accessible instances use the existing hero parts, preserving
    # their source transforms, textures, root fit and shared mesh data.
    if key=='island_tree_01' and height>=9.:
        level='hero'
    return make_prop(key,name,location,height=height,yaw=rng.random()*math.tau,collection=collection,lod=level)

def make_shrub(name,location,scale=1.,seed=0,collection=None,height=None,lod='low'):
    """One shrub cluster. scale=1 targets 0.85m tall; height overrides it.
    The original canopy width is recorded in manifest; use per-object bounds.
    """
    rng=random.Random(seed)
    target=float(height) if height is not None else .85*float(scale)
    return make_prop('shrub_01',name,location,height=target,yaw=rng.random()*math.tau,collection=collection,lod=lod)

def make_debris_group(name,location,seed=0,collection=None,scale=1.,yaw=0.):
    """1.8m×1.4m corner cluster: real bin, two bags, one crate.
    User supplies a location away from required walking space.
    """
    rng=random.Random(seed);out=[];base=Vector(location);rot=Matrix.Rotation(yaw,3,'Z')
    def put(key,label,dx,dy,h,angle):
        p=base+rot@Vector((dx*scale,dy*scale,0))
        out.extend(make_prop(key,name+'_'+label,p,height=h*scale,yaw=yaw+angle,collection=collection))
    bin_key='metal_trash_can_rust' if seed%2 else 'metal_trash_can_clean'
    put(bin_key,'bin',-.3,0,.76,rng.uniform(-.15,.15))
    put('trashbag','bagA',.42,-.19,.49,rng.random()*math.tau)
    put('trashbag','bagB',.66,.24,.38,rng.random()*math.tau)
    if 'plastic_crate_01' in setup()['prepared_assets']:
        put('plastic_crate_01','crate',-.25,.64,.30,rng.uniform(-.2,.2))
    return out

def make_crate_group(name,location,seed=0,collection=None,count=3,yaw=0.,scale=1.):
    rng=random.Random(seed);out=[]
    for i in range(count):
        p=Vector(location)+Matrix.Rotation(yaw,3,'Z')@Vector(((i%2)*.44*scale,0,(i//2)*.28*scale))
        out.extend(make_prop('plastic_crate_01',name+f'_{i:02d}',p,height=.28*scale,yaw=yaw+rng.uniform(-.09,.09),collection=collection))
    return out

def make_covered_car(name,location,yaw=0.,collection=None,length=4.4,seed=0):
    """Parked car beneath a real worn fabric cover, sized by longest width.
    Long axis is inherited from the source; yaw is radians in Blender Z-up.
    """
    return make_prop('covered_car',name,location,width=length,yaw=yaw,collection=collection)
