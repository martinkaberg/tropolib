from tropolib.docker import Compose2TaskDefinitionDataDog
from troposphere import (Template, Parameter, Ref, ecs, elasticloadbalancing)
import os
t = Template()
php_image = t.add_parameter(Parameter(
    "PhpImage",
    Type="String",
    Default="php:latest"

))

php2_image = t.add_parameter(Parameter(
    "Php2Image",
    Type="String",
    Default="php2:latest"

))

web_image = t.add_parameter(Parameter(
    "WbImage",
    Type="String",
    Default="web:latest"

))

db_host = t.add_parameter(Parameter(
    "DbHost",
    Type="String",
    Description="hostname of the database"
))

# Map the cloudformation parameters or hard code the FQDN including tag to ECR for each container name in your compose
# file
image_map = {
    "php7": Ref(php_image),
    "php56": Ref(php2_image),
    "web": Ref(web_image)
}


filename = os.path.join(os.path.dirname(__file__), "docker-compose.yml")
# Create the intermediary task definition from docker compose file, and pass the image map
task = Compose2TaskDefinitionDataDog(filename, image_map,"datadog/docker-dd-agent:latest", "abc")


# Set an environment variable
task.environment("php7")["DB_HOST"]=Ref(db_host)



# Retrieves the troposphere.ecs.TaskDefinition object and sets its title ( LogicalId ) equal to the title parameter
t.add_resource(task.get_task_definition(title="taskdef"))
print t.to_json()
