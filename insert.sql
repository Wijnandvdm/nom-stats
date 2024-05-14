-- Insert a component first
INSERT INTO raw.components (component_name, component_grams) VALUES ('calories', 178);
INSERT INTO raw.components (component_name, component_grams) VALUES ('proteins', 9.1);
INSERT INTO raw.components (component_name, component_grams) VALUES ('calories', 33);
INSERT INTO raw.components (component_name, component_grams) VALUES ('proteins', 1.4);
INSERT INTO raw.components (component_name, component_grams) VALUES ('calories', 365 );
INSERT INTO raw.components (component_name, component_grams) VALUES ('proteins', 4.1);
INSERT INTO raw.components (component_name, component_grams) VALUES ('calories', 143 );
INSERT INTO raw.components (component_name, component_grams) VALUES ('proteins', 8.5);

-- Insert an ingredient that uses the component inserted above
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (1, 'Ravioli', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (2, 'Ravioli', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (3, 'Tomatenblokjes', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (4, 'Tomatenblokjes', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (5, 'Pesto', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (6, 'Pesto', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (7, 'Ricotta', 100);
INSERT INTO raw.ingredients (component_id, ingredient_name, ingredient_grams_or_milliliters) VALUES (8, 'Ricotta', 100);

-- Insert a meal prep that uses the ingredient inserted above
INSERT INTO raw.meal_preps (ingredient_id, meal_prep_name) VALUES (1, 'Puffy Pesto Pillows');