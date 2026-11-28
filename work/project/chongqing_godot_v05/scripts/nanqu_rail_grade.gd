extends RefCounted

const MODEL := "res://assets/district_500/nanqu-rail-grade.glb"
const PLAN := "res://assets/district_500/nanqu-rail-grade.json"
const LANDSIDE := "res://assets/district_500/nanqu-landside.glb"
const PREFIX := "Grade__"

static func install(city: Node3D) -> Dictionary:
	var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var layer := (load(MODEL) as PackedScene).instantiate() as Node3D
	layer.name="NanquRailGrade"
	var donors: Dictionary={}
	var replacements: Dictionary={}
	var missing: Array[String]=[]
	for part: MeshInstance3D in layer.find_children("*", "MeshInstance3D", true, false):
		var key:=str(part.name)
		if not key.begins_with(PREFIX): continue
		key=key.trim_prefix(PREFIX)
		var donor:=city.find_child(key,true,false) as MeshInstance3D
		if donor==null or not spec.corrected_meshes.has(key) or donor.mesh.get_surface_count()!=part.mesh.get_surface_count():
			missing.append(key)
			continue
		donors[key]=donor
		replacements[key]=part
	if not missing.is_empty() or replacements.size()!=spec.corrected_meshes.size():
		push_error("Nanqu grade donor surfaces unresolved: %s (%d/%d)"%[missing,replacements.size(),spec.corrected_meshes.size()])
		layer.free()
		return {"installed":false,"missing":missing,"found":replacements.keys()}
	city.add_child(layer)
	for key: String in replacements:
		var part: MeshInstance3D=replacements[key]
		var donor: MeshInstance3D=donors[key]
		var materials: Array[Material]=[]
		for index in donor.mesh.get_surface_count():
			materials.append(donor.get_active_material(index))
		donor.mesh=part.mesh
		donor.global_transform=part.global_transform
		for index in materials.size():
			donor.set_surface_override_material(index,null if key in spec.get("use_export_materials",[]) else materials[index])
		part.free()
	var landside_sha := ""
	if "--qa-nanqu-landside-parent" not in OS.get_cmdline_user_args():
		var landside := (load(LANDSIDE) as PackedScene).instantiate()
		landside.name = "NanquLandside"
		layer.add_child(landside)
		landside_sha = FileAccess.get_sha256(LANDSIDE)
	return {"installed":true,"corrected_meshes":replacements.size(),"model_sha256":FileAccess.get_sha256(MODEL),
		"plan_sha256":FileAccess.get_sha256(PLAN),"landside_sha256":landside_sha}

static func sample(east: float, table: Array) -> float:
	var lo:=0
	var hi:=table.size()-1
	while hi-lo>1:
		var mid: int=(lo+hi)/2
		if east<table[mid][0]: hi=mid
		else: lo=mid
	var a: Array=table[lo]
	var b: Array=table[hi]
	return lerpf(a[1],b[1],(east-a[0])/(b[0]-a[0]))

static func installed_plan(scene: Node3D) -> Dictionary:
	if not scene.scene_identity.get("nanqu_grade",{}).get("installed",false):
		return {}
	return JSON.parse_string(FileAccess.get_file_as_string(PLAN))

static func delta_at(east: float, manifest: Dictionary) -> float:
	if manifest.is_empty(): return 0.
	return sample(east,manifest.road_target_by_east)-sample(east,manifest.old_centre_by_east)

static func adjust(scene: Node3D, rows: Array, at_spur_merge:=false) -> Array:
	var manifest:=installed_plan(scene)
	if manifest.is_empty(): return rows
	var corrected:=rows.duplicate(true)
	for point: Array in corrected:
		var x: float=point[0]
		point[2]+=delta_at(x,manifest)
		if at_spur_merge and manifest.has("spur_merge"):
			var merge: Dictionary=manifest.spur_merge
			var north: float=point[1]
			var level: float=merge.joint[2]+(north-merge.joint[1])*merge.longitudinal_grade
			point[2]=lerpf(point[2],level,smoothstep(merge.north_start,merge.north_match,north))
	return corrected
