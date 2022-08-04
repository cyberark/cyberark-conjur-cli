import unittest
from unittest.mock import patch

from conjur_api import Client
from conjur.logic.resource_logic import ResourceLogic


class ResourceLogicTest(unittest.TestCase):
    @patch('conjur_api.Client.resource_exists')
    def test_resource_exists_calls_client(self, mock_resource_exists):
        mock_client = Client
        mock_resource_logic = ResourceLogic(mock_client)
        mock_resource_logic.exists('some_kind', 'some_id')
        mock_resource_exists.assert_called_once_with('some_kind', 'some_id')
