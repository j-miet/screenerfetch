"""Stores all workbook sheet names."""

import openpyxl

from paths import FilePaths

class WorkbookSheetNames:
    sheet_names: list[str] = []

def update_sheets() -> None:
    WorkbookSheetNames.sheet_names = openpyxl.load_workbook(FilePaths.wb_path).sheetnames