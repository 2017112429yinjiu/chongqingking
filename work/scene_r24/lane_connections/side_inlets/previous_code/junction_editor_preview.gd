@tool
extends Node

var preview:Dictionary={}

func _ready()->void:
	if Engine.is_editor_hint():
		call_deferred("show_junction")

func show_junction()->void:
	if not is_inside_tree() or not preview.is_empty():
		return
	var profile=JSON.parse_string(FileAccess.get_file_as_string("res://assets/render_profile_r24.json"))
	if not profile is Dictionary or not profile.get("east_lane_joint_r24",false):
		return
	if not ResourceLoader.exists("res://assets/lane_connection_r24/editor/openings.glb"):
		return
	var city:=get_parent().get_node_or_null("City") as Node3D
	if city:
		preview=preload("res://scripts/lane_connection_r24.gd").install(city,true)
		print("CQ_EDITOR_JUNCTION ",preview.replaced," ",preview.added)

func _exit_tree()->void:
	if not Engine.is_editor_hint() or preview.is_empty():return
	for source in preview.originals:
		if is_instance_valid(source) and source.is_inside_tree():
			RenderingServer.instance_set_visible(source.get_instance(),source.is_visible_in_tree())
	for drawing in preview.drawings:
		if is_instance_valid(drawing):drawing.queue_free()
	preview.clear()
