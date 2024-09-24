GROUP="bramastyaz-rg"
LOCATION="East US 2"
WORKSPACE="mlops-thesis"

az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION

az extension remove -n ml
az extension add -n ml
