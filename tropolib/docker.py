from troposphere import (ecs, Ref)
import yaml, os


class Compose2TaskDefinition():
    def __init__(self, compose_file, name_image_map):
        self.compose_file = compose_file
        self.container_definitions = {}
        filename = os.path.join(os.path.dirname(__file__), self.compose_file)
        f = open(filename)
        data_map = yaml.safe_load(f)
        f.close()
        defs = []
        for name in data_map:
            port_mappings = Ref("AWS::NoValue")
            if data_map[name].get("ports") is not None:
                port_mappings = []
                for pm in data_map[name].get("ports"):
                    port_mappings.append(
                        ecs.PortMapping(
                            ContainerPort=pm.split(":")[1],
                            HostPort=pm.split(":")[0],
                        )
                    )

            if data_map[name].get("links") is not None:
                links = []
            self.container_definitions[name] = ecs.ContainerDefinition(
                Name=name,
                Image=name_image_map[name],
                Cpu=data_map[name].get("cpu_shares", Ref("AWS::NoValue")),
                # TODO Convert correct with M and G
                Memory=data_map[name]["mem_limit"][:-1],
                Essential=True,
                PortMappings=port_mappings,
                Links=data_map[name].get("links", Ref("AWS::NoValue"))

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
