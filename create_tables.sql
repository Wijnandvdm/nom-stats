CREATE DATABASE raw;
CREATE TABLE raw.components (
    component_id INT AUTO_INCREMENT PRIMARY KEY,
    component_name VARCHAR(255) NOT NULL,
    component_grams INT NOT NULL
);

CREATE TABLE raw.ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT,
    ingredient_name VARCHAR(255) NOT NULL,
    ingredient_grams_or_milliliters INT NOT NULL,
    FOREIGN KEY (component_id) REFERENCES components(component_id)
);

CREATE TABLE raw.meal_preps (
    meal_prep_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT,
    meal_prep_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
);