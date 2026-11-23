"""Fit separately dressed stone flags to the measured structural stair tops."""
import math,random,json
import bpy
from mathutils import Vector

def build(source,layer,architecture,root,kit_dir):
    folder=root/'assets_incoming/district_r21/sandstone_cracks'
    material=bpy.data.materials.new('R21 Worn dressed sandstone');material.use_nodes=True
    nt=material.node_tree;bs=nt.nodes.get('Principled BSDF')
    for rec in json.loads((folder/'PROVENANCE.json').read_text(encoding='utf8'))['files']:
        kind=rec['map'];node=nt.nodes.new('ShaderNodeTexImage')
        node.image=bpy.data.images.load(str((kit_dir/'washed_sandstone.jpg') if kind=='diff' else (folder/rec['file'])),check_existing=True)
        if kind!='diff':node.image.colorspace_settings.name='Non-Color'
        if kind=='nor_gl':
            normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55
            nt.links.new(node.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
        elif kind=='diff':
            attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='Stone patina'
            mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
            nt.links.new(node.outputs['Color'],mix.inputs[1]);nt.links.new(attr.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
        else:nt.links.new(node.outputs['Color'],bs.inputs['Roughness'])
    rng=random.Random(90213);records=[]
    for old in source:
        if old.name not in ['COL_Walk_Central_stair_lane_step_concrete','COL_Walk_West_residential_link_step_concrete']:continue
        tops=[p for p in old.data.polygons if p.normal.z>.998]
        vv=[];ff=[];uvs=[];colors=[];count=0;heights=[];groups=[]
        for i in range(0,len(tops)-1,2):
            pts={tuple(round(c,5) for c in (old.matrix_world@old.data.vertices[k].co)) for f in tops[i:i+2] for k in f.vertices}
            if len(pts)!=4 or max(p[2] for p in pts)-min(p[2] for p in pts)>.001:continue
            points=[Vector(p) for p in pts];center=sum(points,Vector())/4
            points.sort(key=lambda p:math.atan2(p.y-center.y,p.x-center.x))
            groups.append((center,points))
        for i,(center,points) in enumerate(groups):
            neighbour=groups[i+1 if i+1<len(groups) else i-1][0]
            climb=neighbour-center
            if climb.z<0:climb=-climb
            climb.z=0;climb.normalize()
            axes=[(points[k+1]-points[k]).normalized() for k in [0,1]]
            along=max(axes,key=lambda v:abs(v.dot(climb)))
            if along.dot(climb)<0:along=-along
            across=Vector((along.y,-along.x,0))
            half_w=max(abs((p-center).dot(across)) for p in points)
            half_l=max(abs((p-center).dot(along)) for p in points)
            if half_w<.5 or half_l<.09:continue
            def position(x,y,z):return center+across*x+along*y+Vector((0,0,z))
            rows=max(1,round(2*half_l/.86));pieces=0
            for row in range(rows):
                low=-half_l+2*half_l*row/rows;high=-half_l+2*half_l*(row+1)/rows
                edges=[-half_w]
                while half_w-edges[-1]>1.32:edges.append(edges[-1]+rng.uniform(.58,1.04))
                edges.append(half_w)
                for lo,hi in zip(edges,edges[1:]):
                    x0=lo+.003;x1=hi-.003
                    y0=low+(.003 if row else -.010);y1=high-.003
                    chips=[rng.uniform(.008,.024) for j in range(4)]
                    shape=[(x0+chips[0],y0),(x1-chips[1],y0),(x1,y0+chips[1]),(x1,y1-chips[2]),
                           (x1-chips[2],y1),(x0+chips[3],y1),(x0,y1-chips[3]),(x0,y0+chips[0])]
                    middle=Vector(((x0+x1)*.5,(y0+y1)*.5))
                    shade=rng.uniform(.74,.99);offset=Vector((rng.uniform(0,8),rng.uniform(0,8)))
                    top=rng.uniform(.0035,.0069);heights.append(top)
                    rings=[]
                    for level in range(3):
                        ring=[]
                        for k,xy in enumerate(shape):
                            p=Vector(xy)
                            if level==2:p+=(middle-p).normalized()*rng.uniform(.006,.011)
                            z=top if level==2 else top-.009 if level==1 else (-.149 if not row and k in (0,1,2,7) else -.035)
                            ring.append(len(vv));vv.append(position(p.x,p.y,z));uvs.append((p+offset)/1.98)
                            border=max(0.,min(1.,(abs(p.x)/half_w-.56)/.44))
                            damp=border*border*(.73+.20*math.sin(center.y*1.8+p.x*3.))
                            tone=shade*(.74 if level==0 else .93 if level==1 else 1.)*(1-.36*damp)
                            colors.append((tone*(1-.06*damp),tone,tone*(.975-.065*damp),1))
                        rings.append(ring)
                    for l in range(2):
                        for k in range(8):
                            j=(k+1)%8;ff.append((rings[l][k],rings[l][j],rings[l+1][j],rings[l+1][k]))
                    ff.append(tuple(rings[2]));pieces+=1
            count+=pieces
        name='R21_Dressed_'+('Central_steps' if 'Central' in old.name else 'West_steps')
        m=bpy.data.meshes.new(name);m.from_pydata(vv,[],ff);m.update()
        o=bpy.data.objects.new(name,m);layer.objects.link(o);architecture.append(o);m.materials.append(material)
        uv=m.uv_layers.new(name='Metres');wear=m.color_attributes.new(name='Stone patina',type='FLOAT_COLOR',domain='POINT')
        for v in m.vertices:wear.data[v.index].color=colors[v.index]
        m.color_attributes.active_color=wear
        for face in m.polygons:
            side=abs(face.normal.z)<.50
            for j in face.loop_indices:
                k=m.loops[j].vertex_index
                uv.data[j].uv=(uvs[k].x+uvs[k].y,vv[k].z/1.98) if side else uvs[k]
        records.append({'structure':old.name,'mesh':name,'tops':len(groups),'individual_stones':count,'top_above_collision_m':[min(heights),max(heights)]})
    return records
