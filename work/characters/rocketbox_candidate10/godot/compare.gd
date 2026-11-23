extends SceneTree
var camera: Camera3D
var stage: Node3D
func _initialize() -> void:call_deferred("run")
func run() -> void:
	root.size=Vector2i(1000,1000)
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
	camera=Camera3D.new();camera.fov=40;stage.add_child(camera);camera.current=true
	DirAccess.make_dir_recursive_absolute("res://evidence")
	var results: Array=[]
	for name: String in ["baseline20","candidate10"]:
		var actor: Node3D
		if name=="baseline20":
			actor=preload("res://scripts/shopkeeper.gd").new();stage.add_child(actor)
			actor.autonomous=false;actor.animator.play(actor.available_clips["idle"],0);actor.animator.seek(0,true);actor.animator.advance(0);actor.animator.pause()
		else:
			actor=load("res://assets/characters/candidate10.glb").instantiate();stage.add_child(actor)
			for mesh: MeshInstance3D in actor.find_children("*","MeshInstance3D",true,false):
				for surface in range(mesh.mesh.get_surface_count()):
					var mat: StandardMaterial3D=mesh.mesh.surface_get_material(surface).duplicate()
					if mat.resource_name.contains("head"):
						mat.subsurf_scatter_enabled=true;mat.subsurf_scatter_skin_mode=true;mat.subsurf_scatter_strength=.10
					if mat.resource_name.contains("opacity"):
						mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
					mesh.set_surface_override_material(surface,mat)
		for expression: String in ["neutral","warm","blink"]:
			if name=="baseline20":
				actor.set_smile(.30 if expression=="warm" else 0);actor.set_blink(.96 if expression=="blink" else 0)
			else:
				for mesh: MeshInstance3D in actor.find_children("*","MeshInstance3D",true,false):
					for i in range(mesh.mesh.get_blend_shape_count()):
						var label: String=str(mesh.mesh.get_blend_shape_name(i)).to_lower()
						var value: float=0
						# The source includes several naming sets for identical actions.
						# Drive only ARKit shapes, avoiding duplicate facial deformation.
						if label.begins_with("ak_"):
							if expression=="warm" and "mouthsmile" in label:value=.30
							if expression=="warm" and "cheeksquint" in label:value=.08
							if expression=="blink" and "eyeblink" in label:value=.96
						mesh.set_blend_shape_value(i,value)
			camera.position=Vector3(.23,1.60,1.05);camera.look_at(Vector3(0,1.51,0))
			for frame in range(20):await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("res://evidence/"+name+"_"+expression+".png")
			results.append({"model":name,"expression":expression,"camera":str(camera.position),"target":"(0,1.51,0)","shader":"Isolated comparable studio; candidate opacity depth prepass, dielectric materials"})
		actor.queue_free();await process_frame
	FileAccess.open("res://evidence/manifest.json",FileAccess.WRITE).store_string(JSON.stringify({"baseline":FileAccess.get_sha256("res://assets/characters/shopkeeper_r18.glb"),"candidate":FileAccess.get_sha256("res://assets/characters/candidate10.glb"),"views":results},"\t"))
	print("CANDIDATE_COMPARISON_COMPLETE");quit()
