# recipes-db


## for local development
# build docker image
docker build -t recipe-calculator .

# run docker image
docker run -p 5000:5000 recipe-calculator

## for pushing to azure
# build docker image
docker build -t acrhonestdatasolutions.azurecr.io/recipe-calculator .

# push to azure
docker push acrhonestdatasolutions.azurecr.io/recipe-calculator

# create container instance from azure container registry
az container create -g MyResourceGroup --name myapp --image myAcrRegistry.azurecr.io/myimage:latest --registry-password password

# inspiration
https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app?tabs=web-app-flask