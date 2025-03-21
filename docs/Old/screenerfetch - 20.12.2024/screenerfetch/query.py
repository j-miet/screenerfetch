"""
Query is used to fetch screener data from (unofficial) Tradingview API
Original idea for data scraping is from https://github.com/shner-elmo/TradingView-Screener
API requests can be tracked through browser development tools (F12):
-> Network -> filter URL 'scanner' and choose domain -> 'Request'.
JSON code updates as you change screener settings and update page.
"""

MARKET = 'america'
MY_QUERY = {
        'markets': [MARKET],
        'options': {'lang': 'en'},
        'columns': ['name', 'close', 'low', 'high', 'change_from_open', 'change', 'volume',
                    'float_shares_outstanding_current', 'market_cap_basic', 'premarket_change',
                    'premarket_volume', 'premarket_close'],
        'filter': [{'left' : 'premarket_change', 'operation' : 'greater', 'right' : 7},
                   {'left' : 'premarket_volume', 'operation' : 'greater', 'right' : 250000},
                   {'left' : 'premarket_close', 'operation' : 'less', 'right' : 20},
                   {'left' : 'country', 'operation' : 'not_in_range', 'right' : ['Aland Islands', 'Anguilla',
                    'Azerbaijan', 'Barbados', 'Cambodia', 'China', 'Faroe Islands', 'Gibraltar', 'Hong Kong',
                    'Jamaica', 'Kenya', 'Macau', 'Mauritius', 'Montenegro', 'Papua New Guinea',
                    'Russian Federation', 'Thailand', 'Vietnam']},
                   {'left' : 'typespecs', 'operation' : 'has', 'right' : ['common']},
                   {'left' : 'exchange', 'operation' : 'in_range', 'right' : ['AMEX', 'NYSE', 'NASDAQ']}             
                   ],
        'sort': {'sortBy': 'premarket_change', 'sortOrder': 'desc'},
        'range': [0, 50]
}

URL = f'https://scanner.tradingview.com/{MARKET}/scan'
REQUEST_HEADERS = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.5',
    'content-type': 'text/plain;charset=UTF-8',
    'host': 'scanner.tradingview.com',
    'origin': 'https://www.tradingview.com/',
    'referer': 'https://www.tradingview.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'
}

#change these according to MY_QUERY columns
#keep A1 and B1 as date and symbol name, respectively. Other columns you may change freely.
COL_HEADERS = {
    'A1' : 'Date',
    'B1' : 'Symbol',
    'C1' : 'Price',
    'D1' : 'Low',
    'E1' : 'High',
    'F1' : 'Chg from Open',
    'G1' : 'Change %',
    'H1' : 'Volume',
    'I1' : 'Float',
    'J1' : 'Market Cap',
    'K1' : 'Pre-market Chg %',
    'L1' : 'Pre-market Vol',
    'M1' : 'Pre-market Close',
    'N1' : 'Notes'
}
FIRST_COL, LAST_COL = 'B', 'M'  #column A excluded as date header is left aligned, others are right aligned
#Iterate through alphabet, https://stackoverflow.com/a/68037249
TXT_HEADERS = [f'{c}1' for c in list(map(chr,range(ord(FIRST_COL),ord(LAST_COL)+1)))]