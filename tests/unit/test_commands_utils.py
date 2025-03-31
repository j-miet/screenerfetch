"""Unit tests for commands_utils.py"""

from datetime import date

import pandas as pd
import pytest

import commands_utils
from query import QueryVars, FetchData
import helpers.helper_data as helper_data

@pytest.fixture()
def query_vars():
    return QueryVars

@pytest.fixture()
def fetch_data():
    return FetchData

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

def test_requests_api_data(mocker, query_vars):
    query_vars.url = ""
    query_vars.my_query = {}
    mock_requests = mocker.patch("commands_utils.requests.post")
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = helper_data.json_data_test

    api_test = commands_utils.requests_api_data()
    assert api_test == helper_data.json_data_test

    mock_requests.return_value.status_code = 300
    with pytest.raises(Exception, match=r"Could not fetch any data from API."):
        api_test = commands_utils.requests_api_data()

@pytest.mark.parametrize("column", [
    "name", "open", "close", "low", "high", "volume", "float_shares_outstanding_current", "market_cap_basic"
])
def test_clean_fetched_data(column: str, query_vars):
    query_vars.col_headers, query_vars.int_cols, _ = query_vars.get_column_header_data(
        helper_data.query_test["columns"],
        {}, 
        helper_data. header_chars_test)
    query_vars.txt_headers = [header for header in list(query_vars.col_headers)[1:]]

    test_df: pd.DataFrame = commands_utils.clean_fetched_data(helper_data.json_data_test)
    expected_df = pd.DataFrame(
        {
        "name": ['NFLX', 'ORCL', 'ANET', 'MRVL', 'NVDA'],
        "open": ['863.53', '163.87', '121.56', '125.85', '139.16'],
        "close": ['869.68', '172.57', '121.50', '123.78', '140.83'],
        "low": ['854.75', '162.75', '119.50', '122.10', '137.09'],
        "high": ['916.40', '173.37', '121.92', '126.11', '141.83'],
        "volume": [9846543, 30228784, 6366606, 12770695, 197735798],
        "float_shares_outstanding_current": ['424635922.28', '1644595698.24', '1032606375.60', '857983888.50', 
                                             23513142880],
        "market_cap_basic": ['371751783265.99', '482670726843.00', 153060781860, 107106831433, 3448926744843]
        })
    
    if column == 'name':
        pd.testing.assert_series_equal(test_df[column], expected_df[column])
    else:
        pd.testing.assert_series_equal(test_df[column], expected_df[column])

@pytest.mark.parametrize("column", [
    "Symbol", "open", "close", "low", "High", "volume", "Float", "Market Cap"
])
def test_clean_fetched_data_custom_headers(column: str, query_vars):
    query_vars.col_headers, query_vars.int_cols, _ = query_vars.get_column_header_data(
        helper_data.query_test["columns"],
        helper_data.headers_test, 
        helper_data. header_chars_test)
    query_vars.txt_headers = [header for header in list(query_vars.col_headers)[1:]]
    query_vars.int_cols = ['D1', 'F1', 'I1']

    test_df = commands_utils.clean_fetched_data(helper_data.json_data_test)
    expected_df = pd.DataFrame(
        {
        "Symbol": ['NFLX', 'ORCL', 'ANET', 'MRVL', 'NVDA'],
        "open": ['863.53', '163.87', '121.56', '125.85', '139.16'],
        "close": [869, 172, 121, 123, 140],
        "low": ['854.75', '162.75', '119.50', '122.10', '137.09'],
        "High": [916, 173, 121, 126, 141],
        "volume": [9846543, 30228784, 6366606, 12770695, 197735798],
        "Float": ['424635922.28', '1644595698.24', '1032606375.60', '857983888.50', 23513142880],
        "Market Cap": [371751783265, 482670726843, 153060781860, 107106831433, 3448926744843]
        })

    if column == 'Symbol':
        pd.testing.assert_series_equal(test_df[column], expected_df[column])
    else:
        pd.testing.assert_series_equal(test_df[column], expected_df[column])

def test_create_fetch_display_txt(mocker):
    mock_write = mocker.patch("commands_utils.open", mocker.mock_open())
    mock_write.return_value.write('write test')
    mock_write.return_value.write('append test')
    commands_utils.create_fetch_display_txt(["test", "list"])
    
    assert mock_write.call_count == 2

def test_create_screener_data(query_vars):
    query_vars.col_headers, query_vars.int_cols, _ = query_vars.get_column_header_data(
        helper_data.query_test["columns"],
        {}, 
        helper_data. header_chars_test)
    query_vars.txt_headers = [header for header in list(query_vars.col_headers)[1:]]

    test_df: pd.DataFrame = commands_utils.clean_fetched_data(helper_data.json_data_test)
    df_dict = test_df.to_dict()
    assert commands_utils.create_screener_data(df_dict) == helper_data.saved_query_data

def test_select_saved_objects_no_data(fetch_data, capsys):
    fetch_data.query_data = []
    commands_utils.select_saved_objects()
    captured = capsys.readouterr()
    assert captured.out == 'No data available to save. Fetch data before you attempt to save it.\n'

    assert commands_utils.select_saved_objects() == (False, [])

def test_select_saved_object(mocker, fetch_data):
    fetch_data.query_data = helper_data.saved_query_data
    mock_open = mocker.patch("commands_utils.open", mocker.mock_open())
    mock_open.return_value.readlines.return_value = helper_data.select_query_data_to_save

    assert commands_utils.select_saved_objects() == (True, [
        ['NFLX', '863.53', '869.68', '854.75', '916.40', 9846543, '424635922.28', '371751783265.99'],
        ['ORCL', '163.87', '172.57', '162.75', '173.37', 30228784, '1644595698.24', '482670726843.00'],
        ['NVDA', '139.16', '140.83', '137.09', '141.83', 197735798, 23513142880, 3448926744843]])
    
    mock_open.assert_called()

def test_select_saved_objects_invalid_symbol(mocker, fetch_data, capsys):
    fetch_data.query_data = helper_data.saved_query_data
    mock_open = mocker.patch("commands_utils.open", mocker.mock_open())
    mock_open.return_value.readlines.return_value = helper_data.select_query_data_to_save_invalid

    commands_utils.select_saved_objects()
    captured = capsys.readouterr()
    assert captured.out == 'Error: Invalid symbol "TEST", saving process halted.\n'
    assert commands_utils.select_saved_objects() == (False, [])

    mock_open.assert_called()

def test_delete_workbook(mocker):
    mock_listdir = mocker.patch("commands_utils.os.listdir")
    mock_rmtree = mocker.patch("commands_utils.shutil.rmtree")
    mock_listdir.return_value = ["test", "test2"]

    assert commands_utils.delete_workbook("_default") == -1
    assert commands_utils.delete_workbook("test.txt") == -1
    assert commands_utils.delete_workbook("test.json") == -1
    assert commands_utils.delete_workbook("test") == 0

    mock_listdir.assert_called_once()
    mock_rmtree.assert_called_once()