import unittest
from unittest.mock import patch

from conjur_api import Client
from conjur.data_object import ConjurrcData
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.show_logic import ShowLogic


class ShowLogicTest(unittest.TestCase):
    @patch('conjur_api.Client.get_resource')
    def test_show_calls_get_resource(self, mock_show):
        mock_client = Client
        mock_show_logic = ShowLogic(mock_client)
        mock_show_logic.show('some_kind', 'some_id')
        mock_show.assert_called_once_with('some_kind', 'some_id')
