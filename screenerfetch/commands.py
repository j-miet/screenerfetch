"""CLI commands."""

import json
import logging
import os
import shutil

import commands_utils
from paths import FilePaths
from query import QueryVars, FetchData
from sheets import WorkbookSheets
import workbook_tools

logger = logging.getLogger('screenerfetch')

def update_query() -> None:
    """Handles query-related updates using text and json files.
    
    Note that changing query and/or headers will also impact your xlsx file column names.
    """
    logger.debug("commands> update_query")
    QUERY_HELP= (
        '##########################################\n'
        'If you want to set up your current TradingView screener settings, the easiest way is:\n'
        '-open your TradingView screener page, with your desired screener as currently selected.\n'
        '-press F12 and refresh your page (F5).\n'
        '-then have "Network" selected and below it you see "Filter URLs" search box.\n'
        '-now type "scanner" in that box, wait a second or two.'
        ' There should be a few matches, all with 200 status and with method GET or POST.\n'
        ' From the ones saying POST, select the top one/one with \'scan?!label-product=screener-stock\''
        ' under File header.\n'
        '-A window extend to right: select "Requests" page -> right-click and select Copy All.\n'
        '-You have your query in clipboard so click back to this program, type "query" and press Enter\n'
        '-A text file pops up: it contains your current query - if it\'s empty, paste the one you just copied.\n'
        '>Your query columns under "columns" will likely include some extra entries. For example, minimal \n'
        'column list which you get with just including "name" (which by the way, must be included or you\'re in ' 
        'trouble) becomes\n\n'

        '[\n'
        '   "name",\n'
        '   "description",\n'
        '   "logoid",\n'
        '   "update_mode",\n'
        '   "type",\n'
        '   "typespecs",\n'
        '   "exchange"\n'
        ']\n\n'
        'To find out what these columns do, you can always save the query, return to main commands, fetch data and '
        'check the fetched data with \'txt\' command.\n\n' 
        '---This is everything you need...but if you wish to customize your column names for txt/excel files, check '
        'this out:----\n\n'

        '{\n'
        '"A" : {"name": "Date"},\n'
        '"B" : {"name": "Symbol"},\n'
        '"C" : {"type": "float"},\n'
        '"D" : {"name": "Price", "type": "float", "decimals": 2},\n'
        '"F" : {"name": "Volume", "type": "int"},\n'
        '}\n\n'
        'letters refer to corresponding workbook columns, name is the column name and type is the column value type.\n'
        'Supported type values are "int" or "float": these ensure that numbers are either rounded down to an '
        'integer, or are rounded to desired amount of decimals.\n'
        'To customize decimals of float number, include the "decimals": N, where N is the amount of decimals.\n\n'
        'These int/float values also ensure excel doesn\'t complain about using string '
        'value with numbers in xlsx files.\n'
        'name/type values are optional so you can have name, but not type and vice versa.\n'
        'However, use "decimals" only with float values (they would not make sense for ints or other types...)\n'
        'And if you want to leave default name values and don\'t care about rounding, remove the entire row!\n'
        '# Note that date column is always A; rest depend on the order they appear in query columns.\n'
        '# Supports excel columns A-Z and AA-AZ; if your workbook exceeds this limit of 52 column names, '
        'program crashes.')
    QUERY_COMMANDS_HELP = (
            '/////////////////////////////\n'
            'Query commands:\n'
            'query => current query; must be in JSON format. NOTE that order in \'columns\' matters:\n'
            '\t Nth value will be N+1 column in .xlsx file (because first column is always date value).\n'
            'headers => custom header values, useful if you want to save data in excel; must be in JSON format.\n'
            'OTHER: \'help\' for detailed info, or \'back\' to return to main ui.')
    print(QUERY_COMMANDS_HELP)
    while True:
        user_input = input('[update query]>>>')
        match user_input:
            case 'help':
                print(QUERY_HELP)
                input("\n~Press Enter to continue...")
                print(QUERY_COMMANDS_HELP)
            case 'back':
                logger.debug("commands.py> update_commands: Input 'back'")
                QueryVars.update_query_variables()
                print('Query values updated.')
                return    
            case _:
                logger.debug(f"commands.py> update_commands: Input '{user_input}'")
                commands_utils.update_settings_json(user_input)

