extends "../../scene_r24/outer_neighborhood/survey.gd"

const FRAME_LAYER := 1 << 15

func wall_point(p: Dictionary, side: int, along: float, outward: float, height: float) -> Vector3:
	match side:
		0: return world(p,along,-p.depth*.5-outward,height)
		1: return world(p,along,p.depth*.5+outward,height)
		2: return world(p,p.width*.5+outward,along,height)
		_: return world(p,-p.width*.5-outward,along,height)

func hit_shell(p: Dictionary, side: int, along: float, height: float) -> bool:
	var a:=wall_point(p,side,along,.21,height)
	var b:=wall_point(p,side,along,-.23,height)
	var ray:=PhysicsRayQueryParameters3D.create(a,b,FRAME_LAYER)
	ray.hit_back_faces=true
	return not scene.get_world_3d().direct_space_state.intersect_ray(ray).is_empty()

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(12)
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var rows:=[]
	var errors:=[]
	var total:=0
	var sill_and_head:=0
	var street_total:=0
	var street_edges:=0
	var facade: StaticBody3D=scene.find_child("COL_Outer500_Building_envelopes",true,false).get_node("CQ_StaticCollision")
	for p: Dictionary in layout.plots:
		var mesh:=scene.find_child("COL_Outer500_Frame_%02d"%int(p.plot_id),true,false)
		var body: StaticBody3D=mesh.get_node("CQ_StaticCollision")
		body.collision_layer |= FRAME_LAYER
		var windows:=0
		for level in range(1,int(p.floors)):
			for side in 4:
				var axes: Array=p.frame.u if side<2 else p.frame.v
				for j in range(axes.size()-1):
					var mid: float=(axes[j]+axes[j+1])*.5
					var base: float=level*p.frame.storey
					if hit_shell(p,side,mid,base+1.46):continue
					windows+=1
					if hit_shell(p,side,mid,base+.09) and hit_shell(p,side,mid,base+2.30):
						sill_and_head+=1
					else: errors.append([p.plot_id,level,side,j,"missing sill or lintel"])
		body.collision_layer &= ~FRAME_LAYER
		facade.collision_layer |= FRAME_LAYER
		for window: Dictionary in p.street_windows:
			var mid: float=(window.left+window.right)*.5
			var above_sill: float=window.sill+.17
			street_total+=1
			if not hit_shell(p,0,mid,above_sill) and hit_shell(p,0,mid,window.sill-.065) and hit_shell(p,0,mid,window.head+.065):
				street_edges+=1
			else: errors.append([p.plot_id,mid,"street-level opening"])
		facade.collision_layer &= ~FRAME_LAYER
		if windows!=int(p.facade_work.windows):
			errors.append([p.plot_id,windows,p.facade_work.windows])
		rows.append({"plot":p.plot_id,"openings":windows})
		total+=windows
	var info={"engine":Engine.get_version_info().string,"plots":rows,"openings":total,
		"street_windows":street_total,"street_sills_and_lintels":street_edges,"paired_sills_and_lintels":sill_and_head,"failures":errors}
	FileAccess.open(output.path_join("openings.json"),FileAccess.WRITE).store_string(JSON.stringify(info,"  "))
	quit(0 if errors.is_empty() and total>0 else 2)
