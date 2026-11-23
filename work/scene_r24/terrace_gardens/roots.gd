extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	if DisplayServer.get_name()=="headless":
		push_error("Use the graphics renderer to read the planted instance transforms.")
		quit(3);return
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15)
	var space:=scene.get_world_3d().direct_space_state
	var roots:=[]
	var skip:Array[RID]=[]
	var trunk:=scene.find_child("COLH_Terrace21_Trunks",true,false)
	if trunk:skip.append(trunk.get_node("CQ_StaticCollision").get_rid())
	for inst:MultiMeshInstance3D in scene.find_children("TerracePlant_*","MultiMeshInstance3D",true,false):
		var tree:=str(inst.name).contains("Planted_tree")
		if tree and not str(inst.name).ends_with("_00"):continue
		var mm:=inst.multimesh
		var vertices:PackedVector3Array=mm.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
		for i in mm.instance_count:
			var transform:=inst.global_transform*mm.get_instance_transform(i)
			var low:=INF
			for v in vertices:low=minf(low,(transform*v).y)
			var sum:=Vector3.ZERO;var count:=0
			for v in vertices:
				var p:=transform*v
				if p.y<=low+.025:sum+=p;count+=1
			var root_pos:=sum/float(count);root_pos.y=low
			var ray:=PhysicsRayQueryParameters3D.create(root_pos+Vector3.UP*.12,root_pos-Vector3.UP*.25,1)
			ray.exclude=skip
			var hit:=space.intersect_ray(ray)
			roots.append({"donor":str(inst.name),"instance":i,"root":str(root_pos),"basis_origin":str(transform.origin),"bed":str(hit.collider.get_parent().name) if hit else "missing","root_minus_soil_m":root_pos.y-hit.position.y if hit else null})
	FileAccess.open(output.path_join("roots.json"),FileAccess.WRITE).store_string(JSON.stringify(roots))
	quit()
