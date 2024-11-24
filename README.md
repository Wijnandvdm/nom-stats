# nom-stats

## for local development
### build docker image
docker build -t nom-stats .

### run docker image
docker run -p 5000:5000 nom-stats

## for pushing to azure container registry (acr)
### build docker image
docker build -t acrhonestdatasolutions.azurecr.io/nom-stats .

### acr login
az acr login --name acrhonestdatasolutions

### push to azure
docker push acrhonestdatasolutions.azurecr.io/nom-stats

# static site
az storage account create -n nomstats -g rg-nom-stats -l westeurope --sku Standard_LRS --hns true

az storage blob service-properties update --account-name nomstats --static-website --404-document 404.html --index-document index.html

az storage blob upload-batch -s static_site -d '$web' --account-name nomstats --overwrite

