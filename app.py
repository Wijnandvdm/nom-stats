from flask import Flask, render_template, send_from_directory
import os
import yaml

app = Flask(__name__)

# Load the ingredients from ingredients.yaml
def load_ingredients(ingredients_file):
    with open(ingredients_file, 'r') as file:
        ingredients_data = yaml.safe_load(file)
    return ingredients_data['ingredients']

# Find an ingredient by name
def find_ingredient(ingredient_name, all_ingredients):
    for ingredient in all_ingredients:
        if ingredient['name'] == ingredient_name:
            return ingredient
    return None

# Calculate the nutrition values based on the ingredients
def calculate_nutrition(yaml_content, all_ingredients):
    total_protein = 0
    total_calories = 0
    total_weight = 0

    for recipe_ingredient in yaml_content['ingredients']:
        ingredient_name = recipe_ingredient['name']
        quantity = recipe_ingredient['quantity']
        total_weight += quantity
        
        # Lookup the ingredient details in the ingredients file
        ingredient = find_ingredient(ingredient_name, all_ingredients)
        if ingredient:
            for component in ingredient['components']:
                if component['name'] == 'protein':
                    total_protein += (quantity * component['quantity_per_100_g']) / 100
                elif component['name'] == 'calories':
                    total_calories += (quantity * component['quantity_per_100_g']) / 100

    protein_per_100g = (total_protein / total_weight) * 100 if total_weight else 0
    calories_per_100g = (total_calories / total_weight) * 100 if total_weight else 0

    return total_protein, total_calories, protein_per_100g, calories_per_100g

# Process all recipes by referencing ingredients
def process_all_recipes(directory, all_ingredients):
    recipes = []
    for filename in os.listdir(directory):
        # Skip the ingredients.yaml file and only process recipe files
        if filename == "ingredients.yaml":
            continue

        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                yaml_content = yaml.safe_load(file)
            
            # Ensure the yaml_content contains recipe data
            if 'recipe_name' in yaml_content and 'ingredients' in yaml_content:
                protein, calories, protein_per_100g, calories_per_100g = calculate_nutrition(yaml_content, all_ingredients)
                recipe = {
                    'Recipe Name': yaml_content['recipe_name'],
                    'Description': yaml_content.get('description', 'No description available'),
                    'Total Protein': f"{protein:.2f}",
                    'Total Calories': f"{calories:.2f}",
                    'Protein/100g': f"{protein_per_100g:.2f}",
                    'Calories/100g': f"{calories_per_100g:.2f}"
                }
                recipes.append(recipe)
            else:
                print(f"Warning: Skipping file '{filename}' due to missing 'recipe_name' or 'ingredients'")
    
    return recipes


@app.route('/')
def index():
    current_directory = os.path.dirname(__file__)
    configuration_directory = os.path.join(current_directory, 'configuration')
    
    # Load ingredients once
    ingredients_file = os.path.join(configuration_directory, 'ingredients.yaml')
    all_ingredients = load_ingredients(ingredients_file)

    # Process recipes using the loaded ingredients
    data = process_all_recipes(configuration_directory, all_ingredients)
    data.sort(key=lambda x: x['Recipe Name'])
    columns = ['Recipe Name', 'Total Protein', 'Total Calories', 'Protein/100g', 'Calories/100g']
    return render_template('index.html', data=data, columns=columns)

@app.route('/recipe/<recipe_name>')
def recipe_detail(recipe_name):
    current_directory = os.path.dirname(__file__)
    configuration_directory = os.path.join(current_directory, 'configuration')

    # Load the specific recipe file
    normalized_recipe_name = recipe_name.lower().replace(' ', '_')
    recipe_file = os.path.join(configuration_directory, f"{normalized_recipe_name}.yaml")
    
    # Check if the recipe file exists
    if not os.path.exists(recipe_file):
        return "Recipe not found", 404
    
    # Load the recipe from the YAML file
    with open(recipe_file, 'r') as file:
        recipe = yaml.safe_load(file)

    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
