extends SceneTree
## Neutral stage inspection of production materials; separate from city acceptance.
var stage: Node3D
var camera: Camera3D
var actor: Node3D
var animator: AnimationPlayer
var clips: Dictionary={}
var skeleton: Skeleton3D
var capture_dir: String="res://verification_r18/character_lab"

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	root.size=Vector2i(1000,1000)
	root.scaling_3d_scale=1.0
	root.msaa_3d=Viewport.MSAA_4X
	stage=Node3D.new()
	root.add_child(stage)
	var environment: WorldEnvironment=WorldEnvironment.new()
	var env: Environment=Environment.new()
	env.background_mode=Environment.BG_COLOR
	env.background_color=Color(.065,.08,.09)
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color(.77,.84,1)
	env.ambient_light_energy=.40
	env.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled=true
	env.ssao_radius=.3
	env.ssao_intensity=1.1
	env.ssao_light_affect=.65
	environment.environment=env
	stage.add_child(environment)
	var key: DirectionalLight3D=DirectionalLight3D.new()
	key.rotation_degrees=Vector3(-38,-32,0)
	key.light_color=Color(1,.9,.79)
	key.light_energy=1.25
	key.shadow_enabled=true
	key.light_angular_distance=.8
	key.directional_shadow_max_distance=7
	key.shadow_bias=.02
	key.shadow_normal_bias=.10
	stage.add_child(key)
	var rim: DirectionalLight3D=DirectionalLight3D.new()
	rim.rotation_degrees=Vector3(-30,155,0)
	rim.light_color=Color(.69,.80,1)
	rim.light_energy=.65
	stage.add_child(rim)
	var plane: MeshInstance3D=MeshInstance3D.new()
	var ground: PlaneMesh=PlaneMesh.new()
	ground.size=Vector2(200,200)
	plane.mesh=ground
	var mat: StandardMaterial3D=StandardMaterial3D.new()
	mat.albedo_color=Color(.115,.13,.14)
	mat.roughness=.95
	plane.material_override=mat
	stage.add_child(plane)
	actor=preload("res://scripts/shopkeeper.gd").new()
	stage.add_child(actor)
	actor.autonomous=false
	animator=actor.animator
	skeleton=actor.skeleton
	for clip: String in animator.get_animation_list():
		for name: String in ["idle","serve","greet"]:
			if clip.to_lower().contains(name): clips[name]=clip
	camera=Camera3D.new()
	camera.fov=34
	stage.add_child(camera)
	camera.current=true
	DirAccess.make_dir_recursive_absolute(capture_dir)
	var evidence: Array=[]
	for view: Dictionary in [
		{"name":"front","position":Vector3(0,1.24,3.5),"target":Vector3(0,.94,0),"clip":"idle","time":0.0},
		{"name":"three_quarter","position":Vector3(1.6,1.35,3.0),"target":Vector3(0,.95,0),"clip":"idle","time":1.5},
		{"name":"face","position":Vector3(.50,1.68,1.24),"target":Vector3(0,1.50,0),"clip":"idle","time":0.0},
		{"name":"reach","position":Vector3(1.6,1.35,3.0),"target":Vector3(0,.95,0),"clip":"serve","time":1.15},
		{"name":"lift","position":Vector3(1.6,1.35,3.0),"target":Vector3(0,.95,0),"clip":"serve","time":1.65},
		{"name":"place","position":Vector3(1.6,1.35,3.0),"target":Vector3(0,.95,0),"clip":"serve","time":2.3}
		,{"name":"grip_close","position":Vector3(-.55,1.36,1.1),"target":Vector3(-.12,1.17,.4),"clip":"serve","time":1.65}
		,{"name":"blink_closed","position":Vector3(.50,1.68,1.24),"target":Vector3(0,1.50,0),"clip":"idle","time":0.0}
	]:
		camera.position=view.position
		camera.look_at(view.target)
		actor.attention.tracking=view.name in ["face","blink_closed"]
		actor.attention.target=camera.global_position
		animator.play(clips[view.clip],0)
		animator.seek(view.time,true)
		animator.advance(0)
		animator.pause()
		for mesh: MeshInstance3D in actor.find_children("*","MeshInstance3D",true,false):
			for shape: String in ["Blink_left","Blink_right"]:
				var index: int=mesh.find_blend_shape_by_name(shape)
				if index>=0:mesh.set_blend_shape_value(index,.96 if view.name=="blink_closed" else 0)
		for i in range(12):await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(capture_dir+"/"+view.name+".png")
		skeleton.force_update_all_bone_transforms()
		var wrist: Vector3=(skeleton.global_transform*skeleton.get_bone_global_pose(skeleton.find_bone("hand_r"))).origin
		evidence.append({"view":view.name,"clip":view.clip,"time":view.time,"wrist":str(wrist)})
	FileAccess.open(capture_dir+"/captures.json",FileAccess.WRITE).store_string(JSON.stringify({"asset":FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH),"runtime_materials":true,"bone_count":skeleton.get_bone_count(),"views":evidence},"\t"))
	print("CHARACTER_LAB_CAPTURED ",evidence.size())
	quit()
