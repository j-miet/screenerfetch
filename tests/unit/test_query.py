"""Unit tests for query.py"""

import pathlib

import pytest

from paths import FilePaths
from query import QueryVars
import helpers.helper_data as helper_data

def test_get_actual_column_values():
    assert QueryVars.get_actual_column_values(helper_data.query_test['columns']) == [
        'name',
        'open',
        'close', 
        'low',
        'high', 
        'volume',
        'float_shares_outstanding_current',
        'market_cap_basic'
        ]

def test_get_column_header_data():
    assert QueryVars.get_column_header_data(helper_data.actual_columns_test,
                                        helper_data.headers_test, 
                                        helper_data.header_chars_test) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )

@pytest.fixture
def file_paths():
    """Creates a fixture of FilePaths class. 
    
    Very important to return FilePaths, not Filepaths(). Latter calls the default constructor and would create a class 
    instance instead.
    """
    return FilePaths

def test_update_query_variables(mocker, file_paths):
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

    assert QueryVars.actual_columns == [
        'name',
        'open',
        'close', 
        'low',
        'high', 
        'volume',
        'float_shares_outstanding_current',
        'market_cap_basic'
        ]
    assert QueryVars.header_chars == ['A','B','C','D','E','F','G','H','I']
    assert (QueryVars.col_headers, QueryVars.int_cols, QueryVars.float_cols) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )

    assert QueryVars.date_col == 'A'
    assert QueryVars.first_col == 'B'
    assert QueryVars.last_col == 'I'
    assert QueryVars.txt_headers == ['B1','C1','D1','E1','F1','G1','H1','I1']
    assert QueryVars.sheet_xlsx_int_cols == [4,6,7,9]
    assert QueryVars.sheet_xlsx_float_cols == [3]

    assert mock_open.call_count == 1