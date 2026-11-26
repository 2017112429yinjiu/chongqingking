# 金马寺小学二楼 · 阅览室装帧

从 [山城巷送单入口](../../../沿山城巷送一单.cmd) 取餐，走到仁爱堂收件架签收，再上金马寺小学二楼。下图左右分别取自两次实走录像的最后一帧，人物和书架的相对位置对应玩家报出的画面。[本次连续实走](evidence/delivery_to_shelf.mp4)

![沿送单线走到同一排书架的前后对照](evidence/before_after.jpg)

## 改到了哪些书

旧生成器用一个长方体做整本立书，轮换使用墙面、瓦面等建筑材质。桌上的平放书用两片板拼成。先前的走通检查只验证了人能上楼，远景截图也没有查到这个问题。

三排书架现有 3,161 本立书，三张展桌共有 18 本闭合书和 1 本摊开的书。每本闭合书的封面、封底和四段弯书脊取印刷图集上的不同区域；纸芯略缩进封板，露出的书顶、书底、前书口带有页层。薄册和精装的封板厚度、书脊弧度各异。摊开的书有书沟、拱起的纸页和跨页正文。书架靠近房间两侧，书脊相向朝着读者。[书脊近看](evidence/spines.jpg) · [对面书架](evidence/opposing_case.jpg) · [另一排书架](evidence/far_case.jpg) · [展示桌](evidence/display.jpg) · [书口近看](evidence/page_edges.jpg)

同址实拍用于核对共享书架上混排的厚薄与颜色、桌面叠书的方式，以及旧书纸边的色差。游戏内的 64 种封套、书名、插画和跨页内文均为项目原创设计。第一次上架后，索书签的位置、纸色和邻书的排列显得过于整齐。复看实景后调整了书标比例、装帧色块和纸边色调，并拉开同一格里相同书名的间距。[馆内实拍与采访](https://app.cqrb.cn/html/2022-07-21/1253645_pc.html) · [第一版近景](evidence/first_pass.jpg) · [纹理、字形和参考图来源](sources.json)

## 复验

Blender 4.3.2 重开独立馆舍与整城组合，逐排核对打包图像、封面与书脊的 UV 范围、弧面以及三个外露书口。Godot 4.6.3 从默认 `first_shift.tscn` 检查实际导入的四个书本模型，并从玩家视角观察三排书架、桌面和纸口。正常取餐、一次签收和连续上楼走到架前均已执行。[Blender 源检查](evidence/blender.json) · [Godot 实际表面和贴图](evidence/godot_materials.json) · [玩家实走数据](evidence/walk.json) · [原生回归与实测帧时间](evidence/regression.json)

在 RTX 4070 Laptop 上以 Forward+ 单独采样，窗口为 1152 × 648，实际渲染视口为 692 × 389。走道、书脊近景和展桌各取 150 帧，GPU 帧时间 P95 分别为 6.50、6.77、7.35 毫秒。

沿用上一级 `verify.py --output <新目录> --capture`，传入本机的 `--godot` 和 `--blender` 可重新执行。每次在编辑器内改过材质后，复开并验证实际导出的 GLB。继续编辑时打开 `../delivery_courts.blend`。印刷图由 `print_atlas.py` 使用项目已有的 Noto 字体、布纹扫描、Pillow 和 NumPy 生成。运行 `../architecture.py` 时用 `../../district_500/outer_district.blend` 作为地形输入；它会同时更新馆舍 Blender 源和 Godot 使用的 `historic_courts.glb`。
