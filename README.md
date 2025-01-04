# NomStats

NomStats is a tool for generating and hosting recipe websites with nutritional information. It calculates nutritional values based on provided ingredients and recipes, generates HTML pages, and deploys them to Azure Blob Storage.

## How It Works
1. **Recipe & Ingredient Configuration**:
   - Define ingredients with nutritional data in `ingredients.yaml`.
   - Create recipe files (e.g., `individual_recipe.yaml`) with ingredients, steps, and ratings.

3. **Deployment**:
   - Use GitHub Actions to:
        - Run the `generate_static_website.py` script to generate HTML pages for all recipes.
        - Deploy the html pages to Azure Blob Storage (`Create NomStats`) and or clean up resources (`Delete NomStats`).
        - Use Azure CLI to turn on static website capability.

That's it! NomStats makes it easy to share delicious recipes with nutritional insights online.

Want to know more? Ask the creator of this repo!
