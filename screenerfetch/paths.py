"""FilePaths class."""

from pathlib import Path

class FilePaths:
    """File paths and a method to update them.

    Uses pathlib.PATH to find location of this file. 
    Currently, all paths use string format, might change them all to pathlib eventually.
    """
    PATH = str(Path(__file__).parent)

    WB_FILES_ROOT_PATH = PATH+'\\workbooks'

    wb_name = ''
    wb_files_path = WB_FILES_ROOT_PATH+'\\'+wb_name
    data_path = wb_files_path+'\\data'
    settings_path = wb_files_path+'\\settings'

    wb_autocopy_name = f'{wb_name} - autocopy'
    wb_manual_copy_name = f'{wb_name} - copy'

    wb_path = wb_files_path+f'\\{wb_name}.xlsx'
    wb_autocopy_path = wb_files_path+f'\\{wb_autocopy_name}.xlsx'
    wb_manual_copy_path= wb_files_path+f'\\{wb_manual_copy_name}.xlsx'

    TXT_NAME = 'api_data'
    TXT_PATH = wb_files_path+f'\\{TXT_NAME}.txt'

    @staticmethod
    def update_filepaths() -> None:
        """Updates all workbook file paths."""
        FilePaths.wb_files_path = FilePaths.PATH+'\\workbooks\\'+FilePaths.wb_name
        FilePaths.data_path = FilePaths.wb_files_path+'\\data'
        FilePaths.settings_path = FilePaths.wb_files_path+'\\settings'

        FilePaths.wb_autocopy_name = f'{FilePaths.wb_name} - autocopy'
        FilePaths.wb_manual_copy_name = f'{FilePaths.wb_name} - copy'

        FilePaths.wb_path = FilePaths.wb_files_path+f'\\{FilePaths.wb_name}.xlsx'
        FilePaths.wb_autocopy_path = FilePaths.wb_files_path+f'\\{FilePaths.wb_autocopy_name}.xlsx'
        FilePaths.wb_manual_copy_path= FilePaths.wb_files_path+f'\\{FilePaths.wb_manual_copy_name}.xlsx'
        print("File paths updated.")