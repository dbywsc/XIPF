"""Post-build contestant merge: combine split records for the same person.

Run after `build.py`. Reads contestant_merges.json and merges the
specified contestants in dist/, updating contestant JSONs, contest
references, and summary.json.

Usage:
    python3 scripts/merge_contestants.py
"""

import json
from pathlib import Path
from collections import Counter


ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
MERGES_FILE = ROOT / "contestant_merges.json"


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compute_medal_summary(records: list) -> dict:
    medals = Counter(r.get("medal") for r in records if r.get("medal"))
    champions = Counter(r.get("champion") for r in records if r.get("champion"))
    return {
        "champion": champions.get("冠军", 0),
        "runner_up": champions.get("亚军", 0),
        "third": champions.get("季军", 0),
        "gold": medals["gold"],
        "silver": medals["silver"],
        "bronze": medals["bronze"],
    }


def merge():
    if not MERGES_FILE.exists():
        print("contestant_merges.json not found, nothing to merge.")
        return

    merges_data = load(MERGES_FILE)
    merges = merges_data.get("merges", [])
    if not merges:
        print("No merge rules configured.")
        return

    contestants_dir = DIST_DIR / "contestants"
    if not contestants_dir.exists():
        print("dist/ not found. Run build.py first.")
        return

    # Build lookup: (name, org) → (id, filepath)
    lookup: dict[tuple, tuple[str, Path]] = {}
    for fp in sorted(contestants_dir.glob("*.json")):
        data = load(fp)
        lookup[(data["name"], data["organization"])] = (data["id"], fp)

    summary = load(DIST_DIR / "summary.json")

    merged_count = 0
    source_ids_to_remove: set[str] = set()
    id_remap: dict[str, str] = {}  # old source_id → target_id

    for m in merges:
        s_name = m["source"]["name"]
        s_org = m["source"]["organization"]
        t_name = m["target"]["name"]
        t_org = m["target"]["organization"]
        s_key = (s_name, s_org)
        t_key = (t_name, t_org)

        if s_key not in lookup:
            print(f"  SKIP: source not found — {s_name} @ {s_org}")
            continue
        if t_key not in lookup:
            print(f"  SKIP: target not found — {t_name} @ {t_org}")
            continue

        s_id, s_path = lookup[s_key]
        t_id, t_path = lookup[t_key]

        if s_id == t_id:
            print(f"  SKIP: source and target are the same — {s_name}")
            continue

        source = load(s_path)
        target = load(t_path)

        # Copy gender if target lacks it
        if source.get("gender") and not target.get("gender"):
            target["gender"] = source["gender"]

        # Merge records
        target["records"].extend(source["records"])
        target["records"].sort(key=lambda r: r.get("date", ""))
        target["medal_summary"] = compute_medal_summary(target["records"])

        save(t_path, target)
        source_ids_to_remove.add(s_id)
        id_remap[s_id] = t_id
        del lookup[s_key]
        merged_count += 1
        print(f"  Merged: {s_name} ({s_org}) → {t_name} ({t_org})")

    if merged_count == 0:
        print("No merges performed.")
        return

    # Fix contestant_id references in contest JSONs
    contests_dir = DIST_DIR / "contests"
    for cf in contests_dir.glob("*.json"):
        contest_data = load(cf)
        changed = False
        for team in contest_data.get("teams", []):
            for member in team.get("members", []):
                old_id = member.get("contestant_id", "")
                if old_id in id_remap:
                    member["contestant_id"] = id_remap[old_id]
                    changed = True
        if changed:
            save(cf, contest_data)

    # Delete source contestant files
    for s_id in source_ids_to_remove:
        s_path = contestants_dir / f"{s_id}.json"
        if s_path.exists():
            s_path.unlink()

    # Update summary
    current_ids = {load(fp)["id"] for fp in contestants_dir.glob("*.json")}
    summary["contestants"] = [
        c for c in summary["contestants"] if c["id"] in current_ids
    ]

    # Update record counts and medals for merged targets
    for c in summary["contestants"]:
        if c["id"] in id_remap.values():
            cf = contestants_dir / f"{c['id']}.json"
            if cf.exists():
                data = load(cf)
                c["record_count"] = len(data["records"])
                c["medals"] = data["medal_summary"]
                c["org"] = data["organization"]
                c["org_id"] = data.get("org_id", "")

    # Rebuild search index
    summary["search_index"] = [
        {"name": c["name"], "type": "contestant", "id": c["id"]}
        for c in summary["contestants"]
    ] + [e for e in summary["search_index"] if e["type"] != "contestant"]

    save(DIST_DIR / "summary.json", summary)

    print(f"\nMerge done: {merged_count} contestant(s) merged, "
          f"{len(source_ids_to_remove)} file(s) removed.")
    print("Don't forget: cp -r dist/* web/public/data/")


if __name__ == "__main__":
    merge()
