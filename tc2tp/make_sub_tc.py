from pathlib import Path
from typing import Dict, List

import xlsxwriter

from tc2tp.common.constant import CaseIndex as CI
from tc2tp.common.constant import TCSheetCfg
from tc2tp.common.logger import logger

# from tc2tp.models import CaseBase


class MakeSubTC:
    def __init__(self,
                 sub_tc_file_path: str,
                 datas: Dict[str, List] = None) -> None:
        self.sub_tc_file_path = Path(sub_tc_file_path)
        self.datas = None
        if datas:
            self.load(datas)
        self.workbook = xlsxwriter.Workbook(self.sub_tc_file_path)
        self.worksheet = self.workbook.add_worksheet("Test Case")
        self.common_format_obj = {
            "font_name": TCSheetCfg.font_name,
            "font_size": TCSheetCfg.font_size,
            "align": "left",
            "valign": "top",
            "text_wrap": 1,
        }
        self.default_row_height = TCSheetCfg.default_row_height
        self.row_ind = 0
        self.init_flag = True  # if Ture, write header

    def load(self, datas: Dict[str, List]) -> None:
        self.datas = datas

    def _writeHeader(self) -> None:
        self.init_flag = False
        header_format = self.workbook.add_format(
            dict(
                self.common_format_obj,
                bold=1,
                valign="vcenter",
                font_size=TCSheetCfg.font_size,
            ))
        for col, width in TCSheetCfg.sheet_column_width_mapper:
            self.worksheet.set_column(col, width)
        self.worksheet.set_row(self.row_ind, 2 * self.default_row_height)
        header = [str(name) for name in CI]
        self.worksheet.write_row(self.row_ind, 0, header, header_format)
        self.row_ind += 1

    def _writeSubTCs(self) -> None:
        for tc in self.datas.values():
            for sub_tc in tc:
                self._writeSubTC(sub_tc)
                self.row_ind += 1

    def _writeSubTC(self, tc) -> None:
        cell_format = self.workbook.add_format(self.common_format_obj)
        self.worksheet.set_row(
            self.row_ind,
            sum((len(step.contents)
                 for step in tc.detail_steps)) * self.default_row_height)
        for k in CI:
            v = getattr(tc, k.name.lower())
            if isinstance(v, list):
                v = "\n".join(
                    map(lambda x: str(x).replace("\"", "").replace("\'", ""),
                        v))
            else:
                v = str(v).replace("\"", "").replace("\'", "")
            self.worksheet.write(self.row_ind, k.value, v, cell_format)

    def make(self) -> None:
        if self.datas is None:
            logger.info("Please load TC sheet data firstly!")
            return False
        if self.init_flag:
            self._writeHeader()
        self._writeSubTCs()
        logger.info(
            f"======{self.sub_tc_file_path.stem} Write Successfully!======")
        self.workbook.close()
        return True
