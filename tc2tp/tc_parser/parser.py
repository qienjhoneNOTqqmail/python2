from collections import defaultdict
from typing import DefaultDict, List

from tc2tp.common.constant import CaseIndex as CI
from tc2tp.common.custom_error import CustomError, MismatchError
from tc2tp.common.logger import logger
from tc2tp.models import CaseBase, DetailStepsParser, ExpectedResultParser


class TCParser:
    def __init__(self) -> None:
        self.tc_dic = None
        self.data = None

    def loadTC(self, tc_dic: DefaultDict[str, List[str]]) -> None:
        self.tc_dic = tc_dic

    @staticmethod
    def parseOneTC(tc: List[str]) -> List[CaseBase]:
        case_id = tc[CI.Case_ID.value]
        detail_step = tc[CI.Detail_Steps.value]
        expected_result = tc[CI.Expected_Result.value]

        results = ExpectedResultParser(expected_result=expected_result).parse()
        logger.debug(results)
        steps = DetailStepsParser(detail_steps=detail_step).parse()
        logger.debug(steps)

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
                    value = case_id if steps_length == 1 else f"{case_id}-{i+1:03}"
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
        logger.debug(parsed_data)
        return parsed_data

    def parse(self):
        data = defaultdict(list)
        count = 0
        for tp_id, tcs in self.tc_dic.items():
            for tc in tcs:
                try:
                    parsed_tc = self.parseOneTC(tc)
                    count += 1
                except Exception as e:
                    logger.error(f"ROW[{tc[CI.Case_ID.value]}]: {e!s}")
                    continue
                data[tp_id] += parsed_tc
        self.data = data
        logger.info(
            f"Test Case data has been parsed! Total {count} valid cases!")
        return data
