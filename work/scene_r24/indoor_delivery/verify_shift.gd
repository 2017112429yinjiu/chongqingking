extends "../../scene_r24/road_and_shift/verify_shift.gd"
const Unit=preload("res://scripts/unit_interior.gd")
func parking_landmark()->Vector3:
	return Unit.COURT
func pupil_return_path()->Array:
	return Array(Unit.downstairs(bike.last_exit))
