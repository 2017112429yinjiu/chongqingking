# 10 号候车棚与门窗可读性复验

父版 `e16d51a878289ab160179e9dd7f3b56eeb7c03dd`。2023-05-15 的 90° 与 72° 可见连续浅遮檐、立柱、两只装纸的玻璃框及棚上浅底绿字「中兴路站」。2021-07-29 正面可见同处棚、上层长窗的横竖分格、檐底灯点及内退门面。站名按原字重绘。候车提示、公交图形、山坡线画和公益文字为本项目自绘，保留框内分层、内容密度和色块大小。同期线路与具体商业广告未获清晰来源。[已登记街眼与指纹](../../registration.json) · [2023年72°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515131746831AU&heading=72&pitch=0&fovy=68&width=800&height=500) · [2023年90°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515131746831AU&heading=90&pitch=0&fovy=68&width=800&height=500) · [2021年89°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=09029200122107291709181571C&heading=89&pitch=0&fovy=76&width=800&height=500)

浅棚补檐口、短肋、灯、落地柱脚、玻璃反光和框件。两张纸面各用独立 UV 全幅展开，前方各有独立低透明玻璃。上窗横竖框、压条与冷色窗面分开；底层区分砖墩、窗台、窗格、内退门、门框、拉手与局部檐灯。对局部暗部门口用贴图的弱反射填充，遮蔽处保留阴影。原双柱帽、灰铺、路缘和白蓝栏的位置及原步线不变。PNG 由 `draw_stop.py` 自绘，文字使用 SIL OFL 1.1 的 Noto Sans CJK，只分发渲染后的图。[字体许可](https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE) · [字牌与两幅内页再现](../../draw_stop.py)

Godot 4.6.3，700 × 440 原生 PNG，Mesa llvmpipe Compatibility。八组的视图、投影、窗口和日照设置一致。北侧90°实看可读站名，窗口框和上部玻璃分格在街侧可辨。近景看玻璃背纸、柱脚、暗檐及门框退进。前一阶段五张原图继续原目录保存。[八组相机矩阵与指纹](fixed-views.json) · [Blender 4.3.2 复开](verified-source.json) · [Godot 导入](after/import.log)

| 机位 | 父版 | 本次 |
|---|---|---|
| 北侧90° | [原图](before/north-90.png) | [原图](after/north-90.png) |
| 北侧72° | [原图](before/north-72-field.png) | [原图](after/north-72-field.png) |
| 2021 年89° | [原图](before/history-89.png) | [原图](after/history-89.png) |
| 南侧42° | [原图](before/south-42.png) | [原图](after/south-42.png) |
| 街缘入廊 | [原图](before/walk-approach.png) | [原图](after/walk-approach.png) |
| 檐下回望 | [原图](before/under-arcade-return.png) | [原图](after/under-arcade-return.png) |
| 候车棚近看 | [原图](before/shelter-detail.png) | [原图](after/shelter-detail.png) |
| 门槛近看 | [原图](before/threshold-detail.png) | [原图](after/threshold-detail.png) |

原步线在正常首班场景中，从街到廊下 25.867 米、回到同一街点 25.907 米，两向各 8/8，铺面 9/9，无卡停。门后室内和店号仍没有充分资料。[实际逐向原数据](after/walk.json)

玩家镜头实测也完成原去回路，记录 [街缘](player/street-at-the-new-curb.png)、[檐下回望](player/under-the-eaves-look-back.png) 和 [返街](player/returned-to-the-street.png) 原生图。[玩家逐向数据](player/round-trip.json)

邻接实走均通过。11 号凤凰台坡口各 4/4，收藏市场主厅各 7/7，26 号街肩各 5/5。[凤凰台](after/fenghuangtai11.json) · [收藏市场](after/market.json) · [26 号](after/public-26.json)
