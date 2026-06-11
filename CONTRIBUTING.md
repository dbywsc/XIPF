# 贡献指南

如果你有一场 ICPC / CCPC 比赛的数据，欢迎为 XIPF 贡献。

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

# 4. 安装 Python 依赖
pip install openpyxl
```

## 一、放入比赛数据

将你的 `.xlsx` 文件（CCPC 官方导出的 Excel）放到任意位置，然后：

```bash
# 转换为 CSV（自动分离邀请赛和省赛）
python scripts/xlsx_to_csv.py /path/to/contest.xlsx

# 导入邀请赛
python scripts/import_data.py 城市_invitational.csv \
  --date=2026-05-20 \
  --title="2026 年中国大学生程序设计竞赛全国邀请赛（某某城市）"

# 导入省赛（如果有）
python scripts/import_data.py 城市_provincial.csv \
  --date=2026-05-20 \
  --title="第 X 届 XX 省大学生程序设计竞赛"
```

这会在 `contests/2026/` 下自动创建对应目录和文件。

### 为什么不直接用 XLSX？

XLSX 中队员名和教练混在一起，且不同比赛的列布局不同。`xlsx_to_csv.py` 会：

- 自动提取前 3 个队员，跳过教练
- 自动识别女队（通过 Markers 列）
- 自动计算学校排名（本校最优正式队的排名）
- 正确分离邀请赛和省赛为两个独立榜单

## 二、在本地预览验证

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

## 三、提交 PR

```bash
# 创建独立分支
git checkout -b add-contest-2026-某某城市

# 只提交比赛数据，不要提交 dist/
git add contests/2026/某某城市_invitational/
git add contests/2026/某某城市_provincial/
git add organizations.json   # 如果有新增学校

git commit -m "添加 2026 年某某城市邀请赛/省赛数据"
git push origin add-contest-2026-某某城市
```

然后去你的 fork 页面，点击 **Contribute → Open Pull Request**，选择你的分支合并到 `dbywsc/XIPF` 的 `main`。

## CSV 格式参考

如果你需要手动修改 CSV 再导入，格式如下（Tab 分隔）：

```
Rank	Organization Rank	Organization	Team	Member1	Member2	Member3	Unofficial	Girl	Prize
1	1	武汉大学	毕业旅行	张三	李四	王五	N	N	金奖
*			中山纪念中学	烟花巷陌	胡金勇	吴同春	蔡明辉	Y	N	
```

| 列 | 说明 |
|----|------|
| Rank | 数字 = 正式队排名，`*` = 打星队伍 |
| Organization Rank | 校排，由工具自动计算 |
| Organization | 学校全名 |
| Team | 队伍名称 |
| Member1-3 | 队员姓名 |
| Unofficial | `Y` = 打星，`N` = 正式 |
| Girl | `Y` = 女队 |
| Prize | 金奖 / 银奖 / 铜奖，打星队伍留空 |

## 目录结构

```
contests/YYYY/城市_类型/
├── contest_data.json    # 比赛数据
└── roster.json          # 队员名册
```

- 城市从文件名自动识别（中文或拼音均可）
- 类型：`invitational`（邀请赛）、`provincial`（省赛）

## 注意事项

- **不要提交 `dist/` 目录**（已在 `.gitignore` 中排除）
- 同一姓名在不同学校会自动区分为不同选手
- 冠亚季军每场比赛自动计算，不需要手动标记
- 女队标签从原始 Excel 的 Markers 列自动识别
