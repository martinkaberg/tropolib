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
