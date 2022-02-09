import hashlib
import pickle
from functools import wraps
from time import time
from typing import Any, Union

from pymongo.database import Database

from tc2tp.common import mongo_db
from tc2tp.common.constant import SYN_LIST
from tc2tp.common.logger import logger


def upperKeyWord(key_word: str) -> str:
    return key_word.strip(": ：").upper()


def toStr(v: Any) -> str:
    """tansfer float to int"""
    s = str(v)
    if s.endswith(".0"):
        s = s[:-2]
    return s


def str2num(s: str) -> Union[int, float]:
    if s.upper() == "TRUE":
        return 1
    elif s.upper() == "FALSE":
        return 0
    try:
        v = int(s)
        return v
    except ValueError:
        v = float(s)
        return v
    except ValueError:
        raise


def getFuncKey(id_: str) -> str:
    func_key = id_.split('-')[2]
    if func_key in SYN_LIST:
        func_key = "SYN"
    return func_key


def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_spend = time_end - time_start
        logger.info('[%s] cost time: %.3f s' % (func.__name__, time_spend))
        return result

    return func_wrapper


class MyCache:
    def __init__(self, db: Database = mongo_db, force: bool = False) -> None:
        self.db = db
        self.force = force

    def __call__(self, func):
        @wraps(func)
        def _inner(*args, **kw):
            if self.force:
                return func(*args, **kw)
            hash_str = hashlib.md5()
            hash_str.update(str(args).encode("utf-8"))
            hash_str.update(str(kw).encode("utf-8"))
            key = f"{func.__name__}:{hash_str.hexdigest()}"
            res = self.get(key)
            if res is None:
                logger.debug(f"[Cache]: {func.__name__}({args}, {kw}) miss")
                res = func(*args, **kw)
                res = pickle.dumps(res)
                self.set(key, res)
            else:
                logger.debug(f"[Cache]: {func.__name__}({args}, {kw}) find")
            return pickle.loads(res)

        return _inner

    def set(self, key, value):
        self.db.cache.save({"_id": key, "value": value})

    def get(self, key, default=None):
        res = self.db.cache.find_one({"_id": key})
        if res is not None:
            return res.get("value")
        return default

    def clear(self):
        self.db.drop_collection("cache")


cache = MyCache()
