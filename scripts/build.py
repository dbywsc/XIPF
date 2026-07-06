"""Main build pipeline: scan → parse → compute → normalize → output."""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

from models import (
    Contest, Team, TeamMember, Problem, ProblemStatus,
    Contestant, ContestRecord, Organization,
)

try:
    from xcpc_rating.engines.incremental import UNRATED_CONTESTS
except ImportError:
    UNRATED_CONTESTS = {}


ROOT = Path(__file__).resolve().parent.parent
CONTESTS_DIR = ROOT / "contests"
DIST_DIR = ROOT / "dist"
ORGS_FILE = ROOT / "organizations.json"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_time(seconds: int) -> str:
    """Format seconds to HH:MM:SS."""
    h, m = divmod(seconds, 3600)
    m, s = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}"


def parse_contest_data(filepath: Path) -> Contest:
    """Parse a contest_data.json file into a Contest object."""
    data = load_json(filepath)

    title = data.get("title", "")
    date = data.get("date", "")
    year = data.get("year", 2026)

    problems = [
        Problem(alias=p["alias"], accepted=p.get("accepted", 0), submitted=p.get("submitted", 0))
        for p in data.get("problems", [])
    ]

    teams = []
    for t in data.get("teams", []):
        statuses = [
            ProblemStatus(
                alias=p["alias"],
                result=p.get("result") or "",
                time=p.get("time", 0),
                tries=p.get("tries", 0),
            )
            for p in t.get("problems", [])
        ]
        members = [
            TeamMember(name=m.get("name", ""), gender=m.get("gender", ""))
            for m in t.get("members", [])
        ]
        team = Team(
            id=t["id"],
            name=t.get("name", ""),
            organization=t.get("organization", ""),
            official=t.get("official", True),
            solved=t.get("solved", 0),
            penalty=t.get("penalty", 0),
            problems=statuses,
            members=members,
            rank=t.get("rank", 0),
            medal=t.get("medal", ""),
            girl_team=t.get("girl_team", False),
            champion=t.get("champion", ""),
            division_medals=t.get("division_medals", {}),
        )
        teams.append(team)

    # Sort teams by ICPC rules and assign ranks
    official_teams = [t for t in teams if t.official]

    # Global rank: all teams sorted together (always recompute)
    all_sorted = sorted(teams, key=lambda t: (-t.solved, t.penalty))
    for rank, team in enumerate(all_sorted, 1):
        team.rank = rank

    # Official rank: official teams only
    official_sorted_cd = sorted(official_teams, key=lambda t: (-t.solved, t.penalty))
    for i, team in enumerate(official_sorted_cd):
        team.official_rank = i + 1

    # Assign medals: use pre-set if available, otherwise calculate from team count
    pre_set_medals = any(t.medal for t in teams if hasattr(t, 'medal') and t.medal)
    official_count = len(official_teams)

    if pre_set_medals:
        # Medals came from imported data — count them
        gold_count = sum(1 for t in official_teams if t.medal == "gold")
        silver_count = sum(1 for t in official_teams if t.medal == "silver")
        bronze_count = sum(1 for t in official_teams if t.medal == "bronze")
    else:
        gold_count = max(1, (official_count * 1 + 9) // 10)
        silver_count = max(1, (official_count * 2 + 9) // 10)
        bronze_count = max(1, (official_count * 3 + 9) // 10)
        official_sorted = sorted(official_teams, key=lambda t: (-t.solved, t.penalty))
        for i, team in enumerate(official_sorted):
            if i < gold_count:
                team.medal = "gold"
            elif i < gold_count + silver_count:
                team.medal = "silver"
            elif i < gold_count + silver_count + bronze_count:
                team.medal = "bronze"

    contest_id = filepath.parent.name
    category_dir = filepath.parent.parent.name
    year_dir = filepath.parent.parent.parent.name
    if year_dir.isdigit():
        # 3-level: contests/2026/icpc/南昌_invitational → 2026-icpc-南昌_invitational
        contest_id = f"{year_dir}-{category_dir}-{contest_id}"
    elif category_dir.isdigit():
        # 2-level: contests/2026/北京 → 2026-北京
        contest_id = f"{category_dir}-{contest_id}"

    return Contest(
        id=contest_id,
        title=title,
        date=date or f"{year}-01-01",
        duration=0,
        frozen_duration=0,
        problems=problems,
        teams=teams,
        gold_count=gold_count,
        silver_count=silver_count,
        bronze_count=bronze_count,
    )


def parse_srk(filepath: Path) -> Contest:
    """Parse an SRK format JSON file into a Contest object."""
    data = load_json(filepath)

    contest_data = data["contest"]
    title = contest_data["title"].get("zh-CN") or contest_data["title"].get("fallback", "")
    date = contest_data["startAt"][:10]

    # Parse duration
    duration_val = contest_data["duration"]
    if isinstance(duration_val, list):
        duration_sec = duration_val[0]
        if duration_val[1] == "h":
            duration_sec *= 3600
        elif duration_val[1] == "min":
            duration_sec *= 60
    else:
        duration_sec = duration_val

    frozen = contest_data.get("frozenDuration", [0, "h"])
    if isinstance(frozen, list):
        frozen_sec = frozen[0]
        if frozen[1] == "h":
            frozen_sec *= 3600
        elif frozen[1] == "min":
            frozen_sec *= 60
    else:
        frozen_sec = frozen

    # Parse problems
    problems = [
        Problem(alias=p["alias"], accepted=p["statistics"]["accepted"], submitted=p["statistics"]["submitted"])
        for p in data.get("problems", [])
    ]

    # Parse award rules
    award_counts = [36, 72, 108]  # defaults
    if "series" in data:
        for series in data["series"]:
            if series["title"] == "#" and "rule" in series:
                rule = series["rule"]
                if rule.get("preset") == "ICPC":
                    award_counts = rule.get("options", {}).get("count", {}).get("value", [36, 72, 108])
                break

    # Parse teams
    teams = []
    for i, row in enumerate(data.get("rows", [])):
        user = row["user"]
        score = row.get("score", {})
        solved = score.get("value", 0)
        penalty = score.get("time", [0, "s"])[0] if isinstance(score.get("time"), list) else 0

        statuses = []
        problems_list = data.get("problems", [])
        for j, status in enumerate(row.get("statuses", [])):
            if status:
                alias = problems_list[j]["alias"] if j < len(problems_list) else f"P{j}"
                status_time = status.get("time", [0, "s"])
                time_sec = status_time[0] if isinstance(status_time, list) else 0
                statuses.append(ProblemStatus(
                    alias=alias,
                    result=status.get("result", ""),
                    time=time_sec,
                    tries=status.get("tries", 0),
                ))

        team = Team(
            id=user["id"],
            name=user.get("name", ""),
            organization=user.get("organization", ""),
            official=user.get("official", False),
            solved=solved,
            penalty=penalty,
            problems=statuses,
        )
        teams.append(team)

    # Sort teams by ICPC rules (solved desc, penalty asc), then assign ranks
    official_teams = [t for t in teams if t.official]

    # Global rank: all teams sorted together
    all_sorted = sorted(teams, key=lambda t: (-t.solved, t.penalty))
    for rank, team in enumerate(all_sorted, 1):
        team.rank = rank

    # Official rank + awards: SRK count values are absolute (not cumulative)
    # [36, 72, 108] means gold=36, silver=72, bronze=108
    official_sorted = sorted(official_teams, key=lambda t: (-t.solved, t.penalty))
    gold_count = award_counts[0]
    silver_count = award_counts[1]
    bronze_count = min(award_counts[2], len(official_sorted) - gold_count - silver_count)
    for i, team in enumerate(official_sorted):
        team.official_rank = i + 1
        if i < gold_count:
            team.medal = "gold"
        elif i < gold_count + silver_count:
            team.medal = "silver"
        elif i < gold_count + silver_count + bronze_count:
            team.medal = "bronze"

    # Determine contest ID from directory name
    contest_id = filepath.parent.name
    category_dir = filepath.parent.parent.name
    year_dir = filepath.parent.parent.parent.name
    if year_dir.isdigit():
        # 3-level: contests/2026/icpc/南昌_invitational
        contest_id = f"{year_dir}-{category_dir}-{contest_id}"
    elif category_dir.isdigit():
        # 2-level: contests/2026/北京
        contest_id = f"{category_dir}-{contest_id}"

    return Contest(
        id=contest_id,
        title=title,
        date=date,
        duration=duration_sec,
        frozen_duration=frozen_sec,
        problems=problems,
        teams=teams,
        gold_count=gold_count,
        silver_count=silver_count,
        bronze_count=bronze_count,
    )


def load_roster(filepath: Path, contest: Contest):
    """Load roster.json and attach member data to teams.
    Only adds members if the team doesn't already have them."""
    roster = load_json(filepath)
    teams_data = roster.get("teams", {})

    for team in contest.teams:
        if team.id in teams_data:
            td = teams_data[team.id]
            # Only load from roster if team has no members yet
            if not team.members:
                for m in td.get("members", []):
                    team.members.append(TeamMember(
                        name=m.get("name", ""),
                        gender=m.get("gender", ""),
                    ))
            if td.get("organization_override"):
                team.organization = td["organization_override"]


def load_organizations():
    """Load organizations.json into a lookup dict by canonical name and aliases.
    Returns (orgs_dict, name_to_id_dict). Both empty if file doesn't exist."""
    if not ORGS_FILE.exists():
        return {}, {}

    orgs: dict[str, Organization] = {}
    name_to_id: dict[str, str] = {}
    data = load_json(ORGS_FILE)

    for org_data in data.get("organizations", []):
        org = Organization(
            id=org_data["id"],
            canonical=org_data["canonical"],
            aliases=org_data.get("aliases", []),
            province=org_data.get("province", ""),
            city=org_data.get("city", ""),
        )
        orgs[org.id] = org
        name_to_id[org.canonical] = org.id
        for alias in org.aliases:
            name_to_id[alias] = org.id

    return orgs, name_to_id


def load_org_name_map() -> dict:
    """Load English→Chinese organization name mapping."""
    map_path = ROOT / "org_names_map.json"
    if map_path.exists():
        with open(map_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


_ORG_NAME_MAP = None


def translate_org_name(name: str) -> str:
    """Translate an English org name to Chinese, and normalize parentheses."""
    global _ORG_NAME_MAP
    if _ORG_NAME_MAP is None:
        _ORG_NAME_MAP = load_org_name_map()
    # Strip whitespace first
    name = name.strip()
    # Direct mapping
    mapped = _ORG_NAME_MAP.get(name, name)
    # Normalize half-width parens → full-width parens for Chinese text
    if any('\u4e00' <= c <= '\u9fff' for c in mapped):
        mapped = mapped.replace('(', '（').replace(')', '）')
    return mapped.strip()


def resolve_organizations(contest: Contest, orgs: dict, name_to_id: dict[str, str]) -> set:
    """Match team organizations to canonical orgs. Returns set of unmatched org names."""
    unmatched = set()
    for team in contest.teams:
        org_name = translate_org_name(team.organization)
        team.organization = org_name
        if org_name in name_to_id:
            pass  # will be resolved to canonical later
        else:
            unmatched.add(org_name)
    return unmatched


def generate_contestant_id(name: str, contest: Contest) -> str:
    """Generate a stable ID for a contestant."""
    # Use pinyin-like slug: simple transliteration for now
    # In production, use pypinyin for proper Chinese → pinyin conversion
    import re
    # Simple slug: just use name + contest for uniqueness
    # Real merging happens in the merge step
    slug = re.sub(r'[^a-zA-Z0-9一-鿿]', '', name)
    return slug


def sanitize_id(name: str) -> str:
    """Sanitize org name for use as a file-safe ID."""
    return name.lower().replace(" ", "-").replace("/", "-").replace("\\", "-").replace(":", "-")


def classify_tier(contest_id: str, title: str, slug: str = "") -> str:
    """Classify contest into: final / regional / invitational / provincial / preliminary."""
    cid = contest_id.lower()
    t = title.lower()

    # Finals: CCPC Final or ICPC EC Final
    if 'ecfinal' in cid or cid.endswith('final_regional'):
        return 'final'

    # For provincial-category directories, check provincial BEFORE invitational,
    # even for co-branded events (邀请赛+省赛). The corresponding invitational entry
    # lives under the icpc/ccpc directory and will be classified as invitational.
    if 'provincial' in cid or 'provincial' in slug:
        # Co-branded: title contains "邀请赛" → classify as invitational
        if '邀请赛' in t:
            return 'invitational'
        return 'provincial'

    # Invitationals: explicit invitational OR special restricted fields
    if 'invitational' in cid or 'srni' in cid or '邀请赛' in t:
        return 'invitational'
    if 'ladies' in cid or '女生' in t or 'hv' in cid or '高职' in t:
        return 'invitational'

    # Provincials: explicit provincial tag OR title contains province-level contest pattern
    if '省赛' in t:
        return 'provincial'
    if '省' in t and ('大学生' in t or '程序设计' in t):
        return 'provincial'

    # Preliminaries / online qualifiers: separate module
    if 'preliminary' in cid or '预选' in t or '网络赛' in t or 'online' in cid:
        return 'preliminary'

    # Everything else is regional
    return 'regional'


def has_real_awards(contest_dir: Path) -> bool:
    """Check if the contest's source data has real award definitions."""
    # Try SRK file first
    srk_file = contest_dir / "rank.srk.json"
    if not srk_file.exists():
        # Try to find the original SRK from conversion metadata or path
        # For contest_data.json format, check the awards in the file
        cd_file = contest_dir / "contest_data.json"
        if cd_file.exists():
            with open(cd_file, encoding="utf-8") as f:
                data = json.load(f)
            # If awards section has non-zero values, check if they came from fallback
            awards = data.get("awards", {})
            # If we have a roster file, the contest was converted from SRK
            roster_file = contest_dir / "roster.json"
            if roster_file.exists():
                # Try to find original SRK from the directory structure
                # contests/YYYY/category/slug/ -> srk-collection-master/official/category/YYYY/...srk.json
                try:
                    return _check_original_srk(contest_dir)
                except:
                    pass
            # Default: if awards exist with non-zero values, assume real
            return awards.get("gold", 0) > 0 or awards.get("silver", 0) > 0 or awards.get("bronze", 0) > 0
        return True  # No file found, assume real

    with open(srk_file, encoding="utf-8") as f:
        data = json.load(f)
    return _has_real_series_awards(data)


def _has_real_series_awards(data: dict) -> bool:
    """Check if SRK data has real ICPC award counts or ratios."""
    for s in data.get("series", []):
        rule = s.get("rule", {})
        if rule.get("preset") == "ICPC":
            options = rule.get("options", {})
            # Check explicit counts
            counts = options.get("count", {}).get("value", [])
            if counts and counts[-1] > 0:
                return True
            # Check ratios (e.g., [0.1, 0.2, 0.3])
            ratio = options.get("ratio", {}).get("value", [])
            if ratio and len(ratio) > 0:
                return True
            # Neither counts nor ratios -> no real awards
            return False
    return False


def _check_original_srk(contest_dir: Path) -> bool:
    """Try to locate the original SRK file for a converted contest."""
    srk_base = ROOT / "srk-collection-master" / "official"
    # Derive category and year from the directory structure
    # contests/YYYY/category/slug/
    parts = contest_dir.relative_to(CONTESTS_DIR).parts
    if len(parts) < 3:
        return True
    year_dir = parts[0]  # e.g., "2025"
    category = parts[1]  # e.g., "ccpc" or "provincial"
    slug = parts[2]     # e.g., "北京_provincial"

    # Try to find matching SRK file
    candidates = []
    if category in ("ccpc", "icpc"):
        # Try {category}{year}* pattern
        prefix = f"{category}{year_dir}"
        candidates = list(srk_base.glob(f"{category}/{category}{year_dir}/*.srk.json"))
    elif category == "provincial":
        # Try matching by slug (province)
        province_code = slug.split("_")[0] if "_" in slug else ""
        if province_code:
            candidates = list(srk_base.glob(f"provincial/{province_code}/*.srk.json"))

    for cand in candidates:
        with open(cand, encoding="utf-8") as f:
            data = json.load(f)
        # Check if this SRK matches our contest (by title similarity)
        srk_title = ""
        t = data.get("contest", {}).get("title", {})
        if isinstance(t, dict):
            srk_title = (t.get("zh-CN") or t.get("fallback") or "").strip()
        elif isinstance(t, str):
            srk_title = t.strip()
        # Read our contest title
        cd_file = contest_dir / "contest_data.json"
        our_title = ""
        if cd_file.exists():
            with open(cd_file, encoding="utf-8") as f:
                cd = json.load(f)
            our_title = cd.get("title", "").strip()
        # Compare
        if srk_title and our_title and srk_title[:30] == our_title[:30]:
            return _has_real_series_awards(data)

    return True  # Can't determine, assume real
    """First pass: scan all contest data to collect unique organization names."""
    names = set()
    for contest_dir in sorted(CONTESTS_DIR.rglob("*")):
        if not contest_dir.is_dir():
            continue
        for fname in ["rank.srk.json", "contest_data.json"]:
            fpath = contest_dir / fname
            if fpath.exists():
                data = load_json(fpath)
                if "rows" in data:
                    for row in data["rows"]:
                        names.add(row["user"]["organization"])
                elif "teams" in data:
                    for t in data["teams"]:
                        names.add(t["organization"])
                break
    return names


def build():
    """Main build pipeline."""
    import shutil

    # Auto-bootstrap organizations.json if missing
    if not ORGS_FILE.exists():
        print("organizations.json not found, collecting org names...")
        org_names = collect_org_names()
        # Write temp unmatched so bootstrap can use it
        DIST_DIR.mkdir(exist_ok=True)
        with open(DIST_DIR / "unmatched_orgs.json", "w", encoding="utf-8") as f:
            json.dump(sorted(org_names), f, ensure_ascii=False, indent=2)
        print(f"Found {len(org_names)} unique organizations")
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "scripts" / "bootstrap_orgs.py")], check=False)

    # Clean and recreate dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(exist_ok=True)
    (DIST_DIR / "contests").mkdir(exist_ok=True)
    (DIST_DIR / "contestants").mkdir(exist_ok=True)
    (DIST_DIR / "organizations").mkdir(exist_ok=True)

    # Load org normalization
    orgs, name_to_id = load_organizations()

    # Scan and parse all contests
    all_contests: list[Contest] = []
    all_contestants: dict[str, Contestant] = {}  # keyed by (name, org)
    all_org_stats: dict[str, dict] = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0, "count": 0})
    unmatched_orgs: set[str] = set()

    for contest_dir in sorted(CONTESTS_DIR.rglob("*")):
        if not contest_dir.is_dir():
            continue
        srk_file = contest_dir / "rank.srk.json"
        contest_data_file = contest_dir / "contest_data.json"
        roster_file = contest_dir / "roster.json"

        # Determine data source
        if srk_file.exists():
            print(f"Parsing (SRK): {contest_dir.relative_to(CONTESTS_DIR)}")
            contest = parse_srk(srk_file)
        elif contest_data_file.exists():
            print(f"Parsing: {contest_dir.relative_to(CONTESTS_DIR)}")
            contest = parse_contest_data(contest_data_file)
        else:
            continue

        if roster_file.exists():
            load_roster(roster_file, contest)

        # Check if source data has real awards
        # Online preliminaries are always award-less but still rated
        is_prelim = "preliminary" in contest.id.lower() or "预选" in contest.title or "网络赛" in contest.title or "Online" in contest.title
        contest.no_awards = (not has_real_awards(contest_dir)) and not is_prelim
        if contest.no_awards or is_prelim:
            # Clear medals for preliminaries (no awards) and no-award contests
            for team in contest.teams:
                team.medal = ""

        # Classify tier NOW so records can use it
        slug = ""
        parts = contest.id.split("-")
        if len(parts) >= 3:
            slug = parts[-1]
        contest.tier = classify_tier(contest.id, contest.title, slug)
        tier = contest.tier

        # Resolve orgs
        unmatched = resolve_organizations(contest, orgs, name_to_id)
        unmatched_orgs.update(unmatched)

        # Aggregate org stats for ALL teams (skip medals if no real awards)
        for team in contest.teams:
            org_name = team.organization
            all_org_stats[org_name]["count"] += 1
            if team.medal and not contest.no_awards:
                all_org_stats[org_name][team.medal] += 1
            if team.champion:
                all_org_stats[org_name][f"champion_{team.champion}"] = all_org_stats[org_name].get(f"champion_{team.champion}", 0) + 1

        # Link team members to contestants
        for team in contest.teams:
            for member in team.members:
                if not member.name:
                    continue
                key = (member.name, team.organization)
                if key not in all_contestants:
                    all_contestants[key] = Contestant(
                        id="",  # will be assigned after merge
                        name=member.name,
                        gender=member.gender,
                        organization=team.organization,
                    )
                contestant = all_contestants[key]
                contestant.records.append(ContestRecord(
                    contest_id=contest.id,
                    contest_title=contest.title,
                    date=contest.date,
                    team_name=team.name,
                    rank=team.rank,
                    official_rank=team.official_rank,
                    official=team.official,
                    medal=team.medal,
                    champion=team.champion,
                    solved=team.solved,
                    penalty=team.penalty,
                    tier=tier,
                ))

        all_contests.append(contest)

    # --- Dedup by title ---
    # Group contests by normalized title. Co-branded events (same title, different
    # sub-type like invitational vs provincial) are NOT deduped — they are distinct
    # sub-contests of the same physical event.
    from collections import OrderedDict

    def _dedup_key(contest: Contest) -> str:
        title = contest.title.strip()
        # Append sub-type (invitational/provincial) for co-branded events
        cid = contest.id.lower()
        if 'provincial' in cid:
            return title + '||provincial'
        if 'invitational' in cid:
            return title + '||invitational'
        return title

    title_groups: dict[str, list[Contest]] = OrderedDict()
    for c in all_contests:
        key = _dedup_key(c)
        if key not in title_groups:
            title_groups[key] = []
        title_groups[key].append(c)

    deduped = []
    dupes_removed = 0
    for title, group in title_groups.items():
        if len(group) == 1:
            deduped.append(group[0])
        else:
            # Keep the one with most members, break ties by preferring provincial path
            def _score(contest):
                member_count = sum(len(t.members) for t in contest.teams)
                from_provincial = 'provincial' in contest.id.lower()
                return (member_count, 1 if from_provincial else 0)
            best = max(group, key=_score)
            deduped.append(best)
            dupes_removed += len(group) - 1

    if dupes_removed:
        print(f"\nDedup: removed {dupes_removed} duplicate contests ({len(deduped)} unique)")

    # Merge duped contest's org stats and members into the kept one
    for title, group in title_groups.items():
        if len(group) <= 1:
            continue
        best = max(group, key=lambda c: sum(len(t.members) for t in c.teams))
        for other in group:
            if other is best:
                continue
            # Merge members from other into best (dedup by name+org)
            best_members = {(m.name, t.organization) for t in best.teams for m in t.members}
            for team in other.teams:
                for member in team.members:
                    key = (member.name, team.organization)
                    if key not in best_members and member.name:
                        if key not in all_contestants:
                            all_contestants[key] = Contestant(
                                id="", name=member.name, gender=member.gender,
                                organization=team.organization,
                            )
                        all_contestants[key].records.append(ContestRecord(
                            contest_id=best.id, contest_title=best.title, date=best.date,
                            team_name=team.name, rank=team.rank,
                            official_rank=team.official_rank, official=team.official,
                            medal=team.medal, champion=team.champion,
                            solved=team.solved, penalty=team.penalty,
                            tier=best.tier,
                        ))
                        best_members.add(key)

    all_contests = deduped

    # --- Second dedup pass: same date + high team name overlap ---
    # Skip dedup for co-branded sub-contests (invitational vs provincial) — they
    # share the same date and have subset team overlap but are distinct contests.
    def _sub_type(contest: Contest) -> str:
        cid = contest.id.lower()
        if 'provincial' in cid: return 'provincial'
        if 'invitational' in cid: return 'invitational'
        return ''

    deduped2 = []
    removed2 = 0
    for i, c in enumerate(all_contests):
        c_names = {t.name.strip() for t in c.teams if t.name.strip()}
        is_dup = False
        for j, other in enumerate(deduped2):
            if c.date != other.date:
                continue
            o_names = {t.name.strip() for t in other.teams if t.name.strip()}
            if not c_names or not o_names:
                continue
            min_size = min(len(c_names), len(o_names))
            if min_size == 0:
                continue
            overlap = len(c_names & o_names)
            if overlap / min_size > 0.8:
                # Don't merge co-branded sub-contests (invitational vs provincial)
                if _sub_type(c) and _sub_type(other) and _sub_type(c) != _sub_type(other):
                    continue
                # Same event, merge into the kept one (prefer more members)
                if sum(len(t.members) for t in c.teams) > sum(len(t.members) for t in other.teams):
                    deduped2[j] = c
                is_dup = True
                removed2 += 1
                break
        if not is_dup:
            deduped2.append(c)
    if removed2:
        print(f"Dedup pass 2: removed {removed2} more duplicates ({len(deduped2)} unique)")

    all_contests = deduped2

    # --- Classify tiers ---
    for contest in all_contests:
        # Extract slug from directory structure
        slug = ""
        parts = contest.id.split("-")
        if len(parts) >= 3:
            slug = parts[-1]
        contest.tier = classify_tier(contest.id, contest.title, slug)

    # Assign stable IDs to contestants based on name+org hash (not sorted index)
    for key, contestant in all_contestants.items():
        import hashlib
        # Use name+org as the stable key — same person at same school gets same ID across rebuilds
        id_key = f"{contestant.name}@{contestant.organization}"
        h = hashlib.md5(id_key.encode()).hexdigest()[:10]
        contestant.id = f"c{h}"

    # --- OUTPUT ---

    # Build contestant lookup: (name, org) → contestant_id
    contestant_lookup: dict[tuple, str] = {
        (c.name, c.organization): c.id
        for c in all_contestants.values()
    }

    # 1. Summary
    summary = {
        "contests": [
            {
                "id": c.id,
                "title": c.title,
                "date": c.date,
                "tier": c.tier,
                "no_awards": c.no_awards,
                "team_count": len(c.teams),
                "official_count": sum(1 for t in c.teams if t.official),
                "problem_count": len(c.problems),
            }
            for c in sorted(all_contests, key=lambda c: c.date, reverse=True)
        ],
        "organizations": [
            {
                "id": name_to_id.get(org_name, sanitize_id(org_name)),
                "name": org_name,
                **stats,
            }
            for org_name, stats in sorted(all_org_stats.items())
        ],
        "contestants": [
            {
                "id": c.id,
                "name": c.name,
                "org": c.organization,
                "org_id": name_to_id.get(c.organization, sanitize_id(c.organization)),
                "medals": c.medal_summary,
                "record_count": len(c.records),
            }
            for c in sorted(all_contestants.values(), key=lambda c: -sum(c.medal_summary.values()))
        ],
        "search_index": [
            {"name": c.name, "type": "contestant", "id": c.id}
            for c in all_contestants.values()
        ] + [
            {"name": name, "type": "organization", "id": name_to_id.get(name, name.lower().replace(" ", "-"))}
            for name in all_org_stats
        ],
    }

    with open(DIST_DIR / "contests.json", "w", encoding="utf-8") as f:
        json.dump(summary["contests"], f, ensure_ascii=False, indent=2)
    with open(DIST_DIR / "organizations.json", "w", encoding="utf-8") as f:
        json.dump(summary["organizations"], f, ensure_ascii=False, indent=2)
    with open(DIST_DIR / "contestants.json", "w", encoding="utf-8") as f:
        json.dump(summary["contestants"], f, ensure_ascii=False, indent=2)
    with open(DIST_DIR / "search_index.json", "w", encoding="utf-8") as f:
        json.dump(summary["search_index"], f, ensure_ascii=False, indent=2)
    print(f"Wrote split data ({len(summary['contests'])} contests, {len(summary['contestants'])} contestants, {len(summary['organizations'])} orgs)")

    # 2. Per-contest JSON
    for contest in all_contests:
        contest_json = {
            "id": contest.id,
            "title": contest.title,
            "date": contest.date,
            "tier": contest.tier,
            "no_awards": contest.no_awards,
            "unrated": contest.id in UNRATED_CONTESTS,
            "unratedNote": UNRATED_CONTESTS.get(contest.id),
            "duration": contest.duration,
            "problems": [{"alias": p.alias, "accepted": p.accepted, "submitted": p.submitted} for p in contest.problems],
            "awards": {
                "gold": contest.gold_count,
                "silver": contest.silver_count,
                "bronze": contest.bronze_count,
            },
            "teams": [
                {
                    "id": t.id,
                    "name": t.name,
                    "official": t.official,
                    "organization": t.organization,
                    "rank": t.rank,
                    "official_rank": t.official_rank,
                    "medal": t.medal,
                    "champion": t.champion,
                    "girl_team": t.girl_team,
                    "division_medals": t.division_medals,
                    "score": {"solved": t.solved, "penalty": t.penalty},
                    "members": [
                        {"name": m.name, "gender": m.gender,
                         "contestant_id": contestant_lookup.get((m.name, t.organization), "")}
                        for m in t.members
                    ],
                    "problems": [
                        {"alias": p.alias, "result": p.result, "time": p.time, "tries": p.tries}
                        for p in t.problems
                    ],
                }
                for t in contest.teams
            ],
        }
        with open(DIST_DIR / "contests" / f"{contest.id}.json", "w", encoding="utf-8") as f:
            json.dump(contest_json, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_contests)} contest files")

    # 3. Per-contestant JSON
    for contestant in all_contestants.values():
        cj = {
            "id": contestant.id,
            "name": contestant.name,
            "gender": contestant.gender,
            "organization": contestant.organization,
            "org_id": name_to_id.get(contestant.organization, contestant.organization.lower().replace(" ", "-")),
            "records": [
                {
                    "contest_id": r.contest_id,
                    "contest_title": r.contest_title,
                    "date": r.date,
                    "team_name": r.team_name,
                    "rank": r.rank,
                    "official_rank": r.official_rank,
                    "official": r.official,
                    "medal": r.medal,
                    "champion": r.champion,
                    "tier": r.tier,
                    "score": {"solved": r.solved, "penalty": r.penalty},
                }
                for r in sorted(contestant.records, key=lambda r: r.date)
            ],
            "medal_summary": contestant.medal_summary,
            "medal_summary_by_tier": contestant.medal_summary_by_tier,
        }
        with open(DIST_DIR / "contestants" / f"{contestant.id}.json", "w", encoding="utf-8") as f:
            json.dump(cj, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_contestants)} contestant files")

    # 4. Organizations JSON
    for org_name, stats in all_org_stats.items():
        org_id = name_to_id.get(org_name, sanitize_id(org_name))
        org_output = {
            "id": org_id,
            "name": org_name,
            "stats": stats,
        }
        # Add canonical info if available
        if org_name in name_to_id and name_to_id[org_name] in orgs:
            o = orgs[name_to_id[org_name]]
            org_output["province"] = o.province
            org_output["city"] = o.city
            org_output["aliases"] = o.aliases
        with open(DIST_DIR / "organizations" / f"{org_id}.json", "w", encoding="utf-8") as f:
            json.dump(org_output, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_org_stats)} organization files")

    # 5. Unmatched orgs (for community to review)
    if unmatched_orgs:
        with open(DIST_DIR / "unmatched_orgs.json", "w", encoding="utf-8") as f:
            json.dump(sorted(unmatched_orgs), f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(unmatched_orgs)} unmatched organizations to unmatched_orgs.json")

    # 6. Copy announcement if exists
    announcement_src = ROOT / "announcement.json"
    if announcement_src.exists():
        shutil.copy(announcement_src, DIST_DIR / "announcement.json")
        print("Copied announcement.json")

    print("\nBuild complete!")

    # Compute Elo ratings
    print("\nComputing Elo ratings...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "compute_ratings.py"),
         "--data", str(DIST_DIR), "--out", str(DIST_DIR)],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Rating computation failed:", result.stderr, file=sys.stderr)


if __name__ == "__main__":
    build()
