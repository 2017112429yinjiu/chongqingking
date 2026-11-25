"""Run with Blender's --python-exit-code. Preserve the Git-controlled master."""
import json
import os
import sys
from pathlib import Path

import bpy

root = Path(os.environ.get("CQ_PROJECT_ROOT", Path(__file__).resolve().parents[2])).resolve()
source = root / "work/scene_r24/district_patrol/city_and_patrol.blend"
game = root / "work/project/chongqing_godot_v05"
run = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
portable = run / "city_and_patrol.blend"
if bpy.app.version != (4, 3, 2) or Path(bpy.data.filepath).resolve() != source:
    raise RuntimeError("Expected the build 25b master opened with Blender 4.3.2")
if portable.exists():
    raise FileExistsError(portable)


def target_for(stored):
    # Windows absolute paths survive even when the .blend is opened on Linux.
    normalized = stored.replace("\\", "/")
    if normalized.startswith("//"):
        target = (source.parent / normalized[2:]).resolve()
    else:
        prefix, separator, suffix = normalized.rpartition("/work/")
        if not separator:
            raise ValueError(f"Cannot map external path {stored!r}")
        target = (root / "work" / suffix).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise FileNotFoundError(target)
    return target


def external_images():
    return [im for im in bpy.data.images
            if im.source == "FILE" and im.filepath and not im.packed_file]


for lib in bpy.data.libraries:
    lib.filepath = bpy.path.relpath(str(target_for(lib.filepath)), start=str(source.parent))
for im in external_images():
    if not im.library:
        im.filepath = bpy.path.relpath(str(target_for(im.filepath)), start=str(source.parent))

bpy.ops.wm.save_as_mainfile(filepath=str(portable), relative_remap=True)
bpy.ops.wm.open_mainfile(filepath=str(portable), load_ui=False)


def checked_path(datablock):
    if not datablock.filepath.startswith("//"):
        raise ValueError(f"External path must be relative: {datablock.name}")
    path = Path(bpy.path.abspath(datablock.filepath, library=datablock.library)).resolve()
    if not path.is_file() or not path.is_relative_to(root):
        raise FileNotFoundError(path)
    return path.relative_to(root).as_posix()


libraries = {}
for lib in bpy.data.libraries:
    path = checked_path(lib)
    if not lib.users_id or any(item.is_missing for item in lib.users_id):
        raise ValueError(f"Unresolved linked data: {path}")
    libraries[path] = len(lib.users_id)

images = []
for im in external_images():
    images.append(checked_path(im))
    im.reload()
    if min(im.size) == 0:
        raise ValueError(f"Image could not be decoded: {im.name}")

layout = json.loads((game / "assets/district_patrol/layout.json").read_text(encoding="utf-8"))
objects = bpy.context.scene.objects
for name in layout["new"] + layout["changed"]:
    if not objects[name].data.polygons:
        raise ValueError(f"District geometry is empty: {name}")
for name in layout["retired"]:
    if not objects[name].hide_render:
        raise ValueError(f"Retired geometry is visible: {name}")

expected = json.loads((root / "docs/version-control/blender-source-check.json").read_text(encoding="utf-8"))
for ref in expected["reference_paths"]:
    if ref["repository_path"] not in (libraries if ref["kind"] == "library" else images):
        raise ValueError(f"Expected reference missing after reopen: {ref['repository_path']}")

report = {
    "blender": bpy.app.version_string, "scene": bpy.context.scene.name,
    "objects": len(objects), "libraries": libraries, "external_images": sorted(images),
    "packed_images": sum(bool(im.packed_file) for im in bpy.data.images),
    "district_objects_checked": {key: len(layout[key]) for key in ("changed", "new", "retired")},
}
(run / "blender.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("Portable district reopened", len(objects), "objects,", len(libraries), "linked libraries")
