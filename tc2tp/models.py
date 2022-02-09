import re
from collections import defaultdict
from enum import Enum
from typing import Any, DefaultDict, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validate_arguments, validator

from tc2tp.common.custom_error import MismatchError
from tc2tp.common.logger import logger
from tc2tp.utils import str2num, upperKeyWord


class StepKey(str, Enum):
    set = "SET"
    ramp = "RAMP"
    wait = "WAIT"
    action = "ACTION"
    comment = "COMMENT"

    def __str__(self) -> str:
        return self.value


class VMethod(str, Enum):
    test = "Test"
    inspection = "Inspection"
    review = "Review"
    analysis = "Analysis"

    def __str__(self) -> str:
        return self.value


class TestType(str, Enum):
    test = "Test Procedure"
    inspection = "Inspection Checklist"
    review = "Review Comments"
    analysis = "Analysis Report"

    def __str__(self) -> str:
        return self.value


class VCaseApprovalStatus(str, Enum):
    develope = "Development"
    in_review = "In Review"
    on_hold = "On Hold"
    open_pr = "Open PR"
    verified = "Verified"

    def __str__(self) -> str:
        return self.value


class VSite(str, Enum):
    aircraft = "Aircraft"
    comac_sivb = "COMAC SIVB"
    aviage_sivb = "AVIAGE SIVB"
    iron_bird = "Iron Bird"
    savic_ssdl = "SAVIC SSDL"
    savic_sdib = "SAVIC SDIB"
    savic_cptd = "SAVIC CPTD"
    savic_isistd = "SAVIC ISISTD"
    unknown = "N/A"

    def __str__(self) -> str:
        return self.value


class VStatus(str, Enum):
    develope = "Development"
    dry_run = "Dry Run"
    in_review = "In Review"
    ready_for_trr = "Ready for TRR"
    for_credit = "For Credit"
    on_hold = "On Hold"
    open_pr = "Open PR"
    passed = "Passed"
    failed = "Failed"

    def __str__(self) -> str:
        return self.value


class CoverageAnalysis(str, Enum):
    in_work = "In Work"
    in_review = "In Review"
    complete = "Complete"

    def __str__(self) -> str:
        return self.value


# class FuncKeyEnum(str, Enum):
#     DMH = "DMH"
#     DMI = "DMI"


class ParamNodeBase(BaseModel):
    param_name: str
    rp: Optional[str] = None
    hf: Optional[str] = None
    value: Any
    validity: Dict[str, int]

    def __str__(self) -> str:
        ext_l = []
        if self.rp:
            ext_l.append(f"RP: {self.rp}")
        if self.hf:
            ext_l.append(f"HF: {self.hf}")
        ext_str = f"({', '.join(ext_l)})" if ext_l else ""
        value_str = f"{self.value} and " if self.value is not None else ""
        validity_str = "valid" if self.validity.get(
            "if_valid") == 1 else "invalid"
        fsb = self.validity.get("FSB")
        ssm = self.validity.get("SSM")
        if fsb is not None and ssm is not None:
            validity_str += f"(FSB:{fsb}, SSM:{ssm})"
        elif fsb is not None:
            validity_str += f"(FSB:{fsb})"
        elif ssm is not None:
            validity_str += f"(SSM:{ssm})"
        return f"{self.param_name}{ext_str} = {value_str}{validity_str}"


class StepBase(BaseModel):
    step_key: StepKey = StepKey.action
    contents: List[Union[str, ParamNodeBase]]

    def __str__(self) -> str:
        content_str = f"{self.step_key!s}:\n"
        if self.step_key in [StepKey.set, StepKey.ramp]:
            content_str += "\n-AND-\n".join(map(str, self.contents))
        else:
            content_str += "\n".join(map(str, self.contents))
        return content_str


class ExpectedResultBase(BaseModel):
    verify: List[str]
    check: Optional[List[str]] = None

    def __str__(self) -> str:
        check_str = ""
        if self.check is not None:
            check_str = '\n'.join(self.check)
            check_str = "\nCheck:\n" + check_str
        verify_str = '\n'.join(self.verify)
        return f"Verify:\n{verify_str}{check_str}"


