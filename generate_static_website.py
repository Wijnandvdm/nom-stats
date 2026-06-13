import csv
import os
import re
from typing import Any, Dict, List, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "static_site"
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configuration")
INGREDIENTS_FILE = os.path.join(CONFIG_DIR, "ingredients.csv")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"'{OUTPUT_DIR}' didn't exist yet, folder created! Moving on...")


def load_ingredients_csv(ingredients_file: str) -> dict:
    ingredients = {}
    with open(ingredients_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ingredients[row["name"]] = {
                "name": row["name"],
                "measurement_unit": row["measurement_unit"],
                "weight_per_unit": float(row["weight_per_unit"]) if row["weight_per_unit"] else 0,
                "components": [
                    {
                        "name": "protein",
                        "quantity_per_100_g": float(row.get("protein_per_100g", 0) or 0),
                    },
                    {
                        "name": "calories",
                        "quantity_per_100_g": float(row.get("calories_per_100g", 0) or 0),
                    },
                    {
                        "name": "fat",
                        "quantity_per_100_g": float(row.get("fat_per_100g", 0) or 0),
                    },
                    {
                        "name": "carbohydrates",
                        "quantity_per_100_g": float(row.get("carbohydrates_per_100g", 0) or 0),
                    },
                ],
                "alcohol_percentage": float(row["alcohol_percentage"])
                if row.get("alcohol_percentage")
                else 0,
            }
    return ingredients


def _get_flat_ingredients(yaml_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    if "components" in yaml_content:
        return [i for c in yaml_content["components"] for i in c.get("ingredients", [])]
    return yaml_content.get("ingredients", [])


def _format_ingredient_display(recipe_ingredient: dict, ingredient: dict) -> dict:
    quantity = recipe_ingredient.get("quantity", 0)
    name = recipe_ingredient["name"]
    weight_per_unit = ingredient.get("weight_per_unit", 0)
    measurement_unit = ingredient.get("measurement_unit")
    if weight_per_unit:
        display = f"{float(quantity)} {measurement_unit} {name}"
    else:
        display = f"{quantity} {measurement_unit} {name}"
    return {"display": display, "slug": slugify(name), "recipe_reference": recipe_ingredient.get("recipe_reference")}


def _build_display_components(
    yaml_content: Dict[str, Any],
    all_ingredients: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    def resolve(ingredient_list):
        result = []
        for ri in ingredient_list:
            ingredient = all_ingredients.get(ri["name"])
            if ingredient:
                result.append(_format_ingredient_display(ri, ingredient))
        return result

    if "components" in yaml_content:
        return [
            {"name": c["name"], "ingredients": resolve(c.get("ingredients", []))}
            for c in yaml_content["components"]
        ]
    return [{"name": None, "ingredients": resolve(yaml_content.get("ingredients", []))}]


def calculate_nutrition(
    ingredient_list: List[Dict[str, Any]],
    all_ingredients: Dict[str, Dict[str, Any]],
) -> Tuple[int, int, float, float, int, int, float, float, float]:
    total_protein = total_calories = total_weight = 0
    total_alcohol_ml = total_fat = total_carbs = 0

    for recipe_ingredient in ingredient_list:
        ingredient_name = recipe_ingredient["name"]
        quantity = recipe_ingredient.get("quantity", 0)
        ingredient = all_ingredients.get(ingredient_name)

        if ingredient:
            weight_per_unit = ingredient.get("weight_per_unit", 0)
            if weight_per_unit:
                quantity *= weight_per_unit
            total_weight += quantity

            protein_per_100g = next(
                (c["quantity_per_100_g"] for c in ingredient["components"] if c["name"] == "protein"),
                0,
            )
            calories_per_100g = next(
                (c["quantity_per_100_g"] for c in ingredient["components"] if c["name"] == "calories"),
                0,
            )
            fat_per_100g = next(
                (c["quantity_per_100_g"] for c in ingredient["components"] if c["name"] == "fat"),
                0,
            )
            carbs_per_100g = next(
                (c["quantity_per_100_g"] for c in ingredient["components"] if c["name"] == "carbohydrates"),
                0,
            )
            total_protein += round((quantity * protein_per_100g) / 100)
            total_calories += round((quantity * calories_per_100g) / 100)
            total_fat += round((quantity * fat_per_100g) / 100)
            total_carbs += round((quantity * carbs_per_100g) / 100)

            abv = ingredient.get("alcohol_percentage", 0)
            if abv > 0:
                total_alcohol_ml += (quantity * abv) / 100

    protein_per_100g = round((total_protein / total_weight) * 100, 1) if total_weight else 0
    calories_per_100g = round((total_calories / total_weight) * 100) if total_weight else 0
    fat_per_100g = round((total_fat / total_weight) * 100, 1) if total_weight else 0
    carbs_per_100g = round((total_carbs / total_weight) * 100, 1) if total_weight else 0
    alcohol_percentage = round((total_alcohol_ml / total_weight) * 100, 1) if total_weight else 0

    return (
        total_protein,
        total_calories,
        protein_per_100g,
        calories_per_100g,
        total_fat,
        total_carbs,
        fat_per_100g,
        carbs_per_100g,
        alcohol_percentage,
    )


def process_all_recipes(
    directory: str,
    all_ingredients: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
    categories = {}
    all_recipes = []

    for category in os.listdir(directory):
        category_path = os.path.join(directory, category)
        if os.path.isdir(category_path):
            category_recipes = []
            category_recipe_names = []

            for filename in os.listdir(category_path):
                if filename.endswith(".yaml") and filename != "ingredients.yaml":
                    filepath = os.path.join(category_path, filename)
                    with open(filepath, "r") as file:
                        yaml_content = yaml.safe_load(file)

                    if "recipe_name" in yaml_content:
                        flat_ingredients = _get_flat_ingredients(yaml_content)
                        (
                            total_protein,
                            total_calories,
                            protein_100g,
                            calories_100g,
                            total_fat,
                            total_carbs,
                            fat_100g,
                            carbs_100g,
                            alcohol_percentage,
                        ) = calculate_nutrition(flat_ingredients, all_ingredients)

                        recipe_data = {
                            "name": yaml_content["recipe_name"],
                            "description": yaml_content.get("description", ""),
                            "protein_100g": protein_100g,
                            "calories_100g": calories_100g,
                            "total_protein": total_protein,
                            "total_calories": total_calories,
                            "fat_100g": fat_100g,
                            "carbs_100g": carbs_100g,
                            "total_fat": total_fat,
                            "total_carbs": total_carbs,
                            "components": _build_display_components(yaml_content, all_ingredients),
                            "steps": yaml_content.get("steps", []),
                            "rating": yaml_content.get("rating", 0),
                            "spice_level": yaml_content.get("spice_level", 0),
                            "preparation_time": yaml_content.get("preparation_time"),
                            "filename": filename.replace(".yaml", ".html"),
                            "dietary_labels": yaml_content.get("dietary_labels", []),
                            "category": category.title(),
                        }

                        labels = recipe_data["dietary_labels"]
                        if "alcoholic" in labels or "non_alcoholic" in labels:
                            recipe_data["alcohol_percentage"] = alcohol_percentage

                        category_recipe_names.append(recipe_data)
                        category_recipes.append(recipe_data)
                        all_recipes.append(recipe_data)

            if category_recipe_names:
                categories[category.title()] = category_recipe_names

    return categories, all_recipes


def generate_static_pages() -> None:
    all_ingredients = load_ingredients_csv(INGREDIENTS_FILE)
    categories, recipes = process_all_recipes(CONFIG_DIR, all_ingredients)

    index_template = env.get_template("index.html")
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as file:
        file.write(index_template.render(categories=categories, recipes=recipes))

    recipe_template = env.get_template("recipe_detail.html")
    for recipe in recipes:
        with open(os.path.join(OUTPUT_DIR, recipe["filename"]), "w") as file:
            file.write(recipe_template.render(recipe=recipe))

    ingredients_dir = os.path.join(OUTPUT_DIR, "ingredients")
    os.makedirs(ingredients_dir, exist_ok=True)
    ingredient_template = env.get_template("ingredient_detail.html")
    for ingredient in all_ingredients.values():
        slug = slugify(ingredient["name"])
        with open(os.path.join(ingredients_dir, f"{slug}.html"), "w") as file:
            file.write(ingredient_template.render(ingredient=ingredient))


if __name__ == "__main__":
    generate_static_pages()
