from troposphere import rds, Ref, Sub


class Zone(object):
    def __init__(self):
        self.public = False
        self.subnets = []
        self.efs_mount_targets = []
        self.azs = []


class PublicZone(Zone):
    def __init__(self):
        super(PublicZone, self).__init__()
        self.public = True


class DbZone(Zone):
    count = 0

    def __init__(self):
        super(DbZone, self).__init__()

    def get_db_subnet_group(self):
        group = rds.DBSubnetGroup(
            "DbSubnetGroup{}".format(DbZone.count),
            DBSubnetGroupDescription=Sub("Db subnet group created in ${AWS::StackName}"),
            SubnetIds=[]
        )
        for s in self.subnets:
            group.SubnetIds.append(Ref(s))

        DbZone.count += 1
        return group
