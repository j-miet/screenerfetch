"""Checks _default workbook values.

Screenerfetch cannot be run unless it can initialize default values for path, query and sheets data. If for some reason 
the currently used workbook is deleted manually, settings.json won't get updated. The next time program is run, program 
fails to find current wb and defaults to _default.

This test ensures that _default workbook can be read and it has the required default initialization data.
"""

import pathlib

from paths import FilePaths
from query import QueryVars

def test_update_query_variables_with_default():
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

    assert QueryVars.header_chars == ['A','B']
    assert (QueryVars.col_headers, QueryVars.int_cols, QueryVars.float_cols) == (
        {'A1': 'date', 'B1': 'name'},
        [],
        []
    )

    assert QueryVars.date_col == 'A'
    assert QueryVars.txt_headers == ['B1']
    assert QueryVars.sheet_xlsx_int_cols == []
    assert QueryVars.sheet_xlsx_float_cols == []