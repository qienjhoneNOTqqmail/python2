from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from pymongo.database import Database
from tc2tp.common.constant import (FORBIDDEN_SDI_FUNC, FUNC_MAPPER, REAL_RDIU,
                                   SSM_MAPPER, SYN_LIST)
from tc2tp.common.custom_error import (CustomError, IncorrectError,
                                       InvalidParamError, NotFoundError)
from tc2tp.common.db import mongo_db
from tc2tp.common.logger import logger
from tc2tp.models import ParamNodeBase, StepBase, VSite
from tc2tp.utils import cache


def _checkData(db: Database = mongo_db,
               *,
               collection_name: str,
               query: Dict = None) -> bool:
    query = query or {}
    return db.get_collection(collection_name).count_documents(query) > 0


@cache
def _findData(db: Database = mongo_db,
              *,
              collection_name: str,
              query: dict = None,
              ret: dict = None) -> List:
    query = query or {}
    res = db.get_collection(collection_name).find(query, ret)
    return list(res)


@cache
def _aggregateData(db: Database = mongo_db,
                   *,
                   collection_name: str,
                   pipeline: list) -> list:
    return list(db.get_collection(collection_name).aggregate(pipeline))


@cache
def _deDuplication(collection_name: str, match: dict, group_by: List) -> List:
    group = {
        "_id": {key: (f"${key}")
                for key in group_by} or {
                    "None": "$None"
                }
    }
    project = dict({"_id": 0}, **{key: (f"$_id.{key}") for key in group_by})
    pipeline = [{"$match": match}, {"$group": group}, {"$project": project}]
    return _aggregateData(collection_name=collection_name, pipeline=pipeline)


@cache
def getInputParamDP(logic_param: str,
                    rp: str = None,
                    hf: str = None,
                    *,
                    func_pos: List[str]) -> List:
    rp_pattern = rp if rp is not None else ".*"
    hf_pattern = f"^{hf}" + r"\." if hf is not None else ".*"
    query = {
        "Input Logic Parameter": {
            "$regex": f"^{logic_param}$",
            "$options": "i"
        },
        "origin": {
            "$in": func_pos,
        },
        "RP": {
            "$regex": rp_pattern,
            "$options": "i"
        },
        "DP": {
            "$regex": hf_pattern,
            "$options": "i"
        }
    }
    ret = {"_id": 0}
    return _findData(collection_name="DDIN", query=query, ret=ret)


# def getOutputParamDP(self, logic_param: str, func_key: str = "ALL"):
#     pattern = f"^{func_key}.*" if func_key != "ALL" else ".*"
#     query = {
#         "Output Logic Parameter": logic_param,
#         "ID": {
#             "$regex": pattern
#         }
#     }
#     ret = {"_id": 0}
#     res = self._findData("DDOUT", query, ret)
#     if res:
#         return dict(data=res)


@cache
def getFuncPos(func_keys: List[str], deep: bool = True) -> List[str]:
    func_pos = []
    for func_key in func_keys:
        if func_key in SYN_LIST:
            func_key = "SYN"
        if deep:
            func_pos += FUNC_MAPPER.get(func_key, [])
        else:
            func_pos.append(func_key)
    if not func_pos:
        msg = f"The function key {func_keys!r} doesn't exist!"
        raise NotFoundError(msg)
    return func_pos


@cache
def _getInputSignal(bus_type: str,
                    dp: str,
                    rp: str = None,
                    *,
                    func_pos: List[str]) -> List:
    rp_pattern = rp if rp is not None else ".*"
    collection_name = f"Input{bus_type}Signals"
    match = {
        "$expr": {
            "$and": [
                {
                    "$regexMatch": {
                        "input": "$Pub_Ref",
                        "regex": f"^{dp}",
                        "options": "i"
                    }
                    # "eq": ["$Pub_Ref", dp]
                },
                {
                    "$regexMatch": {
                        "input": "$RP",
                        "regex": rp_pattern,
                        "options": "i"
                    }
                },
                {
                    "$in": ["$origin", func_pos]
                }
            ]
        }
    }
    group_by = [
        "Skip", "RP", "Pub_Ref", "HostedFunction", "TxPort", "CodedSet",
        "A429Word"
    ]
    return _deDuplication(collection_name=collection_name,
                          match=match,
                          group_by=group_by)


