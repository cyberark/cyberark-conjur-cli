import unittest

from conjur.variable import VariableData

class VariableDataTest(unittest.TestCase):

    def test_get_variable_input_data_with_all_fields_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT="Getting variable values for: 'somevar' with version '2'"
        mock_variable_data = VariableData(action='get', id='somevar', variable_version='2', value=None)

        rep_obj = mock_variable_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    def test_set_variable_input_data_with_all_fields_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT="Setting variable value for: 'somevar'"
        mock_variable_data = VariableData(action='set', id='somevar', variable_version= None, value='someval')

        rep_obj = mock_variable_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    def test_variable_input_data_without_version_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT="Getting variable values for: 'somevar'"
        mock_variable_data = VariableData(action='get', id='somevar', variable_version=None, value=None)

        rep_obj = mock_variable_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
