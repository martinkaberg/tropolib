from troposphere import (ecs, Ref)
import yaml, os


class Compose2TaskDefinition():
    def __init__(self, compose_file):
        self.compose_file = compose_file

    def get_task_definition(self, title, name_image_map):

        filename = os.path.join(os.path.dirname(__file__), '../docker-compose.yml')
        f = open(filename)
        data_map = yaml.safe_load(f)
        f.close()
        print data_map
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

            defs.append(
                ecs.ContainerDefinition(
                    Name=name,
                    Image=name_image_map[name],
                    Cpu=data_map[name].get("cpu_shares", Ref("AWS::NoValue")),
                    # TODO Convert correct with M and G
                    Memory=data_map[name]["mem_limit"][:-1],
                    Essential=True,
                    PortMappings=port_mappings,
                    Links=data_map[name].get("links", Ref("AWS::NoValue"))

                )
            )
        return ecs.TaskDefinition(
            title,
            ContainerDefinitions=defs
        )
