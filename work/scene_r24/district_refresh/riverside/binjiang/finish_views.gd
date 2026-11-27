extends "walk.gd"

const CAMERAS := [
	["72-entry", [125.3, -103.0, null], [117.67, -126.48, null], 51.0],
	["72-back", [117.4, -135.4, 9.51], [120.9, -111.0, 9.51], 54.0],
	["73-north", [149.9, -121.6, 13.96], [143.4, -139.25, 14.65], 55.0],
	["73-south", [143.10, -181.967, -1.888], [143.56, -170.0, 5.2], 57.0],
	["70-threshold", [88.15, -109.9, 9.35], [84.5, -115.04, 9.45], 56.0],
]

func site_plan() -> Dictionary:
	var route := super.site_plan()
	var footway := "COL_Binjiang_Entry72_Footway"
	if scene.find_child(footway,true,false) != null:
		var east := [[123.8,-111.85],[123.0,-115.63],[122.42,-119.16]]
		var west := [[117.65,-110.05],[116.95,-113.74],[116.05,-117.45]]
		var samples := []
		for en: Array in east + west:
			var layers := column(en)
			var supported: bool = not layers.is_empty() and layers[0][0] == footway and float(layers[0][2]) > .84
			samples.append({"en":en,"layers":layers,"paved":supported})
		check("two_distinct_entry_footways",samples.all(func(row: Dictionary) -> bool: return row.paved),samples)
		if "--binjiang-sidewalk-walk" in OS.get_cmdline_user_args():
			var stations: Array = route.stations
			route.stations = [stations[0]] + east + [[120.5,-120.15]] + stations.slice(3)
			route.id = "binjiang_72_east_footway"
	return route

func eye_frame(label: String, focus: Variant) -> void:
	if label == "street":
		for registered: Array in CAMERAS:
			if "--binjiang-entry-only" in OS.get_cmdline_user_args() and registered[0] != "72-entry":
				continue
			var frame := registered.duplicate(true)
			var eye: Array = frame[1]
			var hits := column([eye[0],eye[1]])
			if eye[2] == null and not hits.is_empty():
				eye[2] = float(hits[0][1])+1.63
				frame[2][2] = eye[2]-.96
			var eye_clearance: float = eye[2] - float(hits[0][1]) if not hits.is_empty() else 0.
			check("ground_below_"+frame[0], eye_clearance >= 1.37 and eye_clearance <= 1.78,
				{"hits":hits,"eye_height_m":eye_clearance})
			await fixed_view(frame)
	elif label == "inside_look_back":
		await super.eye_frame(label, focus)
