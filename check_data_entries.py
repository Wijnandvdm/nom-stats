"""
Pre-commit checks for NomStats configuration files.

Runs three jobs in sequence:
  1. Strip leading/trailing whitespace from all fields in ingredients.csv (auto-fix).
  2. Validate the structure and content of ingredients.csv.
  3. Validate all recipe YAML files for correct structure, types, and ingredient references.

Exits 1 if the CSV was modified (user must re-stage) or if any issues are found.
"""

import csv
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

INGREDIENTS_CSV = Path("configuration/ingredients.csv")
RECIPES_DIR = Path("configuration")

VALID_DIETARY_LABELS = {"alcoholic", "non_alcoholic", "vegetarian"}

CSV_SCHEMA = pd.DataFrame(
    [
        {"column": "name", "is_numeric": False, "allowed_empty": False},
        {"column": "measurement_unit", "is_numeric": False, "allowed_empty": False},
        {"column": "weight_per_unit", "is_numeric": True, "allowed_empty": True},
        {"column": "protein_per_100g", "is_numeric": True, "allowed_empty": False},
        {"column": "fat_per_100g", "is_numeric": True, "allowed_empty": False},
        {"column": "carbohydrates_per_100g", "is_numeric": True, "allowed_empty": False},
        {"column": "calories_per_100g", "is_numeric": True, "allowed_empty": False},
        {"column": "alcohol_percentage", "is_numeric": True, "allowed_empty": False},
    ]
)


# ---------------------------------------------------------------------------
# CSV fixer
# ---------------------------------------------------------------------------


def fix_csv_spaces(path: Path) -> bool:
    """Strip leading/trailing whitespace from every field in the CSV. Returns True if changed."""
    with path.open(newline="") as f:
        rows = list(csv.reader(f))

    cleaned = [[field.strip() for field in row] for row in rows]
    if cleaned == rows:
        return False

    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cleaned)

    return True


# ---------------------------------------------------------------------------
# CSV validator
# ---------------------------------------------------------------------------


def check_required_columns(df: pd.DataFrame, schema: pd.DataFrame) -> list[str]:
    """Return issues for any schema columns missing from the CSV."""
    return [f"Missing required column: '{col}'" for col in schema["column"] if col not in df.columns]


def check_unexpected_columns(df: pd.DataFrame, schema: pd.DataFrame) -> list[str]:
    """Return a warning if the CSV contains columns not defined in the schema."""
    extra = set(df.columns) - set(schema["column"])
    if extra:
        return [
            f"Unexpected columns found: {', '.join(extra)}. "
            "Remove them or update the schema if they are intentional."
        ]
    return []


def check_missing_values(df: pd.DataFrame, schema: pd.DataFrame) -> list[str]:
    """Return issues for empty values in columns that do not allow them."""
    issues = []
    for _, row in schema.iterrows():
        col = row["column"]
        if row["allowed_empty"] or col not in df.columns:
            continue
        missing = df[df[col].isnull() | (df[col].astype(str).str.strip() == "")]
        for i, r in missing.iterrows():
            issues.append(f"Line {i + 2}: missing value for '{col}' (ingredient '{r.get('name', '?')}')")
    return issues


def check_numeric_columns(df: pd.DataFrame, schema: pd.DataFrame) -> list[str]:
    """Return issues for non-numeric or negative values in numeric columns."""
    issues = []
    for col in schema[schema["is_numeric"]]["column"]:
        if col not in df.columns:
            continue
        non_numeric = df[~df[col].apply(lambda x: str(x).replace(".", "", 1).isdigit() or pd.isna(x))]
        if not non_numeric.empty:
            issues.append(f"Column '{col}' contains non-numeric values.")
        negatives = df[pd.to_numeric(df[col], errors="coerce") < 0]
        if not negatives.empty:
            issues.append(f"Column '{col}' contains negative values.")
    return issues


def check_measurement_units(df: pd.DataFrame) -> list[str]:
    """Return issues for non-base units that are missing a weight_per_unit conversion."""
    if "measurement_unit" not in df.columns:
        return []
    base_units = {"g", "ml"}
    mismatches = df[
        (~df["measurement_unit"].isin(base_units))
        & (df["weight_per_unit"].isnull() | (df["weight_per_unit"] == ""))
    ]
    return [
        f"Line {i + 2}: '{row['name']}' uses unit '{row['measurement_unit']}' "
        "but has no weight_per_unit conversion."
        for i, row in mismatches.iterrows()
    ]


