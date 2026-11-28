# 东片近景材质

01 取件盘中七段姜使用 Oliver Harries 的 Food Ginger 01 扫描。保留原 UV，改变朝向与尺寸后计算各根最低点，使它们落在原托盘衬纸上。颜色、法线和粗糙度由工程既有三通道源生成，并扩展 UV 岛外沿以防近景采样混入黑底。果蔬表皮和叶脉独立生成，使用可复现的种子和逐件展开的 UV。 [Poly Haven CC0](https://polyhaven.com/a/food_ginger_01) · [仓库原件清单](../../../../assets_incoming/r24_noodle/ginger/PROVENANCE.json) · [原 UV 坐标核验](scan-uv-export.json)

22 竖向石板有五档矿物颜色，沿板实际尺寸布置 UV。法线和粗糙度由已有洗石材的颗粒图确定性生成。剪草、浅砾、紫灌与放射叶使用各自 UV。叶片用完整几何和双面着色，运行证据记录材质绑定和非退化 UV 三角数。

    python3 work/scene_r24/district_refresh/acceptance/east/material_maps.py
    blender -b work/scene_r24/district_500/outer_district.blend -P work/scene_r24/district_refresh/acceptance/build.py -- east /absolute/build/output
