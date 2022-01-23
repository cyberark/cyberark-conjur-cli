import unittest
from unittest.mock import MagicMock, patch

from conjur_api  import Client
from conjur.errors import MissingRequiredParameterException
from conjur.controller.host_controller import HostController
from conjur.data_object.host_resource_data import HostResourceData
from conjur.resource import Resource


class HostControllerTest(unittest.TestCase):
    client = Client
    host_resource_data = HostResourceData(action='someaction', host_to_update='somehost')
    host_controller = HostController(client, host_resource_data)

    def test_host_controller_constructor(self):
        mock_client = None
        mock_host_resource_data = None
        host_controller = HostController(mock_client, mock_host_resource_data)
        assert host_controller.client == mock_client
        assert host_controller.host_resource_data == mock_host_resource_data

    @patch('conjur_api.Client')
    def test_rotate_api_key_calls_necessary_functions(self, mock_client):
        mock_host_resource_data = HostResourceData(action='someaction', host_to_update='somehost')
        mock_host_controller = HostController(mock_client, mock_host_resource_data)
        mock_host_controller.prompt_for_host_id_if_needed = MagicMock()
        mock_host_controller.client.rotate_other_api_key = MagicMock()
        mock_host_controller.rotate_api_key()
        mock_host_controller.prompt_for_host_id_if_needed.assert_called_once()

        mock_host_controller.client.rotate_other_api_key.assert_called_once_with(Resource(kind='host', identifier=mock_host_resource_data.host_to_update))

    def test_user_does_not_provide_host_id_raises_exception(self):
        mock_client=Client
        mock_host_resource_data = HostResourceData(action='someaction', host_to_update=None)
        mock_host_controller = HostController(mock_client, mock_host_resource_data)
        # Raise error that the ID is required
        with self.assertRaises(MissingRequiredParameterException):
            with patch('builtins.input', return_value=''):
                mock_host_controller.prompt_for_host_id_if_needed()
                assert mock_host_resource_data.host_to_update == ''
