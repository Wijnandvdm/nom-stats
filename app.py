from flask import Flask, render_template, send_from_directory
import os
import yaml

app = Flask(__name__)

def get_configuration_and_ingredients():
    configuration_directory = os.path.join(os.path.dirname(__file__), 'configuration')
    ingredients_file = os.path.join(configuration_directory, 'ingredients.yaml')
    all_ingredients = load_ingredients(ingredients_file)
    return configuration_directory, all_ingredients

def load_ingredients(ingredients_file):
    with open(ingredients_file, 'r') as file:
        ingredients = yaml.safe_load(file)['ingredients']
    return {ingredient['name']: ingredient for ingredient in ingredients}

def calculate_nutrition(yaml_content, all_ingredients):
    total_protein = total_calories = total_weight = 0
    human_readable_ingredients = []

    for recipe_ingredient in yaml_content['ingredients']:
        ingredient_name = recipe_ingredient['name']
        quantity = recipe_ingredient.get('quantity', 0)

        # Lookup the ingredient details in the ingredients file
        ingredient = all_ingredients.get(ingredient_name)
        if ingredient:
            # Check if the ingredient has a weight per unit
            weight_per_unit = ingredient.get('weight_per_unit')
            
            # If weight_per_unit exists, interpret quantity as units and convert to grams
            if weight_per_unit:
                quantity = quantity * weight_per_unit  # Convert units to grams
            
            # Accumulate total weight for nutritional calculations
            total_weight += quantity

            # Retrieve protein and calorie values per 100g
            protein_per_100g = next((comp['quantity_per_100_g'] for comp in ingredient['components'] if comp['name'] == 'protein'), 0)
            calories_per_100g = next((comp['quantity_per_100_g'] for comp in ingredient['components'] if comp['name'] == 'calories'), 0)

            measurement_unit = ingredient.get('measurement_unit', ' g/ml')  # Default to 'g/ml' if not specified

            # Calculate total protein and calories based on the adjusted quantity
            total_protein += (quantity * protein_per_100g) / 100
            total_calories += (quantity * calories_per_100g) / 100

            # Create human-readable format for grocery shopping list
            if weight_per_unit:
                human_readable_ingredients.append(f"{int(quantity / weight_per_unit)} {measurement_unit} {ingredient_name}")
            else:
                human_readable_ingredients.append(f"{quantity}{measurement_unit} {ingredient_name}")

    # Calculate protein and calories per 100g for the overall recipe
    protein_per_100g = (total_protein / total_weight) * 100 if total_weight else 0
    calories_per_100g = (total_calories / total_weight) * 100 if total_weight else 0

    return total_protein, total_calories, protein_per_100g, calories_per_100g, human_readable_ingredients

def process_all_recipes(directory, all_ingredients):
    recipes = []
    for filename in os.listdir(directory):
        if filename == "ingredients.yaml":
            continue

        if filename.endswith(".yaml"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                yaml_content = yaml.safe_load(file)

            if 'recipe_name' in yaml_content and 'ingredients' in yaml_content:
                # Get only the first 4 returned values, discard the human-readable list
                protein, calories, protein_per_100g, calories_per_100g, _ = calculate_nutrition(yaml_content, all_ingredients)
                recipe = {
                    'Recipe Name': yaml_content['recipe_name'],
                    'Description': yaml_content.get('description', 'No description available'),
                    'Total Protein': f"{protein:.1f}",
                    'Total Calories': f"{calories:.0f}",
                    'Protein/100g': f"{protein_per_100g:.1f}",
                    'Calories/100g': f"{calories_per_100g:.0f}"
                }
                recipes.append(recipe)
            else:
                print(f"Warning: Skipping file '{filename}' due to missing 'recipe_name' or 'ingredients'")

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
        
        # Extract nutrition info
        total_protein, total_calories, _, _, human_readable_ingredients = calculate_nutrition(recipe, all_ingredients)
        
        # Pass the steps along with other recipe details
        return render_template(
            'recipe_detail.html',
            recipe=recipe,
            total_protein=f"{total_protein:.0f}",
            total_calories=f"{total_calories:.0f}",
            ingredients=human_readable_ingredients,
            steps=recipe.get('steps', []),
            rating=recipe.get('rating', 0)
            
        )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=80)
