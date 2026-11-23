梯坎里 · 重庆街区 05 — 离线重建源文件与素材

对应最终场景 revision：15
本包与主 Blender 包使用同一个 chongqing_blender_v05 根目录；可解压到同一个父目录合并。
只进行脚本重建时，当前目录已经包含生成器、依赖模块、字体、源平面数据、当前材质贴图与准备好的模型库；不需要重新下载原始资产。

重建
在本目录执行，将 blender 替换为本机 Blender 程序路径。
Linux / macOS：
CQ_REVISION=15 blender --background --python build_district.py

Windows 命令提示符：
set CQ_REVISION=15
blender --background --python build_district.py

默认结果写入 outputs，并按生成器设置写入 godot_project/assets。若设置 CQ_OUTPUT_DIR，则使用指定输出目录。
将 outputs 中新生成的 chongqing_district.glb、scene_manifest.json、viewpoints.json、landscape_report.json、terrain_interior_audit.json、context_ownership_audit.json，以及源目录的 architecture_manifest.json、materials/material_provenance.json 一并同步到单独的 Godot 工程 assets；继续使用该工程提供的 scripts、shaders、字体、HDRI 和 render_profile_v05.json。
重建后的结果需要重新运行和截图复核，旧验收清单不能直接用于新导出的文件。

打包内容
当前生成器本地导入闭包：
  architecture_full.py
  bake_vertex_ao.py
  build_district.py
  district_geometry.py
  district_layout.py
  drain_support.py
  interior_domains.py
  interior_scenes.py
  landscape_v05.py
  material_library.py
  props_library.py
  scanned_assets.py
  terrain_interiors.py
  tree_root_support.py
  urban_fabric.py

当前材质清单引用 73 个唯一源图文件，存放于 materials；原始来源和许可信息保存在 materials/material_provenance.json 及来源附档。
scanned_assets/prepared_assets.blend 是本轮使用的准备模型库，其清单包含 12 个资产键。对应来源、准备记录与所需贴图一起保留。
interior_scenes.py 与 landscape_v05.py 随当前导入闭包提供，分别生成室内生活场景和地表/种植关系。
drain_support.py 根据已建成的实际地面生成格栅支撑，并在 outputs/drain_grate_support_audit.json 写出本次生成记录；该记录属于源构建检查，导出的 GLB 仍需独立复核。
source_data 保存平面资料；fonts 保存生成器字体及许可证。

边界
本包不包含下载缓存、旧导出、.blend1、引擎缓存、旧诊断渲染配置或 GLB 提取出的重复图片。
主 .blend 单独提供。当前源代码、素材和验收身份可按随包清单核对；不同软件版本重新导出不保证输出文件字节完全相同。
资料范围与逐图视觉复核见 docs/review_zh.txt 和 verification 文件夹。
