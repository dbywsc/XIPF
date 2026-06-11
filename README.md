# XIPF

大学生程序设计竞赛（ICPC / CCPC）数据追踪平台，专注于邀请赛和省赛的获奖统计。

记录选手、学校在各项比赛中的排名、奖牌、冠亚季军，支持搜索、排行、数据分析。

## 功能

- **选手追踪** — 跨比赛追踪同一选手，自动合并参赛记录
- **学校排名** — 按冠军 > 亚军 > 季军 > 金牌 > 银牌 > 铜牌排序
- **冠亚季军** — 每场比赛计算校排前 3，仅本校最优队伍计数
- **打星队伍** — 有排名、不评奖、正确穿插在正式队伍之间
- **女队标记** — XLSX 导入时自动识别
- **双榜单** — 同一场比赛的邀请赛和省赛自动分离

## 快速开始

```bash
# 环境
pip install openpyxl    # 仅 XLSX 导入需要
Node.js 18+

# 步骤一：导入数据
python scripts/xlsx_to_csv.py contest.xlsx
# → 生成 城市_invitational.csv 和 城市_provincial.csv

python scripts/import_data.py 城市_invitational.csv --date=2026-05-20 --title="2026 年比赛名称"

# 步骤二：构建
python scripts/build.py

# 步骤三：启动前端
cd web && npm install && npm run dev
```

打开 `http://localhost:5173`。

## 数据格式

### CSV（Tab 分隔）

```
Rank	Organization Rank	Organization	Team	Member1	Member2	Member3	Unofficial	Girl	Prize
1	1	清华大学	零基础新生 1 队	张三	李四	王五	N	N	金奖
*			中山纪念中学	烟花巷陌	胡金勇	吴同春	蔡明辉	Y	N	
```

| 列 | 说明 |
|----|------|
| Rank | `*` = 打星，数字 = 正式队排名 |
| Organization Rank | 校排（`xlsx_to_csv.py` 自动计算） |
| Organization | 学校全名 |
| Team | 队伍名称 |
| Member1-3 | 队员姓名 |
| Unofficial | `Y` = 打星 |
| Girl | `Y` = 女队 |
| Prize | 金奖 / 银奖 / 铜奖 或留空 |

### 导入命令

```bash
# XLSX → CSV
python scripts/xlsx_to_csv.py contest.xlsx

# CSV → 导入（CLI）
python scripts/import_data.py file.csv --date=2026-05-20 --title="比赛名称"

# CSV → 导入（Web）
# 浏览器打开 http://localhost:5173/#/import 拖拽上传
```

## 命令参考

| 命令 | 用途 |
|------|------|
| `python scripts/xlsx_to_csv.py file.xlsx` | XLSX 转 CSV，自动分离邀请赛/省赛 |
| `python scripts/import_data.py file.csv --date=YYYY-MM-DD --title="名称"` | CSV 导入为比赛数据 |
| `python scripts/build.py` | 构建静态 JSON 到 `dist/` |
| `python scripts/validate.py` | 校验数据格式 |

## 目录结构

```
├── contests/            # 比赛数据（Git 跟踪）
│   └── YYYY/
│       └── 城市_类型/
│           ├── contest_data.json
│           └── roster.json
├── organizations.json   # 学校名映射（自动生成）
├── scripts/             # Python 工具
│   ├── xlsx_to_csv.py      # XLSX → CSV
│   ├── import_data.py      # CSV → JSON
│   ├── build.py            # 构建静态站点数据
│   ├── validate.py         # CI 校验
│   └── bootstrap_orgs.py   # 学校名自动归类
├── web/                 # Vue 3 前端
│   └── src/pages/
│       ├── Home.vue              # 首页
│       ├── Contest.vue           # 比赛详情
│       ├── Contestant.vue        # 选手主页
│       ├── Organization.vue      # 学校主页
│       ├── Contests.vue         # 全部比赛
│       ├── Contestants.vue      # 全部选手
│       ├── Organizations.vue    # 全部学校
│       └── Import.vue           # 在线导入
├── dist/                 # 构建产物（不提交 Git）
└── .github/workflows/    # CI/CD
```

## 技术栈

| 层 | 技术 |
|----|------|
| 数据处理 | Python 3 + openpyxl |
| 前端 | Vue 3 + TypeScript + Vite |
| 搜索 | Fuse.js |
| 部署 | GitHub Pages |

## License

AGPL-3.0
