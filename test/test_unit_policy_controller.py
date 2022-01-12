import unittest
from unittest.mock import MagicMock

import conjur
from conjur_api import Client
from conjur_api.errors.errors import HttpStatusError
from conjur.logic.policy_logic import PolicyLogic
from conjur.controller.policy_controller import PolicyController


class PolicyControllerTest(unittest.TestCase):
    def test_policy_syntax_error_raises_unprocessable_exception(self):
        client = Client
        mock_policy_logic = PolicyLogic(client)
        mock_policy_controller = PolicyController(mock_policy_logic, "somedata")
        mock_policy_logic.run_action = MagicMock(side_effect=HttpStatusError(status=422))
        with self.assertRaises(conjur.errors.InvalidFormatException):
            mock_policy_controller.load()

    def test_policy_syntax_error_raises_general_https_exception(self):
        client = Client
        mock_policy_logic = PolicyLogic(client)
        mock_policy_controller = PolicyController(mock_policy_logic, "somedata")
        mock_policy_logic.run_action = MagicMock(side_effect=HttpStatusError(status=404))
        with self.assertRaises(HttpStatusError):
            mock_policy_controller.load()
