"""Unit tests for commands_utils.py"""

from datetime import date

import pandas as pd
import pytest

import commands_utils
import query
from query import QueryVars, FetchData
import helpers.helper_data as helper_data

def test_get_date():
    today = date.today()
    if str(today.day)[0] == '0':
        assert commands_utils.get_date() == '0'+str(today.day)+'/0'+str(today.month)+'/'+str(today.year)
    else:
        assert commands_utils.get_date() == str(today.day)+'/0'+str(today.month)+'/'+str(today.year)

@pytest.mark.parametrize("float_val, int_val", [
    (2.99, 2),
    (1.12345, 1),
    (5.1e6+0.1, 5100000),
    (0, 0),
    (None, '-')
])
def test_round_to_int(float_val: float, int_val: int):
    assert commands_utils.round_to_int(float_val) == int_val

@pytest.mark.parametrize("column", [
    "name", "open", "close", "low", "high", "volume", "float_shares_outstanding_current", "market_cap_basic"
])
def test_clean_fetched_data(column: str):
    QueryVars.col_headers, QueryVars.int_cols, _ = query.get_column_header_data(helper_data.actual_columns_test,
                                                        {}, 
                                                        helper_data. header_chars_test)
    first_col = [header[0] for header in QueryVars.col_headers.keys()][1]
    last_col = [header[0] for header in QueryVars.col_headers.keys()][-1]
    QueryVars.txt_headers = [f'{char}1' for char in list(map(chr,range(ord(first_col),ord(last_col)+1)))]

    test_df: pd.DataFrame = commands_utils.clean_fetched_data(helper_data.json_data_test)
    expected_df = pd.DataFrame(
        {
        "name": ['NFLX', 'ORCL', 'ANET', 'MRVL', 'NVDA'],
        "open": [863.53, 163.87, 121.56, 125.85, 139.16,],
        "close": [869.68, 172.57, 121.5, 123.78, 140.83],
        "low": [854.745, 162.75, 119.5001, 122.1, 137.09],
        "high": [916.4, 173.37, 121.92, 126.11, 141.83],
        "volume": [9846543, 30228784, 6366606, 12770695, 197735798],
        "float_shares_outstanding_current": [424635922.28, 1644595698.24, 1032606375.6000001, 857983888.5, 
                                             23513142880,],
        "market_cap_basic": [371751783265.99, 482670726843.00, 153060781860, 107106831433, 3448926744843]
        })
    
    if column == 'name':
        pd.testing.assert_series_equal(test_df[column], expected_df[column])
    else:
        pd.testing.assert_series_equal(test_df['open'].astype('float'), expected_df['open'].astype('float'))

@pytest.mark.parametrize("column", [
    "Symbol", "open", "close", "low", "High", "volume", "Float", "Market Cap"
])
def test_clean_fetched_data_custom_headers(column: str):
    QueryVars.col_headers, QueryVars.int_cols, _ = query.get_column_header_data(helper_data.actual_columns_test,
                                                        helper_data.custom_headers_test, 
                                                        helper_data. header_chars_test)
    first_col = [header[0] for header in QueryVars.col_headers.keys()][1]
    last_col = [header[0] for header in QueryVars.col_headers.keys()][-1]
    QueryVars.txt_headers = [f'{char}1' for char in list(map(chr,range(ord(first_col),ord(last_col)+1)))]
    QueryVars.int_cols = ['D1', 'F1', 'I1']

    test_df = commands_utils.clean_fetched_data(helper_data.json_data_test)
    expected_df = pd.DataFrame(
        {
        "Symbol": ['NFLX', 'ORCL', 'ANET', 'MRVL', 'NVDA'],
        "open": [863.53, 163.87, 121.56, 125.85, 139.16,],
        "close": [869, 172, 121, 123, 140],
        "low": [854.745, 162.75, 119.5001, 122.1, 137.09],
        "High": [916, 173, 121, 126, 141],
        "volume": [9846543, 30228784, 6366606, 12770695, 197735798],
        "Float": [424635922.28, 1644595698.24, 1032606375.6000001, 857983888.5, 23513142880,],
        "Market Cap": [371751783265, 482670726843, 153060781860, 107106831433, 3448926744843]
        })

    if column == 'Symbol':
        pd.testing.assert_series_equal(test_df[column], expected_df[column])
    else:
        pd.testing.assert_series_equal(test_df[column].astype('float'), expected_df[column].astype('float'))

def test_create_fetch_display_txt(mocker):
    mock_write = mocker.patch("commands_utils.open", mocker.mock_open())
    mock_write.return_value.write('write test')
    mock_write.return_value.write('append test')
    commands_utils.create_fetch_display_txt(["test", "list"])
    
    assert mock_write.call_count == 2

def test_create_screener_data():
    QueryVars.col_headers, QueryVars.int_cols, _ = query.get_column_header_data(helper_data.actual_columns_test,
                                                        {}, 
                                                        helper_data. header_chars_test)
    first_col = [header[0] for header in QueryVars.col_headers.keys()][1]
    last_col = [header[0] for header in QueryVars.col_headers.keys()][-1]
    QueryVars.txt_headers = [f'{char}1' for char in list(map(chr,range(ord(first_col),ord(last_col)+1)))]

    test_df: pd.DataFrame = commands_utils.clean_fetched_data(helper_data.json_data_test)
    df_str = test_df.to_string(index=False).split('\n')
    assert commands_utils.create_screener_data(df_str) == helper_data.saved_query_data

def test_select_saved_objects_no_data(capsys):
    FetchData.query_data = []
    commands_utils.select_saved_objects()
    captured = capsys.readouterr()
    assert captured.out == 'No data available to save. Fetch data before you attempt to save it.\n'

    assert commands_utils.select_saved_objects() == (False, [])

def test_select_saved_object(mocker):
    FetchData.query_data = helper_data.saved_query_data
    mock_open = mocker.patch("commands_utils.open", mocker.mock_open())
    mock_open.return_value.readlines.return_value = helper_data.select_query_data_to_save

    assert commands_utils.select_saved_objects() == (True, [
        ['NFLX', '863.53', '869.68', '854.75', '916.40', '9846543', '424635922.28', '371751783265.99'],
        ['ORCL', '163.87', '172.57', '162.75', '173.37', '30228784', '1644595698.24', '482670726843.00'],
        ['NVDA', '139.16', '140.83', '137.09', '141.83', '197735798', '23513142880', '3448926744843']])
    
    mock_open.assert_called()

def test_select_saved_objects_invalid_symbol(mocker, capsys):
    FetchData.query_data = helper_data.saved_query_data
    mock_open = mocker.patch("commands_utils.open", mocker.mock_open())
    mock_open.return_value.readlines.return_value = helper_data.select_query_data_to_save_invalid

    commands_utils.select_saved_objects()
    captured = capsys.readouterr()
    assert captured.out == 'Error: Invalid symbol "TEST", saving process halted.\n'
    assert commands_utils.select_saved_objects() == (False, [])

    mock_open.assert_called()