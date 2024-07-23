import os
import yaml

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
    for filename in os.listdir(directory):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                yaml_content = yaml.safe_load(file)
            protein, calories, protein_per_100g, calories_per_100g = calculate_nutrition(yaml_content)
            print(f"Recipe: {yaml_content['meal_prep_name']}")
            print(f"Description: {yaml_content['description']}")
            print(f'Total Protein: {protein:.2f} grams')
            print(f'Total Calories: {calories:.2f} kcal')
            print(f'Protein per 100g: {protein_per_100g:.2f} grams')
            print(f'Calories per 100g: {calories_per_100g:.2f} kcal')
            print('---')

# Example usage:
current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
configuration_directory = os.path.join(parent_directory, 'configuration')
process_all_recipes(configuration_directory)
