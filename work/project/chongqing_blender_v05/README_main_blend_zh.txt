梯坎里 · 重庆街区 05 — Blender 主文件

本包包含可编辑的 chongqing_district.blend，以及对应最终 revision 15 的身份与复核记录。
Blender 中的建模预览环境和 Godot 的最终运行环境分别保存；最终照片与灯光记录以 Godot 验收文件为准。

打开与编辑
在 Blender 中打开 chongqing_district.blend。保留原文件，手工编辑时另存副本。
完整生成脚本、当前源贴图、扫描资产库、字体和许可证另见 chongqing_street_blender_rebuild_v05.zip。
需要离线重建时，把主文件包和重建包解压到同一个父目录，合并 chongqing_blender_v05 文件夹，再阅读 README_rebuild_zh.txt。

身份核对
对应 Godot GLB SHA256：06c280f56fb58152688aaf058cd87f7a3f71819478bea0ad7ab2869ce5bd5223
核心范围：200 × 200 米
最终机位：22 个，最终照片尺寸为 1920×1080。
主 .blend 文件的实际字节数与 SHA256 记录在 docs/delivery_metadata.json。
脚本生成的场景与任意后续手工改动是两条编辑路径；生成器不会自动吸收手工改动。

复核依据
docs/review_zh.txt 汇总实际清单并附三份逐图视觉复核原文。
本打包流程只校验文件身份和已有证据，不代替 Blender 或 Godot 的建模、视觉及运行复核。
