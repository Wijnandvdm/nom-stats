import yaml
import app
import mysql.connector
from mysql.connector import Error
import os

def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def empty_tables():
    conn = app.get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = ["meal_prep_ingredients", "ingredients_components", "meal_preps", "ingredients", "components"]
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def insert_data_into_db(data):
    try:
        conn = app.get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        meal_prep_name = data['meal_prep_name']
        description = data['description']
        cursor.execute("INSERT INTO meal_preps (meal_prep_name, description) VALUES (%s, %s)",(meal_prep_name, description))
        meal_prep_id = cursor.lastrowid

        for ingredient in data['ingredients']:
            ingredient_name = ingredient['name']
            ingredient_quantity = ingredient['quantity']

            cursor.execute("SELECT ingredient_id FROM ingredients WHERE ingredient_name = %(ingredient_name)s", {'ingredient_name': ingredient_name})
            ingredient_result = cursor.fetchone()

            if ingredient_result is None:
                cursor.execute("INSERT INTO ingredients (ingredient_name) VALUES (%s)",(ingredient_name,))
                ingredient_id = cursor.lastrowid
            else:
                ingredient_id = ingredient_result['ingredient_id']

            cursor.execute("INSERT INTO meal_prep_ingredients (meal_prep_id, ingredient_id, ingredient_quantity) VALUES (%s, %s, %s)",(meal_prep_id, ingredient_id, ingredient_quantity))

            for component in ingredient['components']:
                component_name = component['name']
                component_quantity_per_100_g = component['quantity_per_100_g']

                cursor.execute("SELECT component_id FROM components WHERE component_name = %(component_name)s", {'component_name': component_name})
                component_result = cursor.fetchone()

                if component_result is None:
                    cursor.execute("INSERT INTO components (component_name) VALUES (%s) ON DUPLICATE KEY UPDATE component_name=component_name",(component_name,))
                    component_id = cursor.lastrowid
                else:
                    component_id = component_result['component_id']

                cursor.execute("INSERT INTO ingredients_components (ingredient_id, component_id, component_quantity) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE component_quantity=%s",(ingredient_id, component_id, component_quantity_per_100_g, component_quantity_per_100_g))

        conn.commit()

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    empty_tables()
    config_dir = os.path.join(os.path.dirname(os.getcwd()), 'configuration')        # Define the path to the "configuration" directory
    if os.path.isdir(config_dir):                                                   # Check if the "configuration" directory exists and is a directory
        for file in os.listdir(config_dir):
            if os.path.isfile(os.path.join(config_dir, file)):
                data = load_yaml_file(os.path.join(config_dir, file))
                insert_data_into_db(data)
                print(f"Upserted file {file}!")
    else:
        print(f"The directory '{config_dir}' does not exist or is not a directory.")
