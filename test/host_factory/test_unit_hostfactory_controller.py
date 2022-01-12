import unittest

from conjur.controller.hostfactory_controller import HostFactoryController
from conjur_api.models import CreateHostData, CreateTokenData
from conjur.errors import MissingRequiredParameterException
from conjur_api.errors.errors import MissingRequiredParameterException as SdkMissingRequiredParameterException
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
        with self.assertRaises(SdkMissingRequiredParameterException):
            mock_hostfactory_controller.create_token(create_token_data=CreateTokenData())

    def test_empty_host_data_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(MissingRequiredParameterException):
            mock_hostfactory_controller.create_host(create_host_data=None)

    def test_empty_host_id_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(SdkMissingRequiredParameterException):
            mock_hostfactory_controller.create_host(create_host_data=CreateHostData())

    def test_empty_token_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(SdkMissingRequiredParameterException):
            mock_hostfactory_controller.create_host(create_host_data=CreateHostData(host_id="foo"))

    def test_empty_revoke_token_raises_correct_error(self):
        mock_hostfactory_logic = HostFactoryLogic
        mock_hostfactory_controller = HostFactoryController(mock_hostfactory_logic)
        with self.assertRaises(MissingRequiredParameterException):
            mock_hostfactory_controller.revoke_token(None)
