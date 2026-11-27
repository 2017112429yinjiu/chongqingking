extends "../liangtingzi_45_46/walk.gd"

const PLAN := "res://assets/district_500/zhongxing-plaza-22-finish.json"
const APRON := "COL_Zhongxing22_ContinuousPublicApron"
const RIM := "COL_Zhongxing22_SealedStonePlanter"

func verification_site() -> Dictionary:
	return {"resource":PLAN,"surfaces":{"22":APRON}}

func ray(at: Array, top: float, bottom: float) -> Dictionary:
	var from := Vector3(at[0],top,-at[1])
	return scene.get_world_3d().direct_space_state.intersect_ray(
		PhysicsRayQueryParameters3D.create(from,Vector3(from.x,bottom,from.z),1))

func name_of(hit: Dictionary) -> String:
	return "" if hit.is_empty() else String(hit.collider.get_parent().name)

func measure_exposed_border() -> void:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var sections := []
	for row: Dictionary in plan.exposure_sections:
		var top: float = row.cap_y
		var floor_hit := ray(row.floor_en,top+.05,top-1.05)
		var cap_hit := ray(row.cap_en,top+.25,top-.18)
		var floor_y: float = floor_hit.position.y if not floor_hit.is_empty() else -999.
		var cap_y: float = cap_hit.position.y if not cap_hit.is_empty() else -999.
		var center := Vector3(row.wall_en[0],floor_y+.030,-row.wall_en[1])
		var normal := Vector3(row.test_normal[0],0.,-row.test_normal[1])
		var query := PhysicsRayQueryParameters3D.create(center+normal*.072,center-normal*.072,1)
		var face := scene.get_world_3d().direct_space_state.intersect_ray(query)
		var valid: bool = (name_of(floor_hit)==APRON and name_of(cap_hit)==RIM and name_of(face)==RIM
			and cap_y-floor_y >= .42 and cap_y-floor_y <= .70 and row.base_y<floor_y-.07)
		sections.append({"east_north":row.floor_en,"floor_y":floor_y,"cap_y":cap_y,
			"exposed_m":cap_y-floor_y,"base_below_floor_m":floor_y-row.base_y,
			"floor":name_of(floor_hit),"cap":name_of(cap_hit),"face_30mm_above_grade":name_of(face),"pass":valid})
	var valid_sections := sections.filter(func(section: Dictionary) -> bool: return section.pass)
	check("all_caps_exposed_and_faces_touch_paving",valid_sections.size()==48,valid_sections.size())
	FileAccess.open(output.path_join("cap-sections.json"),FileAccess.WRITE).store_string(JSON.stringify(sections,"  "))

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	if label.ends_with("_out"):
		measure_exposed_border()
	var result := await super.leg_without_placement(label,goals)
	var supported := 0
	var trace: Array = walks.back().trace_enu
	for row: Array in trace:
		var hit := ray(row.slice(0,2),row[2]+.18,row[2]-.24)
		supported += int(name_of(hit)==APRON)
	check(label+"_apron_contacts",supported==trace.size(),{"contacts":supported,"samples":trace.size()})
	return result
