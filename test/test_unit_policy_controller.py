import unittest
from unittest.mock import MagicMock

import requests

import conjur
from conjur import Client
from conjur.logic.policy_logic import PolicyLogic
from conjur.controller.policy_controller import PolicyController


class PolicyControllerTest(unittest.TestCase):
    def test_policy_syntax_error_raises_unprocessable_exception(self):
        mock_response = MagicMock()
        mock_response.status_code = 422
        client = Client
        mock_policy_logic = PolicyLogic(client)
        mock_policy_controller = PolicyController(mock_policy_logic, "somedata")
        mock_policy_logic.run_action = MagicMock(side_effect=requests.exceptions.HTTPError(response=mock_response))
        with self.assertRaises(conjur.errors.InvalidFormatException):
            mock_policy_controller.load()

    def test_policy_syntax_error_raises_general_https_exception(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        client = Client
        mock_policy_logic = PolicyLogic(client)
        mock_policy_controller = PolicyController(mock_policy_logic, "somedata")
        mock_policy_logic.run_action = MagicMock(side_effect=requests.exceptions.HTTPError(response=mock_response))
        with self.assertRaises(requests.exceptions.HTTPError):
            mock_policy_controller.load()
