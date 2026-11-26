extends "../../../scene_r24/street_blocks/timing.gd"

# Registered player locations in the ground-floor school room.
func timing_views() -> Array:
	return [
		["end_shelves", Vector3(-132.12670,23.01430,-48.92344), Vector3(-126.84114,24.16930,-44.91445)],
		["window_desks", Vector3(-129.07928,23.01430,-45.86179), Vector3(-129.30173,23.92930,-44.71160)],
		["stair_foot", Vector3(-130.52897,23.01430,-53.06272), Vector3(-130.66055,24.12930,-47.18345)]
	]
