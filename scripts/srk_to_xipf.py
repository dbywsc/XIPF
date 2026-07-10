"""Convert SRK format (.srk.json) to XIPF format (contest_data.json + roster.json).

Usage:
    python scripts/srk_to_xipf.py path/to/contest.srk.json \
        --year=2025 --type=ccpc --slug=南昌_invitational

Supports co-branded events (邀请赛+省赛): specify --series=invitational or
--series=provincial to extract the corresponding sub-contest with filtered
teams and correct medal counts from the SRK's multi-series structure.

The SRK format is the standard ranklist format from:
https://github.com/algoux/srk-collection
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTESTS_DIR = ROOT / "contests"

# Series title → tier mapping for co-branded events
SERIES_TITLE_HINTS = {
    "invitational": ["邀请"],
    "provincial": ["省", "东北", "区内", "省内", "本科", "专科", "高职"],
}


def load_srk(filepath: Path) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time_value(val) -> int:
    """Parse SRK time value [N, 's'|'min'|'h'] or integer."""
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, list) and len(val) == 2:
        num, unit = val[0], val[1]
        if isinstance(num, list):
            num = num[0] if len(num) == 2 else num[0]
        num = int(num)
        if unit == "h":
            return num * 3600
        elif unit == "min":
            return num * 60
        return num
    return 0


def _find_medal_series(series_data: list, target_tier: str = "") -> dict | None:
    """Find the best matching ICPC medal series for the target tier.

    For co-branded events: match by series title hints (e.g. 邀请赛 → invitational).
    For single events: return the first ICPC-preset series.
    """
    # First pass: collect all ICPC-preset medal series
    icpc_series = []
    for s in series_data:
        rule = s.get("rule", {})
        if rule.get("preset") == "ICPC":
            icpc_series.append(s)

    if not icpc_series:
        return None

    if len(icpc_series) == 1:
        return icpc_series[0]

    # Multiple series: try to match by target_tier
    hints = SERIES_TITLE_HINTS.get(target_tier, [])
    for s in icpc_series:
        title = s.get("title", "")
        for hint in hints:
            if hint in title:
                return s

    # No match: return the first unnamed/generic series (title == "#" or no markers)
    for s in icpc_series:
        title = s.get("title", "")
        if title in ("#", ""):
            return s

    return icpc_series[0]


def _get_series_marker(series: dict) -> str | None:
    """Get the filter.byMarker value from a series, or None."""
    return (series.get("rule", {}).get("options", {}).get("filter", {}).get("byMarker") or None)


def _get_row_markers(user: dict) -> set:
    """Get all marker IDs from a row's user data."""
    markers = set()
    raw = user.get("markers")
    if isinstance(raw, (list, tuple)):
        markers.update(str(m) for m in raw)
    single = user.get("marker")
    if single:
        markers.add(str(single))
    return markers