@cache
def getInputSignal(logic_param: str, rp: str, hf: str,
                   func_keys: List[str]) -> defaultdict(list):
    res = defaultdict(list)
    func_pos = getFuncPos(func_keys, deep=False)
    data = getInputParamDP(logic_param=logic_param,
                           rp=rp,
                           hf=hf,
                           func_pos=func_pos)
    logger.debug(data)
    param = logic_param + f"(rp:{rp or ''},hf:{hf or ''})"
    if not data:
        msg = f"[{param}]: Can't find in {func_pos!r} DDIN!"
        raise NotFoundError(msg)
    visited = set()
    func_pos = getFuncPos(func_keys)
    for dd in data:
        dp = dd.get("DP")
        rp = dd.get("RP")
        if (dp, rp) in visited:
            continue
        visited.add((dp, rp))
        for bus_type in ["664", "429", "825"]:
            tmp = _getInputSignal(bus_type=bus_type,
                                  dp=dp,
                                  rp=rp,
                                  func_pos=func_pos)
            if not tmp:
                continue
            
            #需要精确或模糊RP就把另一部分注释掉

            #确保rp完全一致
            #精确RP
            # for split_tmp in tmp:
            #     split_tmp_rp = split_tmp.get('RP')
            #     if split_tmp_rp == rp:
            #         res[bus_type] += [split_tmp]
            #     else:
            #         continue    
            
            #模糊RP
            res[bus_type] += tmp
            #
    if not res:
        msg = f"[{param}]: Can't find in {func_pos!r} ICD!"
        raise NotFoundError(msg)
    return res


@cache
def _parseSDICodedSet(pub_ref: str, coded_set: str) -> int:
    '''auto get SDI
    '''
    ret = 0
    coded_set = coded_set.strip('\n')
    if not coded_set:
        msg = f"{pub_ref!r}: SDI CodedSet is null"
        raise IncorrectError(msg)
    if '\n' not in coded_set:
        try:
            ret = int(coded_set.split('=')[0])
            return ret
        except ValueError as e:
            msg = f"{coded_set!r} failed to parse correctly!"
            raise IncorrectError(msg) from e
    flag = pub_ref.split(".")[0].split('_')[-1]
    if "Single" in coded_set:
        ret = 0
    elif "DME1" in coded_set:
        ret = 1
    elif "PartitionA" in coded_set:
        ret = 1
    elif "PartitionB" in coded_set:
        ret = 2
    elif flag in ['1', 'L']:
        ret = 1
    elif flag in ['2', 'R']:
        ret = 2
    else:
        msg = "There are cases that are not considered in CodedSet!"
        raise IncorrectError(msg)
    return ret


@cache
def _parseSSMCodedSet(coded_set: str) -> Dict[str, int]:
    '''auto get SSM
    '''
    ret = {}
    coded_set = coded_set.strip('\n')
    if not coded_set:
        msg = "SSM CodedSet is null"
        raise IncorrectError(msg)
    for row in coded_set.split('\n'):
        try:
            v, k = row.strip(" ,").split('=')
            if k.lower() in ("normal operation", "receive function active",
                             "transmit function active", "always"):
                ret["valid"] = int(v)
            if k.lower() in ("no computed data", "not used", "ncd", "unused"):
                ret["invalid"] = int(v)
        except ValueError as e:
            msg = f"{coded_set!r} failed to parse correctly!"
            raise IncorrectError(msg) from e
    if "valid" in ret and "invalid" in ret:
        return ret
    raise IncorrectError(f"{coded_set!r} failed to parse correctly!")


