import unittest
from unittest.mock import patch

from pydantic import ValidationError

from fastapi.testclient import TestClient
from OpenStackFlavorExporter.main import app
from OpenStackFlavorExporter.model import ExtendedFlavor, Flavor
from tests import mock_openstack_connection


@patch('OpenStackFlavorExporter.openstack.create_osclient')
class TestFastAPI(unittest.TestCase): # pylint: disable=missing-class-docstring

    client = TestClient(app)

    def test_gpus_flavors(self,mock):
        """
        Test a legacy GPU flavor list access.
        
        :param self: self
        :param mock: mock object
        """

        mock_openstack_connection(mock)
        response = self.client.get("/gpus/flavors")

        assert response.status_code == 200


        list_of_flavors = response.json()

        # list should return 3 flavor elements
        self.assertEqual(3,len(list_of_flavors))

        # iterate over all and  ...
        for f in list_of_flavors:
            ## ... validate against the model
            try:
                obj = Flavor.model_validate(f)

            except ValidationError as e:
                self.fail(e)


    def test_gpu_flavor(self,mock):
        """
        Test a single flavor access.
        
        :param self: self
        :param mock: mock object
        """

        mock_openstack_connection(mock)
        response = self.client.get("/gpus/flavor/a54ed137-04fe-463f-a2b0-666079d1b2ba")
        assert response.status_code == 200
        try:
            obj = Flavor.model_validate(response.json())
            self.assertEqual("de.NBI GPU V100 medium",obj.name)
            self.assertEqual(4,obj.total)
            self.assertEqual(3,obj.available)
        except ValidationError as e:
            self.fail(e)

    def test_v2_flavors(self,mock):
        """
        Test a flavor list access.
        
        :param self: self
        :param mock: mock object
        """

        mock_openstack_connection(mock)
        response = self.client.get("/v2/flavors")

        assert response.status_code == 200


        list_of_flavors = response.json()

        # list should return 9 flavor elements
        self.assertEqual(9,len(list_of_flavors))

        # iterate over all and  ...
        for f in list_of_flavors:
            ## ... validate against the model
            try:
                obj = ExtendedFlavor.model_validate(f)

            except ValidationError as e:
                self.fail(e)

    def test_v2_flavor(self,mock):
        """
        Test a single flavor access.
        
        :param self: self
        :param mock: mock object
        """
        mock_openstack_connection(mock)
        response = self.client.get("/v2/flavor/a54ed137-04fe-463f-a2b0-666079d1b2ba")
        assert response.status_code == 200
        try:
            obj = ExtendedFlavor.model_validate(response.json())
            self.assertEqual("de.NBI GPU V100 medium",obj.name)
            self.assertEqual(4,obj.total)
            self.assertEqual(3,obj.available)
            self.assertEqual(14,obj.cores)
            self.assertEqual(65535,obj.mem)
            self.assertEqual("gpu",obj.type)
            self.assertEqual("V100",obj.gpu_type)
            self.assertEqual(1,obj.gpu_count)
            self.assertEqual(50,obj.root_disk)
            self.assertEqual(0,obj.ephemeral_disk)

        except ValidationError as e:
            self.fail(e)

if __name__ == "__main__":
    unittest.main()
