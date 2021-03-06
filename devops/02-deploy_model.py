## Register model from last experiment 
## and deploy to Azure Container Instance
##

from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import ContainerImage
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
import json
import sys
from azureml.core.authentication import AzureCliAuthentication

build = sys.argv[1]

webservice_name = 'turbofan-rul'

cli_auth = AzureCliAuthentication()

################ Workspace ##############################
with open("./config/aml_config.json") as f:
    config = json.load(f)

workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
workspace_region = config["location"]

#Interactive Authentication
ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group,
               auth=cli_auth)

run =[x for x in ws.experiments['gbr-turbofan'].get_runs() if x.tags == {'build number': build}][0]

print(run)

model = run.register_model(model_name = "sklearn-gbr-model", model_path = "outputs/model.pkl")


aci_config = AciWebservice.deploy_configuration(cpu_cores = 1, memory_gb = 1,auth_enabled=True)


image_config = ContainerImage.image_configuration(execution_script = "score.py", 
                                    runtime = "python", 
                                    conda_file = "turbofan.yml")


try:
    service = Webservice(ws, webservice_name)        
    service.delete()
    
except Exception as e:
    print("No Existing Service")


service = Webservice.deploy_from_model(workspace=ws,
                                       name = webservice_name,
                                       deployment_config = aci_config,
                                       models = [model],
                                       image_config = image_config)
service.wait_for_deployment(show_output = True)



print(service.get_keys())
print(service.scoring_uri)
