extends RefCounted
## CPU skin the exported distal finger vertices with the imported Godot skin.
var points: Array[Dictionary]=[]
var bones: Array[int]=[]
var inverse_binds: Array[Transform3D]=[]

func setup(npc: Node3D) -> void:
	for mesh: MeshInstance3D in npc.find_children("*","MeshInstance3D",true,false):
		if mesh.find_blend_shape_by_name("Smile")<0:continue
		for i in mesh.skin.get_bind_count():
			bones.append(npc.skeleton.find_bone(mesh.skin.get_bind_name(i)))
			inverse_binds.append(mesh.skin.get_bind_pose(i))
		var arrays: Array=mesh.mesh.surface_get_arrays(0)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array=arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array=arrays[Mesh.ARRAY_WEIGHTS]
		var influences:=indices.size()/vertices.size()
		for i in vertices.size():
			var skin_ids: Array[int]=[]
			var amounts: Array[float]=[]
			var name: String=""
			for k in influences:
				var bind:=indices[i*influences+k]
				var amount:=weights[i*influences+k]
				if amount<.0001:continue
				skin_ids.append(bind)
				amounts.append(amount)
				var joint: String=npc.skeleton.get_bone_name(bones[bind])
				if amount>.48 and joint in ["middle_03_l","index_03_l","ring_03_l","pinky_03_l","thumb_03_l"]:
					name=joint
			if not name.is_empty():points.append({"position":vertices[i],"binds":skin_ids,"weights":amounts,"finger":name})
		return

func clearances(npc: Node3D,bag: Node3D) -> Dictionary:
	var skin_to_bag: Transform3D=bag.global_transform.affine_inverse()*npc.skeleton.global_transform
	var transforms: Array[Transform3D]=[]
	for i in bones.size():
		transforms.append(skin_to_bag*npc.skeleton.get_bone_global_pose(bones[i])*inverse_binds[i])
	var nearest: Dictionary={}
	var inside: Dictionary={}
	for v: Dictionary in points:
		var p:=Vector3.ZERO
		for j in v.binds.size():p+=(transforms[v.binds[j]]*v.position)*float(v.weights[j])
		# Actual two folded faces on the left-hand side of the R18 paper bag.
		if p.y<.055 or p.y>.255:continue
		var u:=clampf((p.y-.055)/(.22-.055),0,1)
		var lip:=clampf((p.y-.22)/(.255-.22),0,1)
		var half_x:=lerpf(.123,.116,u)+.003*lip
		var half_z:=lerpf(.079,.074,u)+.002*lip
		if absf(p.z)>half_z:continue
		var gap: float=p.x-half_x*(.85+.15*absf(p.z)/half_z)
		nearest[v.finger]=minf(float(nearest.get(v.finger,1.0)),absf(gap))
		inside[v.finger]=minf(float(inside.get(v.finger,1.0)),gap)
	return {"nearest_m":nearest,"signed_min_m":inside}
