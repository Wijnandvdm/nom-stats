import sys
from pathlib import Path

import pandas as pd
import yaml

INGREDIENTS_CSV = Path("configuration/ingredients.csv")
RECIPES_DIR = Path("configuration")


def load_known_ingredients() -> set[str]:
    """Read ingredients.csv and return a set of known ingredient names."""
    try:
        df = pd.read_csv(INGREDIENTS_CSV)
    except Exception as e:
        print(f"❌ Cannot read ingredients.csv: {e}")
        sys.exit(1)

    if "name" not in df.columns:
        print("❌ CSV is missing required column 'name'.")
        sys.exit(1)

    return set(df["name"].dropna().astype(str).str.strip())


def find_recipe_files() -> list[Path]:
    """Find all YAML recipe files under configuration/**."""
    return list(RECIPES_DIR.rglob("*.yaml"))


def check_recipe(file: Path, known: set[str]) -> list[str]:
    issues = []
    try:
        with file.open() as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"❌ Could not parse YAML file {file}: {e}"]

    ingredients = data.get("ingredients", [])
    if not isinstance(ingredients, list):
        return [f"❌ Invalid 'ingredients' structure in {file}"]

    for item in ingredients:
        name = item.get("name")
        if name is None:
            issues.append(f"❌ {file}: ingredient entry without a 'name' key")
            continue

        if name not in known:
            issues.append(f"❌ {file}: ingredient '{name}' not found in ingredients.csv")

    return issues


def main():
    known = load_known_ingredients()
    recipe_files = find_recipe_files()

    all_issues = []
    for file in recipe_files:
        all_issues.extend(check_recipe(file, known))

    if not all_issues:
        print("✅ All recipe YAML files reference valid ingredient names.")
        return 0

    for issue in all_issues:
        print(issue)

    return 1


if __name__ == "__main__":
    sys.exit(main())
