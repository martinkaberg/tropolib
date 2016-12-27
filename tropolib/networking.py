from troposphere import rds, Ref, Sub, ec2, GetAZs, Select, Output, Export, GetAtt

from . import ExportTemplate


class Network(ExportTemplate):
    def __init__(self, configuration=None, description="An Export Template", metadata={}):
        super(Network, self).__init__(configuration, description, metadata)
        self.vpc = self.add_resource(ec2.VPC("Vpc",
                                             CidrBlock="10.0.0.0/16",
                                             EnableDnsSupport=True,
                                             EnableDnsHostnames=True
                                             ))
        self.gateways = {}
        self.zones = []
        self.db_subnet_groups = {}
        self.zone_multiplier = 1

        igw = self.add_resource(ec2.InternetGateway(
            "Igw",
        ))

        igw_attachment = self.add_resource(ec2.VPCGatewayAttachment(
            "IgwAttachment",
            VpcId=Ref(self.vpc),
            InternetGatewayId=Ref(igw),
        ))

        self.public_route_table = self.add_resource(ec2.RouteTable(
            "PublicRouteTable",
            VpcId=Ref(self.vpc),
        ))

        public_route = self.add_resource(ec2.Route(
            "PublicRoute",
            DependsOn=[igw_attachment.title],
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=Ref(igw),
            RouteTableId=Ref(self.public_route_table),
        ))

        self.add_output(Output(
            "Vpc",
            Value=Ref(self.vpc),
            Export=Export(
                Sub("${AWS::StackName}-Vpc")
            )
        ))

    def get_zone(self, title):
        for z in self.zones:
            if title == z.title:
                return z
        return None

    def add_zone(self, zone, azs=3):
        azs -= 1

        z = zone
        if self.get_zone(z.title) is not None:
            raise NameError("Zone with the name {} already added".format(z.title))
        self.zones.append(zone)
        if isinstance(z, PublicZone):
            for k, v in [('a', 0), ('b', 1), ('c', 2)]:
                if v > azs:
                    continue
                z.subnets.append(self.add_resource(ec2.Subnet(
                    "{}{}".format(z.title, k.capitalize()),
                    AvailabilityZone=Select(v, GetAZs()),
                    CidrBlock="10.0.{}.0/24".format(v * self.zone_multiplier),
                    MapPublicIpOnLaunch=z.public,
                    VpcId=Ref(self.vpc),
                )))
                self.add_output(Output(
                    "{}{}".format(z.title, k.capitalize()),
                    Value=Ref(z.subnets[v]),
                    Export=Export(
                        Sub("${AWS::StackName}-" + z.title + k.capitalize())
                    )
                ))

            for s in z.subnets:
                self.add_resource(ec2.SubnetRouteTableAssociation(
                    "Assoc{}".format(s.title),
                    RouteTableId=Ref(self.public_route_table),
                    SubnetId=Ref(s)
                ))

        elif isinstance(z, DbZone):
            for k, v in [('a', 0), ('b', 1), ('c', 2)]:
                if v > azs:
                    continue
                z.subnets.append(self.add_resource(ec2.Subnet(
                    "{}{}".format(z.title, k.capitalize()),
                    AvailabilityZone=Select(v, GetAZs()),
                    CidrBlock="10.0.{}.0/24".format(v + self.zone_multiplier),
                    MapPublicIpOnLaunch=z.public,
                    VpcId=Ref(self.vpc),
                )))
                self.add_output(Output(
                    "{}{}".format(z.title, k.capitalize()),
                    Value=Ref(z.subnets[v]),
                    Export=Export(
                        Sub("${AWS::StackName}-" + z.title +  k.capitalize())
                    )
                ))
            db_subnet_group = self.add_resource(
                z.get_db_subnet_group()
            )
            self.add_output(Output(
                db_subnet_group.title,
                Value=Ref(db_subnet_group),
                Export=Export(
                    Sub("${AWS::StackName}-" + db_subnet_group.title)
                )
            ))
            self.db_subnet_groups[db_subnet_group.title] = db_subnet_group

        elif isinstance(z, Zone):
            for k, v in [('a', 0), ('b', 1), ('c', 2)]:
                if v > azs:
                    continue
                z.subnets.append(self.add_resource(ec2.Subnet(
                    "{}{}".format(z.title, k.capitalize()),
                    AvailabilityZone=Select(v, GetAZs()),
                    CidrBlock="10.0.{}.0/24".format(v + self.zone_multiplier),
                    MapPublicIpOnLaunch=z.public,
                    VpcId=Ref(self.vpc),
                )))
                self.add_output(Output(
                    "{}{}".format(z.title, k.capitalize()),
                    Value=Ref(z.subnets[v]),
                    Export=Export(
                        Sub("${AWS::StackName}-" + z.title + k.capitalize())
                    )
                ))
        self.zone_multiplier += (1 * (azs + 1))

    def create_nat_in_zone(self, title):
        zone = self.get_zone(title)
        self.gateways["nat"] = []
        for s in zone.subnets:
            self.gateways["nat"].append(self.add_resource(ec2.NatGateway(
                "NatGw{}".format(s.title),
                SubnetId=Ref(s),
                AllocationId=GetAtt(self.add_resource(
                    ec2.EIP(
                        "NatIp{}".format(s.title),
                        Domain="vpc",
                        DependsOn="IgwAttachment"
                    )
                ), "AllocationId")
            )))

    def create_nat_route(self, zone_title, dest):
        zone = self.get_zone(zone_title)

        for s in range(len(zone.subnets)):
            subnet = zone.subnets[s]
            rt = self.add_resource(ec2.RouteTable(
                "RouteTable{}".format(subnet.title),
                VpcId=Ref(self.vpc),
            ))

            self.add_resource(ec2.Route(
                "Route{}".format(subnet.title),
                DependsOn=[self.gateways["nat"][s].title],
                DestinationCidrBlock=dest,
                NatGatewayId=Ref(self.gateways["nat"][s]),
                RouteTableId=Ref(rt),
            ))

            self.add_resource(ec2.SubnetRouteTableAssociation(
                "RtAssoc{}".format(subnet.title),
                RouteTableId=Ref(rt),
                SubnetId=Ref(subnet)
            ))


class Zone(object):
    def __init__(self, title):
        self.public = False
        self.subnets = []
        self.efs_mount_targets = []
        self.azs = []
        self.title = title


class PublicZone(Zone):
    def __init__(self, title, nat=0):
        super(PublicZone, self).__init__(title)
        self.public = True
        self.nat = nat
        for index in range(nat):
            pass


class DbZone(Zone):
    def __init__(self, title):
        super(DbZone, self).__init__(title)

    def get_db_subnet_group(self):
        group = rds.DBSubnetGroup(
            "DbSubnetGroup{}".format(self.title),
            DBSubnetGroupDescription=Sub("Db subnet group created in ${AWS::StackName}"),
            SubnetIds=[]
        )
        for s in self.subnets:
            group.SubnetIds.append(Ref(s))

        return group
