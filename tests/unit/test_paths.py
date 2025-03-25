"""Unit tests for paths.py"""

import pytest

from paths import FilePaths

def test_text_path():
    assert FilePaths.TXT_PATH == FilePaths.WB_FILES_ROOT_PATH/f'{FilePaths.TXT_NAME}.txt'

@pytest.fixture()
def file_paths():
    return FilePaths

def test_update_filepaths(file_paths):
    file_paths.wb_name = 'test_name'
    file_paths.update_filepaths()

    assert file_paths.wb_files_path == file_paths.PATH/'workbooks'/file_paths.wb_name
    assert file_paths.data_path == file_paths.wb_files_path/'data'
    assert file_paths.settings_path == file_paths.wb_files_path/'settings'

    assert file_paths.wb_autocopy_name == f'{file_paths.wb_name}-autocopy'
    assert file_paths.wb_manual_copy_name == f'{file_paths.wb_name}-copy'

    assert file_paths.wb_path == file_paths.wb_files_path/f'{file_paths.wb_name}.xlsx'
    assert file_paths.wb_autocopy_path == file_paths.wb_files_path/f'{file_paths.wb_autocopy_name}.xlsx'
    assert file_paths.wb_manual_copy_path == file_paths.wb_files_path/f'{file_paths.wb_manual_copy_name}.xlsx'