"""Batch convert SRK files from srk-collection to XIPF format.

Covers 2024-2025 ICPC/CCPC invitationals and provincial contests.
Data source: https://github.com/algoux/srk-collection
"""

import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from srk_to_xipf import convert_srk

ROOT = Path(__file__).resolve().parent.parent
CONTESTS_DIR = ROOT / "contests"
SRK_BASE = ROOT / "srk-collection-master" / "official"

# Province code → Chinese name
PROVINCE_NAMES = {
    "ah": "安徽", "bj": "北京", "cq": "重庆", "fj": "福建", "gd": "广东",
    "gx": "广西", "gz": "贵州", "ha": "河南", "hb": "湖北", "he": "河北",
    "hl": "黑龙江", "hn": "湖南", "jl": "吉林", "js": "江苏", "jx": "江西",
    "ln": "辽宁", "nm": "内蒙古", "northeast": "东北", "sc": "四川",
    "sd": "山东", "sh": "上海", "sn": "陕西", "xj": "新疆", "zj": "浙江",
}

# City mapping for invitationals
CITY_NAMES = {
    "wuhan": "武汉", "xi_an": "西安", "kunming": "昆明", "nanchang": "南昌",
    "fuzhou": "福州", "jinan": "济南", "changchun": "长春", "fujian": "福州",
    "zhengzhou": "郑州", "shenzhen": "深圳", "guangdong-preliminary": "广东",
}


