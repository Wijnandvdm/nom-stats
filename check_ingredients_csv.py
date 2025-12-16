import sys
from typing import List

import pandas as pd

# === Step 1: Define schema ===
SCHEMA = pd.DataFrame(
    [
        {"column": "name", "is_numeric": False, "allowed_empty": False},
        {"column": "measurement_unit", "is_numeric": False, "allowed_empty": False},
        {"column": "weight_per_unit", "is_numeric": True, "allowed_empty": True},
        {"column": "protein_per_100g", "is_numeric": True, "allowed_empty": False},
        {"column": "fat_per_100g", "is_numeric": True, "allowed_empty": False},
        {
            "column": "carbohydrates_per_100g",
            "is_numeric": True,
            "allowed_empty": False,
        },
        {"column": "calories_per_100g", "is_numeric": True, "allowed_empty": False},
        {"column": "alcohol_percentage", "is_numeric": True, "allowed_empty": False},
    ]
)


# === Step 2: Validation functions ===
def check_required_columns(df: pd.DataFrame, schema: pd.DataFrame) -> List[str]:
    """Ensure all required columns in schema exist in CSV."""
    issues = []
    for col in schema["column"]:
        if col not in df.columns:
            issues.append(f"Missing required column: '{col}'")
    return issues


def check_unexpected_columns(df: pd.DataFrame, schema: pd.DataFrame) -> List[str]:
    """Warn if CSV contains columns that are not in the expected schema."""
    issues = []
    expected_cols = set(schema["column"])
    actual_cols = set(df.columns)
    extra_cols = actual_cols - expected_cols

    if extra_cols:
        issues.append(
            f"Unexpected columns found: {', '.join(extra_cols)}. "
            "Please remove them or update the schema if they are new valid fields."
        )

    return issues


def check_missing_values(df: pd.DataFrame, schema: pd.DataFrame) -> List[str]:
    """Ensure that non-optional columns are not empty."""
    issues = []
    for _, row in schema.iterrows():
        col = row["column"]
        if row["allowed_empty"]:
            continue
        if col not in df.columns:
            continue
        missing_mask = df[col].isnull() | (df[col].astype(str).str.strip() == "")
        if missing_mask.any():
            missing_rows = df[missing_mask]
            for i, r in missing_rows.iterrows():
                issues.append(f"Line {i + 2}: Missing value for '{col}' (ingredient '{r.get('name', '?')}')")
    return issues


def check_numeric_columns(df: pd.DataFrame, schema: pd.DataFrame) -> List[str]:
    """Validate numeric columns based on schema flags."""
    issues = []
    numeric_cols = schema[schema["is_numeric"]]["column"]
    for col in numeric_cols:
        if col not in df.columns:
            continue

        # Non-numeric check
        non_numeric = df[~df[col].apply(lambda x: str(x).replace(".", "", 1).isdigit() or pd.isna(x))]
        if not non_numeric.empty:
            issues.append(f"Column '{col}' contains non-numeric values.")

        # Negative check
        negatives = df[pd.to_numeric(df[col], errors="coerce") < 0]
        if not negatives.empty:
            issues.append(f"Column '{col}' contains negative values.")
    return issues


def check_duplicate_names(df: pd.DataFrame) -> List[str]:
    issues = []
    if "name" not in df.columns:
        return ["Missing column: 'name'"]
    duplicates = df["name"][df["name"].duplicated()].unique()
    if len(duplicates) > 0:
        issues.append(f"Duplicate ingredient names found: {', '.join(duplicates)}")
    if df["name"].isnull().any():
        issues.append("Some ingredients have no name.")
    return issues


def check_measurement_units(df: pd.DataFrame) -> List[str]:
    """Special rule: measurement_unit consistency with weight_per_unit"""
    issues = []
    if "measurement_unit" not in df.columns:
        return issues

    base_units = {"g", "ml"}
    mismatches = df[
        (~df["measurement_unit"].isin(base_units))
        & (df["weight_per_unit"].isnull() | (df["weight_per_unit"] == ""))
    ]
    if not mismatches.empty:
        for i, row in mismatches.iterrows():
            issues.append(
                f"Line {i + 2}: ingredient '{row['name']}' uses '{row['measurement_unit']}' "
                f"but has no 'weight_per_unit'. Consider using {base_units} or add a conversion."
            )
    return issues


# === Step 3: Orchestrator ===
def validate_ingredients_csv(csv_path: str) -> List[str]:
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return [f"Could not read CSV: {e}"]

    issues = []
    issues.extend(check_required_columns(df, SCHEMA))
    issues.extend(check_unexpected_columns(df, SCHEMA))
    issues.extend(check_missing_values(df, SCHEMA))
    issues.extend(check_numeric_columns(df, SCHEMA))
    issues.extend(check_measurement_units(df))
    issues.extend(check_duplicate_names(df))

    if not issues:
        return ["No issues found. CSV looks good!"]
    return issues


# === Step 4: CLI usage ===
if __name__ == "__main__":
    problems = validate_ingredients_csv("configuration/ingredients.csv")
    for p in problems:
        print(p)
    if any(p for p in problems if not p.startswith("No issues found")):
        sys.exit(1)
