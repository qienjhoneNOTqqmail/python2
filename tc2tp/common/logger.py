import sys
from pathlib import Path

from loguru import logger
from tc2tp.common.config import config

log_path = Path("logs")
log_path.mkdir(exist_ok=True)

log_path_debug = log_path.joinpath("debug.log")
log_path_error = log_path.joinpath("error.log")
log_path_simple_info = log_path.joinpath("simple_info.log")

if not config.DEBUG:
    logger.remove(handler_id=None)
    logger.add(sys.stderr,
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               level="INFO",
               backtrace=False,
               diagnose=False)
logger.add(log_path_simple_info,
           retention="5 days",
           level="INFO",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           enqueue=True,
           encoding="utf-8",
           backtrace=False,
           diagnose=False)
logger.add(log_path_error,
           retention="5 days",
           level="WARNING",
           enqueue=True,
           encoding="utf-8")
logger.add(log_path_debug,
           retention="2 days",
           level="DEBUG",
           enqueue=True,
           encoding="utf-8")
