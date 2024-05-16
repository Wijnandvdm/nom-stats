CREATE VIEW v_ingredient_nutrition AS
SELECT 
    i.ingredient_id,
    SUM(CASE WHEN c.component_name = 'protein' THEN ic.component_quantity ELSE 0 END) AS protein_per_100g,
    SUM(CASE WHEN c.component_name = 'calories' THEN ic.component_quantity ELSE 0 END) AS calories_per_100g
FROM 
    ingredients i
JOIN 
    ingredients_components ic ON i.ingredient_id = ic.ingredient_id
JOIN 
    components c ON ic.component_id = c.component_id
GROUP BY 
    i.ingredient_id;
