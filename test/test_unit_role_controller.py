import unittest

import conjur
from conjur.controller.role_controller import RoleController
from conjur.logic.role_logic import RoleLogic
from conjur_api import Client


class RoleControllerTest(unittest.TestCase):
    def test_role_exists_resource_id_without_kind_raises_missing_required_parameter_exception(self):
        client = Client
        mock_role_logic = RoleLogic(client)
        mock_role_controller = RoleController(mock_role_logic)

        with self.assertRaises(conjur.errors.MissingRequiredParameterException):
            mock_role_controller.role_exists("resource_id") # missing kind (kind:resource_id)

    def test_role_memberships_resource_id_without_kind_raises_missing_required_parameter_exception(self):
        client = Client
        mock_role_logic = RoleLogic(client)
        mock_role_controller = RoleController(mock_role_logic)

        with self.assertRaises(conjur.errors.MissingRequiredParameterException):
            mock_role_controller.role_memberships("resource_id") # missing kind (kind:resource_id)
