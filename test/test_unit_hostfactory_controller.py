import unittest

from conjur.controller.hostfactory_controller import HostFactoryController
from conjur.data_object.create_token_data import CreateTokenData
from conjur.errors import MissingRequiredParameterException
from conjur.logic.hostfactory_logic import HostFactoryLogic

class HostfactoryControllerTest(unittest.TestCase):

    def test_empty_token_data_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(MissingRequiredParameterException):
            mock_hostfactory_controller.create_token(create_token_data=None)


    def test_empty_host_factory_id_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(MissingRequiredParameterException):
            mock_hostfactory_controller.create_token(create_token_data=None)

    def test_empty_host_factory_count_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(MissingRequiredParameterException):
            mock_hostfactory_controller.create_token(create_token_data=CreateTokenData(count=0))
