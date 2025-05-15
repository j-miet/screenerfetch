"""Current custom workbook commands."""

import custom.small_cap1.plot as plot
import custom.small_cap1.c_workbook_tools as c_workbook_tools
from sheets import WorkbookSheets
import workbook_tools

def plot_data() -> None:
    """Selects a correct plot function from plot.py based on user input."""
    if plot.check_if_empty():
        print("Workbook has no data, cannot plot anything.")
        return
    print('Welcome to plotting mode. To leave, type \'back\'.\n'
                    'avg daily => candlesticks chart, each candle\'s values are averages over all symbols.'
                        'Also displays a line chart of total symbol counts on each day.\n'
                    'avg lines => line whose values are each average from following list: pre-open, pre-close, open, ' 
                        'close .\n'
                    'daily cs => candlestick chart displaying all daily candles for user selected date.\n'
                    'dist => display some distributions.\n'
                    'float => scatter plot distribution of open-to-high prices and share float.\n')
    while True:
        user_input = input('[plot]>>>')
        if user_input == 'back':
            return
        elif user_input == 'avg daily':
            plot.show_daily_average_candles()
        elif user_input == 'avg lines':
            plot.show_average_lines()
        elif user_input == 'daily cs':
            date_input = input('Enter a date found that corresponds to an existing date in your excel workbook. ' 
                               'Date must in format "YYYY-MM-DD" (with \'-\' as separator!).\n'
                               '[plot>daily cs]>>>')
            if workbook_tools.check_date(date_input):
                plot.show_daily_candles(date_input)
        elif user_input == 'dist':
            plot.show_distributions()
        elif user_input == 'float':
            plot.show_high_to_open_vs_float_and_mc()
        else:
            print('Invalid input.')
    
def add_row_in_sheet2() -> None:
    """Adds a new row to second worksheet in workbook.

    This second worksheet is meant to store custom information which must be updated either via existing commands or 
    manually editing xlsx file.
    """
    print(f'Type \'exit\' to stop adding new rows in {WorkbookSheets.sheet_names[1]}.\n'
          'Need date and symbol (always in uppercase) to identify correct rows.\n'
          'Format is SYMBOL YYYY-MM-DD . Example: NVDA 2024-01-31 \n'
          '-> '   
          )
    while True:
        input_data = input('[plot>add row to sheet2]>>>')
        if input_data == 'back':
            return
        try:
            c_workbook_tools.add_row_in_sheet2(input_data)
        except (IndexError, ValueError):
            print('Invalid input.')

def add_notes() -> None:
    """Allows for adding text under 'Notes' section in the second worksheet.

    Will replace *all existing text* so be careful: this command is meant for adding quick initial
    notes before doing actual writeup in excel.
    """
    print('Type \'exit\' to stop editing notes.\n'
          'Need date and symbol (always in uppercase) to identify correct rows.\n'
          'Format is SYMBOL YYYY-MM-DD. Example: NVDA 2024-01-31\n'
          '-> '   
          )
    while True:
        input_data = input('[plot>notes]>>>')
        if input_data == 'back':
            return
        try:
            c_workbook_tools.edit_notes(input_data)
        except (IndexError, ValueError):
            print('Invalid input.')

def add_images() -> None:
    """Add both intraday and daily image hyperlinks of a symbol in the second worksheet.
    
    Images must be located in folder 'custom/images' and have following names:

    SYMBOL YYYY-MM-DD 
    SYMBOL YYYY-MM-DD D

    where YYYY-MM-DD is the date and SYMBOL is the name in all UPPERCASE; D refers to daily image, one without it to 
    intraday image. An example: 

    NVDA 2024-01-31 
    NVDA 2024-01-31 D
    
    You have to add images yourself e.g. could use snipping tool (ctrl + shift + s). 
    (I've tried web screenshotting with Selenium/Playwright, but results were just bad so manual process is better.)

    You can keep adding multiple symbols. When done, type 'back' as input and press enter.
    """
    print('Type \'exit\' to stop adding new images.\n'
          'Need date and symbol (always in uppercase) to identify correct rows.\n'
          'Format is SYMBOL YYYY-MM-DD . Example: NVDA 2024-01-31 \n'
          '-> '   
          )
    while True:
        input_data = input('[plot>images]>>>')
        if input_data == 'back':
            return
        try:
            c_workbook_tools.add_image_hyperlinks(input_data)
        except (IndexError, ValueError):
            print('Invalid input.')

def _update_datetime() -> None:
    c_workbook_tools.custom_update_datetime()

def select_custom_command() -> None:
    """Lists all custom workbook commands for small_cap1 custom package."""
    while True:
        custom_input = input("Type any of the custom commands below, or 'back' to return.\n"
            "add row = adds a row for existing symbol in the second worksheet "
            f"{WorkbookSheets.sheet_names[1]}; has custom columns.\n"
            "notes = adds/overwrites notes for any listed symbol in "
            f"{WorkbookSheets.sheet_names[1]} sheet.\n"
            f"images = add hyperlinks in {WorkbookSheets.sheet_names[1]} sheet which points "
                "to 'small_cap1/images' folder.\n"
            "plot = commands for visualizing symbol data of current workbook.\n"
            "FORMAT WB = formats current workbook to custom format.\n"
            "[custom]>>>")
        if custom_input == 'add row':
            add_row_in_sheet2()
        elif custom_input == 'notes':
            add_notes()
        elif custom_input == 'images':
            add_images()
        elif custom_input == 'update date':
            _update_datetime()
        elif custom_input == 'plot':
            plot_data()
        elif custom_input == 'back':
            return
        else:
            print('Invalid custom command.')