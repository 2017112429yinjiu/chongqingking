extends SceneTree

func _initialize()->void:call_deferred("draw")

func draw()->void:
	var city_scene:=preload("res://main.tscn").instantiate() as Node3D
	city_scene.set_script(null)
	root.add_child(city_scene)
	var city:=city_scene.get_node("City") as Node3D
	var flags:=OS.get_cmdline_user_args()
	var result:=preload("res://scripts/lane_connection_r24.gd").install(city,true,"--alley-inlets" in flags)
	var camera:=Camera3D.new()
	city_scene.add_child(camera)
	camera.global_position=Vector3(26.799273,24.566343,-6.865393)
	camera.look_at(Vector3(28.469639,22.931823,-11.285599),Vector3.UP)
	camera.fov=70.116399
	camera.current=true
	for i in 25:await RenderingServer.frame_post_draw
	var im:=root.get_texture().get_image()
	var ok:bool=result.replaced==9 and result.added==7 and not im.is_empty() and im.save_png(OS.get_cmdline_user_args()[-1])==OK
	print("EDITOR17_DRAW ",result.replaced," ",result.added," ",ok)
	quit(0 if ok else 5)
