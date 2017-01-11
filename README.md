# tropolib
Additional classes for troposphere

usage of Network and Zone
```python
from troposphere import (
    Parameter, Output, Ref, Export, Sub, ec2
)
from tropolib.networking import PublicZone, DbZone, Zone, Network

t = Network(description="Networking")


white_list_ip = t.add_parameter(Parameter(
    "WhiteListIp",
    Type="String",
    Description="White listed ip"
))

vpc = t.vpc
security_group_public = t.add_resource(ec2.SecurityGroup(
    "SecurityGroupPublic",
    VpcId=Ref(vpc),
    GroupDescription="Everything from whitelisted ip",
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="-1",
            FromPort="-1",
            ToPort="-1",
            CidrIp=Ref(white_list_ip),
        )
    ]
))

public_zone = PublicZone("Public")
db_zone = DbZone("Db")
mngmt_zone = Zone("Mngmt")
game_zone = Zone("Game")

t.add_zone(public_zone)
t.add_zone(db_zone)
t.add_zone(mngmt_zone)
t.add_zone(game_zone)


t.create_nat_in_zone(public_zone.title)

t.create_nat_route(game_zone.title,"0.0.0.0/0")
t.create_nat_route(mngmt_zone.title,"0.0.0.0/0")

t.add_output(Output(
    "SecurityGroupPublic",
    Value=Ref(security_group_public),
    Export=Export(
        Sub("${AWS::StackName}-SecurityGroupPublic")
    )

))

print t.to_json()



```

usage of Compose2TaskDefinition

```python
from tropolib.docker import Compose2TaskDefinition
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
task = Compose2TaskDefinition(filename, image_map)


# Set an environment variable
task.environment("php7")["DB_HOST"]=Ref(db_host)



# Retrieves the troposphere.ecs.TaskDefinition object and sets its title ( LogicalId ) equal to the title parameter
t.add_resource(task.get_task_definition(title="taskdef"))
print t.to_json()


```