extends SceneTree
var main: Node3D
func _initialize() -> void:
	call_deferred("run")
func xyz(v: Vector3) -> Array:return [v.x,v.y,v.z]
func run() -> void:
	main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while not is_instance_valid(main.gameplay) or main.street_block.tracks.is_empty():await process_frame
	var dest:="res://verification_r23/current/player"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dest))
	main.hud.visible=false
	var a: Node3D=main.explorer
	var info: Array=[]
	for t in main.street_block.tracks:
		if t.car:continue
		var rig: Skeleton3D=t.node.find_children("*","Skeleton3D",true,false)[0]
		var row: Dictionary={"agent":t.node.name,"bones":{}}
		for i in range(rig.get_bone_count()):
			var bn:=rig.get_bone_name(i)
			if not (bn.ends_with("UpperArm") or bn.ends_with("Hand") or bn.ends_with("Foot")):continue
			row.bones[bn]=xyz(t.node.to_local(rig.to_global(rig.get_bone_global_pose(i).origin)))
		info.append(row)
	var ff:=FileAccess.open(dest+"/rigs.json",FileAccess.WRITE)
	ff.store_string(JSON.stringify(info,"  "));ff.close()
	var path: Curve3D=main.street_block.routes.promenade
	var origin:=path.sample_baked(path.get_baked_length()*.56)
	var target:=path.sample_baked(path.get_baked_length()*.56-8.)
	a.begin_route_test(origin+Vector3.UP*.035,target)
	for i in range(30):await physics_frame
	await shoot("walk_level")
	a._pitch=-1.16
	for i in range(5):await physics_frame
	await shoot("look_at_feet")
	a.automation_axis=Vector2(0.,-.5)
	for i in range(26):await physics_frame
	await shoot("walking_stride")
	# End the deterministic input route before shutting down this review process.
	a.end_route_test()
	a.go_to_view("r23_shop_window")
	var first: Vector3=a.camera.position
	var horizontal: Vector3=a.camera.global_basis.x
	for shift in [-.38,.38]:
		a.camera.position=first+horizontal*float(shift)
		for i in range(5):await process_frame
		await shoot("window_left" if shift<0 else "window_right")
	quit()
func shoot(label: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://verification_r23/current/player/"+label+".png")

