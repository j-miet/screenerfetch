"""Unit tests for query.py"""

import copy
import pathlib

import pytest

from paths import FilePaths
from query import QueryVars
import helpers.helper_data as helper_data

@pytest.fixture
def file_paths():
    """Creates a fixture of FilePaths class. 
    
    Very important to return FilePaths, not Filepaths(). Latter calls the default constructor and would create a class 
    instance instead.
    """
    return FilePaths

@pytest.fixture
def query_vars():
    return QueryVars

def test_header_values(query_vars):
    query_vars.my_query = copy.deepcopy(helper_data.query_test)
    assert query_vars.get_header_values() == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    for counter in range(0,17):
        query_vars.my_query["columns"].append(f"val{counter}")
    assert query_vars.get_header_values() == ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',
                                             'Q','R','S','T','U','V','W','X','Y','Z']
    query_vars.my_query["columns"].append("last_val")
    assert query_vars.get_header_values() == ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',
                                             'Q','R','S','T','U','V','W','X','Y','Z','AA']
    for counter in range(0, 27):
        query_vars.my_query["columns"].append(f"val{counter}")
    assert query_vars.get_header_values() == []

def test_get_column_header_data():
    assert QueryVars.get_column_header_data(helper_data.query_test["columns"],
                                        helper_data.headers_test, 
                                        helper_data.header_chars_test) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )

def test_update_query_variables(mocker, file_paths, query_vars):
    file_paths.settings_path = pathlib.Path(__file__) # any pathlib.Path suffices
    mock_open = mocker.patch("query.open")
    mock_json_load = mocker.patch("query.json.load")
    mock_json_load.return_value = helper_data.settings_test
    QueryVars.update_query_variables()
    
    assert QueryVars.market == mock_json_load.return_value["market"]
    assert QueryVars.url == 'https://scanner.tradingview.com/america/scan'
    assert QueryVars.my_query == mock_json_load.return_value["query"]
    assert QueryVars.custom_headers == mock_json_load.return_value["headers"]
    assert QueryVars.wb_type == "basic"

    assert QueryVars.header_chars == ['A','B','C','D','E','F','G','H','I']
    assert (QueryVars.col_headers, QueryVars.int_cols, QueryVars.float_cols) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )

    assert QueryVars.date_col == 'A'
    assert QueryVars.txt_headers == ['B1','C1','D1','E1','F1','G1','H1','I1']
    assert QueryVars.sheet_xlsx_int_cols == [4,6,7,9]
    assert QueryVars.sheet_xlsx_float_cols == [3]

    assert mock_open.call_count == 1