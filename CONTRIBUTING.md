# 贡献指南

如果你有一场 ICPC / CCPC 比赛的数据，欢迎为 XIPF 贡献。

> **数据来源：** 本项目所有比赛数据均来自 [algoux/srk-collection](https://github.com/algoux/srk-collection)。
> 该仓库使用标准榜单格式（SRK）收录了历年 ICPC / CCPC / 省赛的比赛数据。
> 如果你要添加新比赛，请先从 srk-collection 获取 `.srk.json` 文件，再转换为 XIPF 格式。

## 零、准备工作（只需一次）

> **注意：必须用 `git clone`，不能下载 ZIP。** ZIP 包里没有 `.git`，无法创建分支和提交 PR。

```bash
# 1. Fork 仓库
# 打开 https://github.com/dbywsc/XIPF 点右上角 Fork

# 2. 克隆你的 fork（替换 "你的用户名"）
git clone git@github.com:你的用户名/XIPF.git
cd XIPF

# 3. 关联上游仓库（方便后续同步）
git remote add upstream git@github.com:dbywsc/XIPF.git
```

## 一、数据来源

XIPF 的比赛数据来自 **[algoux/srk-collection](https://github.com/algoux/srk-collection)**，
这是一个开源的竞赛榜单数据仓库，使用标准榜单格式（SRK JSON）收录了历年 ICPC/CCPC/省赛的全部数据。

```bash
# 克隆 srk-collection 到本地
git clone https://github.com/algoux/srk-collection.git srk-collection-master
```

## 二、导入比赛数据

从 srk-collection 获取 `.srk.json` 文件后，使用转换工具：

```bash
# 单个文件转换
python scripts/srk_to_xipf.py srk-collection-master/official/ccpc/ccpc2025/ccpc2025invitational-nanchang.srk.json \
  --year=2025 --type=ccpc --slug=南昌_invitational

# 批量转换（自动扫描 srk-collection-master/official/ 目录）
python scripts/batch_convert_srk.py
```

参数说明：
- `--year`：比赛年份
- `--type`：`ccpc` 或 `icpc`
- `--slug`：目录名（如 `南昌_invitational`、`北京_provincial`）
- `--date`：比赛日期 YYYY-MM-DD（默认从 SRK 文件提取）
- `--title`：比赛标题（默认从 SRK 文件提取）

## 三、在本地预览验证

```bash
# 1. 构建数据
python scripts/build.py

# 2. 创建数据目录（只需首次）
mkdir -p web/public/data
cp -r dist/* web/public/data/

# 3. 安装前端依赖（只需首次）
cd web
npm install

# 4. 启动开发服务器
npm run dev
```

浏览器打开 `http://localhost:5173`，检查：

- 首页能看到新导入的比赛
- 点击比赛可以展开查看队伍和奖牌
- 学校和选手列表的数据正确
- 搜索功能正常

确认无误后 `Ctrl+C` 停止服务器，继续下一步。

## 四、提交 PR

```bash
# 创建独立分支
git checkout -b add-contest-2025-某某城市

# 只提交比赛数据，不要提交 dist/ 和 srk-collection-master/
git add contests/2025/某某城市_invitational/
git add contests/2025/某某城市_provincial/
git add organizations.json   # 如果有新增学校

git commit -m "添加 2025 年某某城市邀请赛/省赛数据"
git push origin add-contest-2025-某某城市
```

然后去你的 fork 页面，点击 **Contribute → Open Pull Request**，选择你的分支合并到 `dbywsc/XIPF` 的 `main`。

## 目录结构

```
contests/YYYY/城市_类型/
├── contest_data.json    # 比赛数据
└── roster.json          # 队员名册
```

- 类型：`invitational`（邀请赛）、`provincial`（省赛）、`regional`（区域赛）、`final`（决赛）
- `_combined` 后缀用于多组别合并榜单

## 注意事项

- **不要提交 `dist/` 目录**（已在 `.gitignore` 中排除）
- **不要提交 `srk-collection-master/` 目录**（使用 srk_to_xipf.py 转换后只提交 contests/）
- **不要提交 `xcpcrating-main/` 目录**（参考项目，不在本仓库中）
- 数据来源请注明 [algoux/srk-collection](https://github.com/algoux/srk-collection)
- 同一姓名在不同学校会自动区分为不同选手
- 冠亚季军每场比赛自动计算，不需要手动标记
