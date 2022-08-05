import unittest

import conjur
from conjur.controller.check_controller import CheckController
from conjur.logic.check_logic import CheckLogic
from conjur_api import Client


class CheckControllerTest(unittest.TestCase):
    def test_check_privilege_on_resource_id_without_kind_raises_missing_required_parameter_exception(self):
        client = Client
        mock_check_logic = CheckLogic(client)
        mock_check_controller = CheckController(mock_check_logic)

        with self.assertRaises(conjur.errors.MissingRequiredParameterException):
            mock_check_controller.check("resource_id", "privilege", "role") # missing kind (kind:resource_id)
