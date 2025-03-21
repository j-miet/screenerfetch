"""CLI commands."""

import json
import os
import shutil

import requests

import commands_utils
from paths import FilePaths
import query
from query import QueryVars, FetchData
import sheets
import workbook_tools

def _create_workbook_files() -> None:
    for folder_path in (FilePaths.wb_files_path, FilePaths.data_path, FilePaths.settings_path):
        os.mkdir(folder_path)
    print(f"{FilePaths.wb_name}, {FilePaths.wb_name}/settings and {FilePaths.wb_name}/data created.")
    with open(FilePaths.settings_path+'\\settings.json', 'w') as sjson:
        json.dump({"headers": {}, "market": "global", "query": {"columns": ["name"]}}, sjson, indent=4)
    print(f"{FilePaths.wb_name}/settings/settings.json created.")
    with open(FilePaths.settings_path+'\\query.txt', 'w') as qf:
        qf.writelines(('{\n', 
                       '    "columns": ["name"],\n', 
                       '    "range": [0,1]\n', 
                       '}'
                       ))
    print(f"{FilePaths.wb_name}/settings/query.txt created")
    with open(FilePaths.settings_path+'\\headers.txt', 'w') as hf:
        hf.writelines(('{\n', 
                       '   {}', 
                       '\n}'
                       ))
    print(f"{FilePaths.wb_name}/settings/headers.txt created.")

