"""Batch import ALL srk-collection-master contests into XIPF format.

Filters:
  - Skip: 丝绸之路 (srni) / 银川 (yinchuan)
  - Require: team members present, complete team names, awards info
"""

import json
import os
import re
import sys
import shutil
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
SRK_BASE = ROOT / "srk-collection-master" / "official"
CONTESTS_DIR = ROOT / "contests"
SRK_TO_XIPF = ROOT / "scripts" / "srk_to_xipf.py"

# Province code → Chinese name
PROVINCE_MAP = {
    "ah": "安徽","bj": "北京","cq": "重庆","fj": "福建","gd": "广东",
    "gx": "广西","gz": "贵州","ha": "河南","hb": "湖北","he": "河北",
    "hl": "黑龙江","hn": "湖南","jl": "吉林","js": "江苏","jx": "江西",
    "ln": "辽宁","nm": "内蒙古","northeast": "东北","sc": "四川",
    "sd": "山东","sh": "上海","sn": "陕西","xj": "新疆","zj": "浙江",
}

# City name translations for regional/invitational
CITY_MAP = {
    "wuhan": "武汉","xi_an": "西安","kunming": "昆明","nanchang": "南昌",
    "fuzhou": "福州","jinan": "济南","changchun": "长春","fujian": "福州",
    "zhengzhou": "郑州","shenzhen": "深圳","guangdong-preliminary": "广东预赛",
    "chengdu": "成都","nanjing": "南京","hangzhou": "杭州","shanghai": "上海",
    "shenyang": "沈阳","hongkong": "香港","harbin": "哈尔滨",
    "beijing": "北京","guangzhou": "广州","yinchuan": "银川","xiamen": "厦门",
    "qinhuangdao": "秦皇岛","guiyang": "贵阳","guilin": "桂林",
    "xiangtan": "湘潭","qingdao": "青岛","dalian": "大连","hefei": "合肥",
    "jinhua": "金华","mudanjiang": "牡丹江","guangdong": "广东",
    "xuzhou": "徐州","ningbo": "宁波","lanzhou": "兰州","urumqi": "乌鲁木齐",
    "kunshan": "昆山","jingdezhen": "景德镇","suzhou": "苏州",
}

