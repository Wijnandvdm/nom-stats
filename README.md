# NomStats
First things first, congratulations for actually reading a README!

Secondly, NomStats is a tool for generating and hosting recipe websites with nutritional information. It calculates nutritional values based on provided ingredients and recipes, generates HTML pages, and deploys them to Azure Blob Storage.

## Schematic overview
![](./docs/schematic_overview.drawio.png)

## How it works
1. **Recipe & Ingredient Configuration**:
   - Define ingredients with nutritional data in `ingredients.csv`.
   - Create recipe files (e.g., `individual_recipe.yaml`) with ingredients, steps, and ratings according to the existing examples.

2. **Deployment**:
   - Store credentials of an Azure Service principal with enough rights on your Azure environment in GitHub.
   - (Automatically done on push to main, but you can also manually) Use GitHub Actions to:
        - Run the `generate_static_website.py` script to generate HTML pages for all recipes.
        - Deploy the html pages to Azure Blob Storage (`Create NomStats`) and or clean up resources (`Delete NomStats`).
        - Use Azure CLI to turn on static website capability.
   - Your [website](https://nomstats.z6.web.core.windows.net/) is now available!

This of course does not explain the complete functionality of this project. Want to know more? Don't be shy, ask the creator of this repo!

## To Do
- spicy spice rating thingy to recipes
- a way to enter ingredients and read straight ingredient data straight from albert heijn
