extends "../../scene_r24/outer_neighborhood/survey.gd"

var cache:Dictionary={}
var meshes:Array[Node]
func trace(eye:Vector3,ray:Vector3) -> Dictionary:
	var limit:=20.
	var best:={}
	for node:MeshInstance3D in meshes:
		if not node.mesh or not node.is_visible_in_tree() or node.name in ["R22_Bank_Outer","R22_Bank_Relief"]:continue
		var local:=node.to_local(eye)
		var end:=node.to_local(eye+ray*limit)
		if node.get_aabb().intersects_segment(local,end)==null:continue
		var id:=node.mesh.get_instance_id()
		if not cache.has(id):cache[id]=node.mesh.generate_triangle_mesh()
		var tree:TriangleMesh=cache[id]
		if not tree:continue
		var hit:=tree.intersect_segment(local,end)
		if hit.is_empty():continue
		var where:=node.to_global(hit.position)
		var dist:=eye.distance_to(where)
		if dist<limit:
			limit=dist
			best={"node":str(scene.get_path_to(node)),"where":[where.x,where.y,where.z],"metres":dist}
	return best

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(25)
	RenderingServer.render_loop_enabled=false
	scene.hud.hide()
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CQ_MAP_VIEWS")))
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.make_current()
	meshes=scene.find_children("*","MeshInstance3D",true,false)
	var report:={}
	for spec:Array in [["plot_56_room",Vector2(.83,.81)],["plot_42_room",Vector2(.654,.606)],["plot_02_street",Vector2(.60,.65)]]:
		var key:String=spec[0]
		var v:Dictionary=records.views.filter(func(r):return r.key==key)[0]
		camera.position=Vector3(v.eye[0],v.eye[1],v.eye[2])
		camera.look_at(Vector3(v.target[0],v.target[1],v.target[2]))
		camera.fov=v.fov
		await process_frame
		RenderingServer.force_draw(false,1./60.)
		root.get_texture().get_image().save_jpg(output.path_join(key+"_live.jpg"),.94)
		var pt:Vector2=spec[1]*root.get_visible_rect().size
		var start:=camera.project_ray_origin(pt)
		var ray:=camera.project_ray_normal(pt)
		var first:=trace(start,ray)
		if first.is_empty():continue
		var node:MeshInstance3D=scene.get_node(first.node)
		node.hide()
		await process_frame
		RenderingServer.force_draw(false,1./60.)
		root.get_texture().get_image().save_jpg(output.path_join(key+"_isolated.jpg"),.94)
		report[key]={"uv":[spec[1].x,spec[1].y],"first":first,"next":trace(start,ray)}
		node.show()
	FileAccess.open(output.path_join("pixels.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	quit(0 if report.size()==3 else 2)