def check_lowercase_names(df: pd.DataFrame) -> list[str]:
    """Return issues for ingredient names containing uppercase letters."""
    if "name" not in df.columns:
        return []
    bad = df[df["name"].astype(str).str.contains(r"[A-Z]", regex=True)]
    return [f"Ingredient name contains uppercase letters: '{row['name']}'" for _, row in bad.iterrows()]


def check_duplicate_names(df: pd.DataFrame) -> list[str]:
    """Return issues for duplicate or missing ingredient names."""
    if "name" not in df.columns:
        return ["Missing column: 'name'"]
    issues = []
    duplicates = df["name"][df["name"].duplicated()].unique()
    if len(duplicates):
        issues.append(f"Duplicate ingredient names found: {', '.join(duplicates)}")
    if df["name"].isnull().any():
        issues.append("Some ingredients have no name.")
    return issues


def validate_ingredients_csv(path: Path) -> list[str]:
    """Run all CSV checks. Returns a list of issue strings (empty means clean)."""
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return [f"Could not read CSV: {e}"]

    issues = []
    issues.extend(check_required_columns(df, CSV_SCHEMA))
    issues.extend(check_unexpected_columns(df, CSV_SCHEMA))
    issues.extend(check_missing_values(df, CSV_SCHEMA))
    issues.extend(check_numeric_columns(df, CSV_SCHEMA))
    issues.extend(check_measurement_units(df))
    issues.extend(check_lowercase_names(df))
    issues.extend(check_duplicate_names(df))
    return issues


# ---------------------------------------------------------------------------
# YAML validator
# ---------------------------------------------------------------------------


def _load_known_ingredients(path: Path) -> set[str]:
    """Return the set of ingredient names from ingredients.csv."""
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Cannot read ingredients.csv: {e}")
        sys.exit(1)

    if "name" not in df.columns:
        print("ingredients.csv is missing the required 'name' column.")
        sys.exit(1)

    return set(df["name"].dropna().astype(str).str.strip())


def _check_ingredient_entry(item: Any, location: str) -> list[str]:
    """Validate a single ingredient dict has a string name and numeric quantity."""
    if not isinstance(item, dict):
        return [f"{location}: ingredient entry must be a mapping, got {type(item).__name__}"]

    issues = []
    if "name" not in item:
        issues.append(f"{location}: ingredient entry missing 'name'")
    elif not isinstance(item["name"], str) or not item["name"].strip():
        issues.append(f"{location}: ingredient 'name' must be a non-empty string")

    if "quantity" not in item:
        issues.append(f"{location}: ingredient '{item.get('name', '?')}' missing 'quantity'")
    elif not isinstance(item["quantity"], (int, float)):
        issues.append(f"{location}: ingredient '{item.get('name', '?')}' quantity must be a number")

    return issues


def _get_flat_ingredients(data: dict) -> list[dict]:
    """Flatten ingredients from either the top-level list, nested components, or all variants."""
    if "components" in data:
        return [i for c in data["components"] for i in c.get("ingredients", [])]
    if "variants" in data:
        return [i for v in data["variants"].values() for i in v.get("ingredients", [])]
    return data.get("ingredients", [])


