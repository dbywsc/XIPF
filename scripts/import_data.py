"""XIPF contest data importer — CSV only.

Format: Tab-separated CSV.
  Rank  Organization Rank  Organization  Team  Member1  Member2  Member3  Unofficial  Girl  Prize

Usage: python scripts/import_data.py contest.csv --date=2026-05-24
"""

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTESTS_DIR = ROOT / "contests"

CITY_NAMES = [
    "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "重庆",
    "西安", "长沙", "郑州", "济南", "青岛", "合肥", "南昌", "福州", "厦门",
    "沈阳", "大连", "哈尔滨", "长春", "昆明", "南宁", "贵阳", "兰州",
    "天津", "石家庄", "太原", "苏州", "徐州", "扬州", "宁波", "温州",
    "秦皇岛", "三亚", "桂林", "珠海", "佛山", "东莞", "中山", "惠州", "河南", "贵州", "广西", "江苏", "山东", "陕西", "吉林", "四川", "广东", "浙江", "内蒙古",
    "汕头", "绍兴", "芜湖", "洛阳", "开封", "湘潭", "株洲", "衡阳",
    "绵阳", "咸阳", "自贡", "包头", "齐齐哈尔",
]

PINYIN_CITIES = {
    "qinhuangdao": "秦皇岛", "beijing": "北京", "shanghai": "上海",
    "guangzhou": "广州", "shenzhen": "深圳", "hangzhou": "杭州",
    "nanjing": "南京", "wuhan": "武汉", "chengdu": "成都", "chongqing": "重庆",
    "xian": "西安", "changsha": "长沙", "zhengzhou": "郑州", "jinan": "济南",
    "qingdao": "青岛", "hefei": "合肥", "nanchang": "南昌", "fuzhou": "福州",
    "xiamen": "厦门", "shenyang": "沈阳", "dalian": "大连", "haerbin": "哈尔滨",
    "changchun": "长春", "kunming": "昆明", "nanning": "南宁", "guiyang": "贵阳",
    "lanzhou": "兰州", "tianjin": "天津", "shijiazhuang": "石家庄", "taiyuan": "太原",
    "suzhou": "苏州", "xuzhou": "徐州", "yangzhou": "扬州", "ningbo": "宁波",
    "wenzhou": "温州", "dongguan": "东莞",
}


def detect_city(filename: str) -> str:
    lower = filename.lower()
    for c in CITY_NAMES:
        if c in lower:
            return c
    for pinyin, chinese in PINYIN_CITIES.items():
        if pinyin in lower:
            return chinese
    m = re.search(r'[（(]([^）)]+)[）)]', filename)
    if m:
        return m.group(1)
    return "unknown"


def parse_medal(v: str) -> str:
    if not v:
        return ""
    s = str(v).strip().lower()
    if "gold" in s or s in ("金奖", "金牌", "金"):
        return "gold"
    if "silver" in s or s in ("银奖", "银牌", "银"):
        return "silver"
    if "bronze" in s or s in ("铜奖", "铜牌", "铜"):
        return "bronze"
    return ""


