extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(35)
	game=scene.gameplay
	var table:Node3D=game.get_node("TakeawayTable")
	print("FITTING counter_world ",table.global_transform)
	for part:MeshInstance3D in table.find_children("*","MeshInstance3D",true,false):
		var bounds:AABB=table.global_transform.affine_inverse()*part.global_transform*part.get_aabb()
		print("FITTING counter_part ",part.name," ",bounds)
	print("FITTING pupil ",table.to_local(game.shopkeeper.food_end)," mentor ",table.to_local(game.lesson.demo.counter_parcel_spot()))
	for part:MeshInstance3D in game.lesson.demo.pupil_box.box.find_children("*","MeshInstance3D",true,false):
		print("FITTING cargo ",part.name," ",game.lesson.demo.pupil_box.box.global_transform.affine_inverse()*part.global_transform*part.get_aabb())
	quit()
