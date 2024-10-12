# recipes-db


## for local development
# build docker image
docker build -t recipe-calculator .

# run docker image
docker run -p 5000:5000 recipe-calculator

## for pushing to azure container registry (acr)
# build docker image
docker build -t acrhonestdatasolutions.azurecr.io/recipe-calculator .

# acr login
az acr login --name acrhonestdatasolutions

# push to azure
docker push acrhonestdatasolutions.azurecr.io/recipe-calculator

# to do:
- Add steps to create a meal from the recipe on the recipe page
- Add scoring system for a meal
- Add the ability to add how many pieces go in instead of grams