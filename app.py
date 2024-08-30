from flask import Flask, render_template
import os
import yaml

app = Flask(__name__)

def calculate_nutrition(yaml_content):
    total_protein = 0
    total_calories = 0
    total_weight = 0

    for ingredient in yaml_content['ingredients']:
        quantity = ingredient['quantity']
        total_weight += quantity
        for component in ingredient['components']:
            if component['name'] == 'protein':
                total_protein += (quantity * component['quantity_per_100_g']) / 100
            elif component['name'] == 'calories':
                total_calories += (quantity * component['quantity_per_100_g']) / 100

    protein_per_100g = (total_protein / total_weight) * 100
    calories_per_100g = (total_calories / total_weight) * 100

    return total_protein, total_calories, protein_per_100g, calories_per_100g

def process_all_recipes(directory):
    recipes = []
    for filename in os.listdir(directory):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                yaml_content = yaml.safe_load(file)
            protein, calories, protein_per_100g, calories_per_100g = calculate_nutrition(yaml_content)
            recipe = {
                'meal_prep_name': yaml_content['meal_prep_name'],
                'description': yaml_content['description'],
                'total_protein': f"{protein:.2f}",
                'total_calories': f"{calories:.2f}",
                'protein_per_100g': f"{protein_per_100g:.2f}",
                'calories_per_100g': f"{calories_per_100g:.2f}"
            }
            recipes.append(recipe)
    return recipes

@app.route('/')
def index():
    current_directory = os.path.dirname(__file__)
    configuration_directory = os.path.join(current_directory, 'configuration')
    data = process_all_recipes(configuration_directory)
    columns = ['meal_prep_name', 'total_protein', 'total_calories', 'protein_per_100g', 'calories_per_100g']
    return render_template('index.html', data=data, columns=columns)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
