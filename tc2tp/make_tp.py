from pathlib import Path
from typing import Dict, List

import xlsxwriter

from tc2tp.common.config import config
from tc2tp.common.constant import TPSheetCfg,CFGSheetCfg
from tc2tp.common.logger import logger
from tc2tp.models import CaseBase, StepKey
from tc2tp.query_builder import QueryBuilder

def addcolumn(ch:chr,num:int):
    return chr(ord(ch)+num)

class MakeTP:
    def __init__(self, tp_dir: str, datas: Dict[str, List], date: str, revisionHistory: Dict[int, List]) -> None:
        self.tp_dir = Path(tp_dir)
        self.datas = datas
        self.date = date
        self.revisionHistory = revisionHistory

    def makeOne(self, tp_id: str) -> None:
        tp_path = self.tp_dir.joinpath(tp_id + ".xlsx")
        tp_datas = self.datas.get(tp_id)
        tp_date = self.date
        tp_revisionHistory = self.revisionHistory
        try:
            _MakeTP(tp_path, tp_datas, tp_date ,tp_revisionHistory).write()
        except Exception as e:
            if config.DEBUG:
                logger.exception(e)
            else:
                logger.error(f"[{tp_id}]:{e!s}")

    def make(self) -> None:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            executor.map(self.makeOne, self.datas.keys())
        # for tp_id in self.datas:
        #     self.makeOne(tp_id)

