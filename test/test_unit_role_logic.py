import unittest
from unittest.mock import MagicMock, patch

from conjur_api import Client

from conjur.logic.role_logic import RoleLogic
from conjur_api.errors.errors import HttpStatusError

MockMemberships = ['default:policy:test', 'default:group:somegroup']

class RoleLogicTest(unittest.TestCase):
    client = Client
    role_logic = RoleLogic(client)

    def test_role_logic_constructor(self):
        mock_client = None
        role_logic = RoleLogic(mock_client)
        self.assertEquals(role_logic.client, mock_client)

    
    @patch('conjur_api.Client.role_exists')
    def test_role_exists_calls_client(self, mock_role_exists):
        self.role_logic.role_exists('some_kind', 'some_id')
        mock_role_exists.assert_called_once_with('some_kind', 'some_id')

    '''
    Raises exception when the request is missing a required parameter
    '''
    def test_role_exists_missing_parameter_raises_exception(self):
        with self.assertRaises(TypeError):
            self.role_logic.role_exists('somekind')

    '''
    Returns true when the API returns true
    '''
    def test_role_exists_response(self):
        self.client.role_exists = MagicMock(return_value=True)
        self.assertEqual(self.role_logic.role_exists('somekind', 'someapp'), True)

    '''
    Raises exception when the API returns an error
    '''
    def test_role_exists_raises_exception_other_http_error(self):
        self.role_logic.client.role_exists = MagicMock(side_effect=HttpStatusError(status=500, message="Server Error"))
        with self.assertRaises(HttpStatusError):
            self.role_logic.role_exists('somekind', 'someapp')

    '''
    Raises exception when the request is missing a required parameter
    '''
    def test_role_memberships_missing_parameter_raises_exception(self):
        with self.assertRaises(TypeError):
            self.role_logic.role_memberships('somekind')

    '''
    Returns list of memberships from the API call
    '''
    def test_role_memberships_response(self):
        self.client.role_memberships = MagicMock(return_value=MockMemberships)
        self.assertEqual(self.role_logic.role_memberships('somekind', 'someuser'), MockMemberships)

    '''
    Raises exception when API error occurs
    '''
    def test_role_memberships_raises_exception_http_error(self):
        self.role_logic.client.role_memberships = MagicMock(side_effect=HttpStatusError(status=404, message="Not found"))
        with self.assertRaises(HttpStatusError):
            self.role_logic.role_memberships('somekind', 'someapp')
