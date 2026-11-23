extends SceneTree
func _initialize()->void:call_deferred("run")

func run()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null or not game.has_node("City/CourtyardLife14"):await physics_frame
	for i in 3:await physics_frame
	var which="court" if "--court" in OS.get_cmdline_user_args() else "west"
	var dest=OS.get_cmdline_user_args()[-1]
	DirAccess.make_dir_recursive_absolute(dest)
	var walker=game.explorer
	var course=[Vector3(-73.61,15.2,24.15),Vector3(-72.25,15.6,22.8),Vector3(-70.92,15.9,21.44),Vector3(-69.46,16.,20.32),Vector3(-68.87,16.,19.5)]
	var footage=[];var positions=[];var tick_count=960 if which=="court" else 620
	var moved:=0.;var max_jump:=0.;var index:=1;var reached:bool=which=="court";var pause:=0
	game.hud.hide()
	if which=="court":
		walker.go_to_view("r24_chess_table")
	else:
		var start=course[0];var hit=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP*2.,start-Vector3.UP*2.,1))
		if hit.is_empty():quit(2);return
		walker.begin_route_test(hit.position+Vector3.UP*.03,course[1])
	for i in 12:await physics_frame
	var last:Vector3=walker.body.global_position
	var scene=game.get_node("City/CourtyardLife14")
	for tick in tick_count:
		if which=="west":
			var pos:Vector3=walker.body.global_position
			var gaze:=Vector3(-67.18,pos.y-.29,18.52)
			walker.aim_route_test(gaze)
			if not reached:
				var target:Vector3=course[index];var dir=target-pos;dir.y=0.
				if dir.length()<.22:
					index+=1
					if index==course.size():reached=true
				if not reached:
					var forward:Vector3=-walker.camera.global_basis.z;forward.y=0;forward=forward.normalized()
					var right=forward.cross(Vector3.UP)
					dir=course[index]-pos;dir.y=0.;dir=dir.normalized()
					walker.automation_axis=Vector2(dir.dot(right),-dir.dot(forward))*.65
			if reached:walker.automation_axis=Vector2.ZERO;pause+=1
		await physics_frame
		if which=="west":
			var cur:Vector3=walker.body.global_position
			moved+=Vector2(cur.x-last.x,cur.z-last.z).length()
			max_jump=maxf(max_jump,cur.distance_to(last));last=cur
		if tick%6==0:
			await RenderingServer.frame_post_draw
			var im=root.get_texture().get_image()
			if im.is_empty() or im.save_jpg(dest.path_join("frame_%03d.jpg"%footage.size()),.91)!=OK:quit(3);return
			footage.append([tick,scene.local_time,scene.sorting_time,scene.eye_contact])
			positions.append([last.x,last.y,last.z])
		if which=="west" and pause>=240:break
	if which=="west":walker.end_route_test()
	var result={"route":which,"reached":reached,"waypoints":index,"frames":footage,"player_positions":positions,"metres":moved,"max_step":max_jump}
	FileAccess.open(dest+"/take.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("COURT14_TAKE ",which," ",reached," ",moved," ",footage.size()," ",max_jump)
	quit(0 if reached and max_jump<.45 else 4)

