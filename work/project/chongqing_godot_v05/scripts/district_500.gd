extends RefCounted

const MODEL := "res://assets/district_500/outer_district.glb"
const LAYOUT := "res://assets/district_500/layout.json"
const INTERIOR_TERRAIN := "res://assets/district_500/interior_terrain.json"
const RIVERSIDE := "res://assets/district_500/riverside.glb"
const MATCH_FACTORY := "res://assets/district_500/match_factory.glb"
const MATCH_FACTORY_SITE := "res://assets/district_500/match_factory.json"
const MATIX_STREETS := "res://assets/district_500/matix_streets.glb"
const MATIX_SITE := "res://assets/district_500/matix_streets.json"
const ZHONGXING_WALL := "res://assets/district_500/zhongxing-retaining.glb"
const ZHONGXING_SITE := "res://assets/district_500/zhongxing-retaining.json"

static func install(city: Node3D) -> Dictionary:
	var district := (load(MODEL) as PackedScene).instantiate() as Node3D
	district.name = "OuterDistrict500"
	var correction: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INTERIOR_TERRAIN))
	var mesh_layer := (load("res://assets/district_500/interior_terrain.glb") as PackedScene).instantiate()
	for mesh_name: String in correction.tiles_and_wall:
		var original := district.find_child(mesh_name, true, false) as MeshInstance3D
		var replacement := mesh_layer.find_child(mesh_name, true, false) as MeshInstance3D
		assert(original and replacement, mesh_name)
		original.mesh = replacement.mesh
	mesh_layer.free()
	var relocated: Array = correction.tree_east_north_up
	var tree_mesh := district.find_child("Outer500_Plant_036", true, false) as MeshInstance3D
	tree_mesh.position = enu(relocated)
	city.add_child(district)
	var low_landing := (load("res://assets/district_500/landing_53.glb") as PackedScene).instantiate() as Node3D
	district.add_child(low_landing)
	var mapped_lane: PackedScene=load("res://assets/district_500/shancheng_lane.glb")
	district.add_child(mapped_lane.instantiate())
	var historic_courts := load("res://assets/district_500/historic_courts.glb") as PackedScene
	district.add_child(historic_courts.instantiate())
	var riverside := (load(RIVERSIDE) as PackedScene).instantiate()
	riverside.name = "RiversideWalk"
	district.add_child(riverside)
	if not "--qa-without-match-factory" in OS.get_cmdline_user_args():
		install_street_group(district, MATCH_FACTORY, MATCH_FACTORY_SITE, "MatchFactory")
		if not "--qa-without-matix-streets" in OS.get_cmdline_user_args():
			install_street_group(district, MATIX_STREETS, MATIX_SITE, "MatixStreets")
			install_street_group(district, ZHONGXING_WALL, ZHONGXING_SITE, "ZhongxingStreetWall")
	var ground := ShaderMaterial.new()
	ground.shader = preload("res://shaders/district_500_ground.gdshader")
	ground.set_shader_parameter("street_mask", load("res://assets/district_500/surface_mask.png"))
	var textures := {
		"asphalt": "asphalt_02_diff_1k.jpg",
		"asphalt_normal": "asphalt_02_nor_gl_1k.jpg",
		"asphalt_rough": "asphalt_02_rough_1k.png",
		"paving": "stone_floor_diff_2k.jpg",
		"paving_normal": "stone_floor_nor_gl_2k.jpg",
		"soil": "brown_mud_leaves_01_diff_2k.jpg",
		"aggregate": "leaf_scattered_gravel_diff_2k.jpg",
	}
	for key: String in textures:
		ground.set_shader_parameter(key, load("res://assets/chongqing_district_" + textures[key]))
	for tile: MeshInstance3D in district.find_children("COL_Outer500_Surface_*", "MeshInstance3D", true, false):
		tile.material_override = ground
	var local_frame := city.find_child("LocalCityFrame", true, false) as Node3D
	if local_frame:
		local_frame.hide()
	for bank_name in ["R22_Bank_Outer", "R22_Bank_Relief"]:
		var bank := city.find_child(bank_name, true, false) as MeshInstance3D
		if bank:
			(bank.get_surface_override_material(0) as ShaderMaterial).set_shader_parameter("outer_district_cut", true)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	for plot: Dictionary in layout.plots:
		if plot.has("repair_court"):
			district.set_meta("repair_court",plot.repair_court)
	var cut: Dictionary = layout.get("interior_rail_return", {})
	if not cut.is_empty():
		var old_rail := city.find_child(cut.original,true,false) as MeshInstance3D
		var new_rail := district.find_child(cut.replacement,true,false) as MeshInstance3D
		if old_rail and new_rail:
			for surface in mini(old_rail.mesh.get_surface_count(),new_rail.mesh.get_surface_count()):
				new_rail.set_surface_override_material(surface,old_rail.get_active_material(surface))
			old_rail.hide()
	for item: MeshInstance3D in district.find_children("Outer500_Household_*","MeshInstance3D",true,false):
		item.visibility_range_end=39.0
		item.lod_bias=1.7
	for mesh: MeshInstance3D in district.find_children("Outer500_CourtDetails_*","MeshInstance3D",true,false):
		mesh.lod_bias=3.0
	for unit: MeshInstance3D in district.find_children("Outer500_Condenser_*","MeshInstance3D",true,false):
		unit.visibility_range_end=55.0
	var edge: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/edge_ground.json"))
	for prefix: String in edge.context_prefixes:
		for mesh: MeshInstance3D in city.find_children(prefix+"*","MeshInstance3D",true,false):
			mesh.global_position.y+=float(edge.context_shift_z)
	var prefixes: Array = layout.get("retired_context_prefixes", [])
	for prior: MeshInstance3D in city.find_children("Context_*","MeshInstance3D",true,false):
		for prefix: String in prefixes:
			if str(prior.name).begins_with(prefix):
				prior.hide()
				break
	var roofs := city.find_child("R21_Rooftop_stairheads",true,false) as MeshInstance3D
	if roofs and not layout.get("retired_roof_positions",[]).is_empty():
		trim_roofs(roofs,layout.retired_roof_positions)
	var trunks := StaticBody3D.new()
	trunks.name = "OuterDistrictTreeTrunks"
	trunks.collision_layer = 1
	trunks.collision_mask = 0
	district.add_child(trunks)
	# Near trees keep the scanned leaves. Beyond the pavement use the same species'
	# four-direction atlas as the existing hillside, grouped into small street cells.
	var distant_trees := []
	var tree_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_r21/layout.json"))
	for plant: MeshInstance3D in district.find_children("Outer500_Plant_*", "MeshInstance3D", true, false):
		plant.lod_bias = 5.0
		plant.visibility_range_end = 38.0
	var court_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	var replaced_roots: Array[Vector2]=[]
	for centre: Array in court_data.superseded_outer_roots:
		replaced_roots.append(Vector2(centre[0],centre[1]))
	var planting: Array=layout.planting
	for index in planting.size():
		var tree: Dictionary=planting[index]
		var p: Array=relocated if index == 36 else tree.east_north_up
		var centre:=Vector2(p[0],p[1])
		if replaced_roots.any(func(old: Vector2): return old.distance_squared_to(centre)<.01):
			var prior:=district.find_child("Outer500_Plant_%03d"%index,true,false) as MeshInstance3D
			if prior:
				prior.hide()
			continue
		var cylinder := CylinderShape3D.new()
		cylinder.radius = 0.13 * tree.width_scale
		cylinder.height = 1.8 * tree.height_scale
		var shape := CollisionShape3D.new()
		shape.shape = cylinder
		shape.position = Vector3(p[0], p[2] + cylinder.height / 2.0, -p[1])
		trunks.add_child(shape)
		var scan_height := 4.54 if int(tree.species) == 0 else 5.02
		distant_trees.append({"position":[p[0], p[2], -p[1]], "height":scan_height * float(tree.height_scale),
			"kind":tree.species, "yaw":deg_to_rad(tree.rotation_deg), "shade":0.94})
	preload("res://scripts/district_r21.gd").install_canopy(district, distant_trees, tree_data.canopy_pivots, 8.0, 34.0)
	var retire: Array = layout.get("osm_building_ids", [])
	for id: int in retire:
		for prior: Node3D in city.find_children("Context_*%s_*" % id, "MeshInstance3D", true, false):
			prior.hide()
	for place: Dictionary in layout.destinations:
		var sign := Label3D.new()
		var northeast: Array = place.east_north
		var angle: float = place.bearing
		var offset: float = place.front_offset - 2.235
		sign.position = Vector3(northeast[0] - sin(angle) * offset, place.height + 2.38,
			-northeast[1] - cos(angle) * offset)
		sign.rotation.y = angle
		sign.text = place.name
		sign.modulate = Color("#f0e2b9")
		sign.outline_modulate = Color("#2d2822")
		sign.outline_size = 12
		sign.font = load("res://assets/district_500/district_signs.otf")
		sign.font_size = 72
		sign.pixel_size = 0.0051
		sign.no_depth_test = false
		district.add_child(sign)
	for plot: Dictionary in layout.get("plots",[]):
		if plot.has("superseded_by"):
			continue
		for spec: Dictionary in plot.get("trade_signs",[]):
			var lettering:=Label3D.new()
			var yaw: float=plot.bearing
			lettering.text=spec.text
			lettering.font=load("res://assets/district_500/district_signs.otf")
			lettering.font_size=64
			lettering.pixel_size=.00325
			lettering.modulate=Color("#e8dec4")
			lettering.outline_size=3
			lettering.rotation.y=yaw
			lettering.position=Vector3(plot.east_north[0]+cos(yaw)*spec.u-sin(yaw)*spec.v,plot.height+spec.h,
				-plot.east_north[1]-sin(yaw)*spec.u-cos(yaw)*spec.v)
			district.add_child(lettering)
		if plot.name=="照相巷便民市场" or plot.name=="南区路车棚修理铺":
			place_worker(district,plot)
		if not plot.has("court"):
			continue
		var court: Dictionary=plot.court
		var label:=Label3D.new()
		var u: float=court.room_u+.83*court.stair_side
		var v: float=court.room_v-1.05
		var a: float=plot.bearing
		label.text="201"
		label.font_size=48
		label.pixel_size=.0022
		label.modulate=Color("#e7dcc7")
		label.outline_modulate=Color("#27433d")
		label.outline_size=9
		label.rotation.y=a
		label.position=Vector3(plot.east_north[0]+cos(a)*u-sin(a)*v,plot.height+court.upper_m+1.76,
			-plot.east_north[1]-sin(a)*u-cos(a)*v)
		district.add_child(label)
	return {"bounds_east_north_m": layout.bounds_east_north_m,
		"glb_sha256": FileAccess.get_sha256(MODEL), "riverside_sha256": FileAccess.get_sha256(RIVERSIDE),
		"match_factory_sha256": FileAccess.get_sha256(MATCH_FACTORY),
		"matix_streets_sha256": FileAccess.get_sha256(MATIX_STREETS),
		"zhongxing_wall_sha256": FileAccess.get_sha256(ZHONGXING_WALL),
		"retired_internal_context": local_frame != null, "osm_building_ids": retire}


