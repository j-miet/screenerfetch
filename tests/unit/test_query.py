"""Unit tests for query_utils.py"""

import query
import helpers.helper_data as helper_data

def test_get_actual_column_values():
    assert query.get_actual_column_values(helper_data.my_query_test['columns']) == [
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

    assert query.get_column_header_data(helper_data.actual_columns_test,
                                        helper_data.custom_headers_test, 
                                        helper_data.header_chars_test) == (
        {'A1': 'Date', 'B1': 'Symbol', 'C1': 'open', 'D1': 'close', 'E1': 'low', 'F1': 'High', 'G1': 'volume', 'H1': 
         'Float', 'I1': 'Market Cap'},
        ['D1', 'F1', 'G1', 'I1'],
        ['C1']
    )