extends SceneTree
var actor: Node3D
var scooter: Node3D
var animator: AnimationPlayer
var camera: Camera3D
var stage: Node3D
func _initialize() -> void:call_deferred("run")
func run() -> void:
	root.size=Vector2i(1440,1080)
	root.msaa_3d=Viewport.MSAA_4X
	stage=Node3D.new();root.add_child(stage)
	var world: WorldEnvironment=WorldEnvironment.new()
	var env: Environment=Environment.new()
	env.background_mode=Environment.BG_COLOR;env.background_color=Color(.065,.08,.09)
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color(.77,.84,1);env.ambient_light_energy=.40
	env.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled=true;env.ssao_radius=.3;env.ssao_intensity=1.1;env.ssao_light_affect=.65
	world.environment=env;stage.add_child(world)
	var key: DirectionalLight3D=DirectionalLight3D.new();key.rotation_degrees=Vector3(-38,-32,0)
	key.light_color=Color(1,.9,.79);key.light_energy=1.25;key.shadow_enabled=true
	key.directional_shadow_max_distance=7;key.shadow_bias=.02;key.shadow_normal_bias=.10
	stage.add_child(key)
	var rim: DirectionalLight3D=DirectionalLight3D.new();rim.rotation_degrees=Vector3(-30,155,0)
	rim.light_color=Color(.69,.80,1);rim.light_energy=.65;stage.add_child(rim)
	var floor_mesh: MeshInstance3D=MeshInstance3D.new();var plane: PlaneMesh=PlaneMesh.new();plane.size=Vector2(200,200)
	floor_mesh.mesh=plane;stage.add_child(floor_mesh)
	var floor_mat: StandardMaterial3D=StandardMaterial3D.new();floor_mat.albedo_color=Color(.17,.19,.20);floor_mat.roughness=.9;floor_mesh.material_override=floor_mat
	camera=Camera3D.new();camera.fov=40;stage.add_child(camera);camera.current=true
	scooter=load("res://assets/scooter.glb").instantiate();stage.add_child(scooter)
	actor=load("res://assets/rider.glb").instantiate();stage.add_child(actor)
	for mesh: MeshInstance3D in actor.find_children("*","MeshInstance3D",true,false):
		for surface in range(mesh.mesh.get_surface_count()):
			var mat: StandardMaterial3D=mesh.mesh.surface_get_material(surface).duplicate()
			if mat.resource_name.contains("head"):
				mat.subsurf_scatter_enabled=true;mat.subsurf_scatter_skin_mode=true;mat.subsurf_scatter_strength=.10
			if mat.resource_name.contains("opacity"):mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
			mesh.set_surface_override_material(surface,mat)
	animator=actor.find_child("AnimationPlayer",true,false)
	print("RIDER_CLIPS ",animator.get_animation_list())
	DirAccess.make_dir_recursive_absolute("res://evidence")
	var views: Array=[
		["side","ride_steer",1.,Vector3(3.1,1.4,0),Vector3(0,.95,0),0.],
		["front","ride_steer",1.,Vector3(1.9,1.7,-2.7),Vector3(0,.9,0),0.],
		["rear","ride_steer",1.,Vector3(-2.0,1.9,2.9),Vector3(0,1.,.1),0.],
		["hands","ride_steer",1.,Vector3(1.05,1.60,-1.25),Vector3(0,1.12,-.36),0.],
		["left","ride_steer",0.,Vector3(1.8,1.8,-2.7),Vector3(0,1.,0),-.32],
		["right","ride_steer",2.,Vector3(-1.8,1.8,-2.7),Vector3(0,1.,0),.32],
		["support","ride_support",0.,Vector3(-2.8,1.2,-1.4),Vector3(0,.85,0),0.],
	]
	for view: Array in views:
		var clip: String=""
		for label: String in animator.get_animation_list():
			if label.ends_with(view[1]):clip=label
		assert(not clip.is_empty(),str(view))
		animator.play(clip,0);animator.seek(view[2],true);animator.advance(0);animator.pause()
		scooter.find_child("Steering",true,false).rotation.y=view[5]
		scooter.find_child("Kickstand",true,false).rotation.z=-1.10
		camera.position=view[3];camera.look_at(view[4])
		for i in range(12):await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://evidence/"+view[0]+".png")
	FileAccess.open("res://evidence/manifest.json",FileAccess.WRITE).store_string(JSON.stringify({"rider":FileAccess.get_sha256("res://assets/rider.glb"),"vehicle":FileAccess.get_sha256("res://assets/scooter.glb"),"views":views},"\t"))
	print("RIDER_REVIEW_CAPTURED");quit()
