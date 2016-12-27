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
