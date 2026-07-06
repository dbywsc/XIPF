"""Regenerate contest_data.json from SRK using directory-path-based matching.

Uses a mapping from SRK filename → (year, category, slug) based on the same
derive_slug logic from import_all_srk.py, then matches contest directories
by (year, category, slug).
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRK_BASE = ROOT / "srk-collection-master" / "official"
CONTESTS_DIR = ROOT / "contests"

# --- import_all_srk.py slug derivation logic ---

PROVINCE_MAP = {
    "ah": "安徽","bj": "北京","cq": "重庆","fj": "福建","gd": "广东",
    "gx": "广西","gz": "贵州","ha": "河南","hb": "湖北","he": "河北",
    "hl": "黑龙江","hn": "湖南","jl": "吉林","js": "江苏","jx": "江西",
    "ln": "辽宁","nm": "内蒙古","northeast": "东北","sc": "四川",
    "sd": "山东","sh": "上海","sn": "陕西","xj": "新疆","zj": "浙江",
}

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
    "macau": "澳门","nanyang": "南阳",
}

# Additional slug→slug normalization for exact matching
SLUG_NORMALIZE = {
    # Synonyms / variations
    "final": "final",
    "ecfinal": "ecfinal",
    "ladies": "ladies",
}

EXCLUDE_KEYWORDS = ["yinchuan", "srni", "silkr", "丝绸之路", "银川"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def should_skip(fpath):
    name = fpath.name.lower()
    if any(k in name for k in EXCLUDE_KEYWORDS):
        return True
    return False


def derive_slug(fname, category, parts):
    """Derive a directory slug from SRK filename, same as import_all_srk.py."""
    # For provincial: {province_code}cpc{N}th → {省}_provincial
    if category == "provincial":
        province_code = parts[1] if len(parts) > 1 else ""
        province = PROVINCE_MAP.get(province_code, province_code)
        return f"{province}_provincial" if province else fname

    for prefix in ["icpc", "ccpc"]:
        if fname.startswith(prefix):
            rest = fname[len(prefix):]
            m = re.match(r"(\d{4})(.*)", rest)
            if m:
                detail = m.group(2)

                if detail.startswith("invitational"):
                    city_key = detail[len("invitational-"):] if "-" in detail else detail[len("invitational"):]
                    city = CITY_MAP.get(city_key, city_key.replace("_", ""))
                    return f"{city}_invitational"

                if "preliminary" in detail:
                    return f"{detail}_preliminary"
                if "ecfinal" in detail:
                    return "ecfinal"
                if "cnfinal" in detail:
                    return "cnfinal"
                if "final" in detail:
                    return "final"
                if "ladies" in detail:
                    return "ladies"

                # Regular regional
                city = CITY_MAP.get(detail, detail)
                return f"{city}_regional"

    return fname


def build_path_index():
    """Build (year, category, slug) → SRK path index."""
    index = {}
    for fpath in sorted(SRK_BASE.rglob("*.srk.json")):
        if should_skip(fpath):
            continue

        rel = fpath.relative_to(SRK_BASE)
        parts = rel.parts
        category = parts[0] if parts else "other"

        # Extract year
        fname = fpath.stem.replace(".srk", "")
        year_match = re.search(r"(\d{4})", fname)
        year = year_match.group(1) if year_match else ""

        if not year:
            # Try to guess year from directory
            for p in parts:
                ym = re.search(r"(\d{4})", p)
                if ym:
                    year = ym.group(1)
                    break

        slug = derive_slug(fname, category, parts)

        key = (year, category, slug)
        if key not in index:
            index[key] = []
        index[key].append(fpath)

    return index


def find_srk_by_path(contest_dir_rel, path_index):
    """Find the matching SRK file using directory structure."""
    parts = contest_dir_rel.split("/")
    if len(parts) < 3:
        return None

    year = parts[0]
    category = parts[1]
    slug = parts[2]

    key = (year, category, slug)
    if key in path_index:
        candidates = path_index[key]
        if len(candidates) == 1:
            return candidates[0]
        # Multiple candidates: prefer exact slug match
        for c in candidates:
            c_slug = derive_slug(c.stem.replace(".srk", ""), category, c.relative_to(SRK_BASE).parts)
            if c_slug == slug:
                return c
        return candidates[0]

    # Try without _regional/_invitational etc suffix
    base_slug = re.sub(r"_(regional|invitational|provincial|preliminary)$", "", slug)
    for (y, cat, s), files in path_index.items():
        if y == year and cat == category:
            base_s = re.sub(r"_(regional|invitational|provincial|preliminary)$", "", s)
            if base_s == base_slug:
                return files[0]

    return None


def regenerate_contest(contest_dir, srk_path):
    """Regenerate contest_data.json and roster.json from SRK."""
    from srk_to_xipf import convert_srk

    rel = contest_dir.relative_to(CONTESTS_DIR)
    parts = rel.parts
    year = int(parts[0]) if parts[0].isdigit() else 2024

    try:
        existing = load_json(contest_dir / "contest_data.json")
        date = existing.get("date", "")
        title = existing.get("title", "")
    except Exception:
        date = ""
        title = ""

    contest_data, roster = convert_srk(srk_path, year, date, title)

    # Preserve existing members if they were manually added
    try:
        existing = load_json(contest_dir / "contest_data.json")
        existing_teams = {t["id"]: t for t in existing.get("teams", [])}
        for team in contest_data["teams"]:
            tid = team["id"]
            if tid in existing_teams:
                if not team.get("members") and existing_teams[tid].get("members"):
                    team["members"] = existing_teams[tid]["members"]
    except Exception:
        pass

    with open(contest_dir / "contest_data.json", "w", encoding="utf-8") as f:
        json.dump(contest_data, f, ensure_ascii=False, indent=2)
    with open(contest_dir / "roster.json", "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=2)

    awards = contest_data["awards"]
    official_count = sum(1 for t in contest_data["teams"] if t["official"])
    return awards, official_count, len(contest_data["teams"])


def main():
    print("Building path index...")
    path_index = build_path_index()
    print(f"  Indexed {sum(len(v) for v in path_index.values())} SRK files ({len(path_index)} unique (year,cat,slug) keys)")

    # Find all contest directories
    contest_dirs = []
    for fpath in sorted(CONTESTS_DIR.rglob("contest_data.json")):
        contest_dirs.append(fpath.parent)

    print(f"\nProcessing {len(contest_dirs)} contest directories...\n")

    fixed = 0
    ok = 0
    not_found = 0
    skipped = 0

    for contest_dir in contest_dirs:
        rel = str(contest_dir.relative_to(CONTESTS_DIR))

        # Read existing data
        existing = load_json(contest_dir / "contest_data.json")
        title = existing.get("title", "")
        old_awards = existing.get("awards", {})

        srk_path = find_srk_by_path(rel, path_index)

        if srk_path is None:
            # Try title-based fallback
            # (keep the previously unmatched ones as-is)
            print(f"  NOT FOUND: {rel} (title: {title[:60]})")
            not_found += 1
            continue

        srk_rel = srk_path.relative_to(SRK_BASE)

        # Check if this SRK actually has count-based medals
        srk_data = load_json(srk_path)
        has_count_series = False
        for s in srk_data.get("series", []):
            rule = s.get("rule", {})
            if rule.get("preset") == "ICPC" and "count" in rule.get("options", {}):
                has_count_series = True
                break

        if not has_count_series:
            print(f"  SKIP (no count series): {rel}")
            skipped += 1
            continue

        # Regenerate
        try:
            awards, official, total = regenerate_contest(contest_dir, srk_path)
            old_g, old_s, old_b = old_awards.get("gold", 0), old_awards.get("silver", 0), old_awards.get("bronze", 0)
            new_g, new_s, new_b = awards["gold"], awards["silver"], awards["bronze"]
            if old_g != new_g or old_s != new_s or old_b != new_b:
                status = "FIXED"
                print(f"  {status}: {rel}")
                print(f"    Awards: G{old_g}/{old_s}/{old_b} → G{new_g}/{new_s}/{new_b} ({total} teams, {official} official)")
            else:
                status = "OK"
                print(f"  {status}: {rel}  G{new_g}/{new_s}/{new_b}")
            if status == "FIXED":
                fixed += 1
            else:
                ok += 1
        except Exception as e:
            print(f"  FAILED: {rel} - {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Results: {fixed} fixed, {ok} OK, {not_found} not found, {skipped} skipped")
    print(f"Total: {len(contest_dirs)}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts"))
    main()
