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
        )
        teams.append(team)

    # Sort teams by ICPC rules and assign ranks
    official_teams = [t for t in teams if t.official]
    all_sorted = sorted(teams, key=lambda t: (-t.solved, t.penalty))
    for rank, team in enumerate(all_sorted, 1):
        if team.rank == 0:  # only assign if not already set
            team.rank = rank

    # Assign medals: use pre-set if available, otherwise calculate from team count
    pre_set_medals = any(t.medal for t in teams if hasattr(t, 'medal') and t.medal)
    official_count = len(official_teams)

    if pre_set_medals:
        # Medals came from imported data — count them
        gold_count = sum(1 for t in official_teams if t.medal == "gold")
        silver_count = sum(1 for t in official_teams if t.medal == "silver")
        bronze_count = sum(1 for t in official_teams if t.medal == "bronze")
    else:
        gold_count = max(1, int(official_count * 0.1))
        silver_count = max(1, int(official_count * 0.2))
        bronze_count = max(1, int(official_count * 0.3))
        official_sorted = sorted(official_teams, key=lambda t: (-t.solved, t.penalty))
        for i, team in enumerate(official_sorted):
            if i < gold_count:
                team.medal = "gold"
            elif i < gold_count + silver_count:
                team.medal = "silver"
            elif i < gold_count + silver_count + bronze_count:
                team.medal = "bronze"

    contest_id = filepath.parent.name
    year_dir = filepath.parent.parent.name
    if year_dir.isdigit():
        contest_id = f"{year_dir}-{contest_id}"

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
    # Official teams ranked separately for awards, but we assign global rank to all
    official_teams = [t for t in teams if t.official]
    unofficial_teams = [t for t in teams if not t.official]

    # All teams sorted together for global rank
    all_sorted = sorted(teams, key=lambda t: (-t.solved, t.penalty))
    for rank, team in enumerate(all_sorted, 1):
        team.rank = rank

    # Awards only for official teams, sorted separately
    official_sorted = sorted(official_teams, key=lambda t: (-t.solved, t.penalty))
    for i, team in enumerate(official_sorted):
        if i < award_counts[0]:
            team.medal = "gold"
        elif i < award_counts[1]:
            team.medal = "silver"
        elif i < award_counts[2]:
            team.medal = "bronze"

    # Determine contest ID from directory name
    contest_id = filepath.parent.name
    year = filepath.parent.parent.name if filepath.parent.parent.name.isdigit() else ""
    if year:
        contest_id = f"{year}-{contest_id}"

    return Contest(
        id=contest_id,
        title=title,
        date=date,
        duration=duration_sec,
        frozen_duration=frozen_sec,
        problems=problems,
        teams=teams,
        gold_count=award_counts[0],
        silver_count=award_counts[1] - award_counts[0],
        bronze_count=award_counts[2] - award_counts[1],
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


def resolve_organizations(contest: Contest, orgs: dict, name_to_id: dict[str, str]) -> set:
    """Match team organizations to canonical orgs. Returns set of unmatched org names."""
    unmatched = set()
    for team in contest.teams:
        org_name = team.organization
        if org_name in name_to_id:
            team.organization = org_name  # will be resolved to canonical later
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


def collect_org_names() -> set:
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

        # Resolve orgs
        unmatched = resolve_organizations(contest, orgs, name_to_id)
        unmatched_orgs.update(unmatched)

        # Aggregate org stats for ALL teams
        for team in contest.teams:
            org_name = team.organization
            all_org_stats[org_name]["count"] += 1
            if team.medal:
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
                    medal=team.medal,
                    champion=team.champion,
                    solved=team.solved,
                    penalty=team.penalty,
                ))

        all_contests.append(contest)

    # Assign IDs to contestants
    for i, (key, contestant) in enumerate(sorted(all_contestants.items())):
        import re, hashlib
        name_lower = contestant.name.lower().strip()
        # For pure Chinese/non-ASCII names, use hash
        if not any(c.isascii() and c.isalpha() for c in name_lower):
            h = hashlib.md5(name_lower.encode()).hexdigest()[:6]
            name_slug = f"c{h}"
        else:
            name_slug = re.sub(r'[^a-zA-Z0-9]', '', name_lower)[:20]
        contestant.id = f"{name_slug}-{i}"

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
                "team_count": len(c.teams),
                "official_count": sum(1 for t in c.teams if t.official),
                "problem_count": len(c.problems),
            }
            for c in all_contests
        ],
        "organizations": [
            {
                "id": name_to_id.get(org_name, org_name.lower().replace(" ", "-")),
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
                "org_id": name_to_id.get(c.organization, c.organization.lower().replace(" ", "-")),
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

    with open(DIST_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Wrote summary.json ({len(summary['contests'])} contests, {len(summary['contestants'])} contestants, {len(summary['organizations'])} orgs)")

    # 2. Per-contest JSON
    for contest in all_contests:
        contest_json = {
            "id": contest.id,
            "title": contest.title,
            "date": contest.date,
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
                    "medal": t.medal,
                    "champion": t.champion,
                    "girl_team": t.girl_team,
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
                    "medal": r.medal,
                    "champion": r.champion,
                    "score": {"solved": r.solved, "penalty": r.penalty},
                }
                for r in sorted(contestant.records, key=lambda r: r.date)
            ],
            "medal_summary": contestant.medal_summary,
        }
        with open(DIST_DIR / "contestants" / f"{contestant.id}.json", "w", encoding="utf-8") as f:
            json.dump(cj, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_contestants)} contestant files")

    # 4. Organizations JSON
    for org_name, stats in all_org_stats.items():
        org_id = name_to_id.get(org_name, org_name.lower().replace(" ", "-"))
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

    print("\nBuild complete!")


if __name__ == "__main__":
    build()
