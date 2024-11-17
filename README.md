# nom-stats

## for local development
# build docker image
docker build -t nom-stats .

# run docker image
docker run -p 5000:5000 nom-stats

## for pushing to azure container registry (acr)
# build docker image
docker build -t acrhonestdatasolutions.azurecr.io/nom-stats .

# acr login
az acr login --name acrhonestdatasolutions

# push to azure
docker push acrhonestdatasolutions.azurecr.io/nom-stats