def import_csv(filepath: Path, year: str, contest_date: str, contest_title: str = "") -> dict:
    teams = []
    roster = {"teams": {}}
    seen_ids = set()

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter="\t")
        rows = list(reader)

    header_row = -1
    for i, row in enumerate(rows):
        if row and str(row[0]).strip() == "Rank":
            header_row = i
            break

    if header_row < 0:
        print("Error: Could not find header row starting with 'Rank'")
        return None

    for row in rows[header_row + 1:]:
        if not row or not any(cell.strip() for cell in row):
            continue
        first = str(row[0]).strip()
        if first.startswith("#") or first.startswith(","):
            continue

        rank = int(first) if first.isdigit() else 0
        org_rank = int(row[1].strip()) if len(row) > 1 and row[1].strip().isdigit() else 0
        organization = str(row[2]).strip() if len(row) > 2 else ""
        team_name = str(row[3]).strip() if len(row) > 3 else ""

        members = []
        for i in range(4, 7):
            if i < len(row) and row[i].strip():
                members.append({"name": row[i].strip(), "gender": ""})

        unofficial = str(row[7]).strip().upper() == "Y" if len(row) > 7 and row[7].strip() else False
        girl_team = str(row[8]).strip().upper() == "Y" if len(row) > 8 and row[8].strip() else False
        medal = parse_medal(row[9]) if len(row) > 9 else ""

        tid = f"T{rank:03d}" if rank > 0 else f"T{len(teams) + 1:03d}"
        base_tid = tid
        counter = 1
        while tid in seen_ids:
            tid = f"{base_tid}_{counter}"
            counter += 1
        seen_ids.add(tid)

        teams.append({
            "id": tid, "name": team_name, "organization": organization,
            "official": not unofficial, "rank": rank, "org_rank": org_rank,
            "solved": 0, "penalty": 0, "problems": [],
            "medal": medal, "members": members, "girl_team": girl_team,
            "champion": "",
        })
        roster["teams"][tid] = {"members": members, "organization_override": None}

    # Compute champion/亚军/季军: only the best-ranked team per org
    # For each org, find the official team with the lowest rank
    org_best: dict[str, int] = {}  # org -> best rank
    org_best_team: dict[str, str] = {}  # org -> team id of best team
    for t in teams:
        if not t["official"] or not t["organization"]:
            continue
        org = t["organization"]
        if org not in org_best or t["rank"] < org_best[org]:
            org_best[org] = t["rank"]
            org_best_team[org] = t["id"]

    # Sort orgs by best rank
    sorted_orgs = sorted(org_best.items(), key=lambda x: x[1])
    champion_labels = {1: "冠军", 2: "亚军", 3: "季军"}
    for i, (org, _) in enumerate(sorted_orgs[:3]):
        best_tid = org_best_team[org]
        for t in teams:
            if t["id"] == best_tid:
                t["champion"] = champion_labels[i + 1]

    gold = sum(1 for t in teams if t["medal"] == "gold")
    silver = sum(1 for t in teams if t["medal"] == "silver")
    bronze = sum(1 for t in teams if t["medal"] == "bronze")

    return {
        "title": contest_title or filepath.stem,
        "year": int(year),
        "date": contest_date,
        "teams": teams,
        "problems": [],
        "awards": {"gold": gold, "silver": silver, "bronze": bronze},
    }, roster


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} path/to/file.csv --date=YYYY-MM-DD [--year YYYY]")
        print()
        print("CSV format (Tab-separated):")
        print("  Rank  Organization Rank  Organization  Team  Member1  Member2  Member3  Unofficial  Girl  Prize")
        sys.exit(1)

    filepath = Path(sys.argv[1]).resolve()
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    year = "2026"
    contest_date = ""
    contest_title = ""
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--year="):
            year = arg.split("=", 1)[1]
        elif arg == "--year" and i + 1 < len(sys.argv):
            year = sys.argv[i + 1]
        elif arg.startswith("--date="):
            contest_date = arg.split("=", 1)[1]
        elif arg == "--date" and i + 1 < len(sys.argv):
            contest_date = sys.argv[i + 1]
        elif arg.startswith("--title="):
            contest_title = arg.split("=", 1)[1]
        elif arg == "--title" and i + 1 < len(sys.argv):
            contest_title = sys.argv[i + 1]

    if not contest_date:
        print("Warning: no --date provided. Use --date=YYYY-MM-DD")

    filename = filepath.stem
    city = detect_city(filename)
    print(f"Processing: {filepath.name}")
    print(f"  City: {city}, Date: {contest_date or 'not set'}")

    result = import_csv(filepath, year, contest_date, contest_title)
    if result is None:
        sys.exit(1)

    contest_data, roster = result

    lower = filename.lower()
    if "邀请赛" in lower or "invitational" in lower:
        slug = f"{city}_invitational"
    elif "省赛" in lower or "provincial" in lower:
        slug = f"{city}_provincial"
    elif "打星" in lower or "unofficial" in lower:
        slug = f"{city}_unofficial"
    else:
        slug = city

    contest_dir = CONTESTS_DIR / year / slug
    contest_dir.mkdir(parents=True, exist_ok=True)

    with open(contest_dir / "contest_data.json", "w", encoding="utf-8") as f:
        json.dump(contest_data, f, ensure_ascii=False, indent=2)
    with open(contest_dir / "roster.json", "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=2)

    print(f"  -> {contest_dir.relative_to(CONTESTS_DIR)}")
    print(f"     {len(contest_data['teams'])} teams, "
          f"G{contest_data['awards']['gold']}/S{contest_data['awards']['silver']}/B{contest_data['awards']['bronze']}")


if __name__ == "__main__":
    main()