static func install_street_group(district: Node3D, model_path: String, plan_path: String, group_name: String) -> void:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	var layer := (load(model_path) as PackedScene).instantiate() as Node3D
	layer.name = group_name
	for mesh_name: String in plan.replacement_meshes:
		var original := district.find_child(mesh_name, true, false) as MeshInstance3D
		var updated := layer.find_child(mesh_name, true, false) as MeshInstance3D
		assert(original and updated, mesh_name)
		original.mesh = updated.mesh
		updated.free()
	for mesh_name: String in plan.retired_objects:
		var old := district.find_child(mesh_name, true, false)
		assert(old, mesh_name)
		old.free()
	district.add_child(layer)


static func place_worker(district: Node3D,p: Dictionary) -> void:
	var market: bool=p.name=="照相巷便民市场"
	var model: Node3D=(load("res://assets/block_r23/neighbor.glb" if market else "res://assets/block_r23/commuter.glb") as PackedScene).instantiate()
	model.name="OuterMarketSeller" if market else "OuterRepairWorker"
	district.add_child(model)
	var a: float=p.bearing
	var u:=2.90 if market else 2.13
	var v: float=-p.depth/2.0+4.65 if market else -.45
	model.position=Vector3(p.east_north[0]+cos(a)*u-sin(a)*v,p.height+.041,-p.east_north[1]-sin(a)*u-cos(a)*v)
	model.rotation.y=a+(.11 if market else PI*.55)
	var player:=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	var library: AnimationLibrary=load("res://assets/frontage_r24/stall_clips.res" if market else "res://assets/courtyard_r24/wait_clips.res")
	var clip: StringName=&"street/watch_street" if market else &"street/commuter"
	player.add_animation_library("street",library)
	player.play(clip)
	player.seek(.57,true)
	var enabler:=VisibleOnScreenEnabler3D.new()
	model.add_child(enabler)
	enabler.aabb=AABB(Vector3(-.65,0,-.65),Vector3(1.3,2.15,1.3))
	enabler.enable_node_path=enabler.get_path_to(player)
	for part: MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
		part.visibility_range_end=45.

