""" Module denbi provides some helper functions to connect Openstack API. """
import os

import openstack


def create_osclient(microversions={'compute':'2.79'}): # pylint: disable=dangerous-default-value

    """
    Create an authorized openstack.connection.Connection object, that allows
    REST API calls.

    :param: microversions - a dict containing microversions, where the key
    describes the service and the value the microversion to be used

    :return: Return an authorized openstack.connection.Connection object
    """

    if os.environ["OS_AUTH_URL"]:
        # if OS_AUTH_URL is set, prefer envvars        
        connection = openstack.connect(load_yaml_config=False,load_envvars=True)
    elif os.environ["OS_CLOUD"]:
        # if OS_CLOUD is set, prefer clouds.yaml
        connection = openstack.connect(load_yaml_config=True,load_envvars=False)
    else:
        # if neither OS_AUTH_URL nor OS_CLOUD is set, use default settings
        connection = openstack.connect()

    # set microversions
    for service in microversions:
        connection.config.config[f'{service}_default_microversion']=microversions[service]

    return connection
