extends SceneTree
func _initialize()->void:call_deferred("show_shop")
func show_shop()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	current_scene=game
	while game.gameplay==null:await physics_frame
	game._view("r24_join18_shop")
	print("PLAY_HERE ",game.get_window().title," ",game.explorer.current_view)
