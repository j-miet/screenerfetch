"""Mock query data for unit testing."""

query_test = {
    'markets': ['america'],
    'options': {'lang': 'en'},
    'columns': ['name',
                'open',
                'close', 
                'low',
                'high', 
                'volume',
                'float_shares_outstanding_current',
                'market_cap_basic'
                ],
    'filter': [{'left' : 'market_cap_basic', 'operation' : 'greater', 'right' : 1e11},
                {'left' : 'typespecs', 'operation' : 'has', 'right' : ['common']},
                {'left' : 'exchange', 'operation' : 'in_range', 'right' : ['AMEX', 
                'NYSE', 'NASDAQ']}             
                ],
    'sort': {'sortBy': 'premarket_change', 'sortOrder': 'desc'},
    'range': [0, 5]
}

headers_test = {
    'A' : {'name': 'Date'},
    'B' : {'name': 'Symbol'},
    'C' : {'type': 'float'},
    'D' : {'type': 'int'},
    'F' : {'name': 'High', 'type': 'int'},
    'G' : {'type': 'int'},
    'H' : {'name': 'Float'},
    'I' : {'name': 'Market Cap', 'type': 'int'}
}

settings_test = {
    'type': 'basic',
    'market': 'america',
    'headers': headers_test,
    'query': query_test
}

header_chars_test = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

json_data_test = {'totalCount': 110, 
            'data': [
            {'s': 'NASDAQ:NFLX', 'd': ['NFLX', 863.53, 869.68, 854.745, 916.40, 9846543, 424635922.284, 
                                        371751783265.99],}, 
            {'s': 'NYSE:ORCL', 'd': ['ORCL', 163.87, 172.57, 162.75, 173.37, 30228784, 1644595698.24, 
                                        482670726842.99994]}, 
            {'s': 'NYSE:ANET', 'd': ['ANET', 121.56, 121.5, 119.5001, 121.92, 6366606, 1032606375.6000001, 
                                        153060781860]}, 
            {'s': 'NASDAQ:MRVL', 'd': ['MRVL', 125.85, 123.78, 122.1, 126.11, 12770695, 857983888.5, 
                                        107106831433]}, 
            {'s': 'NASDAQ:NVDA', 'd': ['NVDA', 139.16, 140.83, 137.09, 141.83, 197735798, 23513142880, 
                                        3448926744843]}]}

saved_query_data = [
        ['NFLX', '863.53', '869.68', '854.75', '916.40', 9846543, '424635922.28', '371751783265.99'],
        ['ORCL', '163.87', '172.57', '162.75', '173.37', 30228784, '1644595698.24', '482670726843.00'],
        ['ANET', '121.56', '121.50', '119.50', '121.92', 6366606, '1032606375.60', 153060781860],
        ['MRVL', '125.85', '123.78', '122.10', '126.11', 12770695, '857983888.50', 107106831433],
        ['NVDA', '139.16', '140.83', '137.09', '141.83', 197735798, 23513142880, 3448926744843]]

# This is not actually needed...
saved_query_data_txt = str(
        "#After calling 'save', insert a single '+' (without quotations) before symbol names you'd like to save in "
         "excel worksheet.\n"
        '\n'
        '[2025-01-20]\n'
        '\n'
        'Date  Symbol  open    low high    volume  float_shares_outstanding_current    market_cap_basic\n'
        '-'*len('#After calling \'save\', insert a single \'+\' (without quotations) before symbol names you\'d '+
         'like to save in excel worksheet.\n\n')+'\n'
        'NFLX   863.53  869.68  854.75  916.40  9846543 424635922.28    371751783265.99 \n'
        'ORCL   163.87  172.57  162.75  173.37  30228784    1644595698.24   482670726843.00 \n'
        'ANET   121.56  121.50  119.50  121.92  6366606 1032606375.60   153060781860    \n'
        'MRVL   125.85  123.78  122.10  126.11  12770695    857983888.50    107106831433    \n'
        'NVDA   139.16  140.83  137.09  141.83  197735798   23513142880 3448926744843')

# commands_utils.select_saved_objects uses readlines()[4:] so 4 filler elements must be added for mocking.
select_query_data_to_save = ['fill1', 'fill2', 'fill3', 'fill4',
        ' +NFLX 863.53 869.68 854.75 916.40 9846543 424635922.28 371751783265.99',
        '+  ORCL 163.87 172.57 162.75 173.37 30228784 1644595698.24 482670726843.00',
        'ANET 121.56 121.50 119.50 121.92 6366606 1032606375.60 153060781860',
        'MRVL 125.85 123.78 122.10 126.11 12770695 857983888.50 107106831433',
        ' + NVDA 139.16 140.83 137.09 141.83 197735798 23513142880 3448926744843']

select_query_data_to_save_invalid = ['fill1', 'fill2', 'fill3', 'fill4',
        ' +NFLX 863.53 869.68 854.75 916.40 9846543 424635922.28 371751783265.99',
        '+  ORCL 163.87 172.57 162.75 173.37 30228784 1644595698.24 482670726843.00',
        'ANET 121.56 121.50 119.50 121.92 6366606 1032606375.60 153060781860',
        'MRVL 125.85 123.78 122.10 126.11 12770695 857983888.50 107106831433',
        ' + NVDA 139.16 140.83 137.09 141.83 197735798 23513142880 3448926744843',
        '+TEST 139.16 140.83 137.09 141.83 197735798 23513142880 3448926744843']
