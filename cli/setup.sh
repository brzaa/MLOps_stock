GROUP="bramastyaz-rg"
LOCATION="eastus2"
WORKSPACE="mlops-thesis"

az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION

az extension remove -n ml
az extension add -n ml
