from flask import Flask, render_template, send_from_directory
import os
import yaml

app = Flask(__name__)

# Helper function to get configuration directory and ingredients
def get_configuration_and_ingredients():
    configuration_directory = os.path.join(os.path.dirname(__file__), 'configuration')
    ingredients_file = os.path.join(configuration_directory, 'ingredients.yaml')
    all_ingredients = load_ingredients(ingredients_file)
    return configuration_directory, all_ingredients

# Load ingredients from a YAML file and return a dictionary
def load_ingredients(ingredients_file):
    with open(ingredients_file, 'r') as file:
        ingredients = yaml.safe_load(file)['ingredients']
    return {ingredient['name']: ingredient for ingredient in ingredients}

# Calculate the nutrition values based on the ingredients
def calculate_nutrition(yaml_content, all_ingredients):
    total_protein = total_calories = total_weight = 0

    for recipe_ingredient in yaml_content['ingredients']:
        ingredient_name = recipe_ingredient['name']
        quantity = recipe_ingredient['quantity']
        total_weight += quantity

        ingredient = all_ingredients.get(ingredient_name)
        if ingredient:
            protein_per_100g = next((comp['quantity_per_100_g'] for comp in ingredient['components'] if comp['name'] == 'protein'), 0)
            calories_per_100g = next((comp['quantity_per_100_g'] for comp in ingredient['components'] if comp['name'] == 'calories'), 0)
            
            total_protein += (quantity * protein_per_100g) / 100
            total_calories += (quantity * calories_per_100g) / 100

    protein_per_100g = (total_protein / total_weight) * 100 if total_weight else 0
    calories_per_100g = (total_calories / total_weight) * 100 if total_weight else 0

    return total_protein, total_calories, protein_per_100g, calories_per_100g

# Process all recipes by referencing ingredients
def process_all_recipes(directory, all_ingredients):
    recipes = []
    for filename in os.listdir(directory):
        if filename == "ingredients.yaml":
            continue

        with open(os.path.join(directory, filename), 'r') as file:
            yaml_content = yaml.safe_load(file)
        
        if 'recipe_name' in yaml_content and 'ingredients' in yaml_content:
            protein, calories, protein_per_100g, calories_per_100g = calculate_nutrition(yaml_content, all_ingredients)
            recipes.append({
                'Recipe Name': yaml_content['recipe_name'],
                'Description': yaml_content.get('description', 'No description available'),
                'Total Protein': f"{protein:.2f}",
                'Total Calories': f"{calories:.2f}",
                'Protein/100g': f"{protein_per_100g:.2f}",
                'Calories/100g': f"{calories_per_100g:.2f}"
            })
    
    return recipes

@app.route('/')
def index():
    configuration_directory, all_ingredients = get_configuration_and_ingredients()
    data = process_all_recipes(configuration_directory, all_ingredients)
    data.sort(key=lambda x: x['Recipe Name'])
    columns = ['Recipe Name', 'Protein/100g', 'Calories/100g']
    return render_template('index.html', data=data, columns=columns)

@app.route('/recipe/<recipe_name>')
def recipe_detail(recipe_name):
    configuration_directory, all_ingredients = get_configuration_and_ingredients()
    recipe_file = os.path.join(configuration_directory, f"{recipe_name.lower().replace(' ', '_')}.yaml")

    if not os.path.exists(recipe_file):
        return "Recipe not found", 404
    else:
        with open(recipe_file, 'r') as file:
            recipe = yaml.safe_load(file)
        total_protein, total_calories, _, _ = calculate_nutrition(recipe, all_ingredients)
    return render_template('recipe_detail.html', recipe=recipe, total_protein=f"{total_protein:.2f}", total_calories=f"{total_calories:.2f}")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=80)
