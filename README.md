# XIPF

Xcpc Invitational Programming contest Finder

大学生程序设计竞赛数据平台，追踪 ICPC / CCPC 选手与学校的竞技实力。

> **数据来源：** 本项目所有比赛数据均来自 [algoux/srk-collection](https://github.com/algoux/srk-collection)，
> 该仓库收集了 ICPC/CCPC 的标准榜单数据（SRK 格式）。
>
> **评级算法：** 基于 [xcpcrating](https://github.com/Hei-MaoM/xcpcrating) Elo 评级系统。

## 架构

```
srk-collection/    ← SRK 格式原始数据（来自 algoux/srk-collection）
      │
      ↓  python scripts/srk_to_xipf.py
      │
contests/          ← XIPF 中间格式（contest_data.json + roster.json）
      │
      ↓  python scripts/build.py
      │
dist/              ← 静态 JSON（前端直接读取）
      │
      ↓  Vue 3 SPA（纯前端 / GitHub Pages）
```

- 数据以文件形式存放，Git 版本控制
- Python 构建脚本处理为静态 JSON
- Vue 3 前端纯客户端渲染，部署于自有服务器

## 功能

- 首页：公告栏 + 快捷导航入口
- 比赛列表：按年份和级别（决赛/区域赛/邀请赛/省赛）分组浏览
- 比赛详情：队伍排名、奖项、Rating 变化，支持队伍名/选手名/学校名搜索
- 选手主页：个人 Rating 曲线图、按级别分组的参赛记录
- 学校主页：Rating、获奖统计、选手列表（可搜索）、比赛记录（校排/总校数 + Rating 变化）
- 学校排行：按 Rating 排序，支持搜索
- 选手排行：按 Rating 排序，支持搜索和分页加载
- 积分规则：xcpcrating Elo 算法公式与参数说明
- 深色/浅色模式切换

## 快速开始

**注意：** 本项目所有代码均由 Opencode + Deepseek 完成。

**环境要求**：Python 3.9+、Node.js 18+

```bash
# 安装 Python 依赖
pip install openpyxl

# 从 SRK 格式导入数据
python scripts/srk_to_xipf.py srk-collection-master/official/ccpc/ccpc2025/ccpc2025invitational-nanchang.srk.json \
  --year=2025 --type=ccpc --slug=南昌_invitational

# 构建数据
python scripts/build.py

# 创建数据目录并复制
mkdir -p web/public/data
cp -r dist/* web/public/data/

# 启动前端
cd web
npm install
npm run dev
```

打开 http://localhost:5173 即可浏览。

## 部署到服务器

前端构建产物在 `web/dist/` 目录，部署到任意静态文件服务器即可。

### Nginx 部署

```bash
# 1. 构建项目（或从 GitHub Actions Artifact 下载）
python scripts/build.py
mkdir -p web/public/data && cp -r dist/* web/public/data/
cd web && npm install && npm run build

# 2. 上传到服务器
rsync -avz web/dist/ user@server:/var/www/xipf/

# 3. 使用项目自带 nginx 配置
cp nginx.conf /etc/nginx/sites-available/xipf
# 编辑 nginx.conf，修改 server_name 和 root 路径
ln -s /etc/nginx/sites-available/xipf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

项目中已包含 `nginx.conf` 配置模板，含 gzip 压缩、预压缩文件支持、缓存头和安全头。

## 目录结构

```
├── contests/                           # XIPF 比赛数据
│   ├── 2016/                           # 按年份组织
│   ├── ...
│   └── 2026/
├── organizations.json                  # 学校归一化映射
├── scripts/
│   ├── srk_to_xipf.py                  # SRK → XIPF 转换工具
│   ├── build.py                        # 构建静态 JSON
│   └── models.py                       # 数据模型
├── web/                                # Vue 3 前端
│   └── src/pages/
│       ├── Home.vue                    # 首页
│       ├── Contests.vue                # 比赛列表
│       ├── Contest.vue                 # 比赛详情
│       ├── Contestants.vue             # 选手排行
│       ├── Contestant.vue              # 选手主页
│       ├── Organizations.vue           # 学校排行
│       ├── Organization.vue            # 学校主页
│       └── Rules.vue                   # 积分规则
├── dist/                               # 构建产物（不提交 Git）
└── .github/workflows/                  # CI/CD
```

## 技术栈

| 层 | 技术 |
|----|------|
| 数据处理 | Python 3 + openpyxl |
| 前端 | Vue 3 + TypeScript + Vite |
| 样式 | CSS 自定义属性（深色/浅色主题） |
| 搜索 | Fuse.js（客户端全文搜索） |
| 数学渲染 | KaTeX |
| 部署 | Nginx / 静态文件服务器 |
| 数据来源 | [algoux/srk-collection](https://github.com/algoux/srk-collection) |
| 评级算法 | [xcpcrating](https://github.com/Hei-MaoM/xcpcrating) |

## License

AGPL-3.0
