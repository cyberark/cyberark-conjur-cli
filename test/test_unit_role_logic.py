import unittest
from unittest.mock import MagicMock, patch

from conjur_api import Client

from conjur.logic.role_logic import RoleLogic
from conjur_api.errors.errors import HttpStatusError

MockRole = {'created_at': None, 'id': 'default:somekind:someapp', 'policy': 'default:policy:test', 
            'members': []}
MockMemberships = ['default:policy:test', 'default:group:somegroup']

class RoleLogicTest(unittest.TestCase):
    client = Client
    role_logic = RoleLogic(client)

    def test_role_logic_constructor(self):
        mock_client = None
        role_logic = RoleLogic(mock_client)
        self.assertEquals(role_logic.client, mock_client)

    '''
    Raises exception when the request is missing a required parameter
    '''
    def test_role_exists_missing_parameter_raises_exception(self):
        with self.assertRaises(TypeError):
            self.role_logic.role_exists('somekind')

    '''
    Returns true when the API returns an existing role
    '''
    def test_role_exists_response(self):
        self.client.get_role = MagicMock(return_value=MockRole)
        self.assertEqual(self.role_logic.role_exists('somekind', 'someapp'), True)

    '''
    Returns false when the API returns a 404 not found error
    '''
    def test_role_exists_response_role_not_found(self):
        self.role_logic.client.get_role = MagicMock(side_effect=HttpStatusError(status=404, message="Not Found"))
        self.assertEqual(self.role_logic.role_exists('somekind', 'someapp'), False)

    '''
    Raises exception when another error besides 404 occurs
    '''
    def test_role_exists_raises_exception_other_http_error(self):
        self.role_logic.client.get_role = MagicMock(side_effect=HttpStatusError(status=500, message="Server Error"))
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
