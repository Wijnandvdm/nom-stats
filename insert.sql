-- Insert components
INSERT INTO components (component_id, component_name, component_weight, component_volume) VALUES
(1, 'Flour', 100, NULL),
(2, 'Tomato', 200, NULL),
(3, 'Basil', 50, NULL),
(4, 'Olive Oil', NULL, 50),
(5, 'Cheese', 150, NULL);

-- Insert ingredients
INSERT INTO ingredients (ingredient_id, ingredient_name, weight_in_grams, volume_in_milliliters) VALUES
(1, 'Ravioli', 300, NULL),
(2, 'Diced Tomatoes', 200, NULL),
(3, 'Pesto', 100, 50),
(4, 'Ricotta', 150, NULL);

-- Link ingredients to components
INSERT INTO ingredients_components (ingredient_id, component_id, component_quantity) VALUES
(1, 1, 100),   -- Ravioli made with Flour
(2, 2, 200),   -- Diced Tomatoes made with Tomato
(3, 3, 50),    -- Pesto made with Basil
(3, 4, 50),    -- Pesto made with Olive Oil
(4, 5, 150);   -- Ricotta made with Cheese

-- Insert meal prep
INSERT INTO meal_preps (meal_prep_id, meal_prep_name, description) VALUES
(1, 'Puffy Pesto Pillows', 'Delicious ravioli pillows with a pesto, ricotta, and diced tomato sauce');

-- Link meal prep to ingredients
INSERT INTO meal_prep_ingredients (meal_prep_id, ingredient_id, ingredient_quantity) VALUES
(1, 1, 300),  -- 300 grams of Ravioli
(1, 2, 200),  -- 200 grams of Diced Tomatoes
(1, 3, 100),  -- 100 grams of Pesto
(1, 4, 150);  -- 150 grams of Ricotta
