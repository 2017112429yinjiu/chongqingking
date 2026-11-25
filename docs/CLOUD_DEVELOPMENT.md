# 云端开发与基线复验

迁移基线为 `main` 上的 `ce1841b079b78c1f876bfa0da3b8b6a404ac9532`。游戏入口是 `work/project/chongqing_godot_v05/first_shift.tscn`，整城制作源是 `work/scene_r24/district_patrol/city_and_patrol.blend`。基线的 LFS 工作树共 10,728 个文件，去重后下载约 11.55 GB，展开后约 14.64 GB。还需为 Git、引擎、导入缓存及重开的 Blender 副本预留空间。

## 新的工作目录

在 GitHub Codespaces 中为本仓库的 `main` 打开开发容器，或在自己的 Linux x86-64 云机器上克隆到一个新的同级目录。Codespaces 会在新容器创建时安装 Godot 4.6.3、Blender 4.3.2 并执行 LFS 拉取。使用自有机器时可参考 [容器系统依赖](../.devcontainer/Dockerfile)。

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --branch main https://github.com/2017112429yinjiu/chongqingking.git chongqingking-cloud
cd chongqingking-cloud
git merge-base --is-ancestor ce1841b079b78c1f876bfa0da3b8b6a404ac9532 HEAD
bash tools/cloud/setup-linux.sh
export PATH="$PWD/.cloud-dev/tools/bin:$PATH"
python3 tools/cloud/verify.py
```

校验脚本执行 `git lfs pull` 与 `git lfs fsck`，再根据 Git 提交中的指针逐文件核对大小和 SHA-256。它在 Godot 中导入工程并启动默认场景 120 次引擎迭代，核对街区 GLB 的导入产物与引擎错误。它还重开 Blender 整城，把人物库和外置图像重新定位到这个克隆，逐一检查库数据、解码图片并检查街区几何。

每次运行的独立目录位于 `.cloud-dev/runs/`。其中的 `city_and_patrol.blend` 是可直接打开的迁移副本，相对路径指向同一克隆里的美术资源。`verification.json` 记录实际提交、工具版本、LFS 数量、引用、场景物体与导入结果。原始制作源和历史证据仍可按 Git 提交核对。旧整城快照及 R15 原始包的归档范围见[版本控制说明](VERSION_CONTROL.md)。

## GitHub Actions

`main` 每次收到推送后，**Chongqing cloud verification** 检查配置、脚本和提交中的 LFS 指针。需要整体验证时，在 **Actions → Chongqing cloud verification → Run workflow** 中选择 `main`，在 `revision` 填写目标提交。首次迁移填写上述完整基线 SHA，后续可留空以验证所选版本。工作流将验证脚本与目标工程分别检出，可复验尚未含有工作流的历史提交。完整运行从 GitHub LFS 拉取当前目标的全部资源，并在干净的 Linux runner 上执行两套引擎。JSON 报告和 Godot 日志保留七天。

## 日常开发

从更新后的 `main` 建工作分支，修改 Blender 源、对应导出和运行代码后一起提交，通过 PR 合入。编辑迁移副本后，需要把已确认的制作改动保存回仓库规定的整城源路径，再从新目录复验相对引用。检出历史版本可另建克隆或工作树。原机版本控制和本地档案使用[既有流程](VERSION_CONTROL.md)。

有图形设备的 Windows 工作区可复用原生巡检，使用独立运行名保存全路网、双向骑行、接缝近景和 GPU 计时。Linux 工作流的无窗口校验覆盖导入与启动。

```powershell
work/scene_r24/district_patrol/verify.ps1 -Run ("cloud_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")) -AllRoads -Timing
```
