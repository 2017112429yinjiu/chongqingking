extends "../../../continuous_site_walk.gd"

var art := {}

func site_plan() -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://assets/district_500/collectibles-market.json"))
	var side := "--qa-market-side" in OS.get_cmdline_user_args()
	if not "--qa-without-collectibles" in OS.get_cmdline_user_args():
		art = plan.interior_art
		check_finish("Huihuigou_TerrazzoPaving","Market terrazzo panel",.95,9.8,false)
		check_finish("Huihuigou_WainscotAndShutters","Market wall exposed plaster",1.44,9.0,true)
		check("entry_finish_imported", scene.find_child("Huihuigou_EntryShoulderAndNosing",true,false)!=null)
	return {"id":"zhongxing_collectibles_side" if side else "zhongxing_collectibles",
		"stations":plan.side_route_east_north if side else plan.route_east_north,
		"street_focus":plan.street_eye_target_east_north_up,
		"return_focus":plan.return_eye_target_east_north_up,
		"destination_y":plan.side_landing_floor_m if side else plan.hall_floor_m}

func check_finish(mesh_name: String, prefix: String, expected_repeat: float, min_x: float, should_have_normal: bool) -> void:
	var item := scene.find_child(mesh_name,true,false) as MeshInstance3D
	if not check(mesh_name+"_exists",item!=null):
		return
	var mesh := item.mesh as ArrayMesh
	var material_checks := []
	for surface in mesh.get_surface_count():
		var finish := mesh.surface_get_material(surface) as BaseMaterial3D
		if finish == null or not finish.resource_name.begins_with(prefix):
			continue
		var arrays := mesh.surface_get_arrays(surface)
		var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		var repeats := PackedFloat32Array()
		if positions.size() == uvs.size():
			for i in range(0,indices.size(),3):
				for link in 3:
					var a := indices[i+link]
					var b := indices[i+((link+1)%3)]
					var dx := absf(positions[a].x-positions[b].x)
					var du := absf(uvs[a].x-uvs[b].x)
					if dx > .10 and du > .04:
						repeats.append(dx/du)
		repeats.sort()
		var repeat_m := repeats[repeats.size()/2] if not repeats.is_empty() else 0.
		var t := finish.albedo_texture
		material_checks.append({"name":finish.resource_name,"vertex_count":positions.size(),
			"uv_count":uvs.size(),"repeat_m":repeat_m,"uv_edge_samples":repeats.size(),
			"albedo_size":str(t.get_size()) if t else "",
			"normal_enabled":finish.normal_enabled,
			"pass":t!=null and uvs.size()==positions.size() and absf(repeat_m-expected_repeat)<.035
				and (finish.normal_enabled or not should_have_normal)})
	check(mesh_name+"_uv_and_scale",item.get_aabb().size.x>min_x and not material_checks.is_empty()
		and material_checks.all(func(entry: Dictionary) -> bool: return entry.pass),
		{"bbox_m":str(item.get_aabb().size),"materials":material_checks})

func eye_frame(label: String, focus: Variant) -> void:
	await super.eye_frame(label,focus)
	if label == "street" and not art.is_empty() and not "--qa-market-side" in OS.get_cmdline_user_args():
		await art_frame("doorway_stock_eye",art.inside_eye_east_north_up,art.inside_target_east_north_up)
		await art_frame("threshold_close",art.threshold_eye_east_north_up,art.threshold_target_east_north_up)

func art_frame(label: String, position: Array, focus: Array) -> void:
	var eye := Vector3(position[0],position[2],-position[1])
	var target := Vector3(focus[0],focus[2],-focus[1])
	await shot(label,eye,target)
	scene.explorer.camera.make_current()
	view_positions.append({"frame":label+".png","eye_enu":enu(eye),
		"target_enu":enu(target),"pixel_size":str(root.size)})
