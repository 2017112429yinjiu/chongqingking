extends SceneTree

func _initialize() -> void:
	call_deferred("inspect")

func inspect() -> void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var obj:=game.get_node("City").find_child("COL_R23_NanquUpperApron",true,false) as MeshInstance3D
	var faces:=obj.mesh.get_faces()
	var points: Array=[]
	for v in faces:
		var p:=obj.to_global(v)
		points.append([p.x,-p.z,p.y])
	var record={"triangles_blender":points,"name":str(obj.name),"profile":game.art_profile.art_revision}
	FileAccess.open(OS.get_cmdline_user_args()[-1]+"/original_apron.json",FileAccess.WRITE).store_string(JSON.stringify(record))
	print("MARKET16_ORIGINAL ",faces.size()/3)
	quit()
