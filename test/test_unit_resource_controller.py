import unittest

import conjur
from conjur.controller.resource_controller import ResourceController
from conjur.logic.resource_logic import ResourceLogic
from conjur_api import Client


class ResourceControllerTest(unittest.TestCase):
    def test_resource_exists_resource_id_without_kind_raises_missing_required_parameter_exception(self):
        client = Client
        mock_resource_logic = ResourceLogic(client)
        mock_resource_controller = ResourceController(mock_resource_logic)

        with self.assertRaises(conjur.errors.MissingRequiredParameterException):
            mock_resource_controller.exists("resource_id") # missing kind (kind:resource_id)
