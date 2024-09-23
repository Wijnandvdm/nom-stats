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
- ingredients in one big yaml for recipe yamls to reference to (only name and quantity in recipe)
- mobile access to site