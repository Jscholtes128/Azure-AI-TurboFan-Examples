## Use Local Machine As Compute
##

from azureml.core import Environment
from azureml.core import ScriptRunConfig
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.core.runconfig import RunConfiguration
import json
import sys

from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()

with open("./../config/aml_config.json") as f:
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

local_run = RunConfiguration()

local_run.environment.python.user_managed_dependencies = True


############# Experiement local-gbr-turbofan ######################
experiement_name = 'gbr-turbofan'


exp = Experiment(workspace=ws, name=experiement_name)
src = ScriptRunConfig(source_directory='./', script='01-train.py',run_config=local_run)

run = exp.submit(src,tags={"python version": sys.version[0:6]})

run.wait_for_completion(show_output = True)
