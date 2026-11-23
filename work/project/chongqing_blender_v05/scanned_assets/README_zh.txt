梯坎里 · 重庆街区 05 — 当前扫描资产库

对应街区 revision：15
prepared_assets.blend 是 scanned_assets.py 读取的准备模型库。实例化时复用模板 mesh 与材质，街区摆放、比例和所用 LOD 由当前源代码决定。
当前 manifest.json 共有 12 个资产键：
  chinese_armchair
  chinese_tea_table
  covered_car
  island_tree_01
  metal_trash_can_clean
  metal_trash_can_rust
  plastic_crate_01
  plastic_monobloc_chair_01
  potted_plant_02
  shrub_01
  trashbag
  tree_small_02

来源与使用范围
来源和许可见 source_credits.json 及 manifest.json 中的各资产网页记录。
这些通用模型用于街区植被、杂物、家具和盆栽，不代表对重庆现场对应对象进行扫描。
textures 保存随当前库提供的源贴图。普通街区重建使用本库与当前生成器，不需要下载缓存。
branch_uv_repair.json 和 furniture_preparation_v05.json（如有）属于相应资产的准备记录；完整街区的最终运行与画面复核见交付 verification 文件夹。

身份
当前库文件 SHA256 保存在重建包 docs/source_inputs.json。
旧库 validation.json 的 passed 字段及旧哈希未作为当前库验收证明收录。
