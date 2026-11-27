extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/zhongxing-bridge-18-21.json"
const WALK := "COL_Zhongxing21_Public_Footway"

func site_plan() -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var baseline := "--qa-without-zhongxing-18-21" in OS.get_cmdline_user_args()
	check("legacy_frame_21", (scene.find_child("COL_Outer500_Frame_21",true,false)!=null) == baseline)
	check("old_deck_retained",scene.find_child("COL_R24_LinkDeck_R24_link_asphalt",true,false)!=null)
	var stations: Array = plan.lower_walk_21
	var hits := []
	var valid := 0
	for p: Array in stations:
		for transverse in [-.72,0.,.72]:
			var probe := [p[0]-.6152*transverse,p[1]+.7884*transverse]
			var row := column(probe)
			var good := row.any(func(surface: Array) -> bool: return surface[0]==WALK and surface[2]>.86)
			hits.append({"point":probe,"hits":row,"walking_surface":good})
			valid += int(good)
	check("lower_21_support",baseline or valid==hits.size(),{"passed":valid,"total":hits.size(),"rays":hits})
	var first: Array = stations.front()
	var last: Array = stations.back()
	var old: Array = plan.lower_existing_terrain_21.back() if plan.has("lower_existing_terrain_21") else last
	return {"id":"zhongxing_21_public_roadside","stations":stations,
		"street_focus":[last[0],last[1],last[2]+1.57],"destination_y":old[2] if baseline else last[2],
		"return_focus":[first[0],first[1],first[2]+1.57]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var offset := INF
	var origin := Vector2(121.422,-44.846)
	var toward_northwest := Vector2(-.6152,.7884)
	for sample: Array in walks.back().trace_enu:
		offset = minf(offset,(Vector2(sample[0],sample[1])-origin).dot(toward_northwest))
	check(label+"_stayed_on_lower_margin",offset>4.13,offset)
	return result
