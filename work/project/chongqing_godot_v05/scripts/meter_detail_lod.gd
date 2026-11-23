extends RefCounted

const DETAIL_FILE = "res://assets/lane_r20/meter_lods.glb"
const MANIFEST = "res://assets/lane_r20/meter_lods.json"

static func install(city: Node3D) -> Dictionary:
	var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	var old_meshes: Array[MeshInstance3D]=[]
	for name: String in spec.source_nodes:
		var original:=city.find_child(name,true,false) as MeshInstance3D
		if original==null:
			push_error("Meter detail missing: "+name)
			return {}
		old_meshes.append(original)
	var packed:=load(DETAIL_FILE) as PackedScene
	if packed==null:return {}
	var spatial:=packed.instantiate() as Node3D
	var near_meshes:=spatial.find_children("MeterClose_*","MeshInstance3D",true,false)
	var far_meshes:=spatial.find_children("MeterFar_*","MeshInstance3D",true,false)
	if near_meshes.size()!=int(spec.sites) or far_meshes.size()!=int(spec.sites):
		spatial.free()
		push_error("Incomplete spatial meter geometry")
		return {}
	# Both ranges use the same frame boundary and the same centre. Tiny numerals,
	# bolts and flakes become subpixel while the cabinet recess stays visible.
	for mesh: MeshInstance3D in near_meshes:
		mesh.visibility_range_end=18.
	for mesh: MeshInstance3D in far_meshes:
		mesh.visibility_range_begin=18.
		var near_name:=str(mesh.name).replace("MeterFar_", "MeterClose_")
		var close:=spatial.find_child(near_name,true,false) as MeshInstance3D
		var bounds:=mesh.mesh.get_aabb().merge(close.mesh.get_aabb())
		mesh.custom_aabb=bounds
		close.custom_aabb=bounds
	spatial.name="SpatialMeterDetails"
	city.add_child(spatial)
	for mesh in old_meshes:mesh.hide()
	return {"sha256":FileAccess.get_sha256(DETAIL_FILE),"sites":near_meshes.size(),"switch_m":18.,"source_triangles":spec.original_triangles}
