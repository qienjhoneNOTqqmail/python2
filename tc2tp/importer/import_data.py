import re
from pathlib import Path
from typing import Any, Dict, List

import xlrd
from pymongo.database import Database
from tc2tp.common import mongo_db
from tc2tp.common.logger import logger
from tc2tp.utils import toStr


class Data2DB:
    """data importer base class"""
    def __init__(
        self,
        work_path: str,
        db: Database = mongo_db,
        name: str = "",
    ) -> None:
        self.work_path = Path(work_path)
        self.name = name
        self.db = db
        self.collection_name_list = [name]
        self.error = False

    def getAllFiles(self) -> list:
        """get all files need to process"""
        return list(self.work_path.rglob("*.xlsx"))

    def processFile(self, file_path: Path) -> None:
        """import one file"""
        pass

    def processAllFiles(self) -> None:
        file_path_list = self.getAllFiles()
        if not file_path_list:
            self.error = True
            logger.error(f"Please check work path {self.work_path}!")
        for file_path in file_path_list:
            self.processFile(file_path)
            logger.info(f"{file_path} over!")
        if self.error:
            logger.error(f"{self.name} data migration has done with error!")
        else:
            logger.info(f"{self.name} data migration has done!")

    def _dropCollection(self, collection_name: str) -> None:
        if collection_name in self.db.list_collection_names():
            self.db.drop_collection(collection_name)
            logger.info(
                f"{collection_name} collection has been deleted successfully!")

    def dropCollections(self) -> None:
        """drop data in db"""
        for collection_name in self.collection_name_list:
            self._dropCollection(collection_name)

    def rebuild(self) -> None:
        self.dropCollections()
        self.processAllFiles()


class ICD2DB(Data2DB):
    """import icd data to db"""
    def __init__(self,
                 work_path: str,
                 db: Database = mongo_db,
                 name: str = "ICD") -> None:
        super(ICD2DB, self).__init__(work_path, db, name)
        self.collection_name_list = [
            "Input664Messages", "Input664Signals", "Output664Messages",
            "Output664Signals", "Input825Messages", "Input825Signals",
            "Output825Messages", "Output825Signals", "Input429Messages",
            "Input429Signals", "Output429Messages", "Output429Signals"
        ]

    def processFile(self, file_path: Path) -> None:
        hf = file_path.stem.rstrip("-icd")
        data = xlrd.open_workbook(file_path)
        for collection_name in self.collection_name_list:
            collection = mongo_db[collection_name]
            table = data.sheet_by_name(collection_name)
            row_tag = table.row_values(0)
            record = {"origin": hf}
            for i in range(1, table.nrows):
                try:
                    collection.insert_one(
                        dict(zip(row_tag, table.row_values(i)), **record))
                except Exception:
                    self.error = True
                    logger.exception("Error!")


