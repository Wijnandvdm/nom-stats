import yaml
import app
import mysql.connector
from mysql.connector import Error

def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def insert_data_into_db(data):
    conn = app.get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = ["meal_prep_ingredients", "ingredients_components", "meal_preps", "ingredients", "components"]
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        conn.commit()

        # Insert meal prep
        meal_prep_name = data['meal_prep_name']
        description = data['description']
        cursor.execute(
            "INSERT INTO meal_preps (meal_prep_name, description) VALUES (%s, %s)",
            (meal_prep_name, description)
        )
        meal_prep_id = cursor.lastrowid

        # Insert ingredients and their components
        for ingredient in data['ingredients']:
            ingredient_name = ingredient['name']
            ingredient_quantity = ingredient['quantity']
            cursor.execute(
                "INSERT INTO ingredients (ingredient_name) VALUES (%s)",
                (ingredient_name,)
            )
            ingredient_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO meal_prep_ingredients (meal_prep_id, ingredient_id, ingredient_quantity) VALUES (%s, %s, %s)",
                (meal_prep_id, ingredient_id, ingredient_quantity)
            )

            for component in ingredient['components']:
                component_name = component['name']
                component_quantity_per_100_g = component['quantity_per_100_g']
                
                cursor.execute(
                    "INSERT INTO components (component_name) VALUES (%s) ON DUPLICATE KEY UPDATE component_name=component_name",
                    (component_name,)
                )

                cursor.execute("SELECT component_id FROM components WHERE component_name = %(component_name)s", { 'component_name': component_name })
                component_id = cursor.fetchone()['component_id']

                cursor.execute(
                    "INSERT INTO ingredients_components (ingredient_id, component_id, component_quantity) VALUES (%s, %s, %s)",
                    (ingredient_id, component_id, component_quantity_per_100_g)
                )

        conn.commit()

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    data = load_yaml_file('../configuration/puffy_pesto_pillows.yaml')
    insert_data_into_db(data)
