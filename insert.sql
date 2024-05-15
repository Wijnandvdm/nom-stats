-- Insert components
INSERT INTO components (component_id, component_name) VALUES
(1, 'protein'),
(2, 'calories');

-- Insert ingredients
INSERT INTO ingredients (ingredient_id, ingredient_name, weight_in_grams, volume_in_milliliters) VALUES
(1, 'Ravioli', 300, NULL),
(2, 'Diced Tomatoes', 200, NULL),
(3, 'Pesto', 100, NULL),
(4, 'Ricotta', 150, NULL);

-- Link ingredients to components
INSERT INTO ingredients_components (ingredient_id, component_id, component_quantity) VALUES
(1, 1, 9.1),   -- protein in Ravioli
(1, 2, 178),   -- calories in Ravioli
(2, 1, 1.4),   -- protein in Diced Tomatoes
(2, 2, 33),    -- calories in Diced Tomatoes 
(3, 1, 4.1),    -- protein in Pesto
(3, 2, 365);   -- calories in Pesto
(4, 1, 8.5),    -- protein in Pesto
(4, 2, 143);   -- calories in Pesto per 100 grams

-- Insert meal prep
INSERT INTO meal_preps (meal_prep_id, meal_prep_name, description) VALUES
(1, 'Puffy Pesto Pillows', 'Delicious ravioli pillows with a pesto, ricotta, and diced tomato sauce');

-- Link meal prep to ingredients
INSERT INTO meal_prep_ingredients (meal_prep_id, ingredient_id, ingredient_quantity) VALUES
(1, 1, 300),  -- 300 grams of Ravioli
(1, 2, 200),  -- 200 grams of Diced Tomatoes
(1, 3, 100),  -- 100 grams of Pesto
(1, 4, 150);  -- 150 grams of Ricotta
