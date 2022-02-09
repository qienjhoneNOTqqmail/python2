import re
from collections import defaultdict
from pathlib import Path
from typing import List

import xlrd

from tc2tp.common.constant import CaseIndex as CI
from tc2tp.common.custom_error import (CustomError, IncorrectError,
                                       MismatchError, NullValueError)
from tc2tp.common.logger import logger
import datetime

def changePythonDate(dates):
    if type(dates) == float or type(dates) == int:
        delta=datetime.timedelta(days=dates)
        today=datetime.datetime.strptime('1899-12-30','%Y-%m-%d')+delta
        return datetime.datetime.strftime(today,'%#Y/%#m/%#d')
    elif type(dates) == str :
        return dates

class ConfigurationReader:
    def __init__(self, file_path: str = None, sheet_name: str = None):
        self.file_path = None
        self.sheet_name = None
        self.workbook = None
        self.worksheet = None
        if file_path:
            self.loadFile(file_path, sheet_name)
        self.date= None
        self.revisionHistory = defaultdict(list)
        
    def loadFile(self, file_path: str, sheet_name: str = None):
        self.file_path = Path(file_path)
        self.workbook = xlrd.open_workbook(self.file_path.resolve())
        self.changTo(sheet_name)

    def changTo(self, sheet_name: str = None):
        if sheet_name is not None:
            self.sheet_name = sheet_name
            self.worksheet = self.workbook.sheet_by_name(self.sheet_name)
        else:
            self.worksheet = self.workbook.sheet_by_index(0)
            self.sheet_name = self.worksheet.name

    def read(self):
        Date_row=-1
        for i in range(1, self.worksheet.nrows):
            header = self.worksheet.row_values(i)
            if header[0]=="Date:":
                Date_row=i
                break

        if Date_row!=-1:
            date_format=changePythonDate(self.worksheet.row_values(Date_row)[3])
            self.date = date_format
        else:
            self.date = None
            logger.info(f"Don't find Date in information")

        RevisionHistory_row=-1
        j=1
        for i in range(1, self.worksheet.nrows):
            header = self.worksheet.row_values(i)
            if header[0]=="Revision History":
                RevisionHistory_row=i
                break
        if RevisionHistory_row!=-1:
            for i in range(RevisionHistory_row+2, RevisionHistory_row+11):
                row = self.worksheet.row_values(i)
            
                if row == ['', '', '', '', '']:
                    break
                
                self.revisionHistory[j]=row
                self.revisionHistory[j][1]=changePythonDate(row[1])
                self.revisionHistory[j][4]=changePythonDate(row[4])
                j+=1
        else:
            self.revisionHistory = defaultdict(list)


class CaseReader:
    def __init__(self, file_path: str = None, sheet_name: str = None):
        self.file_path = None
        self.sheet_name = None
        self.workbook = None
        self.worksheet = None
        self.count = 0
        if file_path:
            self.loadFile(file_path, sheet_name)
        self.tc = defaultdict(list)
        self.ss = defaultdict(list)
        self.mcdc = defaultdict(list)
        self.ac = defaultdict(list)
        self.rc = defaultdict(list)
        self.ic = defaultdict(list)

    def loadFile(self, file_path: str, sheet_name: str = None):
        self.file_path = Path(file_path)
        self.workbook = xlrd.open_workbook(self.file_path.resolve())
        self.changTo(sheet_name)

    def changTo(self, sheet_name: str = None):
        if sheet_name is not None:
            self.sheet_name = sheet_name
            self.worksheet = self.workbook.sheet_by_name(self.sheet_name)
        else:
            self.worksheet = self.workbook.sheet_by_index(0)
            self.sheet_name = self.worksheet.name

    @property
    def attrs(self):
        return self.worksheet.row_values(0)

    def read(self):
        if self.worksheet is None:
            logger.error(f"{self.file_path}: No worksheet loaded")
            return
        ac_count = rc_count = ic_count = ss_count = tc_count = 0
        for i in range(1, self.worksheet.nrows):
            row = self.worksheet.row_values(i)
            try:
                row = list(map(lambda x: str(x).strip(), row))
                key = self._checkRow(row)
            except CustomError as e:
                logger.error(f"ROW[{row[CI.Case_ID.value]}]: {e.msg}")
                continue
            if key == "PASS":
                continue
            procedure_id = row[CI.Verification_Procedure_ID.value]
            if key == "AC":
                self.ac[procedure_id].append(row)
                ac_count += 1
            elif key == "RC":
                self.rc[procedure_id].append(row)
                rc_count += 1
            elif key == "IC":
                self.ic[procedure_id].append(row)
                ic_count += 1
            elif key == "SS":
                self.ss[procedure_id].append(row)
                ss_count += 1
            elif key == "MCDC":
                self.mcdc[procedure_id].append(row)
            elif key == "TC":
                self.tc[procedure_id].append(row)
                tc_count += 1
            else:
                raise CustomError(f"Unknown key {key}")
        tc_msg = f"Test Case: {tc_count};"
        ss_msg = f"Source Selection Case: {ss_count};"
        ac_msg = f"Analysis Case: {ac_count};"
        rc_msg = f"Review Case: {rc_count};"
        ic_msg = f"Inspection Case: {ic_count};"
        logger.info(
            f"Case data has been loaded!\n{tc_msg} {ss_msg} {ac_msg} {rc_msg} {ic_msg}"
        )

    @staticmethod
    def _checkRow(row: List[str]) -> str:
        case_id = row[CI.Case_ID.value]
        procedure_id = row[CI.Verification_Procedure_ID.value]
        description = row[CI.Description.value].replace(" ", "")
        description = description.replace("（", "(").replace("）", ")")
        detail_steps = row[CI.Detail_Steps.value]
        if case_id in ("N/A", "") or description in ("DELETE", ):
            return "PASS"
        case_pattern = re.compile(r"C919-(TC|AC|IC|RC)-(\w+)-S\d+(-\d+)?")
        procedure_pattern = re.compile(r"C919-(TP|IP|AP|RP)-(\w+)-S\d+")
        case_res = case_pattern.match(case_id)
        procedure_res = procedure_pattern.match(procedure_id)
        if not case_res:
            raise IncorrectError(f"Incorrect Case ID {case_id!r}")
        if not procedure_res:
            raise IncorrectError(f"Incorrect Procedure ID {procedure_id!r}")
        if (case_res.group(1)[:1] != procedure_res.group(1)[:1]
                or case_res.group(2) != procedure_res.group(2)):
            raise MismatchError(f"{case_id!r} and {procedure_id!r} mismatched")
        for index in (CI.Requirement_ID, CI.Verification_Method,
                      CI.Detail_Steps, CI.Expected_Result,
                      CI.Function_Allocation):
            if row[index.value] == "":
                raise NullValueError(
                    f"{index.name.replace('_', ' ')!r} is null value")
        if re.match(r"verify<?(.*?)>?sourceselection(?:\((.*?)\))?",
                    description, re.IGNORECASE):
            return "SS"
        if "mcdc set" in detail_steps.lower():
            return "MCDC"
        return case_res.group(1)


if __name__ == "__main__":
    import sys
    reader = CaseReader(sys.argv[1], "Test Case")
    reader.read()
    logger.debug(f"Test Case:\n{reader.tc!r}")
    logger.debug(f"Source Selection:\n{reader.ss!r}")
    logger.debug(f"MCDC:\n{reader.mcdc!r}")
    logger.debug(f"Inspection Case:\n{reader.ic!r}")
    logger.debug(f"Review Case:\n{reader.rc!r}")
    logger.debug(f"Analysis Case:\n{reader.ac!r}")
