import time
import shutil
import os
import requests
from datetime import date

from query import MY_QUERY, COL_HEADERS, URL, REQUEST_HEADERS, TXT_HEADERS
from file_paths import TXT_PATH, WB_PATH, WB_COPY_PATH
import xlsx_tools as xlsx_tools

date_str = str(date.today())
h_spacing = 6   #header spacing in .txt file
query_data = []

def fetch():
    #send the query to Tradingview API and fetch data accordingly. Query and return data are both in JSON format.
    #JSON data has two components: 'totalCount' and 'data'
    #'totalCount' lists the total amount of row elements (= symbols) that request found
    #'data' contains a list of dictionaries with 's' and 'd' keys
    # 's' contains the ticker symbol with market/exchange included in front e.g. 'NASDAQ: NVDA'
    # 'd' contains all data columns, filtered accordingly to your query, in a list format. It preserves order of columns
    #     from MY_QUERY so you can easily pinpoint which value corresponds to which.
    raw_data = requests.post(url=URL, json=MY_QUERY, headers=REQUEST_HEADERS).json()
    time.sleep(3)   #artificial pause so user can't spam requests

    #Handling the JSON data --- everything below this line depends on the columns & their order in MY_QUERY, COL_HEADERS & TXT_HEADERS
    #remove excess decimals
    rounded = []
    for data in raw_data['data']:
        newcolumn = []
        for column in data['d']:
            if isinstance(column, float):
                column = f"{column:.2f}"
            newcolumn.append(column)
        rounded.append(newcolumn)
    #remove all decimals from Float and Market cap; these are 8. and 9. columns, respectively.
    #if float/market cap are NoneTypes (no data available), replace column with '-'
    for col in rounded:
        #float
        try:
            col[7] = int(float(col[7]))
        except:
            col[7] = '-'
        #market cap
        try:
            col[8] = int(float(col[8]))
        except:
            col[8] = '-'
    #finally, sort data to a table-like format and save it to a text file
    #date is in format YYYY-MM-DD
    #first column header & text is handled separately as they're left aligned whereas rest are right aligned
    #'+'-'*total_len+'\n' adds a line that separates headers from data values
    total_len = 0
    with open(TXT_PATH, 'w') as file:
        file.write(
            '['+date_str+']\n'
            f"{COL_HEADERS[TXT_HEADERS[0]] : <{len(COL_HEADERS[TXT_HEADERS[0]])+h_spacing}}"
        )
        total_len += len(COL_HEADERS[TXT_HEADERS[0]])+h_spacing
        for h_index in range(1, len(TXT_HEADERS)):
            file.write(
                f"{COL_HEADERS[TXT_HEADERS[h_index]] : >{len(COL_HEADERS[TXT_HEADERS[h_index]])+h_spacing}}"
            )
            total_len += len(COL_HEADERS[TXT_HEADERS[h_index]])+h_spacing
        file.write(
            '\n'+'-'*total_len+'\n'
        )
        for list in rounded:
            file.write(
                f"{list[0] : <{len(COL_HEADERS[TXT_HEADERS[0]])+h_spacing}}"
            )
            for col in range(1, len(list)):
                file.write(
                    f"{list[col] : >{len(COL_HEADERS[TXT_HEADERS[col]])+h_spacing}}"
                )
            file.write('\n')
        global query_data
        query_data = rounded

def save():
    OK = True
    if query_data == []:
            print('No data available to save. Fetch data before attempting to save it.')
            return
    while OK:
        symbols = input('/////////////////////////////////////////////////////////////////////////////////////////////////\n'
                        f'List all symbols you want to save to .xlsx file, each separated with a space. Symbols are written in UPPERCASE.\n'
                        'Example: NVDA MSFT AAPL\n'
                        '-----------------------\n'
                        'Other commands:\n'
                        'save all = Save all fetched symbol data.\n'
                        'exit = Return to main UI.\n'                    
                        )
        if symbols == 'save all':
            xlsx_tools.save(query_data, date_str)
            print('Following symbols were saved: ')
            for sym in query_data:
                print(sym[0])
        elif symbols == 'exit':
            print('Returning to main UI...')
            OK = False
        else:
            list_data = symbols.split()
            check = False
            added_symbols = []
            for d in list_data:
                check = False
                for symbol_data in query_data:
                    if d in symbol_data:
                        check = True
                        added_symbols.append(symbol_data)
                        break
                if check == False:
                    print(f'Error: Invalid symbol "{d}", saving process halted.')
                    break
            if check == True:
                xlsx_tools.save(added_symbols, date_str)

def edit_notes():
    while True:
        print('Type \'exit\' to stop editing notes.')
        input_data = input('Need date and symbol (always in uppercase) to identify correct row.\n'
                            'Format is YYYY-MM-DD SYMBOL. Example: 2024-01-01 NVDA \n'
                            '-> ')
        if input_data == 'exit':
            return
        xlsx_tools.edit_notes(input_data)
    
def show_txt():  
    os.system(TXT_PATH)

def show_xlsx():
    os.system(WB_PATH)

def copy():
    shutil.copy2(WB_PATH, WB_COPY_PATH)

def create():
    xlsx_tools.create_wb()