extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null:
		await physics_frame
	var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[-1]+"/boundary.json"))
	var layers:Dictionary={}
	var failed:Array=[]
	for tag in ["yard_concrete","pavement"]:
		var mesh:MeshInstance3D=main.get_node("City").find_child("COL_Terrain_200m_"+tag,true,false)
		var body:StaticBody3D=mesh.get_node("CQ_StaticCollision")
		layers[body]=body.collision_layer
		body.collision_layer|=16
	await physics_frame
	var space:PhysicsDirectSpaceState3D=main.get_world_3d().direct_space_state
	var maximum_height_error:=0.0
	var correct:=0
	for sample in fixture.probes:
		var at=Vector3(sample.x,sample.h,sample.z)
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.30,at-Vector3.UP*.30,16))
		var tag="" if hit.is_empty() else str(hit.collider.get_parent().name).trim_prefix("COL_Terrain_200m_")
		var error=999.0 if hit.is_empty() else absf(hit.position.y-at.y)
		maximum_height_error=maxf(maximum_height_error,error)
		if tag!=sample.material or error>.001:
			failed.append([sample.x,sample.z,sample.material,tag,error])
		else:correct+=1
	for body in layers:body.collision_layer=layers[body]
	var installed=main.scene_identity.get("courtyard_paving",[])
	var passed:bool=failed.is_empty() and correct>0 and installed.size()==2
	var result={"passed":passed,"checked":fixture.probes.size(),"matches":correct,"runs":fixture.runs.size(),"failures":failed,"highest_m":maximum_height_error}
	var qa=preload("res://scripts/qa_context.gd")
	qa.decorate(result,main)
	var dir:String=qa.directory()
	DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir+"/paving.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("COURT14_PAVING ",passed," ",correct,"/",fixture.probes.size()," ",maximum_height_error)
	quit(0 if passed else 3)
