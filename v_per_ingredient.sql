CREATE VIEW v_per_ingredient AS
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