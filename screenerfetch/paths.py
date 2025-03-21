"""FilePaths class."""

from pathlib import Path

class FilePaths:
    """File paths and a method to update them.

    Uses pathlib.PATH to find location of this file. 
    Currently, all paths use string format, might change them all to pathlib eventually.
    """
    PATH = str(Path(__file__).parent)
    WB_FILES_PATH = PATH+'\\workbooks'
    DATA_PATH = PATH+'\\data'
    SETTINGS_PATH = PATH+'\\settings'

    TXT_NAME = 'api_data'
    TXT_PATH = DATA_PATH+f'\\{TXT_NAME}.txt'

    wb_name = ''
    wb_autocopy_name = f'{wb_name} - autocopy'
    wb_manual_copy_name = f'{wb_name} - copy'

    wb_path = WB_FILES_PATH+f'\\{wb_name}.xlsx'
    wb_autocopy_path = WB_FILES_PATH+f'\\{wb_autocopy_name}.xlsx'
    wb_manual_copy_path= WB_FILES_PATH+f'\\{wb_manual_copy_name}.xlsx'

    @staticmethod
    def update_filepaths() -> None:
        """Updates all workbook file paths."""
        FilePaths.wb_autocopy_name = f'{FilePaths.wb_name} - autocopy'
        FilePaths.wb_manual_copy_name = f'{FilePaths.wb_name} - copy'

        FilePaths.wb_path = FilePaths.WB_FILES_PATH+f'\\{FilePaths.wb_name}.xlsx'
        FilePaths.wb_autocopy_path = FilePaths.WB_FILES_PATH+f'\\{FilePaths.wb_autocopy_name}.xlsx'
        FilePaths.wb_manual_copy_path= FilePaths.WB_FILES_PATH+f'\\{FilePaths.wb_manual_copy_name}.xlsx'
        print("File paths updated.")