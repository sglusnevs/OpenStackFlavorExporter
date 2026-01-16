import unittest
from unittest.mock import patch

import OpenStackFlavorExporter.openstack
import OpenStackFlavorExporter.openstack.resources
from tests import mock_openstack_connection


@patch('OpenStackFlavorExporter.openstack.create_osclient')
class TestResource(unittest.TestCase): # pylint: disable=missing-class-docstring,invalid-name

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
        # test data contains 9 flavors at all
        self.assertEqual(9, len(resources.__flavors__))


    def test_get_flavors(self,mock): #pylint: disable=invalid-name

        mock_openstack_connection(mock)

        # create new Resources object
        resources = OpenStackFlavorExporter.openstack.resources.Resources()
        # and update data
        resources.update()

        flavors = resources.get_flavors()

        # test data contains 9 enabled flavors, so 9 entries should be returned
        self.assertEqual(9,len(flavors))

        # check expected availibility for each flavor
        denbi_small = resources.get_flavor("299eeca6-ae00-44c2-99ff-eb7e3455d17f")
        self.assertEqual(30,denbi_small.available)
        self.assertEqual(42,denbi_small.total)
        denbi_small_legacy = resources.get_flavor("799eeca6-ae00-44c2-99ff-eb7e3455d17f")
        self.assertEqual(30,denbi_small_legacy.available)
        self.assertEqual(42,denbi_small_legacy.total)
        denbi_medium = resources.get_flavor("161dac45-ae04-4e01-8a49-b81ee8063863")
        self.assertEqual(18,denbi_medium.available)
        self.assertEqual(24,denbi_medium.total)
        denbi_medium_legacy = resources.get_flavor("261dac45-ae04-4e01-8a49-b81ee8063863")
        self.assertEqual(18,denbi_medium_legacy.available)
        self.assertEqual(24,denbi_medium_legacy.total)
        denbi_large = resources.get_flavor("33050139-1b6b-4aee-a39d-6c501fa6ae61")
        self.assertEqual(9,denbi_large.available)
        self.assertEqual(12,denbi_large.total)
        denbi_V100_medium = resources.get_flavor("a54ed137-04fe-463f-a2b0-666079d1b2ba") #pylint: disable=invalid-name
        self.assertEqual(3,denbi_V100_medium.available)
        self.assertEqual(4,denbi_V100_medium.total)
        denbi_V100_large = resources.get_flavor("4e6428f5-a0ec-4450-8f38-112236f056da") #pylint: disable=invalid-name
        self.assertEqual(3,denbi_V100_large.available)
        self.assertEqual(4,denbi_V100_large.total)
        denbi_2V100_large = resources.get_flavor("9a8a5bfc-001e-469b-a787-ddbbc2ea8483") #pylint: disable=invalid-name
        self.assertEqual(1,denbi_2V100_large.available)
        self.assertEqual(2,denbi_2V100_large.total)
        windows_standard = resources.get_flavor("234eac45-ae04-4e01-8a49-b81ee8063863")
        self.assertEqual(18,windows_standard.available)
        self.assertEqual(24,windows_standard.total)

    def test_get_flavors_whitelist_filter(self,mock):
        """Test get_flavors with whitelist filter."""

        mock_openstack_connection(mock)

        # create new Resources object
        resources = OpenStackFlavorExporter.openstack.resources.Resources(whitelist=[r"^de.NBI"])
        # and update data
        resources.update()

        flavors = resources.get_flavors()
        # test data contains 8 enabled flavors starting with "denbi", so 8 entries should be returned
        self.assertEqual(8,len(flavors))

    def test_get_flavors_blacklist_filter(self,mock):
        """Test get_flavors with blacklist filter."""

        mock_openstack_connection(mock)

        # create new Resources object
        resources = OpenStackFlavorExporter.openstack.resources.Resources(blacklist=[r".*LEGACY",r"Windows"])
        # and update data
        resources.update()

        flavors = resources.get_flavors()
        # test data contains 7 non legacy enabled flavors and one flavor starting with "windows", so 6 entries should be returned
        self.assertEqual(6,len(flavors))

    def test_get_flavors_white_and_blacklist_filter(self,mock):
        """Test get_flavors with white_ and blacklist filter."""

        mock_openstack_connection(mock)

        # create new Resources object
        resources = OpenStackFlavorExporter.openstack.resources.Resources(whitelist=[r"^de.NBI"],blacklist=[r".*LEGACY",r".*GPU"])
        # and update data
        resources.update()

        flavors = resources.get_flavors()
        # test data contains 8 enabled de.NBI flavor, two of them are legacy and 3 are GPU flavors, so 3 entries should be returned
        self.assertEqual(7,len(flavors))

if __name__ == "__main__":
    unittest.main()
