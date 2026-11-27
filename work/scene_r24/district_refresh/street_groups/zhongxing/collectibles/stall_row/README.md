# 中兴路收藏品市场东侧摊位

店内同址照片可见连续靠墙柜列、绿釉面下墙、浅色上墙、隔网和卷帘，以及红底黄字分类招贴。本增量只处理入口望向东墙的一排店面和相邻展柜。沿用原货架与柜体，在这一区域重排 6 件现有旧电器，沿用原有设备模型另布置 14 件库存，保留原来其他区域的碰撞几何。墙砖、隔网、卷闸、招牌和价签为独立建模制作。招牌采用通用分类，价签金额是游戏陈设。实拍仅用于观察。 [同址采访照片](https://imagepphcloud.thepaper.cn/pph/image/87/183/882.jpg) · [采访文章](https://m.thepaper.cn/newsDetail_forward_9057120)

## 编辑和重建

`stall-row.blend` 可在 Blender 4.3.2 独立编辑，店招与价签保留文字对象和小型内嵌字库。原市场大源与其增量导出沿用已发布文件。本批单独输出 `market-stall-row.glb` 和店面装配清单，保持原 `first_shift.tscn` 接入方式。图层安装时只替换家具网格，并新加摊位饰面、隔网和牌字。

`build_font.py` 从 Noto Sans CJK SC Bold 裁取五块原创牌字所用字符，改名为 CQ Stall Labels。原 `NotoSansCJK-Bold.ttc` SHA‑256 为 `faa5f3656a78b2e2d450d27fe8382c778bc2b6bb5ea29c986664a6a435056ceb`，内嵌子集为 `6bd1f1f133f3f0053c9585fb1a7314893a73f34ccf8d640ccfaa21af769f7a05`。上游及项目保留 SIL OFL 1.1 许可。饰面沿用工程已许可的 Poly Haven 混凝土、灰泥、木和锈金属贴图。 [Noto CJK](https://github.com/notofonts/noto-cjk) · [字体许可](https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE)

在工程根目录执行下列命令。最后一个参数是前一步生成的字库文件。

```sh
python work/scene_r24/district_refresh/street_groups/zhongxing/collectibles/stall_row/build_font.py /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc /tmp/cq-stall-labels.otf
blender -b --python-exit-code 1 -P work/scene_r24/district_refresh/street_groups/zhongxing/collectibles/stall_row/build.py -- /tmp/cq-stall-labels.otf
```

## 走测与机位

使用上级目录 `walk.gd` 和 `--explore-500 --zhongxing-collectibles` 走主厅回原街边点，另加 `--qa-market-side` 走侧阶和返回。改前对照可用 `--qa-without-market-stall-row`。脚本用 10 个断面、每个 3 层碰撞射线对读净宽，保留原 doorway-stock-eye 固定机位。另取实际步行越过 E225.68 时的玩家眼位，从该位置转向东墙店面拍摄。原生截图和逐断面、逐方向数据见 [evidence](evidence)。