def update_wb_file_name(select_wb: list[str] = []) -> None:
    """Changes current workbook or creates a new one if it doesn't already exist.
    
    Args:
        select_wb (list[str] = []): Workbook name. This variable should only be passed if screenerfetch is passed 
            command line arguments. For this reason, it also has type list[str] instead of str.
    """
    logger.debug("commands.py> update_wb_file_name")
    name_input: str | list[str] = []
    all_workbooks = os.listdir(FilePaths.WB_FILES_ROOT_PATH)
    for f_name in all_workbooks[:]:
        if f_name.endswith(('.txt', '.json')) or f_name == '_default':
            all_workbooks.remove(f_name)
    if select_wb != []:
        name_input = select_wb[0]
    else:
        print("--Non-empty input to select/create workbook, empty input to exit--\n"
                f">Current: {FilePaths.wb_name}\n"
                            "Existing workbooks:\n"
                            "====================")
        for wb in all_workbooks:
            print(wb)
        name_input = input("====================\n[change wb]>>>")
        logger.debug("commands.py> update_wb_file_name: Name input")
    if commands_utils.check_wb_name_validity(name_input) == -1:
        return
    elif name_input in all_workbooks:
        commands_utils.change_workbook(name_input, False, False)
    else:
        new_wb = input(f"Did not find workbook named '{name_input}'. Would you like to create one?\n"
                        f"Folder 'workbooks/{name_input}' with necessary subfolders and files will be created "
                        "during this process.\n"
                        "Type 'yes' to create one, or anything else to exit.\n"
                        "[change wb>new wb]>>>")
        if new_wb == 'yes':
            commands_utils.change_workbook(name_input, True, False)
        
def fetch() -> int:
    """Get api data, modify it based on custom header values, then store it.
    
    Returns:
        int:
        0 if fetching and data creation was succesful  
        -1 if empty dataframe was fetched.  
        1 if dataframe has symbols, but they have no extractable data due to missing columns in settings.json.
    """
    logger.debug("commands.py> fetch")
    print('[fetch]->fetching data... ', end='')
    request_data_json = commands_utils.requests_api_data()
    if request_data_json['totalCount'] != 0:
        if request_data_json['data'][0]['d'] != []:
            dataframe_cleaned = commands_utils.clean_fetched_data(request_data_json)
            dataframe_str_list = dataframe_cleaned.to_string(index=False).split('\n')
            dataframe_dict = dataframe_cleaned.to_dict()
            commands_utils.create_fetch_display_txt(dataframe_str_list)
            FetchData.query_data = commands_utils.create_screener_data(dataframe_dict)
            print('\n-> Done!')
            return 0
        else:
            print("\nERROR: Query found symbols, but can't return data due to missing columns in settings.json.\n"
                "Check your query in query.txt and verify it has at least one valid value under \"columns\".")
            return -1
    else:
        logger.debug("commands.py> fetch: Empty dataframe returned.")
        print('Query returned an empty dataframe, no fetch data was saved.')
        return -1

def save() -> None:
    """Saves selected data to excel workbook.
    
    Saving procedure is done by first opening a txt file with all symbol data: this requires at least a single
    call of fetch() to have stored data. Then user can add '+' symbol in front of each symbol name which
    they wish to include data from. After saving and closing text file, workbook_tools function save()
    is called which handles the formatting and saving data to the workbook.
    """
    logger.debug("commands.py> save")
    print('[save]->', end='')
    if FetchData.query_data == []:
            print('No data available to save. Fetch data before you attempt to save it.')
            return
    os.system(str(FilePaths.TXT_PATH))
    check, added_symbols = commands_utils.select_saved_objects()
    if check or added_symbols != []:
        print('saving...')
        workbook_tools.save(added_symbols, commands_utils.get_date())

def saveall() -> None:
    """Saves all fetched symbol data.

    Like save(), to find data, at least one fetch() call has is needed during program runtime."""
    logger.debug("commands.py> saveall")
    print('[saveall]->', end='')
    if FetchData.query_data == []:
            logger.debug("commands.py> saveall: No query data")
            print('No data available to save. Fetch data before you attempt to save it.')
            return
    print('saving all...')
    workbook_tools.save(FetchData.query_data, commands_utils.get_date())
    print('=>Following symbols were saved:\n')
    for sym in FetchData.query_data:
        print(sym[0])

