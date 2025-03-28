"""Testing workbook creation, switching and deletion.

Commands tested: commands.utils -> change_workbook, delete_workbook.
"""

import json

import run

from paths import FilePaths
import commands_utils

def test_create_and_delete_workbook():
    wb_name: dict[str, str]
    _previous_wb: dict[str, str]

    # if tests failed and previous test workbooks exists
    commands_utils.delete_workbook('integration_test_workbook')
    commands_utils.delete_workbook('integration_test_workbook_2')

    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        wb_name = json.load(wb_name_file)
    _previous_wb = wb_name.copy()
    assert wb_name["wb_name"] == _previous_wb["wb_name"]
    wb_name["wb_name"] = "_default"
    
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        wb_name = json.load(wb_name_file)
    wb_name["wb_name"] = "_default"
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as wb_name_file:
        json.dump(wb_name, wb_name_file, indent=4)
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        wb_name2 = json.load(wb_name_file)
    assert wb_name["wb_name"] == "_default"

    run._initialize_workbook()
    assert FilePaths.wb_name == '_default'

    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        wb_name = json.load(wb_name_file)
        wb_name["wb_name"] = "integration_test_workbook"
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as wb_name_file:
        json.dump(wb_name, wb_name_file, indent=4)
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        wb_name2 = json.load(wb_name_file)
    assert wb_name2["wb_name"] == 'integration_test_workbook'

    assert commands_utils.change_workbook('integration_test_workbook', False) == -2
    assert commands_utils.change_workbook('integration_test_workbook', True) == 2
    assert commands_utils.change_workbook('integration_test_workbook', False) == 1
    assert commands_utils.change_workbook('integration_test_workbook', True) == -3

    run._initialize_workbook()
    assert FilePaths.wb_name == 'integration_test_workbook'
    commands_utils.change_workbook('integration_test_workbook', True) == 2
    assert FilePaths.wb_name == 'integration_test_workbook'
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        wb_name = json.load(wb_name_file)
    assert commands_utils.change_workbook('_default', True) == -1
    assert wb_name["wb_name"] == 'integration_test_workbook'

    assert commands_utils.change_workbook('integration_test_workbook_2', False) == -2
    assert FilePaths.wb_name == 'integration_test_workbook'
    assert commands_utils.change_workbook('integration_test_workbook_2', True) == 2
    assert FilePaths.wb_name == 'integration_test_workbook_2'
    assert commands_utils.change_workbook('integration_test_workbook_2', False) == 1
    assert commands_utils.change_workbook('integration_test_workbook_2', True) == -3

    assert commands_utils.delete_workbook('_default') == -1
    assert commands_utils.delete_workbook('integration_test_workbook') == 0
    assert commands_utils.delete_workbook('integration_test_workbook_2') == 0
    assert commands_utils.delete_workbook('integration_test_workbook') == -1
    assert commands_utils.delete_workbook('integration_test_workbook_2') == -1

    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as wb_name_file:
        json.dump(_previous_wb, wb_name_file, indent=4)
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as wb_name_file:
        check_wb = json.load(wb_name_file)
    assert check_wb == _previous_wb