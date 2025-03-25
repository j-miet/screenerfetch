"""Unit tests for query.py"""

import pathlib

import pytest

from paths import FilePaths
from query import QueryVars
import helpers.helper_data as helper_data

def test_get_actual_column_values():
    assert QueryVars.get_actual_column_values(helper_data.my_query_test['columns']) == [
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
                                        helper_data.custom_headers_test, 
                                        helper_data.header_chars_test) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )

@pytest.fixture
def query_vars():
    return QueryVars()

@pytest.fixture
def file_paths():
    return FilePaths

def test_update_query_variables(mocker, query_vars, file_paths):
    file_paths.settings_path = pathlib.Path(__file__) # any pathlib.Path suffices
    mock_open = mocker.patch("query.open", mocker.mock_open())
    mock_json_load = mocker.patch("query.json.load")
    mock_json_load.return_value = {
        "type": "test_type",
        "market": "america",
        "headers": helper_data.custom_headers_test,
        "query": helper_data.my_query_test}
    QueryVars.update_query_variables()
    
    assert query_vars.market == mock_json_load.return_value["market"]
    assert query_vars.url == 'https://scanner.tradingview.com/america/scan'
    assert query_vars.my_query == mock_json_load.return_value["query"]
    assert query_vars.custom_headers == mock_json_load.return_value["headers"]
    assert query_vars.wb_type == "test_type"

    assert query_vars.actual_columns == [
        'name',
        'open',
        'close', 
        'low',
        'high', 
        'volume',
        'float_shares_outstanding_current',
        'market_cap_basic'
        ]
    assert query_vars.header_chars == ['A','B','C','D','E','F','G','H','I']
    assert (query_vars.col_headers, query_vars.int_cols, query_vars.float_cols) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )

    assert query_vars.date_col == 'A'
    assert query_vars.first_col == 'B'
    assert query_vars.last_col == 'I'
    assert query_vars.txt_headers == ['B1','C1','D1','E1','F1','G1','H1','I1']
    assert query_vars.sheet_xlsx_int_cols == [4,6,7,9]
    assert query_vars.sheet_xlsx_float_cols == [3]

    assert mock_open.call_count == 1

def test_update_query_variables_with_default():
    """Tests with workbook _default which should always exist."""
    FilePaths.settings_path = (
        pathlib.Path(__file__).parent.parent.parent/'screenerfetch'/'workbooks'/'_default'/'settings')    
    QueryVars.update_query_variables()
    
    assert QueryVars.market == 'global'
    assert QueryVars.url == 'https://scanner.tradingview.com/global/scan'
    assert QueryVars.my_query == {
        "columns": ["name"],
        "range": [0,1]
        }
    assert QueryVars.custom_headers == {}
    assert QueryVars.wb_type == "basic"

    assert QueryVars.actual_columns == [
        'name',
        ]
    assert QueryVars.header_chars == ['A','B']
    assert (QueryVars.col_headers, QueryVars.int_cols, QueryVars.float_cols) == (
        {'A1': 'date', 'B1': 'name'},
        [],
        []
    )

    assert QueryVars.date_col == 'A'
    assert QueryVars.first_col == 'B'
    assert QueryVars.last_col == 'B'
    assert QueryVars.txt_headers == ['B1']
    assert QueryVars.sheet_xlsx_int_cols == []
    assert QueryVars.sheet_xlsx_float_cols == []