@cache
def _getParam(bus_type: str,
              message_name: str,
              param_prefix: str,
              func_pos: List[str],
              dp: str = None):
    query = {
        "$and": [{
            "Pub_Ref": {
                "$regex": f"^{message_name}.*"
            }
        }, {
            "DP": {
                "$regex": f"^{dp or '.*'}$",
                "$options": "i"
            }
        }, {
            "origin": {
                "$in": func_pos
            }
        }]
    }
    param_signal = _findData(collection_name=f"Input{bus_type}Signals",
                             query=query)
    if not param_signal:
        raise NotFoundError()
    param_key = ".".join(
        filter(lambda x: x, [param_prefix, param_signal[0].get("Pub_Ref")]))
    if not checkAlias(key=param_key):
        raise NotFoundError(f"Can not find {param_key!r} in ALIAS!")
    return param_key


@cache
def _setSDI(bus_type: str, message_name: str, param_prefix: str,
            func_pos: List[str]) -> Dict:
    query = {
        "$and": [{
            "Pub_Ref": {
                "$regex": f"^{message_name}.*"
            }
        }, {
            "DataFormatType": "A429SDI"
        }, {
            "origin": {
                "$in": func_pos
            }
        }]
    }
    sdi_signal = _findData(collection_name=f"Input{bus_type}Signals",
                           query=query)
    if not sdi_signal:
        return {}
    sdi_key = ".".join(
        filter(lambda x: x, [param_prefix, sdi_signal[0].get("Pub_Ref")]))
    if not checkAlias(key=sdi_key):
        raise NotFoundError(f"Can not find {sdi_key!r} in ALIAS!")
    sdi = _parseSDICodedSet(message_name, sdi_signal[0].get("CodedSet"))
    res = {sdi_key: sdi}
    return res


@cache
def _getSSM(bus_type: str, message_name: str, param_prefix: str,
            func_pos: List[str]):
    query = {
        "$and": [{
            "Pub_Ref": {
                "$regex": f"^{message_name}.*"
            }
        }, {
            "DataFormatType": {
                "$regex": "^A429_SSM.*"
            }
        }, {
            "origin": {
                "$in": func_pos
            }
        }]
    }
    ssm_signal = _findData(collection_name=f"Input{bus_type}Signals",
                           query=query)
    if not ssm_signal:
        raise NotFoundError()
    ssm_key = ".".join(
        filter(lambda x: x, [param_prefix, ssm_signal[0].get("Pub_Ref")]))
    if not checkAlias(key=ssm_key):
        raise NotFoundError(f"Can not find {ssm_key!r} in ALIAS!")
    return ssm_key, ssm_signal[0]


def _setSSM(bus_type: str, message_name: str, param_prefix: str,
            func_pos: List[str], validity: Dict) -> Dict:
    ssm_key, ssm_signal = _getSSM(bus_type, message_name, param_prefix,
                                  func_pos)
    ssm_type = ssm_signal.get("DataFormatType")
    coded_set = ssm_signal.get("CodedSet")
    ssm_value = validity.get("SSM")
    if ssm_value is None:
        ssm_data = SSM_MAPPER.get(ssm_type)
        if ssm_data is None:
            try:
                ssm_data = _parseSSMCodedSet(coded_set)
            except IncorrectError as e:
                raise NotFoundError(
                    f"Can not identify {ssm_type!r}! Error msg: {e.msg}")
        if_valid = validity.get("if_valid")
        ssm_value = ssm_data.get("valid" if if_valid else "invalid")
    res = {ssm_key: ssm_value}
    return res


def _setFSB(param_name: str, validity: Dict, site: VSite) -> Dict:
    if_valid = validity.get("if_valid")
    fsb_value = validity.get("FSB")
    if fsb_value is None:
        fsb_value = 3 if if_valid else 0
    fsb_key = param_name + ".__fsb__"
    if not checkAlias(key=fsb_key):
        msg = f"Can not find '{fsb_key}' in ALIAS!"
        raise NotFoundError(msg)
    res = {fsb_key: fsb_value}
    return res


def _isReal(hf: str, site: VSite):
    if site == VSite.savic_ssdl and hf in REAL_RDIU:
        return True
    return False


def _needForward(hf: str, pub_ref: str, site: VSite = VSite.savic_ssdl):
    if pub_ref.split('.')[0] == hf or _isReal(hf, site):
        return False
    return True


