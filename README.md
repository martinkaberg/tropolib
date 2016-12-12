# tropolib
Additional classes for troposphere


usage

```python
from docker import Compose2TaskDefinition
from troposphere import (Template, Parameter, Ref, ecs)

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

image_map={
    "php" : Ref(php_image),
    "php2": Ref(php2_image),
    "web" : Ref(web_image)
}


task = Compose2TaskDefinition("../docker-compose.yml",image_map)
task.get_container_definition("php").Environment = [ ecs.Environment(
    Name="DB_HOST",
    Value=Ref(db_host)
)]
t.add_resource(task.get_task_definition("taskdef"))
print t.to_json()
```