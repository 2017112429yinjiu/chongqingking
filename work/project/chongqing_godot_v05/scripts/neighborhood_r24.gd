extends RefCounted

const FOLDER := "res://assets/neighborhood_r24/"

static func _v(row: Array) -> Vector3:
	return Vector3(row[0],row[1],row[2])

static func _matrix(matrix: Array) -> Transform3D:
	return Transform3D(Basis(_v(matrix[0]),_v(matrix[1]),_v(matrix[2])),_v(matrix[3]))

static func install(city: Node3D, block: Node3D, canopy_distance: bool=false) -> Dictionary:
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FOLDER+"layout.json"))
	var nodes := {}
	for node: MeshInstance3D in city.find_children("*","MeshInstance3D",true,false):
		if node.is_visible_in_tree():
			nodes[str(node.name).replace(".","_")] = node
	var tree_sources := {}
	for key: String in nodes:
		if key.begins_with("Planted_tree_"):tree_sources[nodes[key]]=key
	var stats := {"removed":[], "missing":[], "shifted":0,"plants":0,"spans":layout.wires.size()}
	for key in layout.retire:
		# The collision builder also visits hidden meshes. Remove the retired geometry before it runs.
		var old := nodes.get(key) as MeshInstance3D
		if old:
			old.free()
			nodes.erase(key)
			stats.removed.append(key)
		else:
			stats.missing.append(key)
	for group in layout.adjustments:
		var complete := true
		for key in group.names:
			if not nodes.has(key):
				complete=false
				stats.missing.append(key)
		if complete:
			var shift := _matrix(group.transform)
			for key in group.names:
				var item: MeshInstance3D=nodes[key]
				item.global_transform=shift*item.global_transform
			stats.shifted+=1
	var layer := (load(FOLDER+"street.glb") as PackedScene).instantiate() as Node3D
	layer.name="Neighborhood13"
	city.add_child(layer)
	for donor_name in layout.donors:
		var replacement := layer.find_child(donor_name,true,false) as MeshInstance3D
		var receiver := nodes.get(layout.donors[donor_name]) as MeshInstance3D
		if not replacement or not receiver:
			stats.missing.append(donor_name)
			continue
		var original_material := receiver.get_active_material(0)
		receiver.mesh = replacement.mesh
		receiver.global_transform = replacement.global_transform
		receiver.set_surface_override_material(0,original_material)
		replacement.free()
	var fixtures := StaticBody3D.new()
	fixtures.name="CourtRestingPlace"
	layer.add_child(fixtures)
	for record in layout.furniture:
		var collider := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size=_v(record["size"])
		collider.shape=shape
		fixtures.add_child(collider)
		collider.global_position=_v(record.at)
	var trunks := StaticBody3D.new()
	trunks.name = "NeighborhoodTreeTrunks"
	layer.add_child(trunks)
	for section in JSON.parse_string(FileAccess.get_file_as_string(FOLDER+"trunk_sections.json")):
		var trunk := CylinderShape3D.new()
		trunk.radius = section.radius
		trunk.height = section.height
		var collider := CollisionShape3D.new()
		collider.shape = trunk
		trunks.add_child(collider)
		collider.global_position = _v(section.base) + Vector3.UP*trunk.height*.5
	stats["trunks"] = trunks.get_child_count()
	var wall := (nodes["COL_Court_side_foundations_stone"] as MeshInstance3D).get_active_material(0).duplicate() as BaseMaterial3D
	wall.cull_mode=BaseMaterial3D.CULL_DISABLED
	var soil := StandardMaterial3D.new()
	soil.albedo_texture=load("res://assets/chongqing_district_brown_mud_leaves_01_diff_2k.jpg")
	soil.albedo_color=Color(.78,.74,.67)
	soil.roughness=.92
	for mesh: MeshInstance3D in layer.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name) in ["COL_N13_BankCutFaces","COL_N13_StairFoundations","COL_N13_PlantingRims","COL_N13_CourtCornerMasonry","COL_N13_LampSockets"]:
			mesh.material_override=wall
		if str(mesh.name)=="N13_PlantingSoil":
			mesh.material_override=soil
	for patch in layout.plants:
		var transform := _matrix(patch.transform)
		for key in patch.donors:
			var source := nodes.get(key) as MeshInstance3D
			if not source:
				stats.missing.append(key)
				continue
			var plant := MeshInstance3D.new()
			plant.mesh=source.mesh
			if key.begins_with("Planted_tree_"):
				tree_sources[plant]=key
			plant.material_override=source.material_override
			for i in source.mesh.get_surface_count():
				plant.set_surface_override_material(i,source.get_surface_override_material(i))
			plant.visibility_range_end=88. if str(key).begins_with("Planted_tree") else 46.
			plant.visibility_range_end_margin=4.
			plant.lod_bias=.72
			layer.add_child(plant)
			plant.global_transform=transform*source.global_transform
		stats.plants+=1
	if canopy_distance:
		stats["tree_distance_meshes"]=install_tree_distances(tree_sources,layer)
	for key in layout.walks:
		var curve := Curve3D.new()
		curve.bake_interval=.24
		for point in layout.walks[key]:
			curve.add_point(_v(point))
		block.routes[key]=curve
	if FileAccess.file_exists(FOLDER+"walk_lanes.json"):
		block.walking_lanes=JSON.parse_string(FileAccess.get_file_as_string(FOLDER+"walk_lanes.json"))
	if not stats.missing.is_empty(): push_error("Neighborhood source missing %s" % str(stats.missing))
	print("CQ_NEIGHBORHOOD ",JSON.stringify(stats))
	return stats


# Keep the photographed leaves and bark at pedestrian distance. Farther trees use
# two mesh densities prepared from the same individual scan, with the same UVs.
static func install_tree_distances(trees:Dictionary, layer:Node3D) -> int:
	var species:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(FOLDER+"tree_species.json"))
	var library:Node3D=(load(FOLDER+"tree_distances.glb") as PackedScene).instantiate()
	var count:=0
	for tree: MeshInstance3D in trees:
		var key:String=trees[tree]
		var root_name:=key.get_slice("_",0)+"_"+key.get_slice("_",1)+"_"+key.get_slice("_",2)
		var group:int=int(key.get_slice("_",3))
		var small:=tree.visibility_range_end>0. and tree.visibility_range_end<=88.
		var near:=24. if small else 40.
		var far:=49. if small else 77.
		var original_end:=tree.visibility_range_end
		var material:=tree.get_active_material(0)
		for level in ["medium","low"]:
			var resource_name:="Canopy_%s_%s_%d"%[species[root_name],level,group]
			var source:=library.find_child(resource_name,true,false) as MeshInstance3D
			assert(source!=null,resource_name)
			var instance:=MeshInstance3D.new()
			instance.mesh=source.mesh
			instance.material_override=material
			instance.cast_shadow=tree.cast_shadow
			instance.visibility_range_begin=near if level=="medium" else far
			instance.visibility_range_end=far if level=="medium" else original_end
			layer.add_child(instance)
			instance.global_transform=tree.global_transform
			count+=1
		tree.visibility_range_end=near
		tree.visibility_range_end_margin=0.
	library.free()
	return count
