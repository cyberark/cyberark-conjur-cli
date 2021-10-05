import unittest
from unittest.mock import MagicMock

from conjur.data_object.create_token_data import CreateTokenData
from conjur.errors import MissingRequiredParameterException
from conjur.logic.hostfactory_logic import HostFactoryLogic

class HostfactoryLogicTest(unittest.TestCase):

    def test_empty_token_data_raises_correct_error(self):
        mock_client = None
        mock_hostfactory_logic = HostFactoryLogic(mock_client)
        with self.assertRaises(MissingRequiredParameterException):
            mock_hostfactory_logic.create_token(create_token_data=None)

    def test_hostfactory_logic_call_passes_object(self):
        mock_client = MagicMock(return_value=None)
        mock_hostfactory_logic = HostFactoryLogic(mock_client)

        mock_create_token_data = CreateTokenData(host_factory="some_host_factory_id")
        mock_hostfactory_logic.create_token(create_token_data=mock_create_token_data)

        mock_hostfactory_logic.client.create_token.assert_called_once_with(mock_create_token_data)
