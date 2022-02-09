from collections import defaultdict
from pathlib import Path

from tc2tp.case_reader import CaseReader, ConfigurationReader
from tc2tp.importer import (ALIAS2DB, DDIN2DB, DDOUT2DB, ICD2DB,
                            FDASAlertICD2DB, INFOAlertICD2DB)
from tc2tp.make_sub_tc import MakeSubTC
from tc2tp.make_tp import MakeTP
from tc2tp.ss_parser import SSParser
from tc2tp.tc_parser.parser import TCParser
from tc2tp.utils import cache, timer


@timer
def importData():
    root_path = r"data/resources/BP6.2-CFG2/"
    icd = ICD2DB(root_path + "ICD")
    icd.rebuild()
    ddout = DDOUT2DB(root_path + "Requirements")
    ddout.rebuild()
    ddin = DDIN2DB(root_path + "Requirements")
    ddin.rebuild()
    alias = ALIAS2DB(root_path + "IO")
    alias.rebuild()
    info_alert = INFOAlertICD2DB(root_path + r"Requirements/INFO DB")
    info_alert.rebuild()
    fdas_alert = FDASAlertICD2DB(root_path + r"Requirements/FDAS DB")
    fdas_alert.rebuild()


def clear():
    cache.clear()


@timer
def convert(case_file_path='', output_dir=''):

    case_file_path = r"F:\TC2TP工具\testTC\C919-VC-AUX12.7 TP版自动化3secondlater.xlsx"
    output_dir = r"F:\TC2TP工具\testTC\新建文件夹"
    case_file_path = Path(case_file_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # create reader to get original data
    try:
        reader = CaseReader(case_file_path, "Verification Case")
    except:
        reader = CaseReader(case_file_path, "Test Case")
    reader.read()

    configurationReader = ConfigurationReader(case_file_path, "Configuration")
    configurationReader.read()

    data = defaultdict(list)  # record test case data

    # parse simple test case
    tc_parser = TCParser()
    tc_parser.loadTC(reader.tc)
    tc_parser.parse()
    data.update(tc_parser.data)

    # parse source selection case
    ss_parser = SSParser()
    ss_parser.loadSS(reader.ss)
    ss_parser.parse()
    data.update(ss_parser.data)

    new_tc_filename = case_file_path.stem + "-new" + case_file_path.suffix
    MakeSubTC(Path(output_dir, new_tc_filename), data).make()

    Date = configurationReader.date
    revisionHistory = configurationReader.revisionHistory

    MakeTP(output_dir, data, Date, revisionHistory).make()


def manager(*args):
    if args[-1] == "import":
        importData()
    else:
        clear()
        #convert(args[1], args[2])
        convert('', '')
