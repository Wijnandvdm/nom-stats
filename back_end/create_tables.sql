CREATE DATABASE raw;
CREATE TABLE raw.meal_preps (
    meal_prep_id INT AUTO_INCREMENT PRIMARY KEY,
    meal_prep_name VARCHAR(255) NOT NULL,
    description VARCHAR(4000)
);

CREATE TABLE raw.ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(255) NOT NULL
);

CREATE TABLE raw.components (
    component_id INT AUTO_INCREMENT PRIMARY KEY,
    component_name VARCHAR(255) NOT NULL,
    CONSTRAINT component_unique UNIQUE (component_name)
);

CREATE TABLE raw.meal_prep_ingredients (
    meal_prep_id INT,
    ingredient_id INT,
    ingredient_quantity INT NOT NULL,
    PRIMARY KEY (meal_prep_id, ingredient_id),
    FOREIGN KEY (meal_prep_id) REFERENCES meal_preps(meal_prep_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
);

CREATE TABLE raw.ingredients_components (
    ingredient_id INT,
    component_id INT,
    component_quantity FLOAT NOT NULL,
    PRIMARY KEY (ingredient_id, component_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),
    FOREIGN KEY (component_id) REFERENCES components(component_id)
);