def convert_one(srk_path: Path, contest_dir: Path) -> bool:
    """Convert one SRK file and write to contest_dir."""
    try:
        contest_data, roster = convert_srk(
            srk_path,
            year=None,  # auto-detect from SRK
        )
        year = contest_data["year"]
        contest_dir = CONTESTS_DIR / contest_dir
        contest_dir.mkdir(parents=True, exist_ok=True)

        with open(contest_dir / "contest_data.json", "w", encoding="utf-8") as f:
            json.dump(contest_data, f, ensure_ascii=False, indent=2)
        with open(contest_dir / "roster.json", "w", encoding="utf-8") as f:
            json.dump(roster, f, ensure_ascii=False, indent=2)

        teams = contest_data["teams"]
        awards = contest_data["awards"]
        rel = contest_dir.resolve().relative_to(ROOT.resolve())
        print(f"  {rel}")
        print(f"    {len(teams)} teams ({sum(1 for t in teams if t['official'])} official), "
              f"G{awards['gold']}/S{awards['silver']}/B{awards['bronze']}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("Batch converting SRK → XIPF format")
    print("Source: https://github.com/algoux/srk-collection")
    print()

    conversions = []

    # === ICPC Invitationals ===
    # 2024
    conversions.append(("ICPC 2024 武汉邀请赛", SRK_BASE / "icpc/icpc2024/icpc2024invitational-wuhan.srk.json", "2024/icpc/武汉_invitational"))
    conversions.append(("ICPC 2024 昆明邀请赛", SRK_BASE / "icpc/icpc2024/icpc2024invitational-kunming.srk.json", "2024/icpc/昆明_invitational"))
    # 2025
    conversions.append(("ICPC 2025 武汉邀请赛", SRK_BASE / "icpc/icpc2025/icpc2025invitational-wuhan.srk.json", "2025/icpc/武汉_invitational"))
    conversions.append(("ICPC 2025 南昌邀请赛", SRK_BASE / "icpc/icpc2025/icpc2025invitational-nanchang.srk.json", "2025/icpc/南昌_invitational"))

    # === CCPC Invitationals ===
    # 2024
    conversions.append(("CCPC 2024 福州邀请赛", SRK_BASE / "ccpc/ccpc2024/ccpc2024invitational-fuzhou.srk.json", "2024/ccpc/福州_invitational"))
    conversions.append(("CCPC 2024 济南邀请赛", SRK_BASE / "ccpc/ccpc2024/ccpc2024invitational-jinan.srk.json", "2024/ccpc/济南_invitational"))
    # 2025
    conversions.append(("CCPC 2025 福州邀请赛", SRK_BASE / "ccpc/ccpc2025/ccpc2025invitational-fujian.srk.json", "2025/ccpc/福州_invitational"))
    conversions.append(("CCPC 2025 广东邀请赛预赛", SRK_BASE / "ccpc/ccpc2025/ccpc2025invitational-guangdong-preliminary.srk.json", "2025/ccpc/广东_invitational"))
    conversions.append(("CCPC 2025 南昌邀请赛", SRK_BASE / "ccpc/ccpc2025/ccpc2025invitational-nanchang.srk.json", "2025/ccpc/南昌_invitational"))
    conversions.append(("CCPC 2025 郑州邀请赛", SRK_BASE / "ccpc/ccpc2025/ccpc2025invitational-zhengzhou.srk.json", "2025/ccpc/郑州_invitational"))

    # === Provincial Contests ===
    # Beijing
    conversions.append(("北京 2024", SRK_BASE / "provincial/bj/bjcpc2024.srk.json", "2024/ccpc/北京_provincial"))
    conversions.append(("北京 2025", SRK_BASE / "provincial/bj/bjcpc2025.srk.json", "2025/ccpc/北京_provincial"))
    # Chongqing
    conversions.append(("重庆 2025", SRK_BASE / "provincial/cq/cqcpc13th.srk.json", "2025/ccpc/重庆_provincial"))
    # Guangdong (standalone provincial, NOT the invitational+provincial combined)
    conversions.append(("广东 2024", SRK_BASE / "provincial/gd/gdcpc21st.srk.json", "2024/ccpc/广东_provincial"))
    conversions.append(("广东 2025", SRK_BASE / "provincial/gd/gdcpc22nd.srk.json", "2025/ccpc/广东_provincial"))
    # Guangxi
    conversions.append(("广西 2024", SRK_BASE / "provincial/gx/gxcpc7th.srk.json", "2024/ccpc/广西_provincial"))
    # Henan (CCPC)
    conversions.append(("河南 CCPC 2024", SRK_BASE / "provincial/ha/haccpc6th.srk.json", "2024/ccpc/河南_provincial"))
    conversions.append(("河南 CCPC 2025", SRK_BASE / "provincial/ha/haccpc7th.srk.json", "2025/ccpc/河南_provincial"))
    # Henan (ICPC)
    conversions.append(("河南 ICPC 2024", SRK_BASE / "provincial/ha/haicpc15th.srk.json", "2024/icpc/河南_provincial"))
    conversions.append(("河南 ICPC 2025", SRK_BASE / "provincial/ha/haicpc16th.srk.json", "2025/icpc/河南_provincial"))
    # Hubei
    conversions.append(("湖北 2024", SRK_BASE / "provincial/hb/hbcpc6th.srk.json", "2024/ccpc/湖北_provincial"))
    # Hebei
    conversions.append(("河北 2024", SRK_BASE / "provincial/he/hecpc8th.srk.json", "2024/ccpc/河北_provincial"))
    conversions.append(("河北 2025", SRK_BASE / "provincial/he/hecpc9th.srk.json", "2025/ccpc/河北_provincial"))
    # Heilongjiang
    conversions.append(("黑龙江 2025", SRK_BASE / "provincial/hl/hlcpc20th.srk.json", "2025/ccpc/黑龙江_provincial"))
    # Hunan
    conversions.append(("湖南 2024", SRK_BASE / "provincial/hn/hncpc20th.srk.json", "2024/ccpc/湖南_provincial"))
    # Jiangsu
    conversions.append(("江苏 2025", SRK_BASE / "provincial/js/jscpc10th.srk.json", "2025/ccpc/江苏_provincial"))
    # Liaoning
    conversions.append(("辽宁 2024", SRK_BASE / "provincial/ln/lncpc5th.srk.json", "2024/ccpc/辽宁_provincial"))
    # Inner Mongolia
    conversions.append(("内蒙古 2024", SRK_BASE / "provincial/nm/nmcpc17th.srk.json", "2024/ccpc/内蒙古_provincial"))
    conversions.append(("内蒙古 2025", SRK_BASE / "provincial/nm/nmcpc18th.srk.json", "2025/ccpc/内蒙古_provincial"))
    # Sichuan
    conversions.append(("四川 2024", SRK_BASE / "provincial/sc/sccpc16th.srk.json", "2024/ccpc/四川_provincial"))
    conversions.append(("四川 2025", SRK_BASE / "provincial/sc/sccpc17th.srk.json", "2025/ccpc/四川_provincial"))
    # Shandong
    conversions.append(("山东 2024", SRK_BASE / "provincial/sd/sdcpc14th.srk.json", "2024/ccpc/山东_provincial"))
    conversions.append(("山东 2025", SRK_BASE / "provincial/sd/sdcpc15th.srk.json", "2025/ccpc/山东_provincial"))
    # Shanghai
    conversions.append(("上海 2024", SRK_BASE / "provincial/sh/shcpc2024.srk.json", "2024/ccpc/上海_provincial"))
    conversions.append(("上海 2025", SRK_BASE / "provincial/sh/shcpc2025.srk.json", "2025/ccpc/上海_provincial"))

    success = 0
    failed = 0
    skipped = 0

    for label, srk_path, rel_dir in conversions:
        print(f"[{label}]")
        print(f"  SRK: {srk_path}")
        if not srk_path.exists():
            print(f"  SKIP: file not found")
            skipped += 1
            continue

        contest_dir = CONTESTS_DIR / rel_dir
        if (contest_dir / "contest_data.json").exists() or (contest_dir / "rank.srk.json").exists():
            print(f"  SKIP: already exists")
            skipped += 1
            continue

        if convert_one(srk_path, Path(rel_dir)):
            success += 1
        else:
            failed += 1

    print()
    print(f"Done: {success} converted, {failed} failed, {skipped} skipped")


if __name__ == "__main__":
    main()
