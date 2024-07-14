DROP DATABASE IF EXISTS raw;
DROP DATABASE IF EXISTS medium;
DROP DATABASE IF EXISTS well_done;

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

CREATE DATABASE medium;

CREATE OR REPLACE VIEW medium.v_total_weight_per_meal_prep AS
SELECT 
    meal_prep_id,
    SUM(ingredient_quantity) AS total_weight_grams
FROM 
    raw.meal_prep_ingredients
GROUP BY 
    meal_prep_id;

CREATE OR REPLACE VIEW medium.v_total_nutrients_per_meal_prep AS
SELECT 
    mp.meal_prep_id,
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
    mp.meal_prep_id, mp.meal_prep_name;

CREATE DATABASE well_done;

CREATE OR REPLACE VIEW well_done.v_per_meal_prep AS
SELECT 
    n.meal_prep_name AS 'Recipe Name',
    ROUND((n.total_calories / w.total_weight_grams) * 100, 1) AS 'Calories per 100 g',
    ROUND((n.total_protein / w.total_weight_grams) * 100, 1) AS 'Protein per 100 g'
FROM 
    medium.v_total_nutrients_per_meal_prep n
JOIN medium.v_total_weight_per_meal_prep w ON n.meal_prep_id = w.meal_prep_id
WHERE 
    w.total_weight_grams > 0;
