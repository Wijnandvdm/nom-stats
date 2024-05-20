CREATE DATABASE raw;
CREATE TABLE raw.meal_preps (
    meal_prep_id INT AUTO_INCREMENT PRIMARY KEY,
    meal_prep_name VARCHAR(255) NOT NULL,
    description VARCHAR(4000)
);

CREATE TABLE raw.ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(255) NOT NULL,
    CONSTRAINT ingredient_unique UNIQUE (ingredient_name)
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

CREATE VIEW raw.v_per_ingredient AS
SELECT 
    mp.meal_prep_name,
    i.ingredient_name,
    SUM(CASE WHEN c.component_name = 'calories' THEN (ic.component_quantity * mi.ingredient_quantity) / 100 ELSE 0 END) AS total_calories,
    SUM(CASE WHEN c.component_name = 'protein' THEN (ic.component_quantity * mi.ingredient_quantity) / 100 ELSE 0 END) AS total_protein
FROM 
    raw.ingredients i
JOIN raw.meal_prep_ingredients mi ON i.ingredient_id = mi.ingredient_id
JOIN raw.meal_preps mp ON mi.meal_prep_id = mp.meal_prep_id 
JOIN raw.ingredients_components ic ON i.ingredient_id = ic.ingredient_id
JOIN raw.components c ON ic.component_id = c.component_id
GROUP BY 
    mp.meal_prep_name, 
    i.ingredient_name;

CREATE VIEW raw.v_per_meal_prep AS
SELECT 
    mp.meal_prep_name,
	SUM(CASE WHEN c.component_name = 'calories' THEN (ic.component_quantity * mi.ingredient_quantity) / 100 ELSE 0 END) AS total_calories,
    SUM(CASE WHEN c.component_name = 'protein' THEN (ic.component_quantity * mi.ingredient_quantity) / 100 ELSE 0 END) AS total_protein
FROM 
    raw.ingredients i
JOIN raw.meal_prep_ingredients mi ON i.ingredient_id = mi.ingredient_id
JOIN raw.meal_preps mp ON mi.meal_prep_id = mp.meal_prep_id 
JOIN raw.ingredients_components ic ON i.ingredient_id = ic.ingredient_id
JOIN raw.components c ON ic.component_id = c.component_id
GROUP BY 
    mp.meal_prep_name;
