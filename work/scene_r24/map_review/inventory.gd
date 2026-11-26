extends RefCounted

var surfaces := {}
var material_by_id := {}

func describe(mat: Material) -> int:
	if mat == null:return -1
	var rid:=mat.get_instance_id()
	if material_by_id.has(rid):return material_by_id[rid]
	var id:=material_by_id.size()
	material_by_id[rid]=id
	var info:={"name":mat.resource_name,"class":mat.get_class(),"path":mat.resource_path,"textures":[]}
	if mat is BaseMaterial3D:
		var base:=mat as BaseMaterial3D
		info["color"]=base.albedo_color.to_html(false)
		info["vertex_color"]=base.vertex_color_use_as_albedo
		for slot in BaseMaterial3D.TEXTURE_MAX:
			var texture:=base.get_texture(slot)
			if texture:info.textures.append([slot,texture.resource_name,texture.resource_path])
	elif mat is ShaderMaterial and mat.shader:
		info["shader"]=mat.shader.resource_path
		for uniform: Dictionary in mat.shader.get_shader_uniform_list():
			var value=mat.get_shader_parameter(uniform.name)
			if value is Texture:info.textures.append([str(uniform.name),value.resource_name,value.resource_path])
	surfaces[id]=info
	return id

func xyz(v: Vector3) -> Array:
	return [snappedf(v.x,.01),snappedf(v.y,.01),snappedf(v.z,.01)]

func collect(scene: Node3D) -> Dictionary:
	var items:Array=[]
	var others:Dictionary={}
	for geom: GeometryInstance3D in scene.find_children("*","GeometryInstance3D",true,false):
		var mesh:Mesh
		var copies:=1
		if geom is MeshInstance3D:mesh=geom.mesh
		elif geom is MultiMeshInstance3D and geom.multimesh:
			mesh=geom.multimesh.mesh
			copies=geom.multimesh.instance_count
		var ids:Array=[]
		if mesh:
			for i in mesh.get_surface_count():
				var mat:Material=geom.material_override
				if not mat:
					mat=geom.get_active_material(i) if geom is MeshInstance3D else mesh.surface_get_material(i)
				ids.append(describe(mat))
		else:others[geom.get_class()]=others.get(geom.get_class(),0)+1
		var box:AABB=geom.global_transform*geom.get_aabb()
		var owner:Node=geom
		while owner!=null and owner.scene_file_path.is_empty():owner=owner.get_parent()
		items.append([str(scene.get_path_to(geom)),geom.is_visible_in_tree(),geom.get_class(),mesh.get_class() if mesh else "",
			owner.scene_file_path if owner else "",xyz(box.get_center()),xyz(box.size),copies,ids,describe(geom.material_overlay)])
	return {"columns":["path","visible_in_tree","class","mesh_class","source_scene","center_xyz","size_xyz","instances","active_material_ids","overlay_id"],
		"nodes":items,"materials":surfaces,"other_geometry_classes":others}

func ground_grid(scene: Node3D) -> Array:
	var grid:=[]
	var space:=scene.get_world_3d().direct_space_state
	for north in range(-245,250,10):
		for east in range(-245,250,10):
			var top:=Vector3(east,350,-north)
			var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(top,top-Vector3.UP*550,1))
			grid.append([east,north,str(scene.get_path_to(hit.collider)) if hit else "",snappedf(hit.position.y,.01) if hit else null])
	return grid
