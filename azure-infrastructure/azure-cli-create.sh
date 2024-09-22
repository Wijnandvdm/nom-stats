resource_group="rg-containers"
location="westeurope"
container_registry="acrhonestdatasolutions"
container_registry_sku="Basic"

image="recipe-calculator"
container_instance="ci-recipe-calculator"

## basic infrastructure
# az group create --name ${resource_group} --location ${location}
# az acr create --resource-group ${resource_group} --name ${container_registry} --sku ${container_registry_sku}

# for docker part, see README.md
acr_password=$(az acr credential show -n ${container_registry} | jq -r .passwords[0].value)

az container create -g ${resource_group} \
  --name ${container_instance} \
  --ip-address Public \
  --image "${container_registry}.azurecr.io/${image}" \
  --registry-password ${acr_password} \
  --registry-username ${container_registry} \
  --ports 5000 80 \
  --dns-name-label tomato
