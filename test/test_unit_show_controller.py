from contextlib import redirect_stdout
import io
import json
import unittest
from unittest.mock import MagicMock
from conjur_api import Client
from conjur_api.errors.errors import HttpStatusError
import conjur
from conjur.logic.show_logic import ShowLogic
from conjur.controller.show_controller import ShowController


class ShowControllerTest(unittest.TestCase):
    capture_stream = io.StringIO()

    def test_show_resource_id_without_kind_raises_missing_required_parameter_exception(self):
        client = Client
        mock_show_logic = ShowLogic(client)
        mock_show_controller = ShowController(mock_show_logic)

        with self.assertRaises(conjur.errors.MissingRequiredParameterException):
            mock_show_controller.load("resource_id") # missing kind (kind:resource_id)

    def test_show_not_found_error_raises_general_https_exception(self):
        client = Client
        mock_show_logic = ShowLogic(client)
        mock_show_controller = ShowController(mock_show_logic)
        mock_show_logic.show = MagicMock(side_effect=HttpStatusError(status=404))

        with self.assertRaises(HttpStatusError):
            mock_show_controller.load("variable:myvar")