def _gen429Entry(source: Dict, param_value: Any, validity: Dict,
                 func_allo: List[str], site: VSite):
    pub_ref = source.get("Pub_Ref")
    hf = source.get("HostedFunction")
    tx_port = source.get("TxPort")
    func_pos = getFuncPos(func_allo)
    if _needForward(hf, pub_ref, site):
        param_prefix = ".".join([hf, tx_port])
        param_name = ".".join([param_prefix, pub_ref])
    else:
        param_prefix = ""
        param_name = pub_ref
    message_name = ".".join(pub_ref.split(".")[:-1])
    if_valid = validity.get("if_valid")
    entry = {}
    ssm_data = _setSSM("429", message_name, param_prefix, func_pos, validity)
    entry.update(ssm_data)
    if if_valid == 1 and not (set(func_allo) & set(FORBIDDEN_SDI_FUNC)):
        sdi_data = _setSDI("429", message_name, param_prefix, func_pos)
        entry.update(sdi_data)
    if param_value is None:
        logger.debug(entry)
        return entry
    if isinstance(param_value, dict):
        for k, v in param_value.items():
            param_name = _getParam("429", message_name, param_prefix, func_pos,
                                   k)
            entry[param_name] = v
    else:
        if not checkAlias(key=param_name):
            raise NotFoundError(f"Can not find {param_name!r} in ALIAS!")
        entry[param_name] = param_value
    return entry


def _gen429In664Entry(source: Dict, param_value: Any, validity: Dict,
                      func_allo: List[str], site: VSite):
    pub_ref = source.get("Pub_Ref")
    hf = source.get("HostedFunction")
    tx_port = source.get("TxPort")
    func_pos = getFuncPos(func_allo)
    skip = source.get("Skip")
    if _needForward(hf, pub_ref, site):
        param_prefix = ".".join([hf, tx_port])
        param_name = ".".join([param_prefix, pub_ref])
    else:
        param_prefix = ""
        param_name = pub_ref
    if skip == "#":
        message_name = pub_ref
    else:
        message_name = ".".join(pub_ref.split(".")[:-1])
    logger.debug(message_name)
    if_valid = validity.get("if_valid")
    entry = {}
    ssm_data = _setSSM("664", message_name, param_prefix, func_pos, validity)
    entry.update(ssm_data)
    if if_valid == 1 or validity.get("FSB"):
        if not (set(func_allo) & set(FORBIDDEN_SDI_FUNC)):
            sdi_data = _setSDI("664", message_name, param_prefix, func_pos)
            entry.update(sdi_data)
        if not _isReal(hf, site):
            for param in [
                    ".".join(filter(lambda x: x,
                                    [param_prefix, message_name])), param_name,
                    ssm_data and list(ssm_data.keys())[0]
            ]:
                try:
                    fsb_data = _setFSB(param, validity, site)
                    entry.update(fsb_data)
                    break
                except NotFoundError:
                    pass
            # else:
            #     raise NotFoundError("Can not find valid fsb data!")
    if param_value is None:
        logger.debug(entry)
        return entry
    if isinstance(param_value, dict):
        for k, v in param_value.items():
            param_name = _getParam("664", message_name, param_prefix, func_pos,
                                   k)
            entry[param_name] = v
    elif skip == "#":
        raise NotFoundError(
            "This parameter is 429 in 664, it's value shall be a dict")
    else:
        if not checkAlias(key=param_name):
            raise NotFoundError(f"Can not find {param_name!r} in ALIAS!")
        entry[param_name] = param_value
    return entry


