"""
Fetches Dutch products from Open Food Facts and writes them to a CSV
in the same format as configuration/ingredients.csv.

Supports resuming interrupted runs via a checkpoint file.

Usage:
    python fetch_off_ingredients.py [output_file] [--max-pages N]

Defaults:
    output_file : off_ingredients.csv
    max-pages   : no limit (fetches everything)

Open Food Facts API docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
"""

import csv
import json
import os
import sys
import time
from typing import Optional

import requests

OFF_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/search"
PAGE_SIZE = 100  # OFF API silently caps at 100
DELAY_BETWEEN_PAGES = 1.0  # seconds — be a good API citizen
REQUEST_TIMEOUT = 90  # seconds — OFF can be slow on large pages
MAX_RETRIES = 3
RETRY_BACKOFF = [10, 30, 60]  # seconds to wait before each retry attempt

CSV_HEADERS = [
    "name",
    "measurement_unit",
    "weight_per_unit",
    "protein_per_100g",
    "calories_per_100g",
    "fat_per_100g",
    "carbohydrates_per_100g",
    "alcohol_percentage",
]

FIELDS = ",".join(
    [
        "product_name",
        "product_name_nl",
        "nutriments",
        "quantity",
    ]
)


# --- Checkpoint helpers ---


def checkpoint_path(output_file: str) -> str:
    return output_file + ".checkpoint.json"


def load_checkpoint(output_file: str) -> Optional[dict]:  # type: ignore[type-arg]
    path = checkpoint_path(output_file)
    if os.path.exists(path) and os.path.exists(output_file):
        with open(path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    return None


def save_checkpoint(output_file: str, page: int, total_written: int, total_fetched: int) -> None:
    path = checkpoint_path(output_file)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"last_completed_page": page, "total_written": total_written, "total_fetched": total_fetched},
            f,
            indent=2,
        )


def delete_checkpoint(output_file: str) -> None:
    path = checkpoint_path(output_file)
    if os.path.exists(path):
        os.remove(path)


# --- Data helpers ---


def guess_unit(quantity: str) -> str:
    """Determine measurement unit (g or ml) from the product quantity string."""
    q = quantity.lower()
    if any(unit in q for unit in ["ml", " l", "cl", "dl", "liter", "litre"]):
        return "ml"
    return "g"


def abv_from_alcohol_100g(alcohol_100g: float) -> float:
    """
    Convert grams of alcohol per 100g product to approximate ABV%.
    Ethanol density ≈ 0.789 g/ml, so: ABV% ≈ alcohol_100g / 0.789.
    This is an approximation that assumes product density ≈ 1 g/ml.
    """
    return round(alcohol_100g / 0.789, 1)


def extract_row(product: dict) -> Optional[dict[str, object]]:  # type: ignore[type-arg]
    """Extract a CSV row from an Open Food Facts product dict, or None if unusable."""
    nutriments = product.get("nutriments", {})

    calories: Optional[float] = nutriments.get("energy-kcal_100g")
    protein: Optional[float] = nutriments.get("proteins_100g")
    fat: Optional[float] = nutriments.get("fat_100g")
    carbs: Optional[float] = nutriments.get("carbohydrates_100g")

    if any(v is None for v in [calories, protein, fat, carbs]):
        return None

    name = (product.get("product_name_nl") or product.get("product_name") or "").strip().lower()
    if not name:
        return None

    alcohol_100g: float = nutriments.get("alcohol_100g") or 0.0
    alcohol_pct = abv_from_alcohol_100g(alcohol_100g) if alcohol_100g > 0 else 0

    unit = guess_unit(product.get("quantity") or "")

    return {
        "name": name,
        "measurement_unit": unit,
        "weight_per_unit": "",  # only relevant for stuks (pieces), can't automate
        "protein_per_100g": round(protein, 1),  # type: ignore[arg-type]
        "calories_per_100g": round(calories, 1),  # type: ignore[arg-type]
        "fat_per_100g": round(fat, 1),  # type: ignore[arg-type]
        "carbohydrates_per_100g": round(carbs, 1),  # type: ignore[arg-type]
        "alcohol_percentage": alcohol_pct,
    }


# --- API fetch with retry ---


def fetch_page(page: int) -> dict:  # type: ignore[type-arg]
    params = {
        "countries_tags": "en:netherlands",
        "fields": FIELDS,
        "page_size": PAGE_SIZE,
        "page": page,
        "json": 1,
    }
    last_error: Exception = RuntimeError("unreachable")
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(OFF_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_error = e
            wait = RETRY_BACKOFF[attempt]
            print(f"\n    Timeout/connection error (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {wait}s...")
            time.sleep(wait)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Non-retryable request error: {e}") from e
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts: {last_error}") from last_error


# --- Main ---


def main() -> None:
    output_file = "off_ingredients.csv"
    max_pages: Optional[int] = None

    args = sys.argv[1:]
    if args and not args[0].startswith("--"):
        output_file = args.pop(0)
    if "--max-pages" in args:
        idx = args.index("--max-pages")
        max_pages = int(args[idx + 1])

    checkpoint = load_checkpoint(output_file)
    if checkpoint:
        resume_from = checkpoint["last_completed_page"] + 1
        total_written = checkpoint["total_written"]
        total_fetched = checkpoint["total_fetched"]
        print(f"Resuming from page {resume_from} (already written: {total_written} products)")
        csv_mode = "a"  # append — don't overwrite existing rows
        write_header = False
    else:
        resume_from = 1
        total_written = 0
        total_fetched = 0
        print(f"Fetching Dutch products from Open Food Facts → {output_file}")
        csv_mode = "w"
        write_header = True

    if max_pages:
        print(f"Limited to {max_pages} page(s) from start ({max_pages * PAGE_SIZE} products max)")

    with open(output_file, csv_mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()

        page = resume_from
        while True:
            if max_pages and page > max_pages:
                break

            print(f"  Page {page}...", end=" ", flush=True)

            try:
                data = fetch_page(page)
            except RuntimeError as e:
                print(f"\nGiving up: {e}")
                print(f"Progress saved. Re-run the script to resume from page {page}.")
                save_checkpoint(output_file, page - 1, total_written, total_fetched)
                sys.exit(1)

            products = data.get("products", [])
            if not products:
                print("no more products.")
                break

            written = 0
            for product in products:
                row = extract_row(product)
                if row:
                    writer.writerow(row)
                    written += 1

            f.flush()  # make sure data hits disk before we update the checkpoint

            total_fetched += len(products)
            total_written += written
            db_count: Optional[int] = data.get("count")
            print(f"{written}/{len(products)} usable  (running total: {total_written}, db total: {db_count or '?'})")

            save_checkpoint(output_file, page, total_written, total_fetched)

            if db_count is not None and total_fetched >= db_count:
                break

            page += 1
            time.sleep(DELAY_BETWEEN_PAGES)

    delete_checkpoint(output_file)
    print(f"\nDone. {total_written}/{total_fetched} products written to {output_file}")
    print("Note: 'weight_per_unit' is left empty — fill in manually for 'stuks' items.")
    print("Note: 'alcohol_percentage' is an ABV% approximation (alcohol_100g / 0.789).")


if __name__ == "__main__":
    main()
