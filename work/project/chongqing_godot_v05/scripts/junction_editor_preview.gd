@tool
extends Node

var preview:Dictionary={}
var district:Dictionary={}

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
		preview=preload("res://scripts/lane_connection_r24.gd").install(city,true,profile.get("east_alley_inlets_r24",false))
		print("CQ_EDITOR_JUNCTION ",preview.replaced," ",preview.added)
		if profile.get("district_connections_r24",false):
			district=preload("res://scripts/district_connections_r24.gd").install(city,true,preview)
			print("CQ_EDITOR_DISTRICT ",district.changed," ",district.drawings.size()," ",district.missing)

func _exit_tree()->void:
	if not Engine.is_editor_hint() or preview.is_empty():return
	for source in district.get("originals",[])+preview.originals:
		if is_instance_valid(source) and source.is_inside_tree():
			RenderingServer.instance_set_visible(source.get_instance(),source.is_visible_in_tree())
	for drawing in district.get("drawings",[])+preview.drawings:
		if is_instance_valid(drawing):drawing.queue_free()
	district.clear()
	preview.clear()
