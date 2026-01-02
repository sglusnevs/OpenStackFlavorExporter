import OpenStackFlavorExporter.openstack
import OpenStackFlavorExporter.openstack.resources
import unittest

from tests import mock_openstack_connection
from unittest.mock import patch

@patch('OpenStackFlavorExporter.openstack.create_osclient')
class TestResource(unittest.TestCase):


    def setUp(self):
        pass
    def setDown(self):
        pass


    def test_resource_update(self, mock):
        mock_openstack_connection(mock) 

        # create new Resources object
        resources = OpenStackFlavorExporter.openstack.resources.Resources()
        # and update data
        resources.update()

        # test data contains 3 hypervisor at all
        self.assertEqual(3, len(resources.__hypervisors__))
        # test data contains 2 aggregate at all
        self.assertEqual(2, len(resources.__map_of_aggregates__))
        # test data contains 6 flavors at all
        self.assertEqual(6, len(resources.__flavors__))

   
    def test_get_flavors(self,mock):
        mock_openstack_connection(mock) 

        # create new Resources object
        resources = OpenStackFlavorExporter.openstack.resources.Resources()
        # and update data
        resources.update()

        flavors = resources.getFlavors();

        # test data contains 6 flavors, so 6 entries should be returned
        self.assertEqual(6,len(flavors))

        # check expected availibility for each flavor
        deNBI_small = resources.getFlavor("299eeca6-ae00-44c2-99ff-eb7e3455d17f")
        self.assertEqual(30,deNBI_small.available)
        self.assertEqual(42,deNBI_small.total)
        deNBI_medium = resources.getFlavor("161dac45-ae04-4e01-8a49-b81ee8063863")
        self.assertEqual(18,deNBI_medium.available)
        self.assertEqual(24,deNBI_medium.total)
        deNBI_large = resources.getFlavor("33050139-1b6b-4aee-a39d-6c501fa6ae61")
        self.assertEqual(9,deNBI_large.available)
        self.assertEqual(12,deNBI_large.total)
        deNBI_V100_medium = resources.getFlavor("a54ed137-04fe-463f-a2b0-666079d1b2ba")
        self.assertEqual(3,deNBI_V100_medium.available)
        self.assertEqual(4,deNBI_V100_medium.total)
        deNBI_V100_large = resources.getFlavor("4e6428f5-a0ec-4450-8f38-112236f056da")
        self.assertEqual(3,deNBI_V100_large.available)
        self.assertEqual(4,deNBI_V100_large.total)
        deNBI_2V100_large = resources.getFlavor("9a8a5bfc-001e-469b-a787-ddbbc2ea8483")
        self.assertEqual(1,deNBI_2V100_large.available)
        self.assertEqual(2,deNBI_2V100_large.total)


if __name__ == "__main__":
    unittest.main()