"""Current custom workbook commands."""

import custom.plot as plot
import custom.c_workbook_tools as c_workbook_tools
from query import QueryVars
from workbook_tools import WorkSheets, check_date

def _check_wb_validity() -> bool:
    """Check if workbook supports current custom plotting commands."""
    if ({"Date", 
        "Symbol",
        "Low",
        "High",
        "Price",
        "Open",
        "Float",
        "Volume",
        "Market Cap",
        "Pre-market Open",
        "Chg from Open %"
     }.issubset(QueryVars.col_headers.values()) and
        {"name",
         "low",
         "high",
         "close",
         "open",
         "float_shares_outstanding_current",
         "volume",
         "market_cap_basic", 
         "premarket_open",
         "change_from_open"
    }.issubset(QueryVars.actual_columns)):
        return True
    print("########################################################\n"
          "### Current workbook doesn't support custom commands ###\n"
          "########################################################\n"
          "Required:\n"
          "<columns> name, low, high, close, open, float_shares_outstanding_current, volume, market_cap_basic, " "premarket_open, premarket_close, change_from_open\n"
          "<custom column headers> Date, Symbol, Low, High, Price, Open, Float, Volume, Market Cap, Pre-market Open, "
          "Chg from Open %")
    return False

def _plot_data() -> None:
    """Selects a correct plot function from plot.py based on user input."""
    print('Welcome to plotting mode. To leave, type \'back\'.\n'
                    'avg daily => candlesticks chart, each candle\'s values are averages over all symbols.'
                        'Also displays a line chart of total symbol counts on each day.\n'
                    'avg lines => line whose values are each average from following list: pre-open, pre-close, open, ' 
                        'close .\n'
                    'daily cs => candlestick chart displaying all daily candles for user selected date.\n'
                    'dist => display some distributions.\n'
                    'float => scatter plot distribution of open-to-high prices and share float.\n')
    while True:
        user_input = input('[plot]-> ')
        if user_input == 'back':
            return
        elif user_input == 'avg daily':
            plot.show_daily_average_candles()
        elif user_input == 'avg lines':
            plot.show_average_lines()
        elif user_input == 'daily cs':
            date_input = input('Enter a date found that corresponds to an existing date in your excel workbook. ' 
                               'Date must in format "YYYY-MM-DD" (with \'-\' as separator!).\n=>')
            if check_date(date_input):
                plot.show_daily_candles(date_input)
        elif user_input == 'dist':
            plot.show_distributions()
        elif user_input == 'float':
            plot.show_high_to_open_vs_float_and_mc()
        else:
            print('Invalid input.')
    
def _add_row_in_sheet2() -> None:
    """Adds a new row to second worksheet in workbook.

    This second worksheet is meant to store custom information which must be updated either via existing commands or 
    by manually inside workbook.
    """
    print(f'Type \'exit\' to stop adding new rows in {WorkSheets.SHEET2}.\n'
          'Need date and symbol (always in uppercase) to identify correct rows.\n'
          'Format is SYMBOL YYYY-MM-DD . Example: NVDA 2024-01-01 \n'
          '-> '   
          )
    while True:
        input_data = input('[sheet2: add row]-> ')
        if input_data == 'back':
            return
        try:
            c_workbook_tools.add_row_in_sheet2(input_data)
        except (IndexError, ValueError):
            print('Invalid input.')

def _add_notes() -> None:
    """Allows for adding text under 'Notes' section in the second worksheet.

    Will replace *all existing text* so be careful: this command is meant for adding quick initial
    notes before doing actual writeup in excel.
    """
    print('Type \'exit\' to stop editing notes.\n'
          'Need date and symbol (always in uppercase) to identify correct rows.\n'
          'Format is SYMBOL YYYY-MM-DD. Example: NVDA 2024-01-01\n'
          '-> '   
          )
    while True:
        input_data = input('[notes]-> ')
        if input_data == 'back':
            return
        try:
            c_workbook_tools.edit_notes(input_data)
        except (IndexError, ValueError):
            print('Invalid input.')

def _add_images() -> None:
    """Add both intraday and daily image hyperlinks of a symbol in the second worksheet.
    
    Images must be located in folder 'custom/images' and have following names:

    SYMBOL YYYY-MM-DD 
    SYMBOL YYYY-MM-DD D

    where YYYY-MM-DD is the date and SYMBOL is the name in all UPPERCASE; D refers to daily image, one without it to 
    intraday image. An example: 

    NVDA 2024-01-01 
    NVDA 2024-01-01 D
    
    You have to add images yourself e.g. could use snipping tool (ctrl + shift + s). 
    (I've tried web screenshotting with Selenium/Playwright, but results were just bad so manual process is better.)

    You can keep adding multiple symbols. When done, type 'back' as input and press enter.
    """
    print('Type \'exit\' to stop adding new images.\n'
          'Need date and symbol (always in uppercase) to identify correct rows.\n'
          'Format is SYMBOL YYYY-MM-DD . Example: NVDA 2024-01-01 \n'
          '-> '   
          )
    while True:
        input_data = input('[images]-> ')
        if input_data == 'back':
            return
        try:
            c_workbook_tools.add_image_hyperlinks(input_data)
        except (IndexError, ValueError):
            print('Invalid input.')

def select_custom_command() -> None:
    """Lists all custom workbook commands and asks user input if workbook format is valid."""
    if _check_wb_validity():
        while True:
            custom_input = input("Type any of the custom commands below, or 'back' to return.\n"
                f"add row = adds a row for existing symbol in the second worksheet {WorkSheets.SHEET2}; has "
                "custom columns.\n"
                f"notes = adds/overrides notes for any listed symbol in {WorkSheets.SHEET2} sheet.\n"
                f"images = add hyperlinks in {WorkSheets.SHEET2} sheet which point to 'custom/images' folder.\n"
                "plot = commands for visualizing symbol data of current workbook.\n"
                "FORMAT CUSTOM WB = formats current workbook to custom format, adding a second sheet "
                f"{WorkSheets.SHEET2}.\n"
                "[custom]>>> ")
            if custom_input == 'add row':
                _add_row_in_sheet2()
            elif custom_input == 'notes':
                _add_notes()
            elif custom_input == 'images':
                _add_images()
            elif custom_input == 'plot':
                _plot_data()
            elif custom_input == 'back':
                return
            elif custom_input == 'FORMAT CUSTOM WB':
                ... # implement this under c_commands + c_workbook_tools
                print('This does currently nothing...')
            else:
                print('Invalid custom command.')