def check_recipe(file: Path, known: set[str]) -> list[str]:
    """
    Validate a single recipe YAML against the expected schema.

    Checks:
    - recipe_name is present and a non-empty string
    - rating and spice_level are integers in the range 0–5
    - description and steps are the correct types when present
    - dietary_labels only contains known values
    - exactly one of 'ingredients', 'components', or 'variants' is present, with valid entries
    - all ingredient names exist in ingredients.csv
    """
    loc = str(file)

    try:
        with file.open() as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"{loc}: could not parse YAML: {e}"]

    if not isinstance(data, dict):
        return [f"{loc}: expected a YAML mapping at the top level"]

    issues = []

    if "recipe_name" not in data:
        issues.append(f"{loc}: missing required key 'recipe_name'")
    elif not isinstance(data["recipe_name"], str) or not data["recipe_name"].strip():
        issues.append(f"{loc}: 'recipe_name' must be a non-empty string")

    if "description" in data and not isinstance(data["description"], str):
        issues.append(f"{loc}: 'description' must be a string")

    for key in ("rating", "spice_level"):
        if key in data:
            val = data[key]
            if not isinstance(val, int):
                issues.append(f"{loc}: '{key}' must be an integer, got {type(val).__name__}")
            elif not (0 <= val <= 5):
                issues.append(f"{loc}: '{key}' must be between 0 and 5, got {val}")

    if "steps" in data:
        if not isinstance(data["steps"], list):
            issues.append(f"{loc}: 'steps' must be a list")
        elif not all(isinstance(s, str) for s in data["steps"]):
            issues.append(f"{loc}: all entries in 'steps' must be strings")

    if "dietary_labels" in data:
        labels = data["dietary_labels"]
        if not isinstance(labels, list):
            issues.append(f"{loc}: 'dietary_labels' must be a list")
        else:
            for label in labels:
                if label not in VALID_DIETARY_LABELS:
                    issues.append(
                        f"{loc}: unknown dietary label '{label}' "
                        f"(valid: {', '.join(sorted(VALID_DIETARY_LABELS))})"
                    )

    has_ingredients = "ingredients" in data
    has_components = "components" in data
    has_variants = "variants" in data

    if sum([has_ingredients, has_components, has_variants]) == 0:
        issues.append(f"{loc}: must have either 'ingredients', 'components', or 'variants'")
    elif sum([has_ingredients, has_components, has_variants]) > 1:
        issues.append(f"{loc}: cannot combine 'ingredients', 'components', and 'variants' — pick one")
    elif has_ingredients:
        if not isinstance(data["ingredients"], list):
            issues.append(f"{loc}: 'ingredients' must be a list")
        else:
            for item in data["ingredients"]:
                issues.extend(_check_ingredient_entry(item, loc))
    elif has_components:
        if not isinstance(data["components"], list):
            issues.append(f"{loc}: 'components' must be a list")
        else:
            for comp in data["components"]:
                if not isinstance(comp, dict):
                    issues.append(f"{loc}: each component must be a mapping")
                    continue
                if "name" not in comp or not isinstance(comp["name"], str):
                    issues.append(f"{loc}: each component must have a string 'name'")
                comp_ingredients = comp.get("ingredients", [])
                if not isinstance(comp_ingredients, list):
                    issues.append(f"{loc}: component '{comp.get('name', '?')}' 'ingredients' must be a list")
                else:
                    for item in comp_ingredients:
                        issues.extend(_check_ingredient_entry(item, loc))
    else:
        if not isinstance(data["variants"], dict):
            issues.append(f"{loc}: 'variants' must be a mapping")
        else:
            for variant_name, variant_content in data["variants"].items():
                if not isinstance(variant_content, dict):
                    issues.append(f"{loc}: variant '{variant_name}' must be a mapping")
                    continue
                v_ingredients = variant_content.get("ingredients", [])
                if not isinstance(v_ingredients, list):
                    issues.append(f"{loc}: variant '{variant_name}' 'ingredients' must be a list")
                else:
                    for item in v_ingredients:
                        issues.extend(_check_ingredient_entry(item, f"{loc} (variant '{variant_name}')"))

    for item in _get_flat_ingredients(data):
        name = item.get("name") if isinstance(item, dict) else None
        if name and name not in known:
            issues.append(f"{loc}: ingredient '{name}' not found in ingredients.csv")

    return issues


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    csv_fixed = fix_csv_spaces(INGREDIENTS_CSV)
    if csv_fixed:
        print("Stripped whitespace from ingredients.csv — file modified, please re-stage it.")

    csv_issues = validate_ingredients_csv(INGREDIENTS_CSV)
    for issue in csv_issues:
        print(issue)

    known = _load_known_ingredients(INGREDIENTS_CSV)
    yaml_issues = []
    for file in RECIPES_DIR.rglob("*.yaml"):
        yaml_issues.extend(check_recipe(file, known))
    for issue in yaml_issues:
        print(issue)

    if csv_fixed or csv_issues or yaml_issues:
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