def update_query() -> None:
    """Handles query-related updates using text and json files.
    
    Note that these will also impact your xlsx file column names.
    """
    print('##########################################\n'
          '==READ THIS IF YOU\'RE A FIRST-TIME USER==\n'
          '##########################################\n'
          'If you want to set up your current TradingView screener settings, the easiest way is:\n'
          '-open your TradingView screener page, with your desired screener as currently selected.\n'
          '-press F12 and refresh your page (F5).\n'
          '-then have "Network" selected and below it you see "Filter URLs" search box.\n'
          '-now type "scanner" in that box, wait a second or two, then select the top one.\n'
          '-A window opens: choose "Requests" page -> right-click and select Copy All => AND KEEP THE WEB PAGE OPEN!\n'
          '-You have your query in clipboard so click back to this program, type "query" and press Enter\n'
          '-A text file pops up: it contains your current query - if it\'s empty, paste the one you just copied.\n'
          '>You\'ve set your query! Next you need to set the market where symbols are searched from:\n\n'

          '-back to developer tools: now select the 3. row/the one below "cached" on the left panel.\n'
          '-again, you choose "Requests", but now scrolls all the way down: there should be a markets section with a' 
          'country name\n'
          'click back to program, type "market" and write your market value, then press Enter.\n'
          '*Note* if you want to search over multiple markets, say "us" and "canada", then type "global" instead!\n'

          '---This is everything you need...but if you wish to customize your column names for txt/excel files, check '
          'this out:----\n\n'

          '{\n'
           '"A" : {"name": "Date"},\n'
           '"B" : {"name": "Symbol"},\n'
           '"C" : {"type": "float"},\n'
           '"D" : {"name": "Price", "type": "float"},\n'
           '"F" : {"name": "Volume", "type": "int"},\n'
          '}\n\n'
          'letters refer to correspondig workbook columns, name is the column name and type is the column value type.\n'
          'Supported type values are "int" or "float": these ensure that numbers are either rounded down to an '
          'integer, or are rounded down to 2 decimals points\n'
          'Neither of the name/type values are necessary so you can have name, but not type and vice versa.\n'
          'And if you want to leave default name values and don\'t care about rounding, remove the entire row!\n'
          '#ONLY EXCEPTION is the date row \'"A" : {"name": "Date"}\': this must always exists (name you can still '
          'customize).\n'
          '#supports only characters A-Z; if your workbook exceeds this column limit, you need to use base values for '
          'the rest\n\n'
          
          '/////////////////////////////\n'
          'Edit workbook settings. Type one of the following commands, or type \'back\' to return to main ui.\n'
          'query => current query; must be in JSON format. NOTE that order in \'columns\' matters: Nth value will '
          'be N+1 column in .xlsx file (because first column is always date value).\n'
          'market => markets where query data is searched in - either a country/region name or \'global\' if '
          'multiple.\n'
          'headers => custom header values, useful if you want to save data in excel; must be in JSON format.\n'
          '...or type \'back\' to return to main ui.\n')
    while True:
        user_input = input('[update query]-> ')
        if user_input == 'back':
            query.update_query_variables()
            print('Query values updated.')
            return  
        
        elif user_input == 'query':
            os.system(FilePaths.settings_path+'\\query.txt')
            try:
                if os.path.getsize(FilePaths.settings_path+'\\query.txt') == 0:
                    current_query = {}
                else:
                    with open(FilePaths.settings_path+'\\query.txt') as f:
                        current_query = json.load(f)
                with open(FilePaths.settings_path+'\\settings.json') as f:
                    settings = json.load(f)
                settings['query'] = current_query
                with open(FilePaths.settings_path+'\\settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)
            except json.decoder.JSONDecodeError:
                print('Invalid json text given. Make sure all properties are enclosed in double quotes.')

        elif user_input == 'market':
            try:
                with open(FilePaths.settings_path+'\\settings.json') as f:
                        current_market = json.load(f)['market']
            except KeyError:
                with open(FilePaths.settings_path+'\\settings.json', 'a') as f:
                    current_market = json.dump({"market": "global"})
            new_market = input("Type a market value: there are no validity checks so make sure the value is correct!\n"
                               "Empty input will keep the current value.\n"
                            f"Current market value: {current_market}.\n"
                            "--> ")
            if new_market != '':
                with open(FilePaths.settings_path+'\\settings.json') as f:
                    settings = json.load(f)
                settings['market'] = new_market
                with open(FilePaths.settings_path+'\\settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)
                print(f"Market set as '{new_market}'.")
                
        elif user_input == 'headers':
            os.system(FilePaths.settings_path+'\\headers.txt')
            try:
                if os.path.getsize(FilePaths.settings_path+'\\headers.txt') == 0:
                    current_headers = {}
                else:
                    with open(FilePaths.settings_path+'\\headers.txt') as f:
                        current_headers = json.load(f)
                with open(FilePaths.settings_path+'\\settings.json') as f:
                    settings = json.load(f)
                settings['headers'] = current_headers
                with open(FilePaths.settings_path+'\\settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)
            except json.decoder.JSONDecodeError:
                print('Invalid json text given. Make sure all properties are enclosed in double quotes.')

def update_wb_file_name() -> None:
    """Changes current workbook or creates a new one if it doesn't already exist."""
    all_workbooks = os.listdir(FilePaths.WB_FILES_ROOT_PATH)
    for f_name in all_workbooks[:]:
        if f_name.endswith(('.txt', '.json')) or f_name == '_default':
            all_workbooks.remove(f_name)
    print(all_workbooks)
    print(f"Give a new workbook file name. Current: {FilePaths.wb_name}\n"
                       "Existing workbooks: \n###")
    for wb in all_workbooks:
        print(wb)
    name_input = input("###\n[wb fname]-> ")
    if len(name_input) == 0:
        print('Name cannot be empty.')
    else:
        with open(FilePaths.WB_FILES_ROOT_PATH+'\\current_wb.json') as f:
            wb_fname = json.load(f)
        wb_fname['wb_name'] = name_input
        if name_input == '_default':
            print("This workbook cannot be selected!")
            return
        for _, dirs, _ in os.walk(FilePaths.WB_FILES_ROOT_PATH):
            for d in dirs:
                if d.endswith(name_input):
                    with open(FilePaths.WB_FILES_ROOT_PATH+'\\current_wb.json', 'w') as f:
                        json.dump(wb_fname, f, indent=4)
                    FilePaths.wb_name = name_input
                    print(f"Workbook '{name_input}' selected.")
                    FilePaths.update_filepaths()
                    query.update_query_variables()
                    sheets.update_sheets()
                    return
        new_wb = input(f"Did not find workbook named '{name_input}'. Would you like to create one?\n"
                       f"Folder 'workbooks/{name_input}' with necessary subfolders and files will be created "
                       "during this process.\n"
                        "Type 'yes' to create one, or anything else to exit.\n"
                        "[change wb]-> ")
        if new_wb.lower() == 'yes':
            with open(FilePaths.WB_FILES_ROOT_PATH+'\\current_wb.json', 'w') as f:
                json.dump(wb_fname, f, indent=4)
            FilePaths.wb_name = name_input
            FilePaths.update_filepaths()
            print("Creating new folder structure under workbooks...")
            _create_workbook_files()
            query.update_query_variables()
            create()
            sheets.update_sheets()
            print(f"Workbook '{name_input}' is now available and currently selected.")
        else:
            return

def fetch() -> None:
    """Send a query to Tradingview API and fetch data based on it.
  
    Query and received data are both in JSON format.
    """
    print('[fetch]->fetching data... ', end='')
    request_data_json = requests.post(url=QueryVars.url, 
                                      json=QueryVars.my_query, 
                                      headers=FetchData.REQUEST_HEADERS).json()
    #for t in range(3, 0, -1):   # artificial pause to prevent user from spamming requests.
    #    print(t, end=' ', flush=True)
    #    time.sleep(1)
    dataframe_cleaned = commands_utils.clean_fetched_data(request_data_json)
    dataframe_str_list = dataframe_cleaned.to_string(index=False).split('\n')
    commands_utils.create_fetch_display_txt(dataframe_str_list)
    FetchData.query_data = commands_utils.create_screener_data(dataframe_str_list)
    print('\n-> Done!')

def save() -> None:
    """Saves selected data to excel workbook.
    
    Saving procedure is done by first opening a txt file with all symbol data: this requires at least a single
    call of fetch() to have stored data. Then user can add '+' symbol in front of each symbol name which
    they wish to include data from. After saving and closing text file, workbook_tools function save()
    is called which handles the formatting and saving data to the workbook.
    """
    check, added_symbols = commands_utils.select_saved_objects()
    if check or added_symbols != []:
        print('[save]->saving...')
        workbook_tools.save(added_symbols, commands_utils.get_date())

def saveall() -> None:
    """Saves all fetched symbol data.

    Like save(), to find data, at least one fetch() call has is needed during program runtime."""
    if FetchData.query_data == []:
            print('No data available to save. Fetch data before you attempt to save it.')
            return
    print('[saveall]->saving all...')
    workbook_tools.save(FetchData.query_data, commands_utils.get_date())
    print('=>Following symbols were saved:\n')
    for sym in FetchData.query_data:
        print(sym[0])

def print_query() -> None:
    """Prints current query in json format."""
    print(json.dumps(QueryVars.my_query, indent=4))

def update_date_format() -> None:
    """Updates dates to current format."""
    first_row = input('Give a row number (>= 2) where updating starts. Base value is 2:'+
                      ' for this, leave empty input.\n')
    if first_row == '':
        workbook_tools.update_datetime(2)
    else:
        try:
            workbook_tools.update_datetime(int(first_row))
        except ValueError:
            print('Input not recognized.')

def update_to_nums() -> None:
    """Updates values of all pre-selected columns to numerical types.
    
    To change selected columns, edit CUSTOM_HEADERS in query.py.
    """
    verify = input('[update floats]-> This process can possible overwrite important data - make sure you have copied'
                   'your current workbook.\n'
                   'To proceed, type "yes".\n =>')
    if verify.lower() == 'yes':
        workbook_tools.update_values_to_nums()
    else:
        print('Updating halted.')

def export_wb() -> None:
    """Exports current workbook data and saves it in selected type."""
    file_type = input('Enter a file type from the following list:\n'
                      'txt, csv, json\n'+
                      'Prererably use csv or json; txt aligns columns poorly.\n'+
                      '>type \'back\' to return to main ui.\n'+
                      '[export_wb]-> ')
    if file_type == 'back':
        print('Exporting of workbook contents halted.')
    else:
        workbook_tools.export_wb(file_type)

def show_txt() -> None:
    """Opens the symbol data text file."""
    os.system(FilePaths.TXT_PATH)

def show_xlsx() -> None:
    """Opens the main xlsx file."""
    os.system(FilePaths.wb_path)
    sheets.update_sheets()

def copy() -> None:
    """Makes a hard copy of the current xlsx workbook file."""
    if input('Are you sure you want to make a hard copy? Type "yes" to copy, or anything else to leave.'
             '\n=>').lower() == 'yes':
        try:
            shutil.copy2(FilePaths.wb_path, FilePaths.wb_manual_copy_path)
            print('Copying was succesful.')
        except FileNotFoundError:
            print('No workbook exists with current name.')
    else:
        print('No copy was made.')

def create() -> None:
    """Creates a new xlsx workbook file template, *replacing the previous one*."""
    workbook_tools.create_wb()

def delete_workbook() -> None:
    print("Select the workbook you'd like to delete permanently.")
    all_workbooks = os.listdir(FilePaths.WB_FILES_ROOT_PATH)
    for f_name in all_workbooks[:]:
        if f_name.endswith(('.txt', '.json')) or f_name == '_default':
            all_workbooks.remove(f_name)
    for wb in all_workbooks:
        print(wb)
    del_input = input("[delete wb]=>")
    if del_input == FilePaths.wb_name:
        print("Cannot delete currently used workbook. Halting deletion process.")
        return
    if del_input in all_workbooks:
        confirm = input(f"Are you absolutely sure you'd wish to remove '{del_input}'?\n"
                        "Type 'delete wb' to proceed, or anything else to halt deleting process.\n=>")
        if confirm == 'delete wb':
            shutil.rmtree(FilePaths.WB_FILES_ROOT_PATH+'\\'+del_input)
            print(f"Workbook '{del_input}' contents deleted succesfully!")
            return
    print("No workbook was deleted this time.")