# 资源与工具许可核查（2026-11-20）

## 2026-11-23 · 带教动作与保温箱

箱体、内胆、铰链、拉片、纸袋提手、纸材质和敲门声为本项目制作。箱体复用项目原电瓶车的橡胶护角。骑手使用已有的 Microsoft Rocketbox Male Adult 10，步态复用项目里同一套骨架的已有剪辑。保留 Microsoft 版权声明和 MIT 许可全文。指节握持、敲门、关节约束和上门动作由本项目在运行时生成。[骑手来源](../assets/characters/rider_r18_provenance.json) · [步态来源](../assets/block_r23/motion_sources.json) · [许可原文](../assets/characters/ROCKETBOX_MIT_LICENSE.txt)

## 第一天的教学文字与骑手

新字体 `assets/fonts/first_shift.otf` 从项目已有的 Noto Sans CJK SC Regular 重新取字并改名，采用 SIL OFL 1.1。同目录 `first_shift_sources.json` 记录上游提交、版权、变更与文件哈希，`R20_OFL.txt` 随附许可。老彭复用已有的骑手和电瓶车资产，黄盔为该角色在运行时的独立材质颜色。

## 球场晾衣的毛圈布 · R24 构建 10

Terry Cloth 由 colormass 拍摄、Rico Cilliers 处理。Poly Haven 以 CC0 1.0 发布，允许商业使用，署名为自愿。项目保留作者信用。原色、遮蔽和 OpenGL 法线三张 1K 输入逐一核对发布方的 MD5，留存 SHA-256。重新组合成一张线性贴图，红绿通道保存切线法线，蓝通道保存去色后的绒圈明暗，颜色与下摆织边在游戏中生成。原件和清单位于 work/scene_r24/cloth_review/originals，运行时清单位于 assets/frontage_r24/terry_sources.json。[素材原页](https://polyhaven.com/a/terry_cloth) · [许可](https://polyhaven.com/license)


## R24 构建 09 · 路口

街名牌、种植带草叶、排水格栅、局部轮胎接触图由本项目制作。街名取自已有 OSM 道路记录，字形继续用项目记录的 Noto Sans CJK；招牌外观为本场景创作。沿用 Poly Haven 的 Brown Mud Leaves 01、Leaf Scattered Gravel、Mossy Stone Wall、Concrete Floor Worn 001 和 Asphalt 02，均为 CC0。原作者、网址、既有原图 SHA-256、字体与 ODbL 派生车道数据在 `assets/frontage_r24/road_sources.json`。游戏内 OSM 署名和各项许可正文沿用项目现有位置。

## R24 南区路与东侧楼群

- 东侧建筑底图来自 OpenStreetMap contributors，使用 ODbL 1.0。游戏现有署名持续显示，派生平面、来源 URL、原始 SHA-256 和许可链接随工程保存在 `source_data/east_r24`。历史高架使用原有 OSM way 59146775。门窗、屋顶、补画阳台和无标签楼高属于场景设计。[地图许可](https://www.openstreetmap.org/copyright)
- 菜摊居民沿用 R23 已有模型与贴图，新增 Microsoft Rocketbox 的两个动作。原始文件链接、作者、Git blob、SHA-256 与改动保存在 `assets/frontage_r24/provenance.json`。再分发时随附 Microsoft 版权和 MIT 许可全文，见同目录 Rocketbox_LICENSE.txt。[固定提交许可](https://github.com/microsoft/Microsoft-Rocketbox/blob/0943055db6ec570bcef9f2c8b41c9e5467c808f9/LICENSE.md)
- 价牌和招牌用 Noto Sans CJK 原授权字体排字，项目保留 fonts/LICENSE_Noto_CJK.txt。木桌和踏面复用 Poly Haven 的 wood_table_worn 和 concrete_floor_worn_001，两项作者均为 Dimitrios Savva 与 Rico Cilliers。高架路面复用 Rob Tuytel 的 asphalt_02。三种表面均为 CC0，详见 MATERIAL_CREDITS_zh.txt。蔬菜、工具、雨篷、远景窗图与高架截面均由本项目制作。

## R23 内部试做

行人模型与两段步态来自 Microsoft Rocketbox 固定提交 0943055db6ec570bcef9f2c8b41c9e5467c808f9。MIT 允许商用，随附版权及完整许可正文。按原文件记录的网址、SHA-256 和改动在 assets/block_r23/PROVENANCE.json 及 Rocketbox_LICENSE.txt。车辆、家具、毛巾、街坎和补修几何为项目自制。路面和砖墙沿用既有 Poly Haven 资源及原署名；道路沿用项目 OSM 数据和原有 ODbL 署名。[Microsoft Rocketbox 固定版本许可](https://github.com/microsoft/Microsoft-Rocketbox/blob/0943055db6ec570bcef9f2c8b41c9e5467c808f9/LICENSE.md)

2026-11-21 的江岸、双桥轴线和建筑轮廓来自 OpenStreetMap。原始三个 XML 的 URL 与 SHA-256 在 work/assets_incoming/r22_city/PROVENANCE.json，裁剪和投影后的数据库以 ODbL 1.0 保存在 source_data/river_r22。游戏内显示贡献者、许可及版权网址。商用发行需保留署名，并随产品提供本次使用的衍生数据库或合规的公开获取方式。桥墩、立面、高程及车辆运动为项目美术。屋面复用 Poly Haven 的 Concrete Floor Worn 001 与 Asphalt 02，均为 CC0。作者、原始散列见 assets/roofs_r22/provenance.json。河岸树冠和泥砾复用已登记的扫描素材。[OpenStreetMap 版权与许可](https://www.openstreetmap.org/copyright) · [Poly Haven 许可](https://polyhaven.com/license)

R21 本次下载的三组 Poly Haven 资产采用 CC0 1.0，可商用、修改、随游戏分发，署名自愿。Mossy Stone Wall 由 Amal Kumar 制作，Sandstone Cracks 由 Rob Tuytel 制作，Kloofendal 28d Misty (Pure Sky) 由 Jenelle van Heerden 摄影、Greg Zaal 处理。树木复用原工程 CC0 扫描。每项的作者、原链接、下载 URL、上游 MD5、本地 SHA-256 和处理过程见 assets/district_r21/provenance.json。外围用地派生自原工程 OpenStreetMap 数据，保留 © OpenStreetMap contributors 与 ODbL 1.0 声明。观察用重庆照片未复制进游戏。[Poly Haven 许可](https://polyhaven.com/license) · [OpenStreetMap 版权](https://www.openstreetmap.org/copyright)。

上巷与树池的木纹、水泥、石材、土及灌木复用 Poly Haven CC0 资源。四张告示及运行字库使用 Noto CJK，衍生字库已更名并附 SIL OFL 1.1 全文。明细在 assets/lane_r20/PROVENANCE.json。第三步道照片只用作环境参考。

树池居民采用 Microsoft Rocketbox 的 Female_Adult_14 及同仓库的两段坐姿动作，固定版本为 0943055db6ec570bcef9f2c8b41c9e5467c808f9。该版本的 MIT 许可允许商用，分发时须附版权及许可声明。模型目录内的 PROVENANCE.json 记录每个下载文件及修改，LICENSE.txt 保留完整声明。[模型仓库与固定版本许可](https://github.com/microsoft/Microsoft-Rocketbox/blob/0943055db6ec570bcef9f2c8b41c9e5467c808f9/LICENSE.md)
这不是新素材集；R16a 没有下载或集成新的第三方美术资产。保留 R15 material_provenance.json、scanned_assets/source_credits.json、字体许可证与 OSM 来源。

| 来源 | 核查结果 | 署名/再分发 | 本次使用 |
|---|---|---|---|
| Poly Haven https://polyhaven.com/license | 资产 CC0，可用于商业作品 | 不强制署名，仍保留来源；可再分发原资产 | 已恢复 R15 既有扫描植物/家具/材质 |
| ambientCG https://docs.ambientcg.com/license/ | CC0，商业可用 | 不强制署名，允许原资产再分发 | 候选旧墙面/地面，未下载 |
| Kenney Food Kit https://kenney.nl/assets/food-kit 与 https://kenney.nl/support | 页面标示 CC0 | 不强制署名 | 候选取餐食物，未下载 |
| Quaternius https://quaternius.com/license.html | 当前 QAL v1.0，页面与部分旧包 CC0 标示冲突 | 可商用但限制原资产再分发；不能直接把它塞进可编辑工程包 | 暂不采用，需逐包许可核实 |
| Godot https://docs.godotengine.org/en/stable/about/complying_with_licenses.html | MIT | 发布引擎运行文件须保留 MIT 与适用第三方通知 | 使用官方 4.6.3 工具，交付工程不附引擎二进制 |
| Blender https://www.blender.org/support/faq/ | 软件 GPL，作品不因此自动 GPL | 如再分发 Blender 程序需履行其义务 | 使用官方 4.3.2 工具，交付工程不附程序 |
| OpenStreetMap https://www.openstreetmap.org/copyright | ODbL 1.0 | 署名 OpenStreetMap contributors、提供许可链接；派生数据库的共享义务需保留 | R15 既有 XY 布局，source_data 完整保留 |

禁止依据网站标题就把整站所有内容归为 CC0。每个新下载包需保留原许可、作者、具体 URL、版本、日期、原始哈希、改动和交付范围。照片只作参考时不得擅自作为贴图封包。

## R17 人物资产

已实际下载 MPFB 2.0.18 源码 ZIP 与 makehuman_system_assets_cc0.zip，校验 ZIP CRC，原包与 SHA256 在 work/assets_incoming/mpfb/PROVENANCE.json。官方来源 https://github.com/makehumancommunity/mpfb2 与 https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html 。

工具程序为 GPL-3.0-or-later，仅用于构建，未置入游戏。核心模型、目标、骨骼和配套包为 CC0-1.0；官方 https://static.makehumancommunity.org/mpfb/faq/can_i_sell_models.html 允许商用。实际使用的 middleage_asian_male、low-poly eyes、eyebrow001、eyelashes01、short02、male_casualsuit01、shoes02 文件头均单独含 CC0 声明。完整使用项与文件哈希、原声明在 assets/characters/shopkeeper_r17_provenance.json，CC0 法律文本已随资源保存。

CC0 无强制署名要求，仍自愿保留 MakeHuman team / Data Collection AB / Joel Palmius / Jonas Hauquier 来源说明。原创围裙、关键帧动作和取餐纸袋另行标注。不能将此结论扩展到未审查的社区人物资产。

## R18 人物及动作（开发中）

- 当前人物改用 old_asian_male、eyebrow012、short04，逐项 CC0 文件头与 SHA256 在 assets/characters/shopkeeper_r18_provenance.json；mhclo 引用的 mhmat 也解析路径并独立检查。服装、鞋及其余核心素材同样逐项核查。eyebrow004/008 与 short01 为历史外观试验，额外睫毛片已从当前角色移除。
- Poly Haven Cotton Jersey，https://polyhaven.com/a/cotton_jersey ，作者 colormass / Rico Cilliers，CC0；1K 色彩、粗糙、法线三图实际下载并核对官方 MD5。保留原始信息及 SHA256 于 work/assets_incoming/cotton_jersey。围裙裁片、磨损顶点色、褶皱和次级骨骼为项目原创。
- 100STYLE，Ian Mason，https://www.ianxmason.com/100style/ ，作者明确以 CC BY 4.0 发布，许可 https://creativecommons.org/licenses/by/4.0/ 。**必须署名 The 100STYLE Dataset - Ian Mason**，保留许可链接、注明改编，无作者背书。仅下载 Neutral_ID、Neutral_FW 和作者 Frame_Cuts.csv，原始哈希在 work/assets_incoming/100style/PROVENANCE.json。
- 当前仅将 Neutral_ID 的 700–1300 帧用于 10 秒店主待机：骨盆、胸、头、腕的实录相对变化重定向、幅度约束、30Hz 重采样、末尾一秒循环混合；脚部固定 IK。serve/greet 仍为原创演出。Neutral_FW 仅保存研究，尚未用于运行时行走。运行时含署名和改编说明于 assets/characters/100STYLE_CC_BY_4.0_NOTICE.txt 与 assets/CREDITS.txt。
- 100STYLE 不要求项目整体采用相同许可证；其改编动作仍必须履行署名义务，不能把整个 GLB 笼统宣称为 CC0。
- Bandai Namco 的动作数据集 1/2 为 CC BY-NC 4.0，不用于商业游戏；仓库脚本 MIT 不改变数据的非商业限制，未下载数据。CMU 官网允许商业作品使用但禁止单独倒卖动作数据，仅查阅条款，未下载或集成动作。

取餐台木层板复用既有 Poly Haven wood_table_worn CC0（Dimitrios Savva / Rico Cilliers）；文字使用随项目保留完整 OFL 的 Noto CJK 字体。人体微法线为本项目在 Blender 实际烘焙的程序纹理，不是扫描皮肤。

## R18 骑手候选

Microsoft Rocketbox 官方仓库 https://github.com/microsoft/Microsoft-Rocketbox ，当前核验提交 `0943055db6ec570bcef9f2c8b41c9e5467c808f9`，根目录 LICENSE.md 为 MIT。实际只取 Male_Adult_10 facial FBX、对应贴图及预览；9文件82,026,924字节，逐一核对 Git blob SHA1、字节数与本地 SHA256。目录树、原文件、许可、README、来源清单保留在 work/assets_incoming/rocketbox_research。该结论不推广至其他站点或另行发布的动作库。

允许商业作品使用、修改及在保留许可条件下再分发。必须保留 Copyright (c) 2020 Microsoft 与完整 MIT 许可正文，已置入 assets/characters/ROCKETBOX_MIT_LICENSE.txt；assets/CREDITS.txt 记录来源和改动。游戏内年轻骑手使用其人体/服装贴图、骨骼与选定表情；身高单位、材质转换、骑姿接触动画、头盔与带子为本项目改编/原创。没有下载或使用 Rocketbox 动作库。店主仍为前述 MakeHuman/MPFB 资产，不能混淆两者的授权和美术状态。

## R24 面馆备料区

Oliver Harries 的 Food Ginger 01 来自 Poly Haven，许可 CC0 1.0，允许商用、修改与随游戏再分发，署名自愿。本项目保留作者署名。保留原 UV，等比调整至 16.9 厘米宽并放置到备料台上。原 glTF、BIN、三张 1K 贴图及每个文件的 SHA-256 在工作区 `work/assets_incoming/r24_noodle/ginger/PROVENANCE.json`。重庆实拍店面仅供视觉对照。[模型原页](https://polyhaven.com/a/food_ginger_01) · [授权说明](https://polyhaven.com/license)

店堂地砖使用 Charlotte Baglioni 的 Interior Tiles，门槛用 Amal Kumar 的 Old Mosaic Floor。两套均为 Poly Haven CC0，可商用，署名自愿。保留 2K 原色、粗糙度和 OpenGL 法线，原图与每文件 SHA-256 在 `work/assets_incoming/r24_noodle` 对应子目录。纸条由项目排版，使用已有 OFL 的 Noto Sans CJK SC。[室内砖](https://polyhaven.com/a/interior_tiles) · [水磨石](https://polyhaven.com/a/old_mosaic_floor)
