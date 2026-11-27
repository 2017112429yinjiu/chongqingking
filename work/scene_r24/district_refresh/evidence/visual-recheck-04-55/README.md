# 04 原轮迹与遮面、55 园门暗侧复查

Godot 4.6.3，普通 `first_shift.tscn`，在 `21e4dd384651eae7fbcbc55fb3e9f2bb7d61d6cb` 用已保存矩阵复射。横坐标 E、北 N、高程 Y 为游戏米。像素坐标基于已归档的 900×506 画幅。每条射线分别登记实体碰撞和原生可见网格，碰撞与背后物体分别列报。[机位](cameras.json) · [全部 31 像素与命中](rays.json)

## 04 车轮

原顺向停在 **E−145.111 / N−79.608**，距登记中线横向 1.085 米，距路缘 1.505 米。对向接触物是原挡边 `COL_Outer500_Retaining_and_boundaries`，按源网格指纹归属 53 号石梯的低挡边。2023-05-15 连续街景在此记录车行铺面，禁行牌和花带在江侧公开步道停止处。原轮迹没越过游戏路缘，保留原输入和路点。发布 `53ea5da9` 中原线 45.63 / 45.64 米、各 8/8，沿江偏线 45.68 / 45.69 米、各 8/8。53 石梯检查 129 点，最大差 4.857 毫米。 [逐点路面与照片](../../street_groups/nanqu_04_06_51/evidence/04-original-wheel-EN-audit.json) · [修前失败](../../street_groups/nanqu_04_06_51/evidence/old-inner-wheel-line-failure.json) · [两套通过轨迹](../../street_groups/nanqu_04_06_51/evidence/wheel-routes.json) · [53 复测](../../street_groups/nanqu_04_06_51/evidence/landing-53-profile.json)

## 04 禁牌及对向高边

游戏核对机位 E−160.000 / N−76.900 / Y9.030，方位 110.804°。禁牌右后先命中原外区地表 `COL_Outer500_Surface_01_03` 约 1.63–5.67 米。像素 445/234 命中 E−155.093 / N−78.698 / Y8.996，距眼 5.23 米，近直立；同射线上 20.85 米处为另一片地表 `Surface_02_03`，这两个距离不能相减当墙厚。左侧 174/171 首击新挡坡墙 `COL_Nanqu_HillsideRetaining`，而 317/198 首击更高的遗留 `COL_Outer500_Retaining_and_boundaries`。挡坡墙顶盖源截面横宽 0.18 米、盖厚 0.10 米，另有前方独立江栏碰撞，650/440 先命中 `COLH_Nanqu_RiverBarrier`。实际回望 E−156.950 / N−77.334 / Y9.381、方位291.334°，左侧 44/218 和 66/322 同样首先见原地表，173/178 是更高的旧外区楼地基。 [发布原生图](../../street_groups/nanqu_04_06_51/evidence/04-pedestrian-limit-after.png) · [挡墙源](../../street_groups/nanqu_04_06_51/build.py)

现场禁牌街景 `0902920012230515142928988AU` /188°，完整反投影得到 E−154.824 / N−76.029；下一可见封闭车段 `0902920012230515142930784AU` /110° 位于 E−139.811 / N−82.137。现场街眼和上面游戏眼位分别登记。2023-10 斜照与两站可确认道路、隔离带、栏与白罩的上下关系；街景 Z 无法定挡坡绝对高度，保留现有原地表和已验石梯。 [禁牌](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515142928988AU&heading=188&pitch=0&fovy=80&width=900&height=560) · [封闭车段](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515142930784AU&heading=110&pitch=0&fovy=80&width=900&height=560) · [竣工斜照](https://epaper.cqrb.cn/cqrb/2023-10/26/004/cqrb20231026004.pdf)

## 55 园门黑楔

街肩游戏机位 E−158.965 / N−159.070 / Y−2.100、104.001°，浅砂区回望 E−168.043 / N−173.993 / Y−5.153、71.785°。在进入画幅黑楔的相邻选点连续命中有材质、可碰撞的 `COL_WestPlayground_PerimeterSupport`，例如 E−153.58/N−161.79 至 E−153.32/N−167.47，随后命中背后地面或园地。上部路面单独命中外区地表及新的 `COL_Changbin55_PublicShoulder`。原暗边与承托侧面相符，本组选点未遇穿空。继续保留先前实走，街肩经园门至浅砂区 42.68 / 42.91 米，各 11/11。 [55 原生图与走测](../../riverside/roadside_55/evidence/README.md) · [连续承托源](../../riverside/west_ramp/playground_grade.py)

复射可从 Godot 项目运行 `--headless --fixed-fps 60 --script <绝对路径>/scene-rays.gd -- --day-one-test --qa-dir=<独立目录> --scene-ray-input=<绝对路径>/cameras.json`。
