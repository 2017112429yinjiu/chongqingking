extends RefCounted
## Exercise the actual post-animation head/eye modifier against front observers.
static func run(npc: Node3D,main: Node3D) -> Dictionary:
	var previous_capture: bool=main.capture_mode
	main.capture_mode=true # Keep gameplay observer updates from overwriting test targets.
	var samples: Array=[]
	var valid: bool=npc.skeleton.find_bone("eye_l")>=0 and npc.skeleton.find_bone("eye_r")>=0
	var max_error: float=0.0
	var max_socket_motion: float=0.0
	# Arrival behaviour must ignore people behind the shopkeeper and avoid timer nods.
	npc.autonomous=true
	npc.visitor_present=false
	npc.last_greeting=-30.0
	npc.greet_nearby(npc.to_global(Vector3(0,1.57,-2)))
	var ignores_behind: bool=npc.last_greeting==-30.0
	npc.greet_nearby(npc.to_global(Vector3(0,1.57,2)))
	var front_greeted: bool=npc.visitor_present and npc.last_greeting>=0
	npc.last_greeting=-30.0 # Simulate passing the old repeat interval without leaving.
	npc.greet_nearby(npc.to_global(Vector3(0,1.57,2)))
	var no_repeat: bool=npc.last_greeting==-30.0
	npc.autonomous=false
	npc.animator.play(npc.available_clips["idle"],0)
	if valid:
		npc.attention.tracking=true
		for angle: float in [-.42,0,.42]:
			npc.attention.target=npc.to_global(Vector3(sin(angle)*2,1.57,cos(angle)*2))
			for frame in range(60):await npc.get_tree().process_frame
			# Modified poses only exist inside this signal, before Godot restores
			# animation inputs. See SkeletonModifier3D.modification_processed.
			await npc.attention.modification_processed
			for name: String in ["eye_l","eye_r"]:
				var index: int=npc.skeleton.find_bone(name)
				var pose: Transform3D=npc.skeleton.global_transform*npc.skeleton.get_bone_global_pose(index)
				var forward: Vector3=pose.basis.y.normalized()
				var direction: Vector3=(npc.attention.target-pose.origin).normalized()
				var error: float=rad_to_deg(acos(clampf(forward.dot(direction),-1,1)))
				max_error=maxf(max_error,error)
				var parent: int=npc.skeleton.get_bone_parent(index)
				var local: Transform3D=npc.skeleton.get_bone_global_pose(parent).affine_inverse()*npc.skeleton.get_bone_global_pose(index)
				max_socket_motion=maxf(max_socket_motion,local.origin.distance_to(npc.skeleton.get_bone_rest(index).origin))
				samples.append({"observer_angle":angle,"eye":name,"angle_error_degrees":error,"forward":str(forward)})
		npc.attention.tracking=false
	main.capture_mode=previous_capture
	return {"tests":{"both_eye_bones":valid,"front_observer_eye_error_under_5deg":valid and max_error<5.0,"eyeballs_remain_in_sockets":valid and max_socket_motion<.0005,"greeting_ignores_people_behind":ignores_behind,"greeting_recognizes_front_arrival":front_greeted,"greeting_does_not_repeat_at_stationary_customer":no_repeat},"max_error_degrees":max_error,"max_socket_motion_m":max_socket_motion,"samples":samples}