class DDIN2DB(Data2DB):
    """import dd-in data to db"""
    def __init__(self,
                 work_path: Path,
                 db: Database = mongo_db,
                 name: str = "DDIN") -> None:
        super(DDIN2DB, self).__init__(work_path, db, name)

    def getAllFiles(self) -> list:
        return list(self.work_path.rglob("*DD-IN*.xlsx"))

    def processFile(self, file_path: Path) -> None:
        data = xlrd.open_workbook(file_path)
        collection = self.db[self.collection_name_list[0]]
        table = data.sheet_by_index(0)
        row_tags = table.row_values(0)
        func_key = file_path.stem.split("-")[0]
        tag_mapper = self.getTagMapper(func_key, row_tags)
        for i in range(1, table.nrows):
            try:
                if tag_mapper.get("ID") is not None:
                    id_ = table.cell_value(i, tag_mapper.get("ID"))
                else:
                    id_ = table.cell_value(i, 0)
                input_param = self.normParam(
                    table.cell_value(i,
                                     tag_mapper.get("Input Logic Parameter")))
                if input_param == '' or input_param.startswith(
                        "[COM]") or input_param.startswith(
                            "DELETE") or input_param.startswith("Input"):
                    continue
                selection_criteria = table.cell_value(
                    i, tag_mapper.get("Selection Criteria"))
                rps = table.cell_value(i, tag_mapper.get("RP")).split('\n')
                dps = table.cell_value(i, tag_mapper.get("DP")).split('\n')
                rps_len, dps_len = len(rps), len(dps)
                if rps_len != dps_len:
                    if rps_len == 1:
                        rps = rps * dps_len
                    elif dps_len == 1:
                        dps = dps * rps_len
                    else:
                        raise Exception("RP and DP mismatch!")
                pilot_order = self.normSelectionOrderValue(
                    table.row_values(i), tag_mapper, 'pilot')
                copilot_order = self.normSelectionOrderValue(
                    table.row_values(i), tag_mapper, 'copilot')
                data = [{
                    "ID": id_,
                    "Input Logic Parameter": input_param,
                    "RP": rp.split('(')[0].strip(),
                    "Selection Criteria": selection_criteria,
                    "Selection Order of Pilot Side": pilot_order,
                    "Selection Order of Copilot Side": copilot_order,
                    "DP": dp.split('(')[0].strip(),
                    "origin": func_key
                } for dp, rp in zip(dps, rps)]
                collection.insert_many(data)
            except Exception:
                self.error = True
                logger.exception("Error!")

    def normParam(self, param: str):
        if "\n" in param:
            return param.split("\n")[0].strip()
        return param

    def getTagMapper(self, func_key: str, tags: List[str]) -> Dict[str, int]:
        tag_mapper = {tag: i for i, tag in enumerate(tags)}
        common_tag = [
            "ID", "Input Logic Parameter", "Selection Criteria", "RP", "DP"
        ]
        mapper = {tag: tag_mapper.get(tag) for tag in common_tag}
        if func_key in ['AUX']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order of IDU_LO"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order of IDU_RO"]
            })
        elif func_key in [
                'CNS', 'DMH', 'DMI', 'FDAS', 'IDU', 'INFO', 'SYN', 'VCP'
        ]:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order"]
            })
        elif func_key in ['EI']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order（all 5 IDUs）"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order（all 5 IDUs）"]
            })
        elif func_key in ['HSI']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order of pilot Side HSI"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order of Copilot Side HSI"]
            })
        elif func_key in ['HUD']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order of Captain Side HUD"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order of First Officer Side HUD"]
            })
        elif func_key in ['PFD']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order of Captain Side PFD"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order of First Officer Side PFD"]
            })
        elif func_key in ['MAP']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order of pilot Side MAP"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order of Copilot Side MAP"]
            })
        elif func_key in ['PIT']:
            mapper.update({
                "Selection Order of Pilot Side":
                tag_mapper["Selection Order(IDU_LI/IDU_LO/IDU_C)"],
                "Selection Order of Copilot Side":
                tag_mapper["Selection Order(IDU_RI/IDU_RO)"]
            })
        else:
            raise Exception(f"Can not identify the func_key {func_key}!")
        return mapper

    def normSelectionOrderValue(self, row: Any, tag_mapper: Dict[str, int],
                                flag: str) -> str:
        """deal with selection order value"""
        value = ""
        selection_criteria = row[tag_mapper.get("Selection Criteria")]
        single_source = ['single source', 'singlesource']
        lane_in_control = ['lane in control', 'lane-in-control', 'in-control']
        if flag == 'pilot':
            value = row[tag_mapper.get("Selection Order of Pilot Side")]
        elif flag == 'copilot':
            value = row[tag_mapper.get("Selection Order of Copilot Side")]
        if not isinstance(value, str):
            value = toStr(value)
        if value.lower() in single_source:
            value = 'single source'
        # 1(first valid)
        if tmp := re.match(r'(\d)\(.*\)', value):
            value = tmp.group(1)
        if (value.lower() in lane_in_control
                or selection_criteria.lower() in lane_in_control):
            value = 'lane in control'
        # IRS Manual Selection(IRS manual switch loop order 1)
        if tmp := re.search(r'.*IRS Manual Selection.*(\d)', value):
            value = str(int(tmp.group(1)) + 4)
        return value


class DDOUT2DB(Data2DB):
    """import dd-out data to db"""
    def __init__(self,
                 work_path: Path,
                 db: Database = mongo_db,
                 name: str = "DDOUT") -> None:
        super(DDOUT2DB, self).__init__(work_path, db, name)

    def getAllFiles(self) -> list:
        return list(self.work_path.rglob("*DD-OUT*.xlsx"))

    def processFile(self, file_path: Path) -> None:
        data = xlrd.open_workbook(file_path)
        collection = self.db[self.collection_name_list[0]]
        table = data.sheet_by_index(0)
        row_tag = table.row_values(0)
        op = "Output Logic Parameter"
        tag_mapper = {}
        for i, tag in enumerate(row_tag):
            if tag == "Output Logic Parameters":
                row_tag[i] = op
                tag_mapper[op] = i
            elif tag in ('', "Object Text") and op not in row_tag:
                row_tag[i] = op
                tag_mapper[op] = i
            else:
                tag_mapper[tag] = i
        for i in range(1, table.nrows):
            try:
                param = table.cell_value(i, tag_mapper.get(op))
                if param.upper().startswith(("[COM]", "DELETE")):
                    continue
                collection.insert_one(dict(zip(row_tag, table.row_values(i))))
            except Exception:
                self.error = True
                logger.exception("Error!")


