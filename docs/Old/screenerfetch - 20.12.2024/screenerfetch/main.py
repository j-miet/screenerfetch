import shutil

import commands
from file_paths import WB_PATH, WB_MANUAL_COPY_PATH

#TODO remove excessive comments, maybe write down some useful parts to a separate help/readme file
#TODO could implement data displaying with Pandas. Currently code is quite messy, especially under commands.fetch()

def main():
    print("Commands (not case-sensitive except CREATE NEW)\n"
          "--------------------------------------------------------\n"
          "f/fetch = fetch data from TradingView API based on your query located in query.py\n"
          "s/save = saves symbols to a .xlsx file. You must fetch data before you can save it\n"
          "open txt = opens screenerdata.txt file where you see the fetched data\n"
          "open excel = opens screenerdata.xlsx file which contains all symbols you saved\n"
          "edit notes = add custom notes to any listed symbol in screenerdata.xlsx\n"
          "copy = copy your current screenerdata.xlsx file as 'screenerdata - manual_copy.xlsx'\n"
          "quit/exit = close the program and copy current xlsx data to 'screenerdata - copy.xlsx'\n"
          "CREATE NEW = overrides your current screenerdata.xlsx. Fresh file has only column headers defined in query/COL_HEADERS"
          )
    while True:
        user_input = input('--------------------\n>>> ')
        if user_input.lower() == 'f' or user_input.lower() == 'fetch':
            commands.fetch()
        elif user_input.lower() == 's' or user_input.lower() == 'save':
            commands.save()
        elif user_input.lower() == 'open txt':
            commands.show_txt()
        elif user_input.lower() == 'open excel':
            commands.show_xlsx()
        elif user_input.lower() == 'edit notes':
            commands.edit_notes()
        elif user_input.lower() == 'copy':
            commands.copy()
        elif user_input.lower() == 'quit' or user_input.lower() == 'exit':
            shutil.copy2(WB_PATH, WB_MANUAL_COPY_PATH)
            return
        elif user_input == 'CREATE NEW':
            commands.create()
        else:
            print('Unknown command')

if __name__ == '__main__':
    main()