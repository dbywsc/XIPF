"""Compute Elo ratings for contestants and schools using the xcpcrating engine.

Loads contest data from the XIPF build output, converts to xcpcrating's model
format, runs the IncrementalEngine (players) and SchoolEngine (schools), and
exports rating JSON files for the Vue frontend to consume.

Usage:
    python scripts/compute_ratings.py [--data web/public/data] [--out web/public/data]
"""

import json
import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Add local xcpc_rating module to path
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from xcpc_rating.model import Contest, Team, Member
from xcpc_rating.engines.incremental import IncrementalEngine
from xcpc_rating.engines.school import SchoolEngine
from xcpc_rating.tier import classify_tier


ROOT = _HERE.parent
DEFAULT_DATA = ROOT / "web" / "public" / "data"
DEFAULT_OUT = ROOT / "web" / "public" / "data"


def deduce_category(contest_id: str) -> str:
    """Deduce the contest category from the XIPF contest ID."""
    cid = contest_id.lower()
    if "_provincial" in cid or "provincial" in cid:
        return "provincial"
    if "icpc" in cid:
        return "icpc"
    if "ccpc" in cid:
        return "ccpc"
    return "other"


def load_xipf_contests(data_dir: Path) -> list[dict]:
    """Load all contest detail JSON files sorted by date."""
    contests_dir = data_dir / "contests"
    if not contests_dir.exists():
        print(f"ERROR: contests directory not found: {contests_dir}", file=sys.stderr)
        sys.exit(1)

    contests = []
    for fpath in sorted(contests_dir.glob("*.json")):
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        contests.append(data)

    contests.sort(key=lambda c: c.get("date", ""))
    return contests


def to_xcpc_model(contest_data: dict) -> Contest:
    """Convert a single XIPF contest JSON to an xcpcrating Contest object."""
    contest_id = contest_data["id"]
    title = contest_data["title"]
    date_str = contest_data.get("date", "2020-01-01")
    # Parse date; try multiple formats
    start_at = None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            start_at = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue
    if start_at is None:
        start_at = datetime(2020, 1, 1)

    category = deduce_category(contest_id)

    teams = []
    for t in contest_data.get("teams", []):
        rank = t.get("official_rank", t.get("rank", 0))
        if rank <= 0:
            rank = t.get("rank", 0)

        score = t.get("score", {}) or {}
        solved = score.get("solved", 0)
        penalty = score.get("penalty", 0)

        # Members
        members = []
        for m in t.get("members", []):
            cid = m.get("contestant_id", "")
            name = m.get("name", "")
            org = t.get("organization", "")
            if name:
                key = cid if cid else f"{name}@{org}"
                members.append(Member(
                    key=key,
                    display_name=name,
                    org=org,
                ))

        official = t.get("official", True)
        participated = solved > 0 or len(members) > 0

        teams.append(Team(
            rank=rank,
            solved=solved,
            penalty=penalty,
            members=tuple(members),
            official=official,
            participated=participated,
        ))

    return Contest(
        id=contest_id,
        title=title,
        start_at=start_at,
        category=category,
        teams=tuple(teams),
    )


def compute_player_ratings(contests: list[Contest]) -> dict:
    """Run the incremental ladder engine and return per-player rating data."""
    # Need to access lse_aggregate for team rating
    global _perf_module
    from xcpc_rating import perf as _perf_module

    engine = IncrementalEngine(official_only=True)
    INITIAL = 1400.0  # xcpcrating INITIAL_EXPECT

    # Track per-player history for the chart
    player_history: dict[str, list[dict]] = defaultdict(list)
    # Track per-contest team rating data
    contest_team_ratings: dict[str, list[dict]] = defaultdict(list)

    for contest in contests:
        # Snapshot member ratings BEFORE processing (pre-contest)
        pre_ratings: dict[str, float] = {}
        for team in contest.teams:
            for member in team.members:
                state = engine._players.get(member.key)
                pre_ratings[member.key] = state["expect"] if state else INITIAL

        # Process contest
        engine.process_contest(contest)

        # Compute per-team rating data
        for team in contest.teams:
            if not team.members or not team.participated or not team.official:
                contest_team_ratings[contest.id].append(None)
                continue

            # Pre-contest team rating (LSE of pre-ratings)
            member_pres = [pre_ratings.get(m.key, INITIAL) for m in team.members]
            pre_team = _perf_module.lse_aggregate(member_pres) if member_pres else None

            # Post-contest team rating (LSE of post-ratings)
            member_posts = []
            for m in team.members:
                state = engine._players.get(m.key)
                member_posts.append(state["expect"] if state else INITIAL)
            post_team = _perf_module.lse_aggregate(member_posts) if member_posts else None

            # Average individual delta (sum of (post - pre) / n)
            deltas = []
            perf_val = None
            for m in team.members:
                state = engine._players.get(m.key)
                if state:
                    post = state["expect"]
                    pre = pre_ratings.get(m.key, INITIAL)
                    deltas.append(post - pre)
                    if perf_val is None:
                        perf_val = state.get("last_perf")

            avg_delta = sum(deltas) / len(deltas) if deltas else 0.0

            contest_team_ratings[contest.id].append({
                "preTeamRating": float(pre_team) if pre_team is not None else None,
                "postTeamRating": float(post_team) if post_team is not None else None,
                "avgDelta": float(avg_delta),
                "perf": float(perf_val) if perf_val is not None else None,
            })

        # Record per-member rating after each contest
        for team in contest.teams:
            for member in team.members:
                state = engine._players.get(member.key)
                if state is None:
                    continue
                rating = state["expect"]  # display score is raw expectation
                contests_count = state["contests"]
                last_perf = state.get("last_perf")

                player_history[member.key].append({
                    "contest_id": contest.id,
                    "contest_title": contest.title,
                    "date": contest.start_at.strftime("%Y-%m-%d"),
                    "rating": float(rating),
                    "perf": float(last_perf) if last_perf is not None else None,
                    "contests": contests_count,
                })

    # Build final leaderboard
    leaderboard = engine.leaderboard(min_contests=1)

    return {
        "leaderboard": [
            {
                "key": p.key,
                "name": p.display_name,
                "org": p.org,
                "rating": float(p.rating),
                "contests": p.contests,
            }
            for p in leaderboard
        ],
        "history": dict(player_history),
        "contest_teams": dict(contest_team_ratings),
    }


