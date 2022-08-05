import unittest
from unittest.mock import MagicMock, patch

from conjur_api import Client
from conjur.logic.check_logic import CheckLogic
from conjur_api.errors.errors import HttpStatusError

class CheckLogicTest(unittest.TestCase):

    client = Client
    check_logic = CheckLogic(client)

    def test_check_logic_constructor(self):
        mock_client = None
        mock_check_logic = CheckLogic(mock_client)
        self.assertEquals(mock_check_logic.client, mock_client)

    @patch('conjur_api.Client.check_privilege')
    def test_check_privilege_calls_client(self, mock_check):
        self.check_logic.check('some_kind', 'some_resource_id', 'some_privilege', 'some_role_id')
        mock_check.assert_called_once_with('some_kind', 'some_resource_id', 'some_privilege', 'some_role_id')

    def test_check_privilege_missing_resource_or_privilege_parameter_raises_exception(self):
        with self.assertRaises(TypeError):
            self.check_logic.check('some_kind', 'some_parameter')

    def test_check_privilege_missing_resource_and_privilege_parameters_raises_exception(self):
        with self.assertRaises(TypeError):
            self.check_logic.check('some_kind')

    def test_check_privilege_response_default_role(self):
        self.client.check_privilege = MagicMock(return_value=True)
        self.assertEqual(self.check_logic.check('some_kind', 'some_resource_id', 'some_privilege'), True)

    def test_check_privilege_response_specified_role(self):
        self.client.check_privilege = MagicMock(return_value=True)
        self.assertEqual(self.check_logic.check('some_kind', 'some_resource_id', 'some_privilege', 'some_role_id'), True)

    def test_check_privilege_response_invalid_credentials_default_role(self):
        self.client.check_privilege = MagicMock(side_effect=HttpStatusError(status=401, message="Invalid Credentials"))
        with self.assertRaises(HttpStatusError):
            self.check_logic.check('some_kind', 'some_resource_id', 'some_privilege')

    def test_check_privilege_response_invalid_credentials_specified_role(self):
        self.client.check_privilege = MagicMock(side_effect=HttpStatusError(status=401, message="Invalid Credentials"))
        with self.assertRaises(HttpStatusError):
            self.check_logic.check('some_kind', 'some_resource_id', 'some_privilege', 'some_role_id')
