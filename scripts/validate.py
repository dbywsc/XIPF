"""CI validation script: checks data format and completeness for PRs."""

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTESTS_DIR = ROOT / "contests"


def check(condition, message):
    if not condition:
        print(f"  ERROR: {message}")
        return False
    return True


def validate_srk(filepath: Path) -> list[str]:
    """Validate an SRK JSON file. Returns list of errors."""
    errors = []

    try:
        data = json.load(open(filepath, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Cannot read file: {e}"]

    # Top-level keys
    for key in ["type", "contest", "rows"]:
        if key not in data:
            errors.append(f"Missing top-level key: '{key}'")

    if "contest" in data:
        c = data["contest"]
        for key in ["title", "startAt"]:
            if key not in c:
                errors.append(f"Missing contest.{key}")

    if "rows" in data:
        rows = data["rows"]
        if not isinstance(rows, list):
            errors.append("'rows' must be a list")
        elif len(rows) == 0:
            errors.append("'rows' is empty")
        else:
            for i, row in enumerate(rows):
                user = row.get("user", {})
                if not user.get("id"):
                    errors.append(f"Row {i}: missing user.id")
                if not user.get("organization"):
                    errors.append(f"Row {i} ({user.get('id', '?')}): missing user.organization")

    return errors


def validate_contest_data(filepath: Path) -> list[str]:
    """Validate a contest_data.json file (from XLSX import). Returns list of errors."""
    errors = []

    try:
        data = json.load(open(filepath, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Cannot read file: {e}"]

    for key in ["title", "teams"]:
        if key not in data:
            errors.append(f"Missing key: '{key}'")

    if "teams" in data:
        teams = data["teams"]
        if not isinstance(teams, list):
            errors.append("'teams' must be a list")
        elif len(teams) == 0:
            errors.append("'teams' is empty")
        else:
            ids = set()
            for i, team in enumerate(teams):
                tid = team.get("id", f"row_{i}")
                if not team.get("name"):
                    errors.append(f"Team {tid}: missing name")
                if not team.get("organization"):
                    errors.append(f"Team {tid}: missing organization")
                if tid in ids:
                    errors.append(f"Team {tid}: duplicate ID")
                ids.add(tid)

    return errors


def validate_roster(filepath: Path, data_filepath: Path) -> list[str]:
    """Validate a roster.json against its corresponding data file. Returns list of errors."""
    errors = []

    try:
        roster = json.load(open(filepath, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Cannot read file: {e}"]

    if "teams" not in roster:
        return ["Missing 'teams' key"]

    teams_data = roster["teams"]
    if not isinstance(teams_data, dict):
        return ["'teams' must be a dict (team_id → team_info)"]

    # Load data file to cross-check team IDs
    data = json.load(open(data_filepath, encoding="utf-8"))
    if "rows" in data:
        # SRK format
        data_team_ids = {row["user"]["id"] for row in data.get("rows", [])}
    elif "teams" in data:
        # contest_data format
        data_team_ids = {t["id"] for t in data.get("teams", [])}
    else:
        data_team_ids = set()

    roster_team_ids = set(teams_data.keys())

    # Check for teams in roster but not in data
    extra = roster_team_ids - data_team_ids
    if extra:
        errors.append(f"Teams in roster but not in data: {extra}")

    # Check for teams in data but not in roster
    missing = data_team_ids - roster_team_ids
    if missing:
        errors.append(f"Teams in data but not in roster: {missing}")

    # Validate member data
    for team_id, team_info in teams_data.items():
        if not isinstance(team_info, dict):
            errors.append(f"Team {team_id}: must be a dict")
            continue

        members = team_info.get("members", [])
        if not isinstance(members, list):
            errors.append(f"Team {team_id}: 'members' must be a list")
            continue

        if len(members) == 0:
            errors.append(f"Team {team_id}: has no members")
        elif len(members) > 3:
            errors.append(f"Team {team_id}: has {len(members)} members (max 3)")

        for j, member in enumerate(members):
            if not isinstance(member, dict):
                errors.append(f"Team {team_id} member {j}: must be a dict")
                continue
            if not member.get("name"):
                errors.append(f"Team {team_id} member {j}: name is empty")

    return errors


def main():
    """Validate all contest directories."""
    all_errors = []
    contest_count = 0
    valid_count = 0

    for contest_dir in sorted(CONTESTS_DIR.rglob("*")):
        if not contest_dir.is_dir():
            continue

        srk_file = contest_dir / "rank.srk.json"
        contest_data_file = contest_dir / "contest_data.json"
        roster_file = contest_dir / "roster.json"

        if not srk_file.exists() and not contest_data_file.exists():
            continue

        contest_count += 1
        rel_path = contest_dir.relative_to(CONTESTS_DIR)
        print(f"\n{'='*60}")
        print(f"Validating: {rel_path}")
        print(f"{'='*60}")

        dir_errors = []

        # Validate based on file type
        if srk_file.exists():
            print(f"  [SRK] {srk_file.name}")
            srk_errors = validate_srk(srk_file)
            for e in srk_errors:
                print(f"    {e}")
            dir_errors.extend(srk_errors)
        elif contest_data_file.exists():
            print(f"  [XLSX] {contest_data_file.name}")
            cd_errors = validate_contest_data(contest_data_file)
            for e in cd_errors:
                print(f"    {e}")
            dir_errors.extend(cd_errors)

        # Validate roster if present
        data_file = srk_file if srk_file.exists() else contest_data_file
        if roster_file.exists():
            print(f"  [Roster] {roster_file.name}")
            roster_errors = validate_roster(roster_file, data_file)
            for e in roster_errors:
                print(f"    {e}")
            dir_errors.extend(roster_errors)
        else:
            print(f"  [Roster] MISSING")

        if dir_errors:
            all_errors.extend(dir_errors)
            print(f"  RESULT: {len(dir_errors)} error(s)")
        else:
            valid_count += 1
            print(f"  RESULT: OK")

    print(f"\n{'='*60}")
    print(f"Summary: {valid_count}/{contest_count} valid, {len(all_errors)} total error(s)")
    print(f"{'='*60}")

    if all_errors:
        sys.exit(1)
    else:
        print("All validations passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