def print_query() -> None:
    """Prints current query in json format."""
    print(json.dumps(QueryVars.my_query, indent=4))

def update_date_format() -> None:
    """Updates dates to current format."""
    logger.debug("commands.py> update_date_formet")
    first_row = input('Give a row number (>= 2) where updating starts. Base value is 2:'+
                      ' for this, leave empty input.\n'
                      '[update date]>>>')
    logger.debug(f"commands.py> update_date_format: Input '{first_row}'")
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
    logger.debug("commands.py> update_to_nums")
    verify = input('This process can possible overwrite important data - make sure you have copied'
                   'your current workbook.\n'
                   'To proceed, type "yes".\n'
                   '[update nums]>>>')
    if verify.lower() == 'yes':
        workbook_tools.update_values_to_nums()
    else:
        print('Updating halted.')

def export_wb() -> None:
    """Exports current workbook data and saves it in selected type."""
    logger.debug("commands.py> export_wb")
    file_type = input('Enter a file type from the following list:\n'
                      'txt, csv, json\n'+
                      'You can also select \'all\' to create all files.\n'+
                      '>type \'back\' to return to main ui.\n'+
                      '[export_wb]>>>')
    if file_type == 'back':
        print('Exporting of workbook contents halted.')
    else:
        workbook_tools.export_wb(file_type)

def show_txt() -> None:
    """Opens the symbol data text file."""
    logger.debug("commands.py> show_txt")
    print(f"[txt]->displaying {FilePaths.TXT_NAME}.txt...")
    os.system(str(FilePaths.TXT_PATH))

def show_xlsx() -> None:
    """Opens the main xlsx file."""
    logger.debug("commands.py> show_xlsx")
    print(f"[excel]->displaying {FilePaths.wb_name}.xlsx...")
    os.system(str(FilePaths.wb_path))
    WorkbookSheets.update_sheets()

def remove_duplicate_data() -> None:
    """Remove duplicate row data from workbook."""
    logger.debug("commands.py> remove_duplicate_data")
    workbook_tools.remove_duplicates()

def copy() -> None:
    """Makes a hard copy of the current xlsx workbook file."""
    logger.debug("commands.py> copy")
    if input('Are you sure you want to make a hard copy? Type "yes" to copy, or anything else to leave.'
             '\n[copy]>>>').lower() == 'yes':
        try:
            shutil.copy2(FilePaths.wb_path, FilePaths.wb_manual_copy_path)
            print('Copying was succesful.')
        except FileNotFoundError:
            print('No workbook exists with current name.')
    else:
        print('No copy was made.')

def create(create_new: bool = True) -> None:
    """Creates a new xlsx workbook file template, *replacing the previous one*.
    
    Args:
        create_new (bool=True): True to create wb with default type files, False to keep existing files so that 
            workbook has updated columns.
    """
    logger.debug("commands.py> create")
    workbook_tools.create_wb(create_new)

def delete_workbook() -> None:
    """Deletes any existing workbook that is not currently in use."""
    logger.debug("commands.py> delete_workbook")
    print("Select the workbook you'd like to *delete permanently*.")
    all_workbooks = os.listdir(FilePaths.WB_FILES_ROOT_PATH)
    for f_name in all_workbooks[:]:
        if f_name.endswith(('.txt', '.json')) or f_name == '_default':
            all_workbooks.remove(f_name)
    for wb in all_workbooks:
        print(wb)
    del_input = input("[delete wb]>>>")
    logger.debug(f"commands.py> delete_workbook: Input '{del_input}'")
    if del_input == FilePaths.wb_name:
        logger.debug("commands.py> delete_workbook: Cannot delete wb")
        print("Cannot delete currently used workbook. Halting deletion process.")
        return
    if del_input in all_workbooks and del_input != '_default':
        confirm = input(f"Are you absolutely sure you'd wish to remove '{del_input}'?\n"
                        "Type 'delete wb' to proceed, or anything else to halt deleting process.\n"
                        "[delete wb]>>>")
        logger.debug(f"commands.py> delete_workbook: Confirm input '{confirm}'")
        if confirm == 'delete wb':
            commands_utils.delete_workbook(del_input)
            return
    logger.debug("commands.py> delete_workbook: No wb deleted")
    print("No workbook was deleted this time.")