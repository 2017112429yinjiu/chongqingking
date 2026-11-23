extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null:await physics_frame
	await physics_frame
	var city:=main.get_node("City")
	var roofs:=city.get_node("RoofsAndBreakfastR22")
	var river:=city.get_node("RiverContextR22")
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/roofs_r22/layout.json"))
	var bank: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/river_r22/layout.json"))
	var tests: Dictionary={}
	if main.art_profile.has("surface_import_revision"):
		var recipes:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/roofs_r22/surface_imports.json"))
		var match_count:=0
		for item:Dictionary in recipes.maps:
			var path:="res://"+str(item.path)
			if FileAccess.get_sha256(path)==item.validated_import_sha256 and FileAccess.get_sha256(path.trim_suffix(".import"))==item.image_sha256:
				match_count+=1
		tests["active_source_and_bptc_recipe_hashes"]=match_count==32 and recipes.revision==main.art_profile.surface_import_revision
	var decks:=0
	for spec: Dictionary in plan.decks:
		var mesh:=roofs.find_child(spec.name,true,false) as MeshInstance3D
		if mesh==null:continue
		var finish:=mesh.get_active_material(0) as StandardMaterial3D
		if finish!=null and finish.albedo_texture!=null and finish.albedo_texture.get_width()>=256:decks+=1
	tests["projected_decks_loaded_with_textures"]=decks==13 and decks==plan.decks.size()
	for activity: String in ["garden","drying","service","pergola"]:
		tests["editable_"+activity+"_present"]=roofs.find_children("R22_"+activity+"_*","MeshInstance3D",true,false).size()>0
	var canvas:=roofs.find_child("R22_Breakfast_canvas",true,false) as MeshInstance3D
	var cloth:=canvas.get_surface_override_material(0) as ShaderMaterial
	tests["breakfast_fabric_and_breeze_loaded"]=cloth!=null and cloth.get_shader_parameter("fabric") is Texture2D
	var low:=Vector3(-30.5,13.237,59.71)
	var space:=main.get_world_3d().direct_space_state
	var floor_hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(low-Vector3.UP*.06,low-Vector3.UP*4,1))
	var clearance: float=low.y-floor_hit.position.y if not floor_hit.is_empty() else -1.
	tests["canopy_front_clears_walk_surface"]=clearance>2.05
	var q: Array=bank.street_sightlines[0].eye
	var eye:=Vector3(q[0],q[1],q[2])
	var walk:=space.intersect_ray(PhysicsRayQueryParameters3D.create(eye,eye-Vector3.UP*2.0,1))
	tests["street_river_view_on_existing_ground"]=not walk.is_empty() and absf(eye.y-walk.position.y-1.65)<.07
	for donor: String in bank.terrain:
		var old:=city.find_child(donor,true,false) as MeshInstance3D
		var new_bank:=river.find_child(bank.terrain[donor].replacement,true,false) as MeshInstance3D
		var surface:=new_bank.get_active_material(0) as ShaderMaterial
		var expected: bool=surface.get_shader_parameter("shore") is Texture2D
		if donor=="Outer_ground_context_ground_dirt":
			expected=expected and surface.get_shader_parameter("outer_ground") and surface.get_shader_parameter("tree_shade")==old.get_active_material(0).get_shader_parameter("tree_shade")
		tests["terrain_finish_"+donor]=not old.visible and new_bank.is_visible_in_tree() and expected
	tests["river_sheet_visible"]=river.find_child("R22_Water_sheet_river",true,false).is_visible_in_tree()
	var shoal:=river.find_child("R22_Sandbar",true,false) as MeshInstance3D
	tests["independent_sandbar_finish"]=shoal.is_visible_in_tree() and shoal.get_active_material(0).get_shader_parameter("shoal")
	tests["two_mapped_bridge_axes"]=bank.axes.size()==2
	tests["outlying_buildings_rendered"]=river.find_children("R22_Opposite_bank*","MeshInstance3D",true,false).size()>0 and bank.mapped_buildings.size()>0
	tests["traffic_has_no_playable_colliders"]=river.find_children("*","CollisionObject3D",true,false).is_empty()
	river.set_process(false)
	river.update_traffic(0.)
	var before: Array=[]
	for row: Dictionary in river.fleet:before.append(row.actor.position)
	river.update_traffic(3.)
	var distances: Array=[]
	for i in river.fleet.size():
		var row: Dictionary=river.fleet[i]
		var delta: Vector3=row.actor.position-before[i]
		var forward: Vector3=(row.to-row.from).normalized()
		var signed_distance:=delta.dot(forward)*(-1 if row.reverse else 1)
		distances.append(signed_distance)
		tests["traffic_direction_and_speed_"+str(i)]=absf(signed_distance-row.speed*3.)<.15
	var vehicle: Dictionary=river.fleet[0]
	var wrap: float=(1.-vehicle.phase)*vehicle.length/vehicle.speed
	river.update_traffic(wrap)
	tests["far_traffic_wrap_hidden"]=not vehicle.actor.visible
	river.update_traffic(wrap+.04*vehicle.length/vehicle.speed)
	tests["far_traffic_reappears_on_deck"]=vehicle.actor.visible
	var passed:=not tests.values().has(false)
	var report: Dictionary={"passed":passed,"tests":tests,"decks":decks,"front_clearance_m":clearance,"traffic_3s_signed_m":distances}
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var path: String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(path)
	FileAccess.open(path+"/art_test.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("R22_ART_TEST ",JSON.stringify(tests))
	quit(0 if passed else 2)
