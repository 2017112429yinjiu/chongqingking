extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/wilderness-50.json"
const FINISH := "res://assets/district_500/wilderness-50-finish.json"

var plan: Dictionary
var parent_run := "--qa-without-wilderness-50" in OS.get_cmdline_user_args()

func site_plan() -> Dictionary:
	plan = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var points: Array = plan.public_route
	var last: Array = points.back()
	if not parent_run:
		var reused := {}
		for id: String in plan.new_meshes:
			var part := scene.find_child(id,true,false) as MeshInstance3D
			if part==null:
				continue
			for index in part.mesh.get_surface_count():
				var finish := part.mesh.surface_get_material(index) as BaseMaterial3D
				if finish!=null and finish.albedo_texture!=null:
					reused[finish.resource_name]=finish.albedo_texture.resource_path
		var expected: Dictionary=plan.surface_textures.duplicate()
		if not "--qa-without-wilderness-50-finish" in OS.get_cmdline_user_args():
			var finish_plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(FINISH))
			for legacy: String in ["Renai remnant damp coursed rubble","Renai remnant worn upper stones"]:
				expected.erase(legacy)
			expected.merge(finish_plan.surface_textures)
		check("uses_registered_stock_texture_resources",reused==expected,reused)
	return {"id":"renai50_public_ruin_edge", "stations":points,
		"destination_y":last[2] - (.074 if parent_run else 0.),
		"street_focus":[points[2][0],points[2][1],points[2][2]+1.35],
		"return_focus":[points[2][0],points[2][1],points[2][2]+1.24]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var trace: Array = walks.back().trace_enu
	var support_count := 0
	var contacts := {}
	for entry: Array in trace:
		var sample := Vector3(entry[0],entry[2]+.20,-entry[1])
		var query := PhysicsRayQueryParameters3D.create(sample,sample-Vector3.UP*.66,1)
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(query)
		var body := "unhit" if hit.is_empty() else String(hit.collider.get_parent().name)
		contacts[body]=int(contacts.get(body,0))+1
		if body=="COL_Renai50_PublicFlagstones":
			support_count+=1
	if not parent_run:
		check(label+"_on_public_flagstones",support_count==trace.size(),{"samples":trace.size(),"surface_contacts":contacts})
	if label.ends_with("_out"):
		var point: Array=walks.back().finish_enu
		var end:=Vector2(point[0],point[1])
		var footprint:=PackedVector2Array()
		for edge: Array in plan.old_outline_en:
			footprint.append(Vector2(edge[0],edge[1]))
		var old_center:=Vector2(plan.old_center_en[0],plan.old_center_en[1])
		var distance:=INF
		for index in footprint.size():
			var edge:=Geometry2D.get_closest_point_to_segment(end,footprint[index],footprint[(index+1)%footprint.size()])
			distance=min(distance,end.distance_to(edge))
		check("turn_outside_old_footprint",not Geometry2D.is_point_in_polygon(end,footprint),
			{"east_north":[end.x,end.y],"old_outline_distance_m":distance,"old_center_distance_m":end.distance_to(old_center)})
	return result
