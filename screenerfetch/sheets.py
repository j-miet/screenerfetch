"""Stores all workbook sheet names."""

import logging

import openpyxl

from paths import FilePaths

logger = logging.getLogger('screenerfetch')

class WorkbookSheets:
    sheet_names: list[str] = []

    @staticmethod
    def update_sheets() -> None:
        """Update workbook sheet names."""
        logger.debug("sheets.py> WorkbookSheets.update_sheets")
        WorkbookSheets.sheet_names = openpyxl.load_workbook(FilePaths.wb_path).sheetnames
        logger.debug("sheets.py> WorkbookSheets.update_sheets: Workbook sheets updated.")