def compute_school_ratings(contests: list[Contest]) -> list[dict]:
    """Run the school Bayesian engine and return per-school rating data."""
    engine = SchoolEngine()

    for contest in contests:
        engine.process_contest(contest)

    board = engine.leaderboard(min_contests=1)
    return [
        {
            "org": s.org,
            "rating": float(s.rating),
            "contests": s.contests,
        }
        for s in board
    ]


def load_org_name_to_id(data_dir: Path) -> dict[str, str]:
    """Load org name → org_id mapping from organizations.json."""
    orgs_file = data_dir / "organizations.json"
    if not orgs_file.exists():
        return {}
    with open(orgs_file, encoding="utf-8") as f:
        orgs = json.load(f)
    return {o["name"]: o["id"] for o in orgs}


def merge_with_xipf(player_ratings: dict, data_dir: Path) -> list[dict]:
    """Merge rating data with XIPF contestant IDs."""
    # Load contestant → id mapping and total record counts from contestants.json
    contestants_file = data_dir / "contestants.json"
    name_org_to_id: dict[tuple, str] = {}
    name_org_to_records: dict[tuple, int] = {}
    org_to_id: dict[str, str] = {}
    if contestants_file.exists():
        with open(contestants_file, encoding="utf-8") as f:
            contestants = json.load(f)
        for c in contestants:
            key = (c["name"].strip().lower(), c["org"].strip().lower())
            name_org_to_id[key] = c["id"]
            name_org_to_records[key] = c.get("record_count", 0)
            if c["org"] not in org_to_id:
                org_to_id[c["org"]] = c.get("org_id", "")

    # Also load org id mapping
    org_name_to_id = load_org_name_to_id(data_dir)

    # Build the output
    # Map key → XIPF id
    key_to_xipf: dict[str, str] = {}
    # First pass: match by key (which is contestant_id)
    leaderboard = player_ratings["leaderboard"]
    for entry in leaderboard:
        xipf_key = (entry["name"].strip().lower(), entry["org"].strip().lower())
        if xipf_key in name_org_to_id:
            key_to_xipf[entry["key"]] = name_org_to_id[xipf_key]
        else:
            # Use the rating engine key as fallback
            key_to_xipf[entry["key"]] = entry["key"]

    # Map rating history keys to XIPF IDs too
    history = player_ratings.get("history", {})
    remapped_history: dict[str, list[dict]] = {}
    for key, rows in history.items():
        xipf_key = None
        # Find the name/org from any row or from leaderboard
        for entry in leaderboard:
            if entry["key"] == key:
                xipf_key = (entry["name"].strip().lower(), entry["org"].strip().lower())
                break
        if xipf_key and xipf_key in name_org_to_id:
            remapped_history[name_org_to_id[xipf_key]] = rows
        elif key in key_to_xipf:
            remapped_history[key_to_xipf[key]] = rows
        else:
            remapped_history[key] = rows

    # Build final player list with XIPF IDs
    players = []
    for entry in leaderboard:
        xipf_id = key_to_xipf.get(entry["key"], entry["key"])
        org_id = org_name_to_id.get(entry["org"], "") or org_to_id.get(entry["org"], "")
        xipf_key = (entry["name"].strip().lower(), entry["org"].strip().lower())
        total_contests = name_org_to_records.get(xipf_key, entry["contests"])
        players.append({
            "id": xipf_id,
            "name": entry["name"],
            "org": entry["org"],
            "org_id": org_id,
            "rating": entry["rating"],
            "contests": total_contests,
        })

    return players, remapped_history


