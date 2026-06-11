"""Cross-contest identity resolution: merge records belonging to the same real person.

Strategy:
- Within the same organization, contestants with the same name are the same person.
- Across organizations, contestants with the same name need heuristic matching
  (timeline coherence, organization transitions, etc.).

For initial implementation, we use simple same-name + same-org matching.
OIerDb-style fuzzy merging can be added later as data grows.
"""

from collections import defaultdict
from models import Contestant


def merge_contestants(contestants: dict[tuple, Contestant]) -> dict[str, Contestant]:
    """
    Merge contestants with the same (name, org) key into single entities.

    This is the baseline strategy. Contestants who change organizations
    between contests will NOT be merged by this simple approach — they
    will appear as separate entries. A more sophisticated merge (like
    OIerDb's attempt_merge) can be added later.

    Returns: dict of contestant_id → Contestant
    """
    merged: dict[str, Contestant] = {}

    for (name, org), contestant in contestants.items():
        # Use (name, org) as the merge key
        # Different org = different person (in the simple model)
        merged[contestant.id] = contestant

    return merged


def merge_by_name_across_orgs(contestants: dict[tuple, Contestant]) -> dict[str, Contestant]:
    """
    More aggressive: merge contestants with the same name even if orgs differ,
    checking timeline coherence.

    Rules:
    - Same name + overlapping contest dates at different orgs → NOT merged (could be different people)
    - Same name + non-overlapping dates at different orgs → merged (likely transferred)
    - Same name + same org → always merged

    Returns: dict of contestant_id → Contestant
    """
    # Group by name (regardless of org)
    by_name: dict[str, list[Contestant]] = defaultdict(list)
    for key, c in contestants.items():
        by_name[c.name].append(c)

    result: dict[str, Contestant] = {}

    for name, group in by_name.items():
        if len(group) == 1:
            c = group[0]
            result[c.id] = c
            continue

        # Sort records across all same-name contestants by date
        all_records = []
        for c in group:
            all_records.extend((r, c) for r in c.records)
        all_records.sort(key=lambda x: x[0].date)

        # Check for date overlaps between different orgs
        org_dates: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for record, c in all_records:
            org_dates[c.organization].append((record.date, record.date))

        # Check pairwise org overlap
        orgs = list(org_dates.keys())
        can_merge = True
        for i in range(len(orgs)):
            for j in range(i + 1, len(orgs)):
                dates_i = org_dates[orgs[i]]
                dates_j = org_dates[orgs[j]]
                # Check if date ranges overlap
                min_i = min(d[0] for d in dates_i)
                max_i = max(d[1] for d in dates_i)
                min_j = min(d[0] for d in dates_j)
                max_j = max(d[1] for d in dates_j)
                if min_i <= max_j and min_j <= max_i:
                    # Overlapping dates at different orgs — likely different people
                    can_merge = False
                    break
            if not can_merge:
                break

        if can_merge:
            # Merge all into the first contestant
            primary = group[0]
            for other in group[1:]:
                primary.records.extend(other.records)
            primary.records.sort(key=lambda r: r.date)
            # Update organization to the most recent one
            if primary.records:
                primary.organization = primary.records[-1].organization
            result[primary.id] = primary
        else:
            # Keep separate
            for c in group:
                result[c.id] = c

    return result