class _MakeTP:
    def __init__(self, tp_path: Path, tp_datas: List[CaseBase], date: str, revisionHistory: Dict[int, List]) -> None:
        self.tp_id = tp_path.stem
        self.workbook = xlsxwriter.Workbook(tp_path)
        # self.configuration_sheet = self.workbook.add_worksheet(
        #     "I Configuration")
        # self.system_test_inputs_sheet = self.workbook.add_worksheet(
        #     "II System Test Inputs")
        # self.functional_area_reqs_sheet = self.workbook.add_worksheet(
        #     "III Functional Area Reqs")
        self.worksheet_cfg = self.workbook.add_worksheet("Configuration")
        self.worksheet = self.workbook.add_worksheet("Test Procedure")
        # self.software_sheet = self.workbook.add_worksheet("V Software")
        self.tp_datas = tp_datas
        self.row_ind = 0
        self.common_format_obj = {
            "font_name": TPSheetCfg.font_name,
            "font_size": TPSheetCfg.font_size,
            "align": "left",
            "valign": "bottom",
            "text_wrap": 1,
        }
        self.cfg_format_obj = {
            "font_name": CFGSheetCfg.font_name,
            "font_size": CFGSheetCfg.font_size,
            "align": "left",
            "valign": "bottom",
            "text_wrap": 1,
        }

        self.default_row_height = TPSheetCfg.default_row_height
        self.max_column_ind = 7
        self.date = date
        self.revisionHistory = revisionHistory
        self.error_flag = False

    def _writeconfiguration(self) -> None:
        for col, width in CFGSheetCfg.sheet_column_width_mapper:
            self.worksheet_cfg.set_column(col, width)
        header = "Shanghai Aviation Electric Co., Ltd.\nC919 MODEL TEST Procedure SPECIFICATION"
        self.worksheet_cfg.set_row(0, 32)
        merge_format = self.workbook.add_format(
            dict(
                self.cfg_format_obj,
                bold=1,
                align="center",
                valign="vcenter",
                font_size=12,
            ))
        merge_format1 = self.workbook.add_format(
            dict(
                bold=0,
                align="center",
                valign="vcenter",
                font_name="Times New Roman",
                text_wrap =1,
                font_size=12
            ))
        merge_format2 = self.workbook.add_format(
            dict(
                bold=1,
                align="left",
                valign="vcenter",
                font_name="Arial",
                font_size=10
            ))
        merge_format3 = self.workbook.add_format(
            dict(
                bold=1,
                align="center",
                valign="vcenter",
                font_name="Arial",
                font_size=12
            ))
        merge_format4 = self.workbook.add_format(
            dict(
                bold=0,
                align="left",
                valign="vcenter",
                font_name="Arial",
                font_size=11
            ))
        merge_format5 = self.workbook.add_format(
            dict(
                bold=0,
                align="center",
                valign="vcenter",
                font_name="宋体",
                text_wrap =1,
                font_size=11
            ))
        merge_format6 = self.workbook.add_format(
            dict(
                bold=1,
                align="center",
                valign="vcenter",
                font_name="等线",
                text_wrap =1,
                font_size=22
            ))
        merge_format7 = self.workbook.add_format(
            dict(
                bold=0,
                align="center",
                valign="vcenter",
                font_name="等线",
                text_wrap =1,
                font_size=11
            ))
        self.worksheet_cfg.merge_range(0, 0, 0, 4, header, merge_format)

        header = "Information"
        self.worksheet_cfg.set_row(2, 40)
        self.worksheet_cfg.merge_range(2, 0, 2, 4, header, merge_format6)

        header = "Document  Title:"
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(3, 0, 3, 2, header, merge_format7)

        header =self.tp_id.split('-')[2]+'-'+'TP'
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(3, 3, 3, 4, header, merge_format7)

        header = "Document  Number:"
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(4, 0, 4, 2, header, merge_format7)

        header = self.tp_id
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(4, 3, 4, 4, header, merge_format7)

        header = "Date:"
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(5, 0, 5, 2, header, merge_format7)

        header = self.date
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(5, 3, 5, 4, header, merge_format7)

        header = "CONFIGURATION"
        # self.worksheet_cfg.set_row(1, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(6, 0, 6, 4, header, merge_format)



        header = "Document Approval"
        DocumentApproval_list=['Document \nApproval','Name','Title','Signature','Date']
        DocumentApproval_row=9

        # self.worksheet_cfg.set_row(3, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(DocumentApproval_row-1, 0, DocumentApproval_row-1, 4, header, merge_format3)
        for i in range(5):
            self.worksheet_cfg.write(addcolumn('A',i)+str(DocumentApproval_row+1), DocumentApproval_list[i],merge_format1)
        # self.worksheet_cfg.write('A10', 'Document \nApproval',merge_format1)
        # self.worksheet_cfg.write('B10', 'Name',merge_format1)
        # self.worksheet_cfg.write('C10', 'Title',merge_format1)
        # self.worksheet_cfg.write('D10', 'Signature',merge_format1)
        # self.worksheet_cfg.write('E10', 'Date',merge_format1)

        self.worksheet_cfg.write('A11', 'Prepared by',merge_format1)
        self.worksheet_cfg.write('A12', 'Checked by',merge_format1)
        self.worksheet_cfg.write('A13', 'Verified by',merge_format1)
        for i in range(13,19):
            self.worksheet_cfg.write(i, 0, 'Reviewed by',merge_format1)
        self.worksheet_cfg.write('A20', 'Approved by',merge_format1)

        revisionHistory_row=23

        header = "Revision History"
        revisionHistory_list=['Rev.','Author.','Change Description','VC Baseline','Release Date']
        # self.worksheet_cfg.set_row(17, self.default_row_height + 2)
        self.worksheet_cfg.merge_range(revisionHistory_row-1, 0, revisionHistory_row-1, 4, header, merge_format)

        for i in range(5):
            self.worksheet_cfg.write(addcolumn('A',i)+str(revisionHistory_row+1), revisionHistory_list[i],merge_format2)


        tp_revisionHistory=self.revisionHistory
        revisionHistory_length=len(tp_revisionHistory)


        for i in range(revisionHistory_length):
            TC_Baseline = 'C919-VC'+'-'+self.tp_id.split('-')[2]+' baseline '+tp_revisionHistory[i+1][0]
            tp_revisionHistory[i+1][3]=TC_Baseline


        for i in range(revisionHistory_length):
            for j in range(len(tp_revisionHistory[i+1])):
                self.worksheet_cfg.write(addcolumn('A',j)+str(revisionHistory_row+2+i),tp_revisionHistory[i+1][j],merge_format4) 
            
        # self.worksheet_cfg.write('A'+str(revisionHistory_high), header,merge_format4)
        # self.worksheet_cfg.write('B25', '2021/4/25',merge_format4)
        # self.worksheet_cfg.write('C25', 'Initial Creation',merge_format4)
        # value = 'C919-TC'+'-'+self.tp_id.split('-')[2]+' baseline A.1'
        # self.worksheet_cfg.write('D25', value, merge_format4)
        # self.worksheet_cfg.write('E25', '2021/4/25',merge_format4)

        # self.worksheet_cfg.write('A26', 'A.2',merge_format4)
        # self.worksheet_cfg.write('B26', '2021/7/15',merge_format4)
        # self.worksheet_cfg.write('C26', 'Updated by Review comments and Dry Run results',merge_format4)
        # value = 'C919-TC'+'-'+self.tp_id.split('-')[2]+' baseline A.2'
        # self.worksheet_cfg.write('D26', value, merge_format4)
        # self.worksheet_cfg.write('E26', '2021/7/15',merge_format4)

        # for i in range(revisionHistory_length):
            
        # value = 'C919-TC'+'-'+self.tp_id.split('-')[2]+' baseline A.1'
        # self.worksheet_cfg.write('D25', value, merge_format4)

        # value = 'C919-TC'+'-'+self.tp_id.split('-')[2]+' baseline A.2'
        # self.worksheet_cfg.write('D26', value, merge_format4)



        header = "Notice\nThis document and the information contained herein are the property of SAVIC. Any reproduction, disclosure or use thereof is prohibited except as authorized in writing by SAVIC.  Recipient accepts the responsibility for maintaining the confidentiality of the contents of this document.\n此文档和所涵盖的信息均属SAVIC所有。除经SAVIC书面授权外，禁止任何复制、披露或使用。接收者具有维护本文档内容的保密责任。"
        self.worksheet_cfg.merge_range(33, 0, 40, 4, header, merge_format5)


    def _writeTPHeader(self) -> None:
        for col, width in TPSheetCfg.sheet_column_width_mapper:
            self.worksheet.set_column(col, width)
        header = "Shanghai Aviation Electric Co., Ltd.\nC919 MODEL TEST Procedure SPECIFICATION"
        self.worksheet.set_row(self.row_ind, 32)
        merge_format = self.workbook.add_format(
            dict(
                self.common_format_obj,
                bold=1,
                align="center",
                valign="vcenter",
                font_size=TPSheetCfg.font_size,
            ))
        self.worksheet.merge_range(self.row_ind, 0, self.row_ind,
                                   self.max_column_ind, header, merge_format)
        self.row_ind += 1
        header = "TEST Procedure"
        self.worksheet.set_row(self.row_ind, self.default_row_height + 2)
        self.worksheet.merge_range(self.row_ind, 0, self.row_ind,
                                   self.max_column_ind, header, merge_format)
        self.row_ind += 1

    def _writeScriptHeader(self) -> None:
        cell_format = self.workbook.add_format(self.common_format_obj)
        header_format = self.workbook.add_format(
            dict(self.common_format_obj, bold=1))
        cell_values = [("SCRIPT NAME", self.tp_id), ("HEADER", None),
                       (None, "Display Aircraft Symbol"),
                       ("END OF HEADER", None)]
        for header, value in cell_values:
            self.worksheet.set_row(self.row_ind, self.default_row_height)
            self.worksheet.write(self.row_ind, 0, header, header_format)
            self.worksheet.merge_range(self.row_ind, 1, self.row_ind,
                                       self.max_column_ind, value, cell_format)
            self.row_ind += 1

        self.row_ind += 1  # add a blank row

    def _writeTestPrompt(self, tp_data: CaseBase) -> None:
        cell_format = self.workbook.add_format(
            dict(self.common_format_obj, valign="top"))

        # write start of TEST PROMPT
        header_format = self.workbook.add_format(
            dict(self.common_format_obj,
                 font_color="green",
                 bold=1,
                 valign="top"))
        description = tp_data.description
        max_length = len(description.split('\n')) if description else 1
        self.worksheet.set_row(self.row_ind,
                               self.default_row_height * max_length)
        self.worksheet.write(self.row_ind, 0, "START OF TEST PROMPT",
                             header_format)
        self.worksheet.write(self.row_ind, 1, "TESTING:", cell_format)
        self.worksheet.write(self.row_ind, 2, description, cell_format)
        self.row_ind += 2

        # write main body
        cell_values = [("REQUIREMENTS TESTED:",
                        "\n".join(tp_data.requirement_id)), (None, None),
                       ("ACTION:", None), (None, None), ("ENSURE:", None)]
        for key, value in cell_values:
            max_length = len(value.split('\n')) if value else 1
            self.worksheet.set_row(self.row_ind,
                                   self.default_row_height * max_length)
            self.worksheet.write(self.row_ind, 1, key, cell_format)
            self.worksheet.write(self.row_ind, 2, value, cell_format)
            self.row_ind += 1

        # write end of TEST PROMPT
        header_format = self.workbook.add_format(
            dict(self.common_format_obj,
                 font_color="green",
                 bold=1,
                 valign="bottom"))
        self.worksheet.set_row(self.row_ind, self.default_row_height)
        self.worksheet.write(self.row_ind, 0, "END OF TEST PROMPT",
                             header_format)
        self.row_ind += 2  # add a blank row

    def _writeTestScript(self, tp_data: CaseBase) -> None:
        header_format = self.workbook.add_format(
            dict(self.common_format_obj, font_color="blue", bold=1))

        # write start of TEST SCRIPT
        self.worksheet.set_row(self.row_ind, self.default_row_height)
        self.worksheet.write(self.row_ind, 0, "START OF TEST SCRIPT",
                             header_format)
        self.row_ind += 1

        # write condition
        cell_format = self.workbook.add_format(
            dict(self.common_format_obj, text_wrap=0))
        detail_steps = tp_data.detail_steps
        rows_values = []
        for c in detail_steps:
            if c.step_key in [StepKey.ramp, StepKey.set]:
                try:
                    results = QueryBuilder(
                        step=c,
                        func_allo=tp_data.function_allocation,
                        site=tp_data.verification_site).query()
                except Exception as e:
                    self.error_flag = True
                    if config.DEBUG:
                        logger.exception(e)
                    else:
                        logger.error(f"[{tp_data.case_id}]:{e!s}")
                    continue
                for result in results:
                    for name, value in result.items():
                        logger.debug(name, value)
                        if isinstance(value, list):
                            rows_values.append(
                                [str(StepKey.ramp), name, "STEP", *value])
                        else:
                            rows_values.append([str(StepKey.set), name, value])
            else:
                for content in c.contents:
                    if c.step_key in [StepKey.action, StepKey.wait]:
                        rows_values.append([str(c.step_key), content])
        i = 1
        for row_values in rows_values:
            self.worksheet.set_row(self.row_ind, self.default_row_height)
            self.worksheet.write(self.row_ind, 0, i, header_format)
            self.worksheet.write_row(self.row_ind, 1, row_values, cell_format)
            i += 1
            self.row_ind += 1

        # write result
        cell_format = self.workbook.add_format(dict(self.common_format_obj))
        result = tp_data.expected_result
        for key, value in result:
            if value is None:
                continue
            self.worksheet.set_row(self.row_ind,
                                   self.default_row_height * (len(value) + 1))
            self.worksheet.write(self.row_ind, 0, i, header_format)
            self.worksheet.write(self.row_ind, 1, key, cell_format)
            self.worksheet.write(self.row_ind, 2, "\n".join(value),
                                 cell_format)
            i += 1
            self.row_ind += 1

        # write end of TEST SCRIPT
        self.worksheet.set_row(self.row_ind, self.default_row_height)
        self.worksheet.write(self.row_ind, 0, "END OF TEST SCRIPT",
                             header_format)
        self.row_ind += 1

    def _writeTestCase(self) -> None:
        header_format = self.workbook.add_format(
            dict(self.common_format_obj, font_color="red", bold=1))
        cell_format = self.workbook.add_format(self.common_format_obj)
        for tp_data in self.tp_datas:
            self.worksheet.set_row(self.row_ind, self.default_row_height)
            self.worksheet.write(self.row_ind, 0, "START OF TEST CASE",
                                 header_format)
            self.worksheet.write(self.row_ind, 1, tp_data.case_id, cell_format)
            self.row_ind += 1
            self._writeTestPrompt(tp_data)
            self._writeTestScript(tp_data)
            self.worksheet.set_row(self.row_ind, self.default_row_height)
            self.worksheet.write(self.row_ind, 0, "END OF TEST CASE",
                                 header_format)
            self.row_ind += 2  # there is a blank row between the TEST CASES

    def _writeEndAll(self) -> None:
        header_format = self.workbook.add_format(
            dict(self.common_format_obj, bold=1))
        self.worksheet.set_row(self.row_ind, self.default_row_height)
        self.worksheet.write(self.row_ind, 0, "END OF ALL TESTS",
                             header_format)

    def write(self) -> None:
        self._writeconfiguration()
        self._writeTPHeader()
        self._writeScriptHeader()
        self._writeTestCase()
        self._writeEndAll()
        if not self.error_flag:
            logger.info(f"======{self.tp_id} Write Successfully!======")
            self.workbook.close()
