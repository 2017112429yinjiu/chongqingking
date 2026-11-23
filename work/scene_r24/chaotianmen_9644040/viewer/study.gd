extends Node3D

var cam := Camera3D.new()
var folder := ProjectSettings.globalize_path("res://../captures/")
var log_data := {}
var captures := []
static var current_view := 1
var interactive := false
var loaded_sample := ""
var status := Label.new()

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var sample := "street" if "--street" in args else "district"
	interactive = args.is_empty() or "--interactive-check" in args
	if interactive:
		sample = "street" if current_view >= 3 else "district"
	loaded_sample = sample
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var path := ProjectSettings.globalize_path("res://../" + sample + ".glb")
	var code := doc.append_from_file(path, state)
	if code != OK:
		push_error("GLB load error %d" % code)
		get_tree().quit(1)
		return
	var city := doc.generate_scene(state)
	if city == null:
		get_tree().quit(1)
		return
	add_child(city)
	var meshes := city.find_children("*","MeshInstance3D",true,false)
	if city is MeshInstance3D:
		meshes.append(city)
	var tris := 0
	for item in meshes:
		for i in item.mesh.get_surface_count():
			var count: int = item.mesh.surface_get_array_index_len(i)
			if count == 0:
				count = item.mesh.surface_get_array_len(i)
			tris += count / 3
	var sample_info = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path("res://../"+sample+"_sample.json")))
	if tris == 0 or tris != int(sample_info.stats.triangles):
		push_error("Triangle count mismatch %d / %d" % [tris,int(sample_info.stats.triangles)])
		get_tree().quit(1)
		return
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(.62,.73,.79)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(.9,.92,.95)
	env.ambient_light_energy = .55
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48,-35,0)
	sun.light_energy=.9
	sun.shadow_enabled=true
	sun.directional_shadow_max_distance=160. if sample == "street" else 2300.
	add_child(sun)
	add_child(cam)
	cam.current=true
	cam.near=.15
	cam.far=35000.
	DirAccess.make_dir_recursive_absolute(folder)
	log_data={"engine":Engine.get_version_info().string,"sample":sample,"meshes":meshes.size(),"triangles_seen_by_engine":tris}
	if interactive:
		add_child(status)
		status.position=Vector2(14,14)
		status.add_theme_constant_override("outline_size",5)
		show_view(current_view)
		Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
		if "--interactive-check" in args:
			if not await snap("interactive_"+str(current_view)):
				get_tree().quit(1)
				return
			if current_view<4:
				show_view(4)
			else:
				get_tree().quit(0)
		return
	var ok := true
	if "--base" in args:
		cam.projection=Camera3D.PROJECTION_ORTHOGONAL
		cam.size=4300.
		cam.global_position=Vector3(0,4500,0)
		cam.look_at(Vector3.ZERO,Vector3.FORWARD)
		ok=await snap("map")
		cam.projection=Camera3D.PROJECTION_PERSPECTIVE
		cam.fov=45.
		cam.global_position=Vector3(-2800,1600,2600)
		cam.look_at(Vector3(350,90,-150))
		ok=await snap("district") and ok
	for arg in args:
		if arg.begins_with("--plan="):
			var p := arg.trim_prefix("--plan=").split(",")
			var center := Vector3(p[1].to_float(),0.,p[2].to_float())
			cam.projection=Camera3D.PROJECTION_ORTHOGONAL
			cam.size=p[3].to_float()
			cam.global_position=center+Vector3.UP*4000.
			cam.look_at(center,Vector3.FORWARD)
			ok=await snap(p[0]) and ok
		if arg.begins_with("--view="):
			var v := arg.trim_prefix("--view=").split(",")
			if v.size()!=8:
				get_tree().quit(2)
				return
			cam.projection=Camera3D.PROJECTION_PERSPECTIVE
			cam.fov=v[7].to_float()
			cam.global_position=Vector3(v[1].to_float(),v[2].to_float(),v[3].to_float())
			cam.look_at(Vector3(v[4].to_float(),v[5].to_float(),v[6].to_float()))
			ok=await snap(v[0]) and ok
	log_data["captures"]=captures
	var key := "base" if "--base" in args else str(captures[0]["name"])
	FileAccess.open(folder.path_join(sample+"_"+key+".json"),FileAccess.WRITE).store_string(JSON.stringify(log_data,"  "))
	get_tree().quit(0 if ok else 1)

func show_view(index: int) -> void:
	current_view=index
	if (index >= 3) != (loaded_sample == "street"):
		get_tree().call_deferred("reload_current_scene")
		return
	var eyes := [Vector3(1650,43,-680),Vector3(2040,240,-1080),Vector3(430,81.549,642),Vector3(489,81.548,598)]
	var targets := [Vector3(385,117,542),Vector3(650,35,210),Vector3(469,84.5,654),Vector3(509,83,608)]
	cam.global_position=eyes[index-1]
	cam.look_at(targets[index-1])
	cam.fov=[50.,55.,67.,65.][index-1]
	status.text="朝天门模型复查    1 江岸    2 半岛    3 广场    4 店面\n鼠标环顾   WASD 自由观察   Q / E 升降   Shift 加速   Esc 释放鼠标"

func _unhandled_input(event: InputEvent) -> void:
	if not interactive or not cam.is_inside_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode>=KEY_1 and event.keycode<=KEY_4:
			show_view(int(event.keycode)-KEY_1+1)
		elif event.keycode==KEY_ESCAPE:
			Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton and event.pressed:
		Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
	elif event is InputEventMouseMotion and Input.mouse_mode==Input.MOUSE_MODE_CAPTURED:
		cam.rotation.y-=event.relative.x*.002
		cam.rotation.x=clampf(cam.rotation.x-event.relative.y*.002,-1.5,1.5)

func _process(delta: float) -> void:
	if not interactive or not cam.is_inside_tree() or Input.mouse_mode!=Input.MOUSE_MODE_CAPTURED:
		return
	var side:=float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A))
	var depth:=float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W))
	var height:=float(Input.is_physical_key_pressed(KEY_E))-float(Input.is_physical_key_pressed(KEY_Q))
	var direction:=cam.global_basis.x*side+cam.global_basis.z*depth+Vector3.UP*height
	var speed:=5.0 if loaded_sample=="street" else 110.0
	if Input.is_physical_key_pressed(KEY_SHIFT):
		speed*=4.0
	cam.global_position+=direction.normalized()*speed*delta

func snap(label: String) -> bool:
	for i in 5:
		await RenderingServer.frame_post_draw
	var im:=get_viewport().get_texture().get_image()
	var path:=folder.path_join(label+".jpg")
	if im == null or im.save_jpg(path,.94)!=OK:
		return false
	captures.append({"name":label,"position":str(cam.global_position),"sha256":FileAccess.get_sha256(path)})
	return true

