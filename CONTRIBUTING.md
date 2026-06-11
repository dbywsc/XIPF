# 贡献指南

## 方式一：XLSX 导入（推荐）

如果你的比赛数据是 CCPC 官方 Excel 格式：

```bash
pip install openpyxl
python scripts/xlsx_to_csv.py contest.xlsx
```

会自动生成两个 CSV：`城市_invitational.csv` 和 `城市_provincial.csv`。

然后导入：

```bash
python scripts/import_data.py 城市_invitational.csv \
  --date=2026-05-20 \
  --title="2026 年中国大学生程序设计竞赛全国邀请赛（城市）"
```

## 方式二：Web 导入

启动前端 `cd web && npm run dev`，访问「导入」页面：

1. 填写比赛名称和日期
2. 拖拽上传 CSV 文件
3. 点击下载两个 JSON 文件
4. 放入 `contests/YYYY/城市_类型/` 目录
5. 运行 `python scripts/build.py`

## CSV 格式

Tab 分隔，UTF-8 编码：

```
Rank	Organization Rank	Organization	Team	Member1	Member2	Member3	Unofficial	Girl	Prize
1	1	武汉大学	毕业旅行	张三	李四	王五	N	N	金奖
*			中山纪念中学	烟花巷陌	胡金勇	吴同春	蔡明辉	Y	N	
```

### 说明

- `Rank` 为 `*` 表示打星队伍，只排名不评奖
- `Organization Rank` 由 `xlsx_to_csv.py` 自动计算（取本校最优正式队排名）
- `Prize` 支持：金奖、银奖、铜奖，或留空
- `Unofficial` 为 `Y` 时队伍不参与奖牌统计
- `Girl` 为 `Y` 时标记为女队
- 队员列（Member1-3）超过 3 人时只取前 3 人，跳过教练

## 冠亚季军

每场比赛自动计算校排前 3 名：

- **冠军** = 校排第 1 的正式队伍
- **亚军** = 校排第 2 的正式队伍
- **季军** = 校排第 3 的正式队伍

同一学校多支队伍参赛时，只有排名最高的那支队伍获得冠亚季军标记。
冠军同时计入金牌统计。

## 构建

```bash
python scripts/build.py
```

构建产物在 `dist/` 目录，前端直接读取。每次添加或修改比赛数据后都需要重新构建。

## 学校名归一化

首次导入新学校时，`build.py` 会自动调用 `bootstrap_orgs.py` 生成 `organizations.json`。学校名会根据城市前缀自动归类省市。

如需手动合并别名：

```json
{
  "id": "org-xxxxxxxx",
  "canonical": "武汉大学",
  "aliases": ["Wuhan University", "WHU"],
  "province": "湖北",
  "city": "武汉"
}
```

## 目录命名

```
contests/YYYY/城市_类型/
```

- 城市从文件名自动检测（中文或拼音均可）
- 类型：`invitational`（邀请赛）、`provincial`（省赛）

## PR 前检查

```bash
python scripts/build.py      # 确保构建成功
python scripts/validate.py   # 校验数据格式
```

CI 也会自动运行以上检查。
