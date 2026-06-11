# XIPF

Xcpc Invitational Programming contest Finder

记录选手们在邀请赛和省赛中的获奖情况

## 架构

```
contests/          ← 原始数据（CSV / XLSX）
     │
     ↓  python scripts/import_data.py
     │
JSON 数据          ← 中间格式
     │
     ↓  python scripts/build.py
     │
dist/              ← 静态 JSON（前端直接读取）
     │
     ↓  Vue 3 SPA（纯前端 / GitHub Pages）
```

- 数据以文件形式存放，Git 版本控制
- Python 构建脚本处理为静态 JSON
- Vue 3 前端纯客户端渲染，托管于 GitHub Pages（免费）

## 快速开始

**注意：** 本项目所有代码均由 Claude + Deepseek 完成。

**环境要求**：Python 3.9+、Node.js 18+

```bash
# 安装 Python 依赖
pip install openpyxl

# 导入数据（支持 .xlsx / .csv）
python scripts/import_data.py path/to/contest.xlsx --date=2026-05-24

# 构建
python scripts/build.py

# 启动前端
cd web
npm install
npm run dev
```

打开 http://localhost:5173 即可浏览。

## 数据导入

### CLI

```bash
# CCPC 官方 XLSX（自动识别邀请赛/省赛/女队）
python scripts/import_data.py contest.xlsx --date=2026-06-01

# CSV（Tab 分隔）
# 格式：Rank  OrgRank  Organization  Team  Member1  Member2  Member3  Unofficial  Girl  Prize
python scripts/import_data.py contest.csv --date=2026-06-01
```

### Web

启动前端后访问「导入」页面，拖拽上传 XLSX 或 CSV，自动解析并下载 JSON 文件。放入 `contests/YYYY/城市名/` 后重新构建即可。

## 目录结构

```
├── contests/                          # 原始数据
│   └── 2026/
│       └── 秦皇岛_invitational/
│           ├── contest_data.json      # 比赛数据（导入生成）
│           └── roster.json            # 队员名册
├── organizations.json                 # 学校归一化（自动生成）
├── scripts/
│   ├── import_data.py                 # 数据导入（CSV / XLSX）
│   ├── build.py                       # 构建静态 JSON
│   ├── validate.py                    # 数据校验（CI）
│   ├── models.py                      # 数据模型
│   └── bootstrap_orgs.py             # 学校名自动归类
├── web/                               # Vue 3 前端
│   └── src/pages/
│       ├── Home.vue                   # 首页（双搜索框）
│       ├── Contest.vue                # 比赛详情（可展开队员）
│       ├── Contestant.vue             # 选手主页
│       ├── Organization.vue           # 学校主页
│       ├── Contests.vue              # 全部比赛
│       ├── Organizations.vue         # 全部学校
│       ├── Contestants.vue           # 全部选手
│       └── Import.vue                # 在线导入
├── dist/                              # 构建产物（不提交 Git）
└── .github/workflows/                 # CI/CD
    ├── validate.yml                   # PR 校验
    └── deploy.yml                     # 自动部署
```

## 贡献数据

1. Fork 本仓库
2. 在 `contests/YYYY/城市名_类型/` 下放入数据文件，或运行 `python scripts/import_data.py`
3. 运行 `python scripts/build.py` 验证
4. 提交 Pull Request

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 技术栈

| 层 | 技术 |
|----|------|
| 数据处理 | Python 3 + openpyxl |
| 前端 | Vue 3 + TypeScript + Vite |
| 搜索 | Fuse.js（客户端全文搜索） |
| 部署 | GitHub Pages（免费） |
| 数据格式 | JSON（静态文件） |

## License

AGPL-3.0
