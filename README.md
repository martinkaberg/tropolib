# tropolib
Additional classes for troposphere


usage

<code>

from docker import Compose2TaskDefinition
from troposphere import Template

t = Template()
image_map={
    "php" : "php:latest",
    "php2": "php2:latest",
    "web" : "web:latest"
}
t.add_resource(Compose2TaskDefinition("../docker-compose.yml",image_map).get_task_definition("taskdef"))
print t.to_json()

</code>