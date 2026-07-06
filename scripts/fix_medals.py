"""Regenerate contest_data.json files from SRK sources to fix medal counts.

The bug: srk_to_xipf.py incorrectly de-cumulated SRK count values.
SRK [30, 60, 90] means gold=30, silver=60, bronze=90 (per-segment),
not gold=30, silver=30, bronze=30 (de-cumulated).

This script reads each existing contest_data.json, finds the matching SRK file,
and regenerates the data with correct medal counts.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRK_BASE = ROOT / "srk-collection-master" / "official"
CONTESTS_DIR = ROOT / "contests"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalized_title(title):
    """Normalize a title for loose matching."""
    return " ".join(title.replace("「", "").replace("」", "").replace("\u200b", "").split())


def build_srk_index():
    """Build title→path index for all SRK files."""
    index = {}
    for fpath in sorted(SRK_BASE.rglob("*.srk.json")):
        data = load_json(fpath)
        contest = data.get("contest", {})
        title_data = contest.get("title", {})
        if isinstance(title_data, dict):
            title = title_data.get("zh-CN") or title_data.get("fallback", "")
        else:
            title = str(title_data) if title_data else ""
        if title:
            idx_key = normalized_title(title)
            # Remove year prefix for matching (e.g., "[2025]" or "2025 ")
            # Title might start with year info
            if idx_key not in index:
                index[idx_key] = []
            index[idx_key].append(fpath)
    return index


def find_srk(title, srk_index, contest_dir_rel):
    """Find the matching SRK file for a contest title."""
    key = normalized_title(title)

    # Direct match
    if key in srk_index:
        candidates = srk_index[key]
        if len(candidates) == 1:
            return candidates[0]
        # Multiple matches: try to disambiguate by path
        # contest_dir_rel like "2025/icpc/上海_regional"
        parts = contest_dir_rel.split("/")
        if len(parts) >= 2:
            year = parts[0]
            category = parts[1]
            for c in candidates:
                rel = str(c.relative_to(SRK_BASE))
                if year in rel and category in rel:
                    return c

    # Try partial match: remove year prefix, remove some suffixes
    # e.g., "第 50 届 ICPC ... 上海站" vs "2025 ICPC ... Shanghai"
    for idx_key, paths in srk_index.items():
        # Check for substantial overlap
        key_words = set(key.split())
        idx_words = set(idx_key.split())
        if len(key_words & idx_words) >= 3 and len(key_words & idx_words) >= len(key_words) * 0.5:
            parts = contest_dir_rel.split("/")
            if len(parts) >= 2:
                year = parts[0]
                category = parts[1]
                for p in paths:
                    rel = str(p.relative_to(SRK_BASE))
                    if year in rel and category in rel:
                        return p

    return None


def regenerate_contest(contest_dir, srk_path):
    """Regenerate contest_data.json and roster.json from SRK."""
    from srk_to_xipf import convert_srk

    # Extract year from path
    rel = contest_dir.relative_to(CONTESTS_DIR)
    parts = rel.parts
    year = int(parts[0]) if parts[0].isdigit() else 2024

    # Extract date from existing contest_data.json
    try:
        existing = load_json(contest_dir / "contest_data.json")
        date = existing.get("date", "")
        title = existing.get("title", "")
    except Exception:
        date = ""
        title = ""

    contest_data, roster = convert_srk(srk_path, year, date, title)

    # Preserve any existing members that were manually added
    try:
        existing = load_json(contest_dir / "contest_data.json")
        existing_teams = {t["id"]: t for t in existing.get("teams", [])}
        for team in contest_data["teams"]:
            tid = team["id"]
            if tid in existing_teams:
                # Preserve members if they exist in original
                if not team.get("members") and existing_teams[tid].get("members"):
                    team["members"] = existing_teams[tid]["members"]
    except Exception:
        pass

    # Write
    with open(contest_dir / "contest_data.json", "w", encoding="utf-8") as f:
        json.dump(contest_data, f, ensure_ascii=False, indent=2)
    with open(contest_dir / "roster.json", "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=2)

    awards = contest_data["awards"]
    official_count = sum(1 for t in contest_data["teams"] if t["official"])
    return awards, official_count, len(contest_data["teams"])


def main():
    # Build SRK index
    print("Building SRK index...")
    srk_index = build_srk_index()
    print(f"  Indexed {sum(len(v) for v in srk_index.values())} SRK files ({len(srk_index)} unique titles)")

    # Find all contest directories with contest_data.json
    contest_dirs = []
    for fpath in sorted(CONTESTS_DIR.rglob("contest_data.json")):
        contest_dirs.append(fpath.parent)

    print(f"\nProcessing {len(contest_dirs)} contest directories...")
    print()

    regenerated = 0
    not_found = 0
    skipped = 0

    for contest_dir in contest_dirs:
        rel = contest_dir.relative_to(CONTESTS_DIR)

        # Read existing data
        existing = load_json(contest_dir / "contest_data.json")
        title = existing.get("title", "")
        old_awards = existing.get("awards", {})

        # Find matching SRK
        srk_path = find_srk(title, srk_index, str(rel))

        if srk_path is None:
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
            # No count-based series, medals might be from ratio or default
            print(f"  SKIP (no count series): {rel}")
            skipped += 1
            continue

        # Regenerate
        try:
            awards, official, total = regenerate_contest(contest_dir, srk_path)
            old_g, old_s, old_b = old_awards.get("gold", 0), old_awards.get("silver", 0), old_awards.get("bronze", 0)
            new_g, new_s, new_b = awards["gold"], awards["silver"], awards["bronze"]
            status = "FIXED" if (old_g != new_g or old_s != new_s or old_b != new_b) else "OK"
            print(f"  {status}: {rel}")
            print(f"    Awards: G{old_g}/{old_s}/{old_b} → G{new_g}/{new_s}/{new_b} ({total} teams, {official} official)")
            print(f"    SRK: {srk_rel}")
            regenerated += 1
        except Exception as e:
            print(f"  FAILED: {rel} - {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Results: {regenerated} regenerated, {not_found} not found, {skipped} skipped")
    print(f"Total: {len(contest_dirs)}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts"))
    main()
