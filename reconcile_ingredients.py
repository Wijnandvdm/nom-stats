"""
reconcile_ingredients.py

1. Deduplicates off_ingredients.csv by name (in-place, keeps first occurrence).
2. For each entry in configuration/ingredients.csv, checks whether it is covered
   by off_ingredients.csv:
     - First tries an exact name match (case-insensitive).
     - If that fails, offers fuzzy candidates interactively, showing both names
       and nutritional values side-by-side so you can make an informed call.

Usage:
    python reconcile_ingredients.py
"""

import csv
import os
import sys
from typing import Optional

from rapidfuzz import fuzz
from rapidfuzz import process as fuzz_process

OFF_CSV = "off_ingredients.csv"
CURATED_CSV = os.path.join("configuration", "ingredients.csv")

FUZZY_THRESHOLD = 45  # minimum score (0-100) to show a candidate
TOP_N = 5  # max fuzzy candidates to display

NUTR_FIELDS = [
    ("calories_per_100g", "kcal"),
    ("protein_per_100g", "prot"),
    ("fat_per_100g", "fat"),
    ("carbohydrates_per_100g", "carbs"),
    ("alcohol_percentage", "abv%"),
]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Step 1: Deduplication
# ---------------------------------------------------------------------------


def deduplicate(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    seen: dict[str, bool] = {}
    deduped: list[dict[str, str]] = []
    for row in rows:
        key = (row["name"].strip().lower(), row["measurement_unit"].strip())
        if key not in seen:
            seen[key] = True
            deduped.append(row)
    return deduped, len(rows) - len(deduped)


# ---------------------------------------------------------------------------
# Step 2: Matching helpers
# ---------------------------------------------------------------------------


def nutr_str(row: dict[str, str]) -> str:
    """Format nutritional values as a compact display string."""
    parts = []
    for field, label in NUTR_FIELDS:
        val = row.get(field, "")
        parts.append(f"{label}={val or '—':>6}")
    return "  ".join(parts)


def print_comparison(curated_row: dict[str, str], off_row: dict[str, str], score: Optional[float] = None) -> None:
    score_str = f"  (similarity: {score:.0f}%)" if score is not None else ""
    print(f"    OFF name : {off_row['name']}{score_str}")
    print(f"    OFF vals : {nutr_str(off_row)}")
    print(f"    Your vals: {nutr_str(curated_row)}")


def find_exact(curated_row: dict[str, str], off_by_name: dict[str, dict[str, str]]) -> Optional[dict[str, str]]:
    candidate = off_by_name.get(curated_row["name"].strip().lower())
    if candidate is None:
        return None
    if candidate["measurement_unit"].strip() != curated_row["measurement_unit"].strip():
        return None
    return candidate


def find_fuzzy_candidates(
    name: str,
    off_names: list[str],
    off_by_name: dict[str, dict[str, str]],
) -> list[tuple[dict[str, str], float]]:
    results = fuzz_process.extract(
        name,
        off_names,
        scorer=fuzz.token_sort_ratio,
        limit=TOP_N,
        score_cutoff=FUZZY_THRESHOLD,
    )
    return [(off_by_name[match], score) for match, score, _ in results]


# ---------------------------------------------------------------------------
# Interactive prompt for fuzzy candidates
# ---------------------------------------------------------------------------


def prompt_fuzzy(
    curated_row: dict[str, str],
    candidates: list[tuple[dict[str, str], float]],
    idx: int,
    total: int,
) -> Optional[dict[str, str]]:
    """
    Display candidates and ask the user to pick one, skip, or mark as unmatched.
    Returns the chosen OFF row, or None if skipped/unmatched.
    """
    name = curated_row["name"]
    print(f"\n{'─' * 70}")
    print(f"[{idx}/{total}] No exact match for: '{name}'")
    print(f"  Your vals: {nutr_str(curated_row)}")
    print("  Top fuzzy candidates:")

    for i, (off_row, score) in enumerate(candidates, start=1):
        print(f"\n    [{i}] '{off_row['name']}'  (similarity: {score:.0f}%)")
        print(f"        OFF vals : {nutr_str(off_row)}")

    valid = [str(i) for i in range(1, len(candidates) + 1)]
    prompt = f"\n  Pick match [{'/'.join(valid)}], s=skip, n=no match, q=quit: "

    while True:
        choice = input(prompt).strip().lower()
        if choice == "q":
            print("\nQuitting. Summary will not be printed.")
            sys.exit(0)
        if choice == "s":
            return None
        if choice == "n":
            return None
        if choice in valid:
            chosen = candidates[int(choice) - 1][0]
            print(f"  ✓ Matched to '{chosen['name']}'")
            return chosen
        print("  Invalid input, try again.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # --- Sanity checks ---
    if not os.path.exists(OFF_CSV):
        print(f"Error: '{OFF_CSV}' not found. Run fetch_off_ingredients.py first.")
        sys.exit(1)
    if not os.path.exists(CURATED_CSV):
        print(f"Error: '{CURATED_CSV}' not found.")
        sys.exit(1)

    # --- Step 1: Deduplicate off_ingredients.csv ---
    print(f"Loading {OFF_CSV}...")
    off_rows = load_csv(OFF_CSV)
    off_fieldnames = list(off_rows[0].keys()) if off_rows else []

    deduped_rows, n_dupes = deduplicate(off_rows)
    if n_dupes > 0:
        print(f"Removed {n_dupes} duplicate name(s) from {OFF_CSV}. Saving...")
        write_csv(OFF_CSV, deduped_rows, off_fieldnames)
    else:
        print(f"No duplicates found in {OFF_CSV}.")

    off_by_name: dict[str, dict[str, str]] = {row["name"].strip().lower(): row for row in deduped_rows}
    off_names = list(off_by_name.keys())

    # --- Step 2: Check coverage ---
    print(f"\nLoading {CURATED_CSV}...")
    curated_rows = load_csv(CURATED_CSV)
    total = len(curated_rows)
    print(f"Checking {total} curated ingredients against {len(off_names)} OFF products...\n")

    matched_exact: list[str] = []
    matched_fuzzy: list[tuple[str, str]] = []  # (curated name, off name)
    unmatched: list[str] = []

    fuzzy_needed = [r for r in curated_rows if not find_exact(r, off_by_name)]

    # Print exact matches first
    for row in curated_rows:
        name = row["name"]
        if find_exact(row, off_by_name):
            matched_exact.append(name)
            print(f"  ✓ exact  '{name}'  [{row['measurement_unit']}]")

    # Interactive fuzzy pass
    for i, curated_row in enumerate(fuzzy_needed, start=1):
        name = curated_row["name"]
        candidates = find_fuzzy_candidates(name, off_names, off_by_name)

        if not candidates:
            print(f"\n{'─' * 70}")
            print(f"[{i}/{len(fuzzy_needed)}] No candidates at all for: '{name}' — marking unmatched.")
            unmatched.append(name)
            continue

        chosen = prompt_fuzzy(curated_row, candidates, i, len(fuzzy_needed))
        if chosen:
            matched_fuzzy.append((name, chosen["name"]))
        else:
            unmatched.append(name)

    # --- Summary ---
    print(f"\n{'═' * 70}")
    print(f"SUMMARY  ({total} curated ingredients)")
    print(f"{'═' * 70}")
    print(f"  ✓ Exact matches  : {len(matched_exact)}")
    print(f"  ~ Fuzzy matches  : {len(matched_fuzzy)}")
    print(f"  ✗ Unmatched      : {len(unmatched)}")
    print()

    if matched_fuzzy:
        print("Fuzzy matches accepted:")
        for curated_name, off_name in matched_fuzzy:
            print(f"  '{curated_name}'  →  '{off_name}'")
        print()

    if unmatched:
        print("Not covered in off_ingredients.csv:")
        for name in unmatched:
            print(f"  ✗ '{name}'")
    else:
        print("All curated ingredients are covered!")


if __name__ == "__main__":
    main()
