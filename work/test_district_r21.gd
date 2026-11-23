extends SceneTree
## Imported mesh, collision, exterior representation, real counter interaction.
func _initialize() -> void:call_deferred("run")

func run() -> void:
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null:await physics_frame
	await physics_frame
	var tests: Dictionary={}
	var c: Node3D=main.get_node("City")
	var kit: Node3D=c.get_node("DistrictEnvironmentR21")
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_r21/layout.json"))
	var surfaces: Array=[]
	var space:=main.get_world_3d().direct_space_state
	for bank: Dictionary in data.terraces:
		for i in bank.front.size()-1:
			var f: Array=bank.front[i]
			var b: Array=bank.rear[i+1]
			var aim:=Vector3((f[0]+b[0])*.5,bank.top,-(f[1]+b[1])*.5)
			var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(aim+Vector3.UP*.44,aim-Vector3.UP*.6,1))
			var ok:=not hit.is_empty() and str(hit.collider.get_parent().name)=="COL_R21_Bank_"+str(bank.name)
			surfaces.append({"name":bank.name,"first_hit":str(hit.collider.get_parent().name) if not hit.is_empty() else "","ok":ok})
	tests["both_terraces_walkable_on_import"]=surfaces.all(func(row):return row.ok)
	var solid_trunks:=0
	var imported_tree_heights: Array=[]
	for i in data.trees_and_shrubs.size():
		var item: Dictionary=data.trees_and_shrubs[i]
		if not item.trunk:continue
		var pos:=Vector3(item.position[0],item.position[1],item.position[2])
		var aim:=pos+Vector3.UP*1.1
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(aim+Vector3.RIGHT*.7,aim,1))
		if not hit.is_empty() and str(hit.collider.name)=="Trunk_%02d"%i:solid_trunks+=1
		var bounds: AABB
		var got:=false
		for label: String in item.donors:
			var piece:=kit.get_node("Plant_%02d_%s"%[i,label]) as MeshInstance3D
			var extent:=piece.global_transform*piece.get_aabb()
			bounds=bounds.merge(extent) if got else extent
			got=true
		imported_tree_heights.append({"specified":item.height,"imported":bounds.size.y,"root":str(pos)})
	tests["five_rooted_trunks_hit"]=solid_trunks==5
	tests["tree_dimensions_match_blender"]=imported_tree_heights.all(func(row):return absf(row.imported-row.specified)<row.specified*.06)
	var card_count:=0
	for patch: MultiMeshInstance3D in kit.find_children("*","MultiMeshInstance3D",true,false):card_count+=patch.multimesh.instance_count
	tests["exterior_instance_count_matches_sites"]=card_count==data.outer_canopy.size()
	var terrain:=c.find_child("Outer_ground_context_ground_dirt",true,false) as MeshInstance3D
	var exterior:=terrain.get_surface_override_material(0) as ShaderMaterial
	var mask:=exterior.get_shader_parameter("tree_shade") as Texture2D
	tests["exterior_receiver_imported"]=is_instance_valid(mask) and mask.get_size()==Vector2(1536,1536)
	# Read the authored linear mask at every world-space pivot; check the live
	# material separately above because a headless GPU image can be compressed.
	var image:=Image.load_from_file("res://assets/district_r21/exterior_sun_mask.png")
	var covered:=0
	for plant: Dictionary in data.outer_canopy:
		var uv: Vector2=(Vector2(plant.position[0],-plant.position[2])+Vector2.ONE*360.)/720.
		var pixel:=Vector2i(uv*Vector2(image.get_size()))
		if image.get_pixelv(pixel).g>.85:covered+=1
	tests["all_rendered_tree_roots_registered"]=covered==card_count
	tests["window_fittings_cover_planned_buildings"]=kit.find_children("R21_Inhabited_facade_*","MeshInstance3D",true,false).size()==10
	tests["stone_flights_visible"]=kit.find_children("R21_Dressed_*","MeshInstance3D",true,false).size()==2
	tests["previous_tread_cover_hidden"]=not c.find_child("R19_Stair_tread_caps_step_concrete",true,false).visible
	tests["previous_collision_present"]=c.find_child("COL_Walk_Central_stair_lane_step_concrete",true,false).has_node("CQ_StaticCollision")
	var footing_hits: Array=[]
	for foundation: Dictionary in data.footings:
		var sample: Dictionary=foundation.sample
		var mid: Array=sample.midpoint
		var outward:=Vector3(sample.outward[0],0,-sample.outward[1])
		var aim:=Vector3(mid[0],mid[2]-.72*float(sample.height),-mid[1])
		var query:=PhysicsRayQueryParameters3D.create(aim+outward*.30,aim-outward*.12,1)
		var hit:=space.intersect_ray(query)
		var outer_face:=str(hit.collider.get_parent().name) if not hit.is_empty() else ""
		# The preserved road kerb projects beyond its backing. Record the
		# first physical hit, then inspect the stone behind that specific kerb.
		if outer_face=="COL_Road_734116597_0_curb_concrete":
			query.exclude=[hit.collider.get_rid()]
			hit=space.intersect_ray(query)
		var backing:=str(hit.collider.get_parent().name) if not hit.is_empty() else ""
		footing_hits.append({"visible_collider":outer_face,"backing":backing})
		tests["masonry_support_"+str(foundation.source)]=backing==foundation.name
	tests["both_underbuilt_edges_present"]=footing_hits.size()==2
	var game: Node3D=main.gameplay
	var actor: Node3D=main.explorer
	actor.begin_route_test(main._pickup+Vector3(.52,.04,0),main._pickup)
	for i in range(45):await physics_frame
	# Fixture starts at the second visit. The separate delivery test covers the first journey.
	game.order=game.Order.DELIVERED
	game.delivered_count=1
	tests["second_order_selected_in_range"]=game.interact() and game.order==game.Order.PREPARING
	for i in range(215):await physics_frame
	tests["sealed_side_portion_requested"]=game.order==game.Order.READY and game.condiments.cup.visible and game.bag.ticket.text.contains("辣子另装")
	tests["pack_action_reachable"]=game.interact() and game.condiments.state==game.condiments.State.ADDING
	game.interact()
	tests["repeat_during_packing_keeps_order_ready"]=game.order==game.Order.READY
	for i in range(63):await physics_frame
	tests["portion_fits_on_noodle_lid"]=game.condiments.cup.get_parent()==game.bag and game.condiments.cup.position.distance_to(game.condiments.INSIDE)<.001
	tests["second_order_picked_up"]=game.interact() and game.order==game.Order.CARRYING and not game.condiments.cup.is_visible_in_tree()
	var used: String=game.bag.ticket.text+"台上那盒辣子另装放稳再提调料"
	tests["ticket_and_ui_glyphs_present"]=true
	for ch in used:
		if ch.unicode_at(0)>127 and not main.UI_FONT.has_char(ch.unicode_at(0)):tests["ticket_and_ui_glyphs_present"]=false
	var ok: bool=not tests.values().has(false)
	var report: Dictionary={"passed":ok,"tests":tests,"terrace_hits":surfaces,"footing_hits":footing_hits,"trunks":imported_tree_heights,"exterior_instance_count":card_count,"scope":"Live imported city geometry and second-order input. Order history initially set to one completed delivery in this isolated test."}
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var path: String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(path)
	FileAccess.open(path+"/district_test.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("DISTRICT_R21_QA ",JSON.stringify(tests))
	quit(0 if ok else 2)
