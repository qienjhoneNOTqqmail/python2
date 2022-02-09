import re
from collections import defaultdict
from typing import DefaultDict, Dict, List, Tuple

from tc2tp.common.config import config
from tc2tp.common.constant import CaseIndex as CI
from tc2tp.common.custom_error import (CustomError, InvalidParamError,
                                       MismatchError, NotFoundError)
from tc2tp.common.logger import logger
from tc2tp.models import (CaseBase, DetailStepsParser, ExpectedResultParser,
                          ParamNodeBase, StepKey)
from tc2tp.query_builder.query import getFuncPos, getInputParamDP


class SSDetailStepsParser(DetailStepsParser):
    def __init__(self, detail_steps: str, func_allo: str, target_param: str,
                 side: str):
        super().__init__(detail_steps)
        self.func_keys = list(
            filter(lambda x: x, map(lambda x: x.strip(),
                                    func_allo.split("\n"))))
        self.target_param = target_param
        self.side = side

    def _judgeSelectionOrder(self, selection_order: str) -> int:
        """
        @ret: 0: lane in control
            -1: ignored sources
            1-9: selection order
        """
        if selection_order.isdigit():
            return int(selection_order)
        elif selection_order == "lane in control":
            return 0
        else:
            return -1

    def getSelectionOrder(self) -> DefaultDict[int, List[List]]:
        func_pos = getFuncPos(self.func_keys, deep=False)
        data = getInputParamDP(logic_param=self.target_param,
                               func_pos=func_pos)
        if not data:
            msg = f"[{self.target_param}]: Can't find in {func_pos!r} DDIN!"
            raise NotFoundError(msg)
        sources = defaultdict(list)
        for dd in data:
            if self.side == "pilot":
                order = dd.get("Selection Order of Pilot Side")
            else:
                order = dd.get("Selection Order of Copilot Side")
            order_type = self._judgeSelectionOrder(order)
            if order_type > -1:
                sources[order_type].append(dd)
        logger.debug(sources)
        return sources

    def _regenSubSET(self, param_data: Dict,
                     selection_order: DefaultDict[int, List[List]],
                     result: List) -> List[List[ParamNodeBase]]:
        valid_value = param_data.get("value")
        invalid_value = param_data.get("invalid_value") or valid_value
        param_name = param_data.get("param_name")
        validity = param_data.get("validity")
        invalidity = param_data.get("invalidity") or {
            "if_valid": 1 - validity.get("if_valid")
        }
        value_length = len(valid_value)
        if value_length != len(invalid_value):
            raise MismatchError(
                "The number of valid values doesn't match the number of invalid values!"
            )
        source_length = len(selection_order)
        subs = [result[0][:] for _ in range(value_length)]
        msg = "The number of target parameter values doesn't match the number of sources!"
        if 0 in selection_order:  # lane in control
            sources = selection_order[0]
            if value_length != len(sources):
                raise MismatchError(msg)
            logger.debug(value_length)
            for i in range(value_length):
                rp = sources[i]["RP"]
                valid_v = valid_value[i]
                invalid_v = invalid_value[i]
                for j in range(value_length):
                    if j != i:  # update validity to invalid
                        new_node = ParamNodeBase(param_name=param_name,
                                                 value=invalid_v,
                                                 rp=rp,
                                                 validity=invalidity)
                    else:
                        new_node = ParamNodeBase(param_name=param_name,
                                                 value=valid_v,
                                                 rp=rp,
                                                 validity=validity)
                    subs[j].append(new_node)
            return subs

        if value_length != source_length:
            raise MismatchError(msg)
        for i in range(value_length):
            rps = {x["RP"] for x in selection_order[i + 1]}
            valid_v = valid_value[i]
            invalid_v = invalid_value[i]
            for j in range(value_length):
                if j > i:  # update validity to invalid
                    subs[j].extend([
                        ParamNodeBase(param_name=param_name,
                                      value=invalid_v,
                                      rp=rp,
                                      validity=invalidity) for rp in rps
                    ])
                else:
                    subs[j].extend([
                        ParamNodeBase(param_name=param_name,
                                      value=valid_v,
                                      rp=rp,
                                      validity=validity) for rp in rps
                    ])
        logger.debug(subs)
        return subs

    def _parseValueAndValid(self, string: str, step_key: StepKey):
        string = string.replace("；", ";")
        if ';' not in string:
            return super()._parseValueAndValid(string, step_key)
        split_string = string.split(';')
        data = super()._parseValueAndValid(split_string[0], step_key)
        invalid_data = super()._parseValueAndValid(split_string[1], step_key)
        data["invalid_value"] = invalid_data.get("value")
        data["invalidity"] = invalid_data.get("validity")
        return data

    def _parseSet(self, values: List[str]):
        results = []
        result = [[]]
        selection_order = self.getSelectionOrder()
        for value in values:
            if value.upper() == "-AND-":
                continue
            elif value.upper() == "-OR-":
                results += result
                result = [[]]
            else:
                param_data = self._parseParamData(string=value)
                param_name = param_data.get("param_name")
                value = param_data.get("value")
                if param_name == self.target_param and isinstance(value, list):
                    result = self._regenSubSET(param_data, selection_order,
                                               result)
                else:
                    if isinstance(value, list):
                        raise MismatchError(
                            "value of other param shall not be a list")
                    result = [
                        r + [ParamNodeBase(**param_data)] for r in result
                    ]
        results += result
        return results


