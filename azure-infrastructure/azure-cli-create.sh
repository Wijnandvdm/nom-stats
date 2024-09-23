resource_group="rg-containers"
location="westeurope"
container_registry="acrhonestdatasolutions"
container_registry_sku="Basic"

image="recipe-calculator"
container_instance="ci-recipe-calculator"
dns_name="recipe-calculator"

# basic infrastructure
az group create -n ${resource_group} -l ${location}
az acr create -n ${container_registry} -g ${resource_group} \
    --sku ${container_registry_sku} --admin-enabled true

# for docker part, see README.md
acr_password=$(az acr credential show -n ${container_registry} | jq -r .passwords[0].value)

# az container create -g ${resource_group} \
#   --name ${container_instance} \
#   --ip-address Public \
#   --image "${container_registry}.azurecr.io/${image}" \
#   --registry-password ${acr_password} \
#   --registry-username ${container_registry} \
#   --ports 80 \
#   --dns-name-label ${dns_name}