class ALIAS2DB(Data2DB):
    """import io data to db"""
    def __init__(self,
                 work_path: Path,
                 db: Database = mongo_db,
                 name: str = "ALIAS") -> None:
        super(ALIAS2DB, self).__init__(work_path, db, name)

    def getAllFiles(self) -> list:
        return list(self.work_path.rglob("*.cvt"))

    def processFile(self, file_path: Path) -> None:
        collection = self.db[self.collection_name_list[0]]
        collection.create_index("alias")
        pattern = re.compile(r'ALIAS = \"(.*?)\";')
        with file_path.open('r') as f:
            for line in f.readlines():
                res = re.search(pattern, line)
                if res is None:
                    continue
                res = res.group(1)
                collection.update_one({"alias": res},
                                      {"$setOnInsert": {
                                          "alias": res
                                      }}, True)


class INFOAlertICD2DB(Data2DB):
    """import info alert icd to dd-in db"""
    def __init__(self,
                 work_path: Path,
                 db: Database = mongo_db,
                 name: str = "DDIN") -> None:
        super().__init__(work_path, db, name)

    def getAllFiles(self) -> list:
        return list(self.work_path.rglob("*ICD*.xlsx"))

    def processFile(self, file_path: Path) -> None:
        data = xlrd.open_workbook(file_path)
        collection = self.db[self.collection_name_list[0]]
        table = data.sheet_by_index(0)
        row_tag = table.row_values(0)
        lane_in_control = [
            'lane in control', 'lane-in-control', 'in-control',
            "local channel in control"
        ]
        tag_mapper = {tag: i for i, tag in enumerate(row_tag)}
        for i in range(1, table.nrows):
            id_ = toStr(table.cell_value(i, tag_mapper['ID']))
            input_param = table.cell_value(i, tag_mapper['Parameter'])
            dp = table.cell_value(i, tag_mapper['Pubref'])
            need_ss = table.cell_value(
                i, tag_mapper['Source Selection']).lower() in ['y', 'yes']
            ss_order = table.cell_value(i, tag_mapper["S. Sel. Order"])
            if need_ss:
                if not isinstance(ss_order, str):
                    ss_order = toStr(ss_order)
                elif ss_order.lower() in lane_in_control:
                    ss_order = 'lane in control'
            else:
                ss_order = 'N/A'
            rp = table.cell_value(i, tag_mapper['RP Name'])
            data = {
                "ID": "INFO_Alert_" + id_,
                "Input Logic Parameter": input_param,
                "RP": rp.strip(),
                "Selection Criteria": '',
                "Selection Order of Pilot Side": ss_order,
                "Selection Order of Copilot Side": ss_order,
                "DP": dp.strip(),
                "origin": "INFO_DB"
            }
            collection.insert_one(data)

    def rebuild(self):
        self.processAllFiles()


class FDASAlertICD2DB(Data2DB):
    """import fdas alert icd to dd-in db"""
    def __init__(self,
                 work_path: Path,
                 db: Database = mongo_db,
                 name: str = "DDIN") -> None:
        super().__init__(work_path, db, name)

    def getAllFiles(self) -> list:
        return list(self.work_path.rglob("*ICD*.xlsx"))

    def processFile(self, file_path: Path) -> None:
        data = xlrd.open_workbook(file_path)
        collection = self.db[self.collection_name_list[0]]
        table = data.sheet_by_index(0)
        row_tag = table.row_values(0)
        lane_in_control = [
            'lane in control', 'lane-in-control', 'in-control',
            "local channel in control"
        ]

        tag_mapper = {self.changeTag(tag): i for i, tag in enumerate(row_tag)}
        if "Parameter" not in tag_mapper:
            logger.error(f"{file_path!s} does not have Parameter!")
            return
        for i in range(1, table.nrows):
            input_param = table.cell_value(i, tag_mapper['Parameter'])
            if input_param == 'DELETE':
                continue
            dp = table.cell_value(i, tag_mapper['Pubref'])
            try:
                need_ss = table.cell_value(
                    i, tag_mapper['Source Selection']).lower() in ['y', 'yes']
            except KeyError:
                need_ss = True
            ss_order = table.cell_value(i, tag_mapper["S. Sel. Order"])
            if need_ss:
                if not isinstance(ss_order, str):
                    ss_order = toStr(ss_order)
                elif ss_order.lower() in lane_in_control:
                    ss_order = 'lane in control'
            else:
                ss_order = 'N/A'
            rp = table.cell_value(i, tag_mapper['RP Name'])
            data = {
                "ID": f"FDAS_Alert_{i}",
                "Input Logic Parameter": input_param,
                "RP": rp.strip(),
                "Selection Criteria": '',
                "Selection Order of Pilot Side": ss_order,
                "Selection Order of Copilot Side": ss_order,
                "DP": dp.strip(),
                "origin": "FDAS_DB"
            }
            collection.insert_one(data)

    def changeTag(self, tag: str) -> str:
        if tag == "Logic Statements Parameter Alias":
            return "Parameter"
        if tag == "ICD Unique Parameter Name (as defined by parameter publisher)":
            return "Pubref"
        return tag

    def rebuild(self):
        self.processAllFiles()
