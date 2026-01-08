""" Module denbi provides some helper functions to connect Openstack API. """
from openstack import connection
import os_client_config

def create_osclient(microversions={'compute':'2.79'}): # pylint: disable=dangerous-default-value

    """
    Create an authorized openstack.connection.Connection object, that allows
    REST API calls.

    :param: microversions - a dict containing microversions, where the key
    describes the service and the value the microversion to be used

    :return: Return an authorized openstack.connection.Connection object
    """

    config=os_client_config.get_config()

    for service in microversions:
        config.config[f'{service}_default_microversion']=microversions[service]

    return connection.Connection(config=config)
