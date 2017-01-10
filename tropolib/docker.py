from troposphere import (ecs, Ref)
import yaml, os


class Compose2TaskDefinition():
    def __init__(self, compose_file, name_image_map):
        self.compose_file = compose_file
        self.container_definitions = {}

        f = open(self.compose_file)
        data_map = yaml.safe_load(f)
        f.close()
        defs = []

        for name in data_map:
            environment = []
            port_mappings = Ref("AWS::NoValue")
            volumes_from = Ref("AWS::NoValue")
            if data_map[name].get("ports") is not None:
                port_mappings = []
                for pm in data_map[name].get("ports"):
                    port_mappings.append(
                        ecs.PortMapping(
                            ContainerPort=pm.split(":")[1],
                            HostPort=pm.split(":")[0],
                        )
                    )
            if data_map[name].get("volumes_from") is not None:
                volumes_from = []
                for vf in data_map[name].get("volumes_from"):
                    volumes_from.append(
                        ecs.VolumesFrom(
                            SourceContainer=vf
                        )
                    )
            for env in data_map[name].get("environment", []):
                environment.append(ecs.Environment(
                    Name=env.split("=", 1)[0],
                    Value=env.split("=", 1)[1]
                ))

            self.container_definitions[name] = ecs.ContainerDefinition(
                Name=name,
                Image=name_image_map[name],
                Cpu=data_map[name].get("cpu_shares", Ref("AWS::NoValue")),
                # TODO Convert correct with M and G
                Memory=data_map[name]["mem_limit"][:-1],
                Essential=True,
                PortMappings=port_mappings,
                Links=data_map[name].get("links", Ref("AWS::NoValue")),
                VolumesFrom=volumes_from,
                Environment=environment
            )

            defs.append(
                self.container_definitions[name]
            )

    def get_container_definition(self, name):
        return self.container_definitions[name]

    def get_task_definition(self, title):

        defs = []
        for name in self.container_definitions:
            defs.append(self.container_definitions[name])
        return ecs.TaskDefinition(
            title,
            ContainerDefinitions=defs
        )

    def environment(self, name):
        return ContainerEnvironment(self.get_container_definition(name))


class ContainerEnvironment(object):
    def __init__(self, container):
        self._items = {}
        self.container = container

    def __setitem__(self, key, value):
        for e in self.container.Environment:
            if e.Name == key:
                e.Value = value
                return
        self.container.Environment.append(ecs.Environment(
            Name=key,
            Value=value
        ))

    def __getitem__(self, key):
        for e in self.container.Environment:
            if e.Name == key:
                return e.Value
        return None

    def __len__(self):
        return len(self.container.Environment)

    def __iter__(self):
        ret = {}
        for e in self.container.Environment:
            ret[e.Name] = e.Value
        return iter(ret)
