from jinja2 import Environment, FileSystemLoader
import os
import yaml

# Setup Jinja Environment
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = 'static_site'
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"'{OUTPUT_DIR}' didn't exist yet, folder created!")
else:
    print(f"'{OUTPUT_DIR}' folder already exists.")

# Directory paths
configuration_directory = os.path.join(os.path.dirname(__file__), 'configuration')
ingredients_file = os.path.join(configuration_directory, 'ingredients.yaml')

# Load ingredients
def load_ingredients(ingredients_file):
    with open(ingredients_file, 'r') as file:
        ingredients = yaml.safe_load(file)['ingredients']
    return {ingredient['name']: ingredient for ingredient in ingredients}

# Calculate nutrition
def calculate_nutrition(yaml_content, all_ingredients):
    total_protein = total_calories = total_weight = 0
    human_readable_ingredients = []

    for recipe_ingredient in yaml_content['ingredients']:
        ingredient_name = recipe_ingredient['name']
        quantity = recipe_ingredient.get('quantity', 0)
        ingredient = all_ingredients.get(ingredient_name)

        if ingredient:
            weight_per_unit = ingredient.get('weight_per_unit', 0)
            if weight_per_unit:
                quantity *= weight_per_unit
            total_weight += quantity

            # Create human-readable format for grocery shopping list
            measurement_unit = ingredient.get('measurement_unit', ' g/ml')  # Default to 'g/ml' if not specified
            if weight_per_unit:
                human_readable_ingredients.append(f"{int(quantity / weight_per_unit)} {measurement_unit} {ingredient_name}")
            else:
                human_readable_ingredients.append(f"{quantity}{measurement_unit} {ingredient_name}")


            protein_per_100g = next((c['quantity_per_100_g'] for c in ingredient['components'] if c['name'] == 'protein'), 0)
            calories_per_100g = next((c['quantity_per_100_g'] for c in ingredient['components'] if c['name'] == 'calories'), 0)

            total_protein += round((quantity * protein_per_100g) / 100)
            total_calories += round((quantity * calories_per_100g) / 100)

    protein_per_100g = round((total_protein / total_weight) * 100, 1) if total_weight else 0
    calories_per_100g = round((total_calories / total_weight) * 100) if total_weight else 0

    return total_protein, total_calories, protein_per_100g, calories_per_100g, human_readable_ingredients


# Process recipes
def process_all_recipes(directory, all_ingredients):
    recipes = []
    for filename in os.listdir(directory):
        if filename.endswith(".yaml") and filename != "ingredients.yaml":
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                yaml_content = yaml.safe_load(file)
            if 'recipe_name' in yaml_content:
                total_protein, total_calories, protein_100g, calories_100g, ingredients = calculate_nutrition(yaml_content, all_ingredients)
                recipes.append({
                    'name': yaml_content['recipe_name'],
                    'description': yaml_content.get('description', ''),
                    'protein_100g': protein_100g,
                    'calories_100g': calories_100g,
                    'total_protein': total_protein,
                    'total_calories': total_calories,
                    'ingredients': ingredients,
                    'steps': yaml_content.get('steps', []),
                    'rating': yaml_content.get('rating', 0),
                    'filename': filename.replace(".yaml", ".html")
                })
    return recipes

# Generate Static Pages
def generate_static_pages():
    ingredients_file = 'configuration/ingredients.yaml'
    recipes_directory = 'configuration'
    all_ingredients = load_ingredients(ingredients_file)
    recipes = process_all_recipes(recipes_directory, all_ingredients)

    # Render the index.html
    index_template = env.get_template('index.html')
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as file:
        file.write(index_template.render(data=recipes, columns=['Recipe Name', 'Protein/100g', 'Calories/100g']))

    # Render individual recipe_detail.html files
    recipe_template = env.get_template('recipe_detail.html')
    for recipe in recipes:
        recipe_filename = recipe['filename']
        with open(os.path.join(OUTPUT_DIR, recipe_filename), 'w') as file:
            file.write(recipe_template.render(recipe=recipe))

if __name__ == '__main__':
    generate_static_pages()