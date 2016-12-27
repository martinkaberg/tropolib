import troposphere
import troposphere.cloudformation as cloudformation
from uuid import uuid4


class ExportTemplate(troposphere.Template):
    def __init__(self, configuration=None, description="An Export Template", metadata={}):
        """

        :param description: Template description
        :param metadata: dictionary of template metadata
        :return:
        """
        super(ExportTemplate, self).__init__()
        self.title = None
        self.add_description(description)
        self.add_version("2010-09-09")
        self.add_metadata(metadata)
        self.interface = {}
        self.interface_params = {}
        self.prefix = ""
        self.add_resource(cloudformation.WaitConditionHandle(
            str(uuid4()).replace("-", "")
        ))
        if configuration is None:
            self.config = {}
        else:
            self.config = configuration
            self.config_name = "Config"
            self.add_mapping(self.config_name, {"Members": self.config})
