extends "../../continuous_site_walk.gd"

func market_point(plot: Dictionary, u: float, v: float) -> Vector3:
	var c := cos(float(plot.bearing))
	var s := sin(float(plot.bearing))
	var center: Array = plot.east_north
	return Vector3(center[0]+u*c-v*s,float(plot.height)+.09,-(center[1]+u*s+v*c))

func site_plan() -> Dictionary:
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary = layout.plots.filter(func(row: Dictionary) -> bool: return int(row.plot_id)==1)[0]
	var half: float = float(p.depth)*.5
	var u: float = p.door_u
	var route := [market_point(p,-float(p.width)*.27,-half-1.92),market_point(p,u,-half-1.96),
		market_point(p,u,-half+.94),market_point(p,u,-half+3.15)]
	return {"id":"market_01_hall","stations":route.map(enu),"destination_y":route.back().y-.09,
		"street_focus":enu(route[2]+Vector3.UP*.9),"return_focus":enu(route[1]+Vector3.UP*.9)}
