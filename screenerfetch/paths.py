"""FilePaths class."""

from pathlib import Path

class FilePaths:
    """File paths and static method upgrade_filepaths to update them."""
    PATH = Path(__file__).parent
    WB_FILES_ROOT_PATH = PATH/'workbooks'

    wb_name: str
    wb_autocopy_name: str
    wb_manual_copy_name: str
    wb_files_path: Path
    data_path: Path
    settings_path: Path
    wb_path: Path
    wb_autocopy_path: Path
    wb_manual_copy_path: Path

    TXT_NAME = 'api_data'
    TXT_PATH = WB_FILES_ROOT_PATH/f'{TXT_NAME}.txt'

    @staticmethod
    def update_filepaths() -> None:
        """Updates all workbook file paths."""
        FilePaths.wb_files_path = FilePaths.PATH/'workbooks'/FilePaths.wb_name
        FilePaths.data_path = FilePaths.wb_files_path/'data'
        FilePaths.settings_path = FilePaths.wb_files_path/'settings'

        FilePaths.wb_autocopy_name = f'{FilePaths.wb_name}-autocopy'
        FilePaths.wb_manual_copy_name = f'{FilePaths.wb_name}-copy'

        FilePaths.wb_path = FilePaths.wb_files_path/f'{FilePaths.wb_name}.xlsx'
        FilePaths.wb_autocopy_path = FilePaths.wb_files_path/f'{FilePaths.wb_autocopy_name}.xlsx'
        FilePaths.wb_manual_copy_path= FilePaths.wb_files_path/f'{FilePaths.wb_manual_copy_name}.xlsx'