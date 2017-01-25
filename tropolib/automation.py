from troposphere import (
    Ref, Join, Base64
)
from troposphere.cloudformation import (
    Metadata, Init, InitConfigSets, InitConfig
)


def userdata_file_path(name):
    return name + '.sh'

def userdata_from_file(userdata_file, parameters=None, references=None,
                       constants=None):
    """
    creates userdata for troposphere and cloudinit
    inserts `parameters` at the top of the script

    :type parameters: list
    :param parameters: list of troposphere.Parameters()

    :type references
    :param parameters: list of troposphere.Ref()

    :type constants
    :param constants: list of tuple(key, value)

    :rtype: troposphere.Base64()
    :return: troposphere ready to consume userdata
    """
    userdata = ['#!/bin/bash\n']
    if parameters is None:
        parameters = []

    if references is None:
        references = []

    if constants is None:
        constants = []

    for param in parameters:
        variable_name = param.title
        userdata = userdata + [variable_name] + ['='] + [Ref(param)] + ['\n']

    for ref in references:
        # Create variable name from Ref function
        # Example: {"Ref": "AWS::Region"} -> AWSRegion
        variable_name = ref.data['Ref'].replace('::', '')
        userdata = userdata + [variable_name] + ['='] + [ref.data] + ['\n']

    for constant in constants:
        userdata = userdata + [constant[0]] + ['='] + [constant[1]] + ['\n']

    # append the actial file
    with open(userdata_file, 'r') as f:
        userdata.extend(f.readlines())

    return Base64(Join('', userdata))




class UserData(object):
    def __init__(self):
        self.shell_scripts = []
        self.upstart_jobs = []

    def add_file(self, userdata_file, type="shell", parameters=None, references=None,
                 constants=None):
        userdata = []
        if parameters is None:
            parameters = []

        if references is None:
            references = []

        if constants is None:
            constants = []

        for param in parameters:
            variable_name = param.title
            userdata = userdata + [variable_name] + ['='] + [Ref(param)] + ['\n']

        for ref in references:
            # Create variable name from Ref function
            # Example: {"Ref": "AWS::Region"} -> AWSRegion
            variable_name = ref.data['Ref'].replace('::', '')
            userdata = userdata + [variable_name] + ['='] + [ref.data] + ['\n']

        for constant in constants:
            userdata = userdata + [constant[0]] + ['='] + [constant[1]] + ['\n']

        with open(userdata_file, 'r') as f:
            userdata.extend(f.readlines())
        if type == "shell":
            self.shell_scripts.append(userdata)
        elif type == "upstart":
            self.upstart_jobs.append(userdata)
        else :
            raise NameError("Type: must be either shell or upstart")

    def get_user_data(self):
        ret = []
        boundary="==BOUNDARY=="
        ret.append('Content-Type: multipart/mixed; boundary="{}"\n'.format(boundary))
        boundary+='\n'
        ret.append('MIME-Version: 1.0\n')

        for u in self.upstart_jobs:
            ret.append('\n--{0}'.format(boundary))
            ret.append('MIME-Version: 1.0\n')
            ret.append('Content-Type: text/upstart-job; charset="us-ascii"\n')
            ret.extend(u)

        for sh in self.shell_scripts:
            ret.append('\n--{0}'.format(boundary))
            ret.append('MIME-Version: 1.0\n')
            ret.append('Content-Type: text/x-shellscript; charset="us-ascii"\n')
            ret.extend(sh)

        return Base64(Join('', ret))


