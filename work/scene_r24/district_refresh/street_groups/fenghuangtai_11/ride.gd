extends "../houci_14_16/ride_connectors.gd"

const JUNCTION := "res://assets/district_500/fenghuangtai-11.json"

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	game=scene.gameplay
	bike=game.scooter
	bike.enter(game.actor)
	bike.automation=true
	var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(JUNCTION))
	var plan: Dictionary=spec.drive_stations
	var results := {}
	for way: String in plan:
		var points: Array=plan[way]
		var allowed := ["COL_Fenghuangtai11_Road_"+way,"COL_Fenghuangtai11_Road_176034697"]
		var forward:=await drive(points,allowed)
		points.reverse()
		var reverse:=await drive(points,allowed)
		for part in [["out",forward],["back",reverse]]:
			check(way+"_"+part[0],part[1].pass,{"metres":part[1].distance_m,"reached":part[1].reached,"targets":part[1].targets})
		results[way]={"forward":forward,"reverse":reverse}
	FileAccess.open(output.path_join("11-rides.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"checks":checks,"results":results,"scene":scene.scene_file_path,"identity":scene.scene_identity.district_500},"  "))
	quit(2 if ever_failed else 0)
