import unittest

from conjur.list import ListData


class ListDataTest(unittest.TestCase):

    def test_list_input_data_with_no_flags_prints_no_flags(self):
        EXPECTED_REP_OBJECT="{}"
        mock_list_data = ListData(kind=None, inspect=None, role=None, search=None, offset=None, limit=None)

        rep_obj = mock_list_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    def test_list_input_data_with_kind_and_inspect_flags_prints_proper_dict(self):
        EXPECTED_REP_OBJECT="{'kind': 'somekind', 'inspect': 'True'}"
        mock_list_data = ListData(kind='somekind', inspect=True, role=None, search=None, offset=None, limit=None)

        rep_obj = mock_list_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    def test_list_input_data_with_one_flag_prints_proper_dict(self):
        EXPECTED_REP_OBJECT="{'offset': '1'}"
        mock_list_data = ListData(kind=None, inspect=None, role=None, search=None, offset='1', limit=None)

        rep_obj = mock_list_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    def test_list_input_data_with_all_flags_prints_proper_dict(self):
        EXPECTED_REP_OBJECT="{'kind': 'somekind', 'limit': '10', 'inspect': 'True', 'search': 'somequery', 'offset': '1', 'role': 'somerole'}"
        mock_list_data = ListData(kind='somekind', inspect=True, role='somerole', search='somequery', offset='1', limit='10')

        rep_obj = mock_list_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