class SSParser:
    def __init__(self) -> None:
        self.ss_dic = None
        self.data = None

    def loadSS(self, ss_dic: DefaultDict[str, List[str]]) -> None:
        self.ss_dic = ss_dic

    def parseOneTC(self, tc: List[str]) -> List[CaseBase]:
        case_id = tc[CI.Case_ID.value]
        detail_steps = tc[CI.Detail_Steps.value]
        expected_result = tc[CI.Expected_Result.value]
        description = tc[CI.Description.value]
        func_allo = tc[CI.Function_Allocation.value]

        target_param, side = self.getTargetParamAndSide(description)
        results = ExpectedResultParser(expected_result=expected_result).parse()
        steps = SSDetailStepsParser(detail_steps,
                                    func_allo,
                                    target_param=target_param,
                                    side=side).parse()

        steps_length = len(steps)
        results_length = len(results)
        if results_length != 1 and results_length != steps_length:
            raise MismatchError("Detail Step and Expected Result mismatched!")
        if len(case_id.split('-')) > 4 and steps_length > 1:
            raise CustomError("Sub TC should not continue to split!")
            # tc_id = '-'.join(tc_id.split('-')[:-1])
        parsed_data = []
        if results_length == 1:
            results = results * steps_length
        for i in range(steps_length):
            step = steps[i]
            result = results[i]
            data = {}
            for index in CI:
                if index == CI.Case_ID:
                    value = case_id if steps_length == 1 else f"{case_id}-{i+1:04}"
                elif index == CI.Detail_Steps:
                    value = step
                elif index == CI.Expected_Result:
                    value = result
                else:
                    value = tc[index.value]
                if value == "":
                    continue
                data[index.name.lower()] = value
            parsed_data.append(CaseBase(**data))
        return parsed_data

    def parse(self):
        data = defaultdict(list)
        count = 0
        for tp_id, tcs in self.ss_dic.items():
            for tc in tcs:
                try:
                    parsed_tc = self.parseOneTC(tc)
                    count += 1
                except Exception as e:
                    if not config.DEBUG:
                        logger.error(f"ROW[{tc[CI.Case_ID.value]}]: {e!s}")
                    else:
                        logger.exception(e)
                    continue
                data[tp_id] += parsed_tc
        self.data = data
        logger.info(
            f"Source Selection data has been parsed! Total {count} valid cases!"
        )
        return data

    def getTargetParamAndSide(self, description: str) -> Tuple[str]:
        sides = ["pilot", "copilot"]
        description = description.replace(" ", "")
        description = description.replace("（", "(").replace("）", ")")
        if res := re.match(r"verify<?(.*?)>?sourceselection(?:\((.*?)\))?",
                           description, re.IGNORECASE):
            param = res.group(1)
            side = res.group(2) and res.group(2).lower() or "pilot"
            if side not in sides:
                raise InvalidParamError(
                    "Only support (pilot and copilot) in source selection")
            return param, side
        raise MismatchError(
            "Description shall look like 'Verify ip... source selection(pilot|copilot)'"
        )
