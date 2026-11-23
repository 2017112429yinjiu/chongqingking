extends SceneTree
func _initialize():call_deferred("run")
func run():
	var scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await preload("res://scripts/qa_performance.gd").run(scene)
