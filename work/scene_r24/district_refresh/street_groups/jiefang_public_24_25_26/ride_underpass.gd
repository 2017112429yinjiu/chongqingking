extends "../houci_14_16/ride_connectors.gd"

const FIELD := "res://../../scene_r24/district_refresh/street_groups/jiefang_public_24_25_26/field.json"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	game = scene.gameplay
	bike = game.scooter
	bike.enter(game.actor)
	bike.automation = true
	var field: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FIELD))
	var road: Dictionary = field.old_plots["02"].ways.filter(
		func(way: Dictionary) -> bool: return int(way.way)==1256859184)[0]
	var a: Array = road.east_north[1]
	var b: Array = road.east_north[2]
	var rows := []
	var road_contacts := []
	var allowed := []
	for east: float in [50.,56.,62.,68.,74.,80.,86.,92.,98.,104.]:
		var north := lerpf(a[1],b[1],(east-a[0])/(b[0]-a[0]))
		var section := support(Vector3(east,-1.4,-north),.78,4.)
		road_contacts.append({"east_north":[east,north],"support":section})
		var body: String = section.get("body","")
		if not body.is_empty() and not body.begins_with("COL_Changbin02"):
			if not body in allowed:
				allowed.append(body)
			rows.append([east,north,section.y])
	check("roadline_separate_from_pier_band",rows.size()==10,road_contacts)
	var results := {}
	if rows.size()==10:
		results.forward = await drive(rows,allowed)
		rows.reverse()
		results.closed_reverse = await drive(rows,allowed)
		for direction: String in results.keys():
			var result: Dictionary = results[direction]
			check("roadline_"+direction,result.pass and result.last_contact.is_empty(),
				[result.distance_m,result.reached,result.airborne_frames,result.last_contact])
	FileAccess.open(output.path_join("underpass-ride.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"road_osm":1256859184,"support":road_contacts,"results":results,"checks":checks},"  "))
	quit(2 if ever_failed else 0)
