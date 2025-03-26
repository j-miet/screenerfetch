"""Stores all workbook sheet names."""

import openpyxl

from paths import FilePaths

class WorkbookSheets:
    sheet_names: list[str] = []

    @staticmethod
    def update_sheets() -> None:
        """Update workbook sheet names."""
        WorkbookSheets.sheet_names = openpyxl.load_workbook(FilePaths.wb_path).sheetnames