class CaseBase(BaseModel):
    case_id: str = Field(...)
    description: Optional[str] = None
    requirement_id: List[str] = Field(...)
    verification_method: VMethod = VMethod.test
    detail_steps: List[StepBase] = Field(...)
    expected_result: ExpectedResultBase = Field(...)
    function_allocation: List[str] = Field(...)
    test_type: TestType = TestType.test
    verification_procedure_id: str = Field(...)
    verification_case_approval_status: VCaseApprovalStatus = VCaseApprovalStatus.develope
    verification_site: VSite = VSite.savic_ssdl
    verification_status: VStatus = VStatus.develope
    coverage_analysis: CoverageAnalysis = CoverageAnalysis.in_work

    @validator("case_id", pre=True)
    def check_case_id(cls, v):
        pattern = re.compile(r"(.*-S)(\d+)(?:-(\d+))?")
        res = pattern.search(v)
        ind = int(res.group(2))
        case_id = f"{res.group(1)}{ind:03}"
        if res.group(3):
            case_id += f"-{int(res.group(3)):03}"
        return case_id

    # @validator("verification_procedure_id", pre=True)
    # def check_verification_procedure_id(cls, v):
    #     pattern = re.compile(r"(.*-S)(\d+)")
    #     res = pattern.search(v)
    #     ind = int(res.group(2))
    #     tp_id = f"{res.group(1)}{ind:04}"
    #     return tp_id

    @validator("requirement_id", "function_allocation", pre=True)
    def check_req_id_and_func_allocation(cls, v):
        if isinstance(v, str):
            return list(
                filter(lambda x: x, map(lambda x: x.strip(), v.split("\n"))))
        return v

    @validator("verification_case_approval_status", pre=True)
    def check_verification_case_approval_status(cls, v):
        if not v:
            return VCaseApprovalStatus.develope
        return v

    @validator("verification_site", pre=True)
    def check_verification_site(cls, v):
        if not v:
            return VSite.savic_ssdl
        return v

    @validator("verification_status", pre=True)
    def check_verification_status(cls, v):
        if not v:
            return VStatus.develope
        return v

    @validator("coverage_analysis", pre=True)
    def check_coverage_analysis(cls, v):
        if not v:
            return CoverageAnalysis.in_work
        return v

    @validator("test_type", pre=True)
    def check_test_type(cls, v):
        if not v:
            return TestType(str(cls.verification_method))
        return v


class ExpectedResultParser:
    @validate_arguments
    def __init__(self, expected_result: str) -> None:
        self.expected_result = expected_result
        self.result = [defaultdict(list)]

    def parse(self) -> List[DefaultDict[str, List[str]]]:
        splited_result = list(
            filter(lambda x: x,
                   map(lambda x: x.strip(), self.expected_result.split('\n'))))
        if splited_result and upperKeyWord(splited_result[0]) == "VERIFY":
            splited_result = splited_result[1:]

        key = "verify"
        for row in splited_result:
            if upperKeyWord(row) == "VERIFY":
                self.result.append(defaultdict(list))
                key = "verify"
            elif upperKeyWord(row) == "CHECK":
                key = "check"
            else:
                self.result[-1][key].append(row)
        return self.result


class DetailStepsParser:
    @validate_arguments
    def __init__(self, detail_steps: str) -> None:
        self.detail_steps = detail_steps
        self.result = None

    def parse(self):
        data = self._init(self.detail_steps)
        result = [[]]
        for key, values in data:
            step_list = self._parseStep(key=key, values=values)
            logger.debug(step_list)
            if key == StepKey.set:
                origin = result[:]
                result = []
                for res in step_list:
                    result += [
                        c + [StepBase(step_key=key, contents=res)]
                        for c in origin
                    ]
            else:
                result = [
                    r + [StepBase(step_key=key, contents=step_list)]
                    for r in result
                ]
        self.result = result
        return result

    def _init(self, detail_steps: str):
        result = []
        splited_steps = list(
            filter(lambda x: x.strip(), detail_steps.split("\n")))
        if splited_steps and upperKeyWord(
                splited_steps[0]) not in StepKey.__dict__.values():
            result.append([StepKey.action, []])
        for step in splited_steps:
            if (key := upperKeyWord(step)) in StepKey.__dict__.values():
                result.append([StepKey(key), []])
            else:
                result[-1][1].append(step)
        return result

    def _parseStep(self, key: str, values: List[str]) -> List:
        if values is None:
            return
        if key == StepKey.set:
            return self._parseSet(values)
        elif key == StepKey.ramp:
            return self._parseRamp(values)
        elif key == StepKey.wait:
            return self._parseWait(values)
        elif key == StepKey.action:
            return self._parseAction(values)
        else:
            return self._parseOther(values)

    def _parseOther(self, values: List[str]):
        return list(map(lambda x: x.strip(), values))

    def _parseAction(self, values: List[str]):
        result = []
        pattern = re.compile(r'\s*(\d+)')
        if values and pattern.match(values[0]):
            for content in values:
                if pattern.match(content):
                    result.append(content.strip())
                else:
                    result[-1] += "\n" + content
        else:
            result = list(map(lambda x: x.strip(), values))
        return result

    def _parseWait(self, values: List[str]):
        result = []
        pattern = re.compile(r"(\d+(?:\.?\d+)?)(\w+)?")
        for content in values:
            content = content.replace(' ', '')
            res = pattern.match(content)
            if res is None:
                raise MismatchError(f"{content!r} can not be parsed!")
            weight = 1
            if (unit := res.group(2)) is not None:
                if unit.lower() in ["m", "minutes", "minute", "min"]:
                    weight = 60
                elif unit.lower() in ["h", "hour", "hours"]:
                    weight = 60 * 60
            result.append(str2num(res.group(1)) * weight)
        return result

    def _parseSet(self, values: List[str]):
        results = []
        result = [[]]
        for value in values:
            value = value.strip()
            if value.upper() == "-AND-":
                continue
            elif value.upper() == "-OR-":
                results += result
                result = [[]]
            else:
                param_data = self._parseParamData(string=value)
                value = param_data.get("value")
                if isinstance(value, list):
                    origin = result[:]
                    result = []
                    for v in value:
                        new_node = ParamNodeBase(**dict(param_data, value=v))
                        tmp = [c + [new_node] for c in origin]
                        result += tmp
                else:
                    result = [
                        r + [ParamNodeBase(**param_data)] for r in result
                    ]
        results += result
        return results

    def _parseRamp(self, values: List[str]):
        result = []
        for value in values:
            param_data = self._parseParamData(string=value,
                                              step_key=StepKey.ramp)
            value = param_data.get("value")
            if isinstance(value, dict) or (isinstance(value, list)
                                           and len(value) == 4):
                result.append(ParamNodeBase(**param_data))
            else:
                raise MismatchError(
                    f"{value!r} does not meet the rules, it shall look like '[start, end, step, freq]'"
                )
        return result

    def _parseValueAndValid(self, string: str, step_key: StepKey):
        value_data = list(map(lambda x: x and x.strip(),
                              string.split(" and ")))
        value = None
        logger.debug(value_data)
        if len(value_data) == 1:
            if "valid" not in value_data[0].lower():
                value = self._formatValue(value_data[0], step_key)
                validity = {"if_valid": 1}
            else:
                validity = self._parseValid(value_data[0])
        elif len(value_data) == 2:
            value = self._formatValue(value_data[0], step_key)
            validity = self._parseValid(value_data[1])
        else:
            raise MismatchError(f"{value_data} Error")
        return {"value": value, "validity": validity}

    def _parseParamData(self,
                        string: str,
                        step_key: StepKey = StepKey.set) -> Dict:
        if string is None:
            return
        s = string.replace("，", ",").replace("：", ":")
        s = s.replace("（", "(").replace("）", ")")
        s = s.replace("【", "[").replace("】", "]")
        pattern = re.compile(
            # r".*?([\[\]\/\w]*)\s*(?:\((?:RP:(.*?))?\))?\s*=\s*(.*)",
            r".*?([\[\]\/\w]*)\s*(?:\((.*?)\))?\s*=\s*(.*)",
            re.IGNORECASE)
        res = pattern.search(s)
        if res is None:
            raise MismatchError(f"{string!r} does not meet the rules!")
        param_name = res.group(1)
        ext = res.group(2)
        ext = ext and ext.replace(" ", "") or ""
        logger.debug(ext)
        rp, hf = None, None
        for d in ext.split(","):
            if not d:
                continue
            try:
                k, v = d.split(":")
            except ValueError:
                raise MismatchError(f"{string!r} does not meet the rules!")
            if k.upper() == "RP":
                rp = v
            if k.upper() == "HF":
                hf = v
        try:
            data = self._parseValueAndValid(res.group(3), step_key)
        except MismatchError as e:
            raise MismatchError(
                f"{string!r} does not meet the rules! From {e!s}")
        return {"param_name": param_name, "rp": rp, "hf": hf, **data}

    def _parseValid(self, valid_string: str) -> Dict[str, int]:
        validity = {}
        pattern = re.compile(r"^(valid|invalid)(?:\((.*)\))?", re.IGNORECASE)
        res = pattern.search(valid_string)
        if res is None:
            raise MismatchError()
        validity["if_valid"] = 1 if res.group(1).lower() == "valid" else 0
        fsb_ssm = res.group(2)
        if fsb_ssm is None:
            return validity
        if fsb_ssm.isdigit():
            validity["FSB"] = int(fsb_ssm)
            return validity
        data = fsb_ssm.split(",")
        for d in data:
            try:
                k, v = d.replace(" ", "").split(":")
                validity[k.upper()] = int(v)
            except ValueError:
                raise MismatchError()
        logger.debug(validity)
        return validity

    def _formatValue(self,
                     value_string: str,
                     step_key: StepKey = StepKey.set) -> Any:
        value_string = value_string.replace(" ", "")
        value_string = value_string.replace("\"", "").replace("\'", "")
        if res := re.match(r"\{(.*)\}", value_string):
            data = {}
            flag = False
            items = re.findall(r"(\w+:(?:-?\d+\.?\d*|\[.*?\]))", res.group(1))
            # items = re.findall(r"(\w+:(?:[^\[\]]+|\[.*?\]))", res.group(1))
            if not items:
                raise MismatchError(f"{value_string} is incorrect")
            for item in items:
                k, v = item.split(":")
                data[k] = self._formatValue(v)
                if isinstance(data[k], list) and step_key == StepKey.set:
                    flag = True
            if flag:
                data = [{k: v
                         for k, v in zip(data.keys(), values)}
                        for values in zip(*data.values())]
            logger.debug(data)
            return data
        if "," in value_string:
            data = []
            for v in value_string.strip("[]").split(","):
                if not v:
                    continue
                data.append(self._formatValue(v))
            logger.debug(data)
            return data
        return str2num(value_string)
