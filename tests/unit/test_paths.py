"""Unit tests for paths.py"""

from paths import FilePaths

def test_text_path():
    assert FilePaths.TXT_PATH == FilePaths.WB_FILES_ROOT_PATH/f'{FilePaths.TXT_NAME}.txt'

def test_update_filepaths():
    FilePaths.wb_name = 'test_name'
    FilePaths.update_filepaths()

    assert FilePaths.wb_files_path == FilePaths.PATH/'workbooks'/FilePaths.wb_name
    assert FilePaths.data_path == FilePaths.wb_files_path/'data'
    assert FilePaths.settings_path == FilePaths.wb_files_path/'settings'

    assert FilePaths.wb_autocopy_name == f'{FilePaths.wb_name}-autocopy'
    assert FilePaths.wb_manual_copy_name == f'{FilePaths.wb_name}-copy'

    assert FilePaths.wb_path == FilePaths.wb_files_path/f'{FilePaths.wb_name}.xlsx'
    assert FilePaths.wb_autocopy_path == FilePaths.wb_files_path/f'{FilePaths.wb_autocopy_name}.xlsx'
    assert FilePaths.wb_manual_copy_path == FilePaths.wb_files_path/f'{FilePaths.wb_manual_copy_name}.xlsx'