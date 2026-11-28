extends "../houci_14_16/ride_connectors.gd"

func thin(rows: Array, first: int, stride: int, size: int) -> Array:
	var paths: Array=[]
	for i in range(first,min(size,rows.size()),stride): paths.append(rows[i])
	var terminal: int=min(size,rows.size())-1
	if not paths.is_empty() and paths.back()!=rows[terminal]: paths.append(rows[terminal])
	return paths

func project_surface(rows: Array, owners: Array) -> Array:
	var revised: Array=[]
	for p: Array in rows:
		var contact:=support(world(p),.5,.55)
		if contact.get("body","") in owners:
			revised.append([p[0],p[1],contact.y])
		else:
			check("standing_join_anchor",false,{"enu":p,"contact":contact})
	return revised

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	game=scene.gameplay
	bike=game.scooter
	var grade:=Grade.installed_plan(scene)
	if grade.is_empty():
		check("grade_active",false)
		quit(2)
		return
	var original: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/nanqu-04-06-51.json"))
	var old_east: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var spur:=Grade.adjust(scene,old_east.roads["16"].centres_enu,true)
	var original_west:=Grade.adjust(scene,original.bike_path)
	var west: Array=grade.west_playable_tie_enu.slice(1,-1)+original_west.slice(0,7)
	var join: Array=thin(grade.east_public_join_enu,0,3,16)
	var spur_join: Array=thin(spur,31,7,spur.size()-2)+join
	var other_join: Array=thin(grade.east_incoming_join_enu,46,4,grade.east_incoming_join_enu.size()-1)+join
	var cases:Array=[
		["west_edge_to_original_lane",west,["COL_NanquGrade_WestPlayableTie","COL_Nanqu_RaisedWestApproach","COL_R24_LinkDeck_R24_link_asphalt"]],
		["mapped_16_into_176034697",spur_join,["COL_Houci16_Road_176968735","COL_NanquGrade_EastPublicJoin","COL_NanquGrade_EastApproachingBranch","COL_NanquGrade_EastJunctionApron"]],
		["mapped_1189963552_into_176034697",other_join,["COL_NanquGrade_EastApproachingBranch","COL_NanquGrade_EastPublicJoin","COL_Houci16_Road_176968735","COL_NanquGrade_EastJunctionApron"]],
	]
	var outcomes: Dictionary={}
	bike.enter(game.actor)
	bike.automation=true
	for course: Array in cases:
		var revised:=project_surface(course[1],course[2])
		if not check(course[0]+"_registered_anchors",revised.size()==course[1].size(),[revised.size(),course[1].size()]): continue
		var out:=await drive(revised,course[2],true)
		revised.reverse()
		var back:=await drive(revised,course[2],true)
		check(course[0]+"_forward",out.pass,out.reached)
		check(course[0]+"_reverse_closed_qa",back.pass,back.reached)
		outcomes[course[0]]={"out":out,"back":back}
	FileAccess.open(output.path_join("join-rides.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"runs":outcomes},"  "))
	quit(2 if ever_failed else 0)
