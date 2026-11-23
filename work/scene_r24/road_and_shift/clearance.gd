extends "../../scene_r24/road_and_shift/probe.gd"
var trace:Array=[]
var observed:Vector3
func sample():
	if is_instance_valid(lesson) and lesson.step==lesson.Step.TO_YARD and observed.distance_to(lesson.mentor.global_position)>.30:
		observed=lesson.mentor.global_position
		trace.append(observed)
func _initialize():
	physics_frame.connect(sample)
	super()
func finish():
	var hits:Dictionary={}
	for mesh:MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):
		if not mesh.mesh or not mesh.is_visible_in_tree() or not scene.get_node("City").is_ancestor_of(mesh):continue
		var box:AABB=mesh.global_transform*mesh.get_aabb()
		if not box.intersects(AABB(Vector3(-50,11,18),Vector3(28,7,40))):continue
		var name_:String=str(mesh.name)
		if name_.begins_with("COL_") or name_.begins_with("COLH_") or mesh.skin:continue
		var near:Array[Vector3]=[]
		for position:Vector3 in trace:
			if box.grow(.74).has_point(position+Vector3.UP*.75):near.append(position)
		if near.is_empty():continue
		for surface in mesh.mesh.get_surface_count():
			var verts:PackedVector3Array=mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
			for v in verts:
				var q:Vector3=mesh.to_global(v)
				for p in near:
					if q.y-p.y<.06 or q.y-p.y>1.85 or Vector2(q.x-p.x,q.z-p.z).length()>.45:continue
					hits[str(mesh.get_path())]={"vertex":str(q),"rider":str(p)}
					break
				if hits.has(str(mesh.get_path())):break
	FileAccess.open(output.path_join("visual_clearance.json"),FileAccess.WRITE).store_string(JSON.stringify(hits,"\t"))
	print("PATH_VISUAL ",JSON.stringify(hits))
	super()
