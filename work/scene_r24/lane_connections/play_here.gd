extends SceneTree

func _initialize()->void:call_deferred("open_junction")

func open_junction()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	current_scene=game
	while game.gameplay==null:await physics_frame
	game._view("r24_east_upper_joint")
	print("PLAY_HERE ",game.get_window().title," ",game.explorer.current_view)