def _gen664Entry(source: Dict, param_value: Any, validity: Dict,
                 func_allo: List[str], site: VSite):
    pub_ref = source.get('Pub_Ref')
    hf = source.get("HostedFunction")
    tx_port = source.get("TxPort")
    func_pos = getFuncPos(func_allo)
    if _needForward(hf, pub_ref, site):
        param_prefix = ".".join([hf, tx_port])
        param_name = ".".join([param_prefix, pub_ref])
    else:
        param_prefix = ""
        param_name = pub_ref
    logger.debug(param_name)
    entry = {}
    if param_name.startswith("HF_FADEC"):
        logger.debug("FADEC")
        splited_pub_ref = param_name.split(".")
        if splited_pub_ref[1].endswith("Discrete"):
            control_message = '.'.join(splited_pub_ref[:2])
            control_key = _getParam("664", control_message, "", func_pos,
                                    "Local_Channel_in_Control")
            entry.update(_setFSB(control_key, validity, site))
            entry[control_key] = 1
    if not _isReal(hf, site):
        fsb_data = _setFSB(param_name, validity, site)
        entry.update(fsb_data)
    if param_value is None:
        logger.debug(entry)
        return entry
    if isinstance(param_value, dict):
        for k, v in param_value.items():
            if param_prefix != "":
                message_name = ".".join(param_name.split(".")[2:])
            else:
                message_name = param_name
            param_name = _getParam("664", message_name, param_prefix, func_pos,
                                   k)
            entry[param_name] = v
    else:
        if not checkAlias(key=param_name):
            raise NotFoundError(f"Can not find {param_name!r} in ALIAS!")
        entry[param_name] = param_value
    return entry


def _gen825Entry(source: Dict, param_value: Any, validity: Dict,
                 func_allo: List[str], site: VSite):
    pub_ref = source.get('Pub_Ref')
    hf = source.get("HostedFunction")
    tx_port = source.get("TxPort")
    func_pos = getFuncPos(func_allo)
    if _needForward(hf, pub_ref, site):
        param_prefix = ".".join([hf, tx_port])
        param_name = ".".join([param_prefix, pub_ref])
    else:
        param_prefix = ""
        param_name = pub_ref
    entry = {}
    if validity.get("if_valid") == 0:
        raise InvalidParamError(
            "The logic param of 825 bus type is always valid!")
    if isinstance(param_value, dict):
        for k, v in param_value.items():
            param_name = _getParam("825", param_name, param_prefix, func_pos,
                                   k)
            entry[param_name] = v
    else:
        if not checkAlias(key=param_name):
            raise NotFoundError(f"Can not find {param_name!r} in ALIAS!")
        entry[param_name] = param_value
    return entry


def generateEntry(bus_type: str, source: Dict, param_value: Any,
                  validity: Dict, func_allo: List[str], site: VSite) -> Dict:
    a429word = source.get("A429Word", "")
    if bus_type == "825":
        logger.debug("825")
        entry = _gen825Entry(source, param_value, validity, func_allo, site)
    elif bus_type == "429":
        logger.debug("429")
        entry = _gen429Entry(source, param_value, validity, func_allo, site)
    elif a429word.strip() != "":
        logger.debug("429 in 664")
        entry = _gen429In664Entry(source, param_value, validity, func_allo,
                                  site)
    else:
        logger.debug("664")
        entry = _gen664Entry(source, param_value, validity, func_allo, site)
    logger.debug(entry)
    return entry


@cache
def checkAlias(key: str) -> bool:
    query = {"alias": {"$regex": f"{key}$"}}
    return _checkData(collection_name="ALIAS", query=query)


class QueryBuilder:
    def __init__(self, step: StepBase, func_allo: List[str], site: VSite):
        self.step = step
        self.func_allo = func_allo
        self.site = site
        self.results = []

    def query(self):
        # for content in self.step.contents:
        #     logger.debug(content)
        #     data = self._query(content)
        #     if data is None:
        #         continue
        #     self.results.append(data)
        # return self.results
        with ThreadPoolExecutor() as pool:
            datas = pool.map(self._query, self.step.contents)
        for data in datas:
            if data is None:
                continue
            self.results.append(data)
        logger.debug(self.results)
        return self.results

    def _query(self, param_node: ParamNodeBase):
        assert isinstance(param_node, ParamNodeBase), "Type Error"
        data = {}
        logic_param = param_node.param_name
        rp = param_node.rp
        hf = param_node.hf
        param_value = param_node.value
        validity = param_node.validity
        res = getInputSignal(logic_param, rp, hf, self.func_allo)
        logger.debug(res)
        for bus_type, sources in res.items():
            for source in sources:
                try:
                    data.update(
                        generateEntry(bus_type, source, param_value, validity,
                                      self.func_allo, self.site))
                except CustomError as e:
                    raise CustomError(f"[{logic_param}]: {e.msg}") from e
        return data