def determine_medals(teams, series_data, target_tier: str = ""):
    """Assign gold/silver/bronze medals to official teams based on series rules.

    If target_tier is specified, uses the matching medal series and filters
    teams by the series' marker. Otherwise uses the first/default ICPC series.
    """
    target_series = _find_medal_series(series_data, target_tier)

    # Filter teams by the target series' marker
    marker = _get_series_marker(target_series) if target_series else None
    if marker:
        eligible_teams = [t for t in teams if t["official"] and marker in t.get("_markers", set())]
    else:
        eligible_teams = [t for t in teams if t["official"]]

    official_sorted = sorted(eligible_teams, key=lambda t: (-t["solved"], t["penalty"]))

    if not target_series:
        # Default: 10%/20%/30%
        n = len(official_sorted)
        gold_count = max(1, (n * 1 + 9) // 10)
        silver_count = max(1, (n * 2 + 9) // 10)
        bronze_count = max(1, (n * 3 + 9) // 10)
    else:
        options = target_series.get("rule", {}).get("options", {})
        if "count" in options:
            counts = options["count"].get("value", [0, 0, 0])
            gold_count = counts[0]
            silver_count = counts[1]
            bronze_count = counts[2]
        elif "ratio" in options:
            ratios = options["ratio"].get("value", [0.1, 0.2, 0.3])
            n = len(official_sorted)
            gold_count = max(1, int(n * ratios[0] + 0.999999))
            silver_count = max(1, int(n * ratios[1] + 0.999999))
            bronze_count = max(1, int(n * ratios[2] + 0.999999))
        else:
            n = len(official_sorted)
            gold_count = max(1, (n * 1 + 9) // 10)
            silver_count = max(1, (n * 2 + 9) // 10)
            bronze_count = max(1, (n * 3 + 9) // 10)

    if gold_count == 0 and silver_count == 0 and bronze_count == 0:
        n = len(official_sorted)
        gold_count = max(1, (n * 1 + 9) // 10)
        silver_count = max(1, (n * 2 + 9) // 10)
        bronze_count = max(1, (n * 3 + 9) // 10)

    for i, team in enumerate(official_sorted):
        if i < gold_count:
            team["medal"] = "gold"
        elif i < gold_count + silver_count:
            team["medal"] = "silver"
        elif i < gold_count + silver_count + bronze_count:
            team["medal"] = "bronze"

    return gold_count, silver_count, bronze_count


def _strip_series_title(title: str) -> str:
    """Series titles in SRK often carry a trailing '#'. Strip it for display."""
    return title.rstrip("#").strip()


def determine_division_medals(teams, series_data):
    """Co-branded 'combined' events: assign per-division medals.

    Every ICPC-preset series that filters by a marker and defines medal counts
    becomes a division (e.g. 邀请赛 / 区内 / 专科 / 中小学). Each team records the
    medal(s) it earned in `division_medals`, and its top-level `medal` is set to
    the best medal it won across all divisions (used for org/contestant stats).

    Returns aggregate award counts summed across all divisions.
    """
    medal_order = {"gold": 3, "silver": 2, "bronze": 1, "": 0}
    total = {"gold": 0, "silver": 0, "bronze": 0}

    for s in series_data:
        rule = s.get("rule", {})
        if rule.get("preset") != "ICPC":
            continue
        options = rule.get("options", {})
        marker = _get_series_marker(s)
        counts = options.get("count", {}).get("value")
        if not marker or not counts:
            continue
        div_name = _strip_series_title(s.get("title", "")) or marker

        eligible = [t for t in teams if t["official"] and marker in t.get("_markers", set())]
        eligible.sort(key=lambda t: (-t["solved"], t["penalty"]))

        gold, silver, bronze = (counts + [0, 0, 0])[:3]
        total["gold"] += gold
        total["silver"] += silver
        total["bronze"] += bronze

        for i, team in enumerate(eligible):
            if i < gold:
                m = "gold"
            elif i < gold + silver:
                m = "silver"
            elif i < gold + silver + bronze:
                m = "bronze"
            else:
                continue
            team.setdefault("division_medals", {})[div_name] = m
            if medal_order[m] > medal_order[team["medal"]]:
                team["medal"] = m

    return total["gold"], total["silver"], total["bronze"]


def normalize_text(val) -> str:
    """SRK fields can be plain strings or localized dicts {'zh-CN': '...', 'fallback': '...'}."""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return val.get("zh-CN") or val.get("fallback") or val.get("en", "") or ""
    return str(val)


def extract_members(row_user: dict, max_members: int = 3) -> list:
    """Extract contestant members from a row, filtering out coaches."""
    team_members = row_user.get("teamMembers", [])
    contestants = []
    for m in team_members:
        if not isinstance(m, dict):
            continue
        role = m.get("role", "")
        if role == "coach":
            continue
        name = normalize_text(m.get("name", ""))
        if name:
            contestants.append({"name": name, "gender": ""})
        if len(contestants) >= max_members:
            break
    return contestants


def convert_srk(filepath: Path, year: int, contest_date: str = "",
                contest_title: str = "", target_tier: str = "") -> tuple[dict, dict]:
    """Convert an SRK JSON file to XIPF format.

    For co-branded events, target_tier should be 'invitational' or 'provincial'
    to select the correct medal series and filter teams by marker.

    Returns (contest_data, roster).
    """
    data = load_srk(filepath)

    # Contest info
    contest = data.get("contest", {})
    if not contest_title:
        title_data = contest.get("title", {})
        contest_title = title_data.get("zh-CN") or title_data.get("fallback", "")

    if not contest_date:
        start_at = contest.get("startAt", "")
        contest_date = start_at[:10]

    # Problems
    problems = data.get("problems", [])
    xipf_problems = []
    for p in problems:
        stats = p.get("statistics", {})
        xipf_problems.append({
            "alias": p.get("alias", ""),
            "accepted": stats.get("accepted", 0),
            "submitted": stats.get("submitted", 0),
        })

    # Determine which series to use
    series_data = data.get("series", [])
    target_series = _find_medal_series(series_data, target_tier)
    marker = _get_series_marker(target_series) if target_series else None

    # Team filtering: only filter for provincial sub-contests.
    # Invitational includes ALL teams (the full competition field).
    filter_marker = marker if target_tier == 'provincial' else None

    # Teams from rows
    rows = data.get("rows", [])
    teams = []
    seen_ids = set()

    for idx, row in enumerate(rows):
        user = row.get("user", {})
        score = row.get("score", {})
        statuses = row.get("statuses", [])

        team_name = normalize_text(user.get("name", ""))
        team_id = user.get("id", f"team_{idx}")
        organization = normalize_text(user.get("organization", ""))
        official = user.get("official", False)
        markers = _get_row_markers(user)

        # For provincial sub-contests: skip teams that don't carry the provincial marker
        if filter_marker and filter_marker not in markers:
            continue

        solved = int(score.get("value", 0))
        penalty_time = score.get("time", [0, "s"])
        penalty = parse_time_value(penalty_time)

        members = extract_members(user)

        # Problem statuses
        ps = []
        for j, status in enumerate(statuses):
            if not status:
                continue
            alias = problems[j]["alias"] if j < len(problems) else f"P{j}"
            stime = status.get("time", [0, "s"])
            ps.append({
                "alias": alias,
                "result": status.get("result", ""),
                "time": parse_time_value(stime),
                "tries": status.get("tries", 0),
            })

        # Ensure unique team ID
        tid = team_id
        counter = 1
        while tid in seen_ids:
            tid = f"{team_id}_{counter}"
            counter += 1
        seen_ids.add(tid)

        teams.append({
            "id": tid,
            "name": team_name,
            "organization": organization,
            "official": official,
            "rank": 0,
            "org_rank": 0,
            "solved": solved,
            "penalty": penalty,
            "problems": ps,
            "medal": "",
            "members": members,
            "girl_team": False,
            "champion": "",
            "division_medals": {},
            "_markers": markers,  # used by determine_medals for marker filtering
        })

    # Assign global ranks (all teams sorted by ICPC rules)
    all_sorted = sorted(teams, key=lambda t: (-t["solved"], t["penalty"]))
    for rank, team in enumerate(all_sorted, 1):
        team["rank"] = rank

    # Assign medals. Combined co-branded events keep every division's awards;
    # single/split events use the matching series only.
    if target_tier == "combined":
        gold_count, silver_count, bronze_count = determine_division_medals(teams, series_data)
    else:
        gold_count, silver_count, bronze_count = determine_medals(teams, series_data, target_tier)

    # Compute org ranks
    teams_by_org = {}
    for t in teams:
        org = t["organization"]
        if org not in teams_by_org:
            teams_by_org[org] = []
        teams_by_org[org].append(t)

    for org, org_teams in teams_by_org.items():
        official_in_org = [t for t in org_teams if t["official"]]
        org_sorted = sorted(official_in_org, key=lambda t: (-t["solved"], t["penalty"]))
        for rank, team in enumerate(org_sorted, 1):
            team["org_rank"] = rank

    # Compute champion/亚军/季军: best official team per organization
    org_best = {}
    org_best_team = {}
    for t in teams:
        if not t["official"] or not t["organization"]:
            continue
        org = t["organization"]
        if org not in org_best or t["rank"] < org_best[org]:
            org_best[org] = t["rank"]
            org_best_team[org] = t["id"]

    sorted_orgs = sorted(org_best.items(), key=lambda x: x[1])
    champion_labels = {1: "冠军", 2: "亚军", 3: "季军"}
    for i, (org, _) in enumerate(sorted_orgs[:3]):
        if i < 3:
            best_tid = org_best_team[org]
            for t in teams:
                if t["id"] == best_tid:
                    t["champion"] = champion_labels.get(i + 1, "")

    # Build roster
    roster = {"teams": {}}
    for t in teams:
        roster["teams"][t["id"]] = {
            "members": t["members"],
            "organization_override": None,
        }

    # Clean internal fields before serializing
    for t in teams:
        t.pop("_markers", None)

    # Build contest_data
    contest_data = {
        "title": contest_title,
        "year": year,
        "date": contest_date,
        "teams": teams,
        "problems": xipf_problems,
        "awards": {
            "gold": gold_count,
            "silver": silver_count,
            "bronze": bronze_count,
        },
    }

    return contest_data, roster


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} path/to/contest.srk.json [options]")
        print()
        print("Options:")
        print("  --year=YYYY      Year of the contest (default: extracted from date)")
        print("  --date=YYYY-MM-DD  Contest date (default: extracted from SRK)")
        print("  --title=TITLE    Contest title (default: extracted from SRK)")
        print("  --type=ccpc|icpc  Contest type for directory placement")
        print("  --slug=NAME      Output directory name (e.g. 武汉_invitational)")
        print("  --series=TYPE    Target series: invitational | provincial (for co-branded events)")
        print("  --outdir=PATH    Direct output dir path (overrides --type --slug)")
        print()
        print("SRK format source: https://github.com/algoux/srk-collection")
        sys.exit(1)

    filepath = Path(sys.argv[1]).resolve()
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    year = None
    contest_date = ""
    contest_title = ""
    contest_type = ""
    slug = ""
    outdir = ""
    target_tier = ""

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--year="):
            year = int(arg.split("=", 1)[1])
        elif arg.startswith("--date="):
            contest_date = arg.split("=", 1)[1]
        elif arg.startswith("--title="):
            contest_title = arg.split("=", 1)[1]
        elif arg.startswith("--type="):
            contest_type = arg.split("=", 1)[1]
        elif arg.startswith("--slug="):
            slug = arg.split("=", 1)[1]
        elif arg.startswith("--series="):
            target_tier = arg.split("=", 1)[1]
        elif arg.startswith("--outdir="):
            outdir = arg.split("=", 1)[1]
        i += 1

    # Auto-detect target_tier from slug if not specified
    if not target_tier:
        if slug.endswith("_invitational"):
            target_tier = "invitational"
        elif slug.endswith("_provincial"):
            target_tier = "provincial"

    print(f"Converting: {filepath.name}" + (f" [series: {target_tier}]" if target_tier else ""))

    contest_data, roster = convert_srk(filepath, year or 2024, contest_date, contest_title, target_tier)

    if not year:
        year = contest_data["year"]

    if not outdir:
        if not slug:
            print("Error: --slug or --outdir required")
            sys.exit(1)
        contest_dir = CONTESTS_DIR / str(year) / contest_type / slug
    else:
        contest_dir = Path(outdir)

    contest_dir.mkdir(parents=True, exist_ok=True)

    with open(contest_dir / "contest_data.json", "w", encoding="utf-8") as f:
        json.dump(contest_data, f, ensure_ascii=False, indent=2)
    with open(contest_dir / "roster.json", "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=2)

    rel = contest_dir.resolve().relative_to(ROOT.resolve())
    teams = contest_data["teams"]
    awards = contest_data["awards"]
    print(f"  -> {rel}")
    print(f"     {len(teams)} teams ({sum(1 for t in teams if t['official'])} official), "
          f"G{awards['gold']}/S{awards['silver']}/B{awards['bronze']}")


if __name__ == "__main__":
    main()
