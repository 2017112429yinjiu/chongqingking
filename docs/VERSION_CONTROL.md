# GitHub 版本控制

2026-11-24 起，本工作区在 `https://github.com/2017112429yinjiu/chongqingking` 使用 Git + Git LFS。远端为私有仓库，默认分支 `main`。首次导入接续原来的 Initial commit，保留远端历史。

## 纳入范围

- R24 构建 24 Godot 主工程，包括 `first_shift.tscn`、脚本、着色器、所有运行资源、`.import` 导入配置与 `.uid` 标识。
- 当前完整 Blender 场景 `work/scene_r24/vertical_run/city_and_crossing.blend`，各独立模型和人物制作源、生成与验证脚本。
- 各轮原生验证记录、原图、录像、失败尝试、素材来源、许可证与交接文档。
- 编辑器还会读取 `work/scene_r24/city_frame_11864101/city_frame.glb`，此文件也纳入版本管理。

`.gitattributes` 通过 Git LFS 管理模型、图像、视频和其他二进制资产。常规 Git 保存可读源码及配置。不要把 LFS 指针当作已经下载的模型：首次克隆须执行 `git lfs pull`。

## 保留在本机的档案

原文件不删除、不挪动。`.gitignore` 排除工具安装目录、`.godot` 和 Python 缓存、Blender 自动备份、历史检查点副本、重复 playtest 工程、R15 原始交付包、第三方 MAX 原包及提取数据，以及当前完整场景之前的整城 Blender 快照。独立制作层仍保留。

这不是整个 57.6 GiB 工作目录的逐字节云备份。首次迁移时排除的非缓存档案，以相对路径、大小及 SHA-256 记录在 [本地档案清单](version-control/local-archives.json)。这些 SHA-256 是迁移清单，不能替换或改写历史验证中的基线哈希。历史脚本若依赖清单中的旧版整城源，需要从原本机档案恢复；当前游戏运行和当前完整场景编辑不依赖这些旧版快照。

GitHub Free / Pro 当前含 10 GiB LFS 存储，后续修改大型二进制会增加完整的新版本占用，具体以账户额度为准：[GitHub 官方 LFS 说明](https://docs.github.com/en/billing/concepts/product-billing/git-lfs)。不自动开通付费额度，不变更仓库可见性。

## 日常开发

### Blender 外部库路径

已用 Blender 4.3.2 只读重开当前完整源，242 张图片已打包，16 个外部引用均可在本机找到并已纳入 Git。这 16 个引用仍为绝对路径：包括 13 张贴图及下列三个人物库。更换克隆目录或机器时，需要在 Blender 中把它们重新定位到新仓库的对应文件；逐项目标路径见下方源引用检查 JSON 的 `reference_paths`。

- `work/scene_r24/courtyard_life/black.blend`
- `work/scene_r24/courtyard_life/red.blend`
- `work/scene_r24/courtyard_life/kitchen/greens.blend`

本次不重写既有 Blender 二进制或历史哈希。Godot 运行时使用已经导出的 GLB，不依赖这三个 Blender 路径。检查结果见 [源引用检查](version-control/blender-source-check.json)。

### 提交改动

每个独立改动完成后，检查差异并执行与改动对应的原有验证；将 Blender 源、导出的 GLB、运行逻辑和必要证据放在同一提交中。不要把通过测试解释为美术验收。

```powershell
git status --short
git diff
git add -- <本次改动的路径>
git diff --cached --stat
git commit -m "说明本次改动"
git push
```

当前本机 `main` 跟踪 `origin/main`。开始跨机器工作前执行 `git pull --ff-only`，并确保 LFS 文件完整。遇到分支分叉先核对双方改动，不强制推送覆盖远端。不要执行 `git clean -fdx`，它会删除本地保留的档案和引擎缓存。

后续如启用新的完整整城 Blender 路径，同时调整 `.gitignore` 中的当前源例外，确认 `git check-ignore <新路径>` 没有忽略它，再把新源与对应导出一起提交。既有旧快照例外不自动扩展成全量历史备份。

本次迁移保留 Godot 4.6.3 / Blender 4.3.2，不修改游戏玩法或美术。新验证目录使用 `github_initial_20261124`，执行范围及结果记录在交接日志。使用新版目录名重跑时不要覆盖本轮或旧轮证据。