def main():
    parser = argparse.ArgumentParser(description="Compute Elo ratings for XIPF")
    parser.add_argument("--data", default=str(DEFAULT_DATA), help="Path to XIPF data directory")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output directory for rating files")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)

    print(f"Loading contests from {data_dir}...")
    started = time.perf_counter()

    xipf_contests = load_xipf_contests(data_dir)
    print(f"Loaded {len(xipf_contests)} contests")

    # Filter out contests without real awards, BUT keep preliminaries (network qualifiers)
    no_awards_contests = [c for c in xipf_contests if c.get("no_awards") and "preliminary" not in c.get("id","").lower() and "预选" not in c.get("title","") and "网络赛" not in c.get("title","")]
    xipf_contests = [c for c in xipf_contests if not c.get("no_awards") or "preliminary" in c.get("id","").lower() or "预选" in c.get("title","") or "网络赛" in c.get("title","")]
    if no_awards_contests:
        print(f"Excluded {len(no_awards_contests)} contests without award data (unrated)")
        for c in no_awards_contests[:5]:
            print(f"  - {c['title'][:50]}")
        if len(no_awards_contests) > 5:
            print(f"  ... and {len(no_awards_contests) - 5} more")

    # Convert to xcpcrating model
    contests = [to_xcpc_model(c) for c in xipf_contests]

    # Log tiers
    from collections import Counter
    tiers = Counter()
    for c in contests:
        try:
            tier = classify_tier(c)
            tiers[tier] += 1
        except ValueError:
            tiers["unclassified"] += 1
    print(f"Contest tiers: {dict(tiers)}")

    # Compute player ratings
    print("Computing player ratings...")
    player_ratings = compute_player_ratings(contests)
    print(f"  {len(player_ratings['leaderboard'])} players rated")

    # Compute school ratings
    print("Computing school ratings...")
    school_ratings = compute_school_ratings(contests)
    print(f"  {len(school_ratings)} schools rated")

    # Merge with XIPF IDs
    print("Merging with XIPF data...")
    players, player_history = merge_with_xipf(player_ratings, data_dir)

    # Load org name → id mapping
    org_name_to_id = load_org_name_to_id(data_dir)

    # ---- Write output files ----
    os.makedirs(out_dir, exist_ok=True)

    # 1. players_ratings.json — leaderboard sorted by rating desc
    players_sorted = sorted(players, key=lambda p: -p["rating"])
    with open(out_dir / "players_ratings.json", "w", encoding="utf-8") as f:
        json.dump(players_sorted, f, ensure_ascii=False, indent=2)
    print(f"Wrote players_ratings.json ({len(players_sorted)} players)")

    # 2. players_ratings/ — per-player detail with history
    ratings_dir = out_dir / "players_ratings"
    os.makedirs(ratings_dir, exist_ok=True)
    for pid, history_rows in player_history.items():
        # Sort history by date
        history_rows.sort(key=lambda r: r["date"])
        detail = {
            "id": pid,
            "history": history_rows,
        }
        with open(ratings_dir / f"{pid}.json", "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False)
    print(f"Wrote {len(player_history)} player rating detail files")

    # 3. schools_ratings.json — school leaderboard sorted by rating desc
    schools_output = []
    for s in school_ratings:
        org_name = s["org"]
        org_id = org_name_to_id.get(org_name, org_name.lower().replace(" ", "-"))
        schools_output.append({
            "id": org_id,
            "name": org_name,
            "rating": s["rating"],
            "contests": s["contests"],
        })
    # Re-sort by rating (may have changed due to org id mapping)
    schools_output.sort(key=lambda s: -s["rating"])
    with open(out_dir / "schools_ratings.json", "w", encoding="utf-8") as f:
        json.dump(schools_output, f, ensure_ascii=False, indent=2)
    print(f"Wrote schools_ratings.json ({len(schools_output)} schools)")

    # 4. contest_ratings/ — per-contest team rating data
    contest_ratings_dir = out_dir / "contest_ratings"
    os.makedirs(contest_ratings_dir, exist_ok=True)
    contest_team_data = player_ratings.get("contest_teams", {})
    for contest_id, team_ratings in contest_team_data.items():
        with open(contest_ratings_dir / f"{contest_id}.json", "w", encoding="utf-8") as f:
            json.dump({"teams": team_ratings}, f, ensure_ascii=False)
    print(f"Wrote {len(contest_team_data)} contest team rating files")

    elapsed = time.perf_counter() - started
    print(f"\nDone in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