static func trim_roofs(node: MeshInstance3D, anchors: Array) -> void:
	var original := node.mesh
	var retained := ArrayMesh.new()
	for surface in original.get_surface_count():
		var arrays := original.surface_get_arrays(surface)
		var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		if indices.is_empty():
			indices=PackedInt32Array(range(positions.size()))
		var keep := PackedInt32Array()
		for i in range(0,indices.size(),3):
			var center := node.to_global((positions[indices[i]]+positions[indices[i+1]]+positions[indices[i+2]])/3.0)
			var removed := false
			for a: Array in anchors:
				if absf(center.x-a[0])<2.35 and absf(center.z-a[2])<1.65 and center.y>a[1]-.10 and center.y<a[1]+4.65:
					removed=true
					break
			if not removed:
				keep.append_array(indices.slice(i,i+3))
		if not keep.is_empty():
			arrays[Mesh.ARRAY_INDEX]=keep
			retained.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
			retained.surface_set_material(retained.get_surface_count()-1,node.get_active_material(surface))
	node.mesh=retained

static func enu(p: Array) -> Vector3:
	return Vector3(p[0],p[2],-float(p[1]))

static func start_exploration(scene: Node3D) -> void:
	var collision := preload("res://scripts/build_collisions.gd")
	var bike := scene.gameplay.scooter as CharacterBody3D
	var road := collision.raycast_ground(scene, Vector3(102.0, 21.0, 42.1), 10.0)
	var shoulder := collision.raycast_ground(scene, Vector3(101.1, 21.0, 41.1), 10.0)
	if road.is_empty() or shoulder.is_empty():
		push_error("The 500 m exploration entry lost its road support")
		return
	bike.global_position = road.position + Vector3.UP * 0.035
	bike.safe_park_position = bike.global_position
	bike.rotation.y = -0.87
	scene.explorer.set_walk_origin(shoulder.position + Vector3.UP * 0.035, bike.global_position + Vector3.UP)
	if "--repair-court" in OS.get_cmdline_user_args():
		var site: Dictionary=scene.get_node("City/OuterDistrict500").get_meta("repair_court")
		bike.global_position=enu(site.bike)
		bike.safe_park_position=bike.global_position
		bike.tyre_pressure=1.15
		scene.explorer.set_walk_origin(enu(site.street)+Vector3.UP*.035,enu(site.porch)+Vector3.UP)
	elif "--shancheng" in OS.get_cmdline_user_args():
		var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
		var a: Array=layout.public_stops[0].approach
		var b: Array=layout.public_stops[0].target
		scene.explorer.set_walk_origin(Vector3(a[0],a[2],-a[1]),Vector3(b[0],b[1],b[2]))
	elif "--riverside" in OS.get_cmdline_user_args():
		var park := collision.raycast_ground(scene, Vector3(-205.0, -12.0, 210.0), 6.0)
		if not park.is_empty():
			scene.explorer.set_walk_origin(park.position + Vector3.UP * 0.035, Vector3(-191.0, -13.5, 214.0))
	elif "--match-factory" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MATCH_FACTORY_SITE))
		var point: Array = plan.walks_east_north.lower_frontage[0]
		var factory := collision.raycast_ground(scene, Vector3(point[0], 20.0, -point[1]), 15.0)
		if not factory.is_empty():
			scene.explorer.set_walk_origin(factory.position + Vector3.UP * .035, Vector3(230, 14, 119))
	elif "--matix-streets" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MATIX_SITE))
		var point: Array = plan.spawn_east_north
		var street := collision.raycast_ground(scene, Vector3(point[0], 48.0, -point[1]), 16.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, Vector3(-64, 42, -145))
	if "--outer-market" in OS.get_cmdline_user_args():
		var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
		for i in layout.plots.size():
			var p: Dictionary=layout.plots[i]
			if p.name!="照相巷便民市场": continue
			var a: float=p.bearing
			var v: float=-p.depth/2.0-1.92
			var u: float=-p.width*.27
			var landing:=Vector3(p.east_north[0]+cos(a)*u-sin(a)*v,p.height+.075,
				-p.east_north[1]-sin(a)*u-cos(a)*v)
			var focus:=Vector3(p.east_north[0],p.height+1.14,-p.east_north[1])
			scene.explorer.set_walk_origin(landing,focus)
			for lane: Dictionary in layout.lanes:
				if lane.type=="street" and lane.plots[0]==i:
					var xy: Array=lane.points[1]
					var ground:=collision.raycast_ground(scene,Vector3(xy[0],p.height+4.0,-xy[1]),22.0)
					if not ground.is_empty():
						bike.global_position=ground.position+Vector3.UP*.035
						bike.safe_park_position=bike.global_position
					break
			break