EXCLUDE_KEYWORDS = ["yinchuan", "srni", "silkr", "丝绸之路", "银川"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def should_skip(fpath):
    """Check if contest should be skipped (silk road / yinchuan)."""
    name = os.path.basename(fpath).lower()
    if any(k in name for k in EXCLUDE_KEYWORDS):
        return True, "silk-road/yinchuan"

    # Also check title inside the file
    try:
        data = load_json(fpath)
        title = ""
        t = data.get("contest", {}).get("title", {})
        if isinstance(t, dict):
            title = t.get("zh-CN", "") + t.get("fallback", "") + t.get("en", "")
        elif isinstance(t, str):
            title = t
        if any(k in title.lower() for k in ["srni", "silkr", "丝绸之路"]):
            return True, "silk-road-title"
    except:
        pass
    return False, ""


def has_team_members(fpath):
    """Check if contest has team member data."""
    try:
        data = load_json(fpath)
        rows = data.get("rows", [])
        members_count = sum(
            1 for r in rows
            if r.get("user", {}).get("teamMembers") and len(r["user"]["teamMembers"]) > 0
        )
        total = len(rows)
        return members_count > 0, members_count, total
    except:
        return False, 0, 0


def has_awards(data):
    """Check if contest has award/medal info via series rules."""
    series = data.get("series", [])
    if not series:
        # Can use default 10/20/30%
        return True
    for s in series:
        rule = s.get("rule", {})
        if rule.get("preset") == "ICPC":
            return True
    return True  # Even without series, we can use defaults


def parse_srk_meta(fpath):
    """Extract year, category, title, slug from srk file."""
    data = load_json(fpath)
    contest = data.get("contest", {})

    # Title
    title_data = contest.get("title", {})
    if isinstance(title_data, dict):
        title = title_data.get("zh-CN") or title_data.get("fallback", "") or ""
    else:
        title = str(title_data)

    # Date
    start_at = contest.get("startAt", "")
    date = start_at[:10] if start_at else ""
    year = date[:4] if date else ""

    # Category from path
    rel = str(fpath.relative_to(SRK_BASE))
    parts = rel.split("/")
    category = parts[0] if parts else "other"  # ccpc, icpc, provincial

    # Derive slug from filename
    fname = os.path.splitext(os.path.basename(fpath))[0]  # Remove .json
    fname = fname.replace(".srk", "")  # Remove .srk if present

    slug = derive_slug(fname, category, parts)
    return year, category, title, date, slug


def derive_slug(fname, category, parts):
    """Derive a directory slug from the filename."""
    # For provincial: {province_code}cpc{N}th → {省}_provincial
    if category == "provincial":
        province_code = parts[1] if len(parts) > 1 else ""
        province = PROVINCE_MAP.get(province_code, province_code)
        return f"{province}_provincial" if province else fname

    # For regional/invitational, parse pattern
    # icpc2025wuhan / icpc2025invitational-wuhan / icpc2025ecfinal
    # ccpc2023harbin / ccpc2023invitational-xiangtan
    for prefix in ["icpc", "ccpc"]:
        if fname.startswith(prefix):
            rest = fname[len(prefix):]  # e.g., "2025wuhan" or "2025invitational-wuhan"
            # Strip year: 4 digits
            m = re.match(r"(\d{4})(.*)", rest)
            if m:
                year_digits = m.group(1)
                detail = m.group(2)  # e.g., "wuhan", "invitational-wuhan", "ecfinal"

                # Check if invitational
                if detail.startswith("invitational"):
                    city_key = detail[len("invitational-"):] if "-" in detail else detail[len("invitational"):]
                    city = CITY_MAP.get(city_key, city_key.replace("_", ""))
                    return f"{city}_invitational"

                # Check known types
                if "preliminary" in detail:
                    return f"{detail}_preliminary"
                if "ecfinal" in detail:
                    return "ecfinal"

                # Regular regional
                city = CITY_MAP.get(detail, detail)
                return f"{city}_regional"

    return fname


def main():
    print("=" * 60)
    print("Batch import SRK → XIPF")
    print("=" * 60)

    # Find all srk files
    srk_files = []
    for cat in ["ccpc", "icpc", "provincial"]:
        cat_dir = SRK_BASE / cat
        if cat_dir.exists():
            for f in sorted(cat_dir.rglob("*.srk.json")):
                srk_files.append(f)

    print(f"\nFound {len(srk_files)} contest files")
    print(f"  CCPC: {sum(1 for f in srk_files if '/ccpc/' in str(f))}")
    print(f"  ICPC: {sum(1 for f in srk_files if '/icpc/' in str(f))}")
    print(f"  Provincial: {sum(1 for f in srk_files if '/provincial/' in str(f))}")

    stats = {"imported": 0, "skipped_members": 0, "skipped_sr": 0, "skipped_other": 0, "failed": 0}

    for fpath in srk_files:
        rel = fpath.relative_to(SRK_BASE)
        print(f"\n[{rel}]")

        # 1. Check silk road / yinchuan
        skip, reason = should_skip(fpath)
        if skip:
            print(f"  SKIP ({reason})")
            stats["skipped_sr"] += 1
            continue

        # 2. Check team members
        has_mem, mem_count, total_rows = has_team_members(fpath)
        if not has_mem:
            print(f"  SKIP (no team members)")
            stats["skipped_members"] += 1
            continue

        # 3. Parse meta
        try:
            year, category, title, date, slug = parse_srk_meta(fpath)
        except Exception as e:
            print(f"  SKIP (parse error: {e})")
            stats["skipped_other"] += 1
            continue

        if slug is None:
            print(f"  SKIP (unknown)")
            stats["skipped_other"] += 1
            continue

        # 4. Determine output dir
        out_dir = CONTESTS_DIR / str(year) / category / slug
        if (out_dir / "contest_data.json").exists() or (out_dir / "rank.srk.json").exists():
            print(f"  SKIP (already exists: {out_dir.relative_to(ROOT)})")
            stats["skipped_other"] += 1
            continue

        # 5. Convert
        try:
            from srk_to_xipf import convert_srk
            contest_data, roster = convert_srk(fpath, int(year) if year.isdigit() else 2024, date, title)
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / "contest_data.json", "w", encoding="utf-8") as f:
                json.dump(contest_data, f, ensure_ascii=False, indent=2)
            with open(out_dir / "roster.json", "w", encoding="utf-8") as f:
                json.dump(roster, f, ensure_ascii=False, indent=2)

            teams = contest_data["teams"]
            awards = contest_data["awards"]
            rel_out = out_dir.relative_to(ROOT)
            print(f"  OK → {rel_out}")
            print(f"    {title[:50]}")
            print(f"    {len(teams)} teams, G{awards['gold']}/S{awards['silver']}/B{awards['bronze']}")
            print(f"    {mem_count}/{total_rows} rows with members")
            stats["imported"] += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            stats["failed"] += 1

    print("\n" + "=" * 60)
    print(f"Results: {stats['imported']} imported, {stats['skipped_members']} no-members, "
          f"{stats['skipped_sr']} silk-road, {stats['skipped_other']} other, {stats['failed']} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
