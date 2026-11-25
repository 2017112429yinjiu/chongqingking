extends "../../scene_r24/street_blocks/timing.gd"

func timing_views() -> Array:
	return [
		["delivery_court",public_floor([-157.,39.5],21.),Vector3(-132.,25.,-49.)],
		["school_gate",public_floor([-138.6,36.1],22.),Vector3(-133.1,25.8,-47.)],
		["library_landing",Vector3(-132.2,26.51,-53.1),Vector3(-123.1,28.18,-55.5)],
	]
