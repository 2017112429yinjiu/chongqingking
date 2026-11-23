import bpy
bpy.ops.file.pack_all()
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]
assert not missing,missing
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
print('R16_PACKED',sum(bool(i.packed_file) for i in bpy.data.images),flush=True)
