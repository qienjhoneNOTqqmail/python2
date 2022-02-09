from enum import Enum, auto
from typing import List, Tuple

IDU_POS = [
    "HF_IDUCENTER", "HF_IDULEFTINBOARD", "HF_IDULEFTOUTBOARD",
    "HF_IDURIGHTINBOARD", "HF_IDURIGHTOUTBOARD"
]

IMA_DM_POS = ["IMA_DM_L4", "IMA_DM_L5", "IMA_DM_R4"]

CNS_POS = ["CNSMENUAPP_L", "CNSMENUAPP_R"]

FDAS_POS = ["FDAS_L1", "FDAS_L3", "FDAS_R3"]

INFO_POS = ["INFOAPP_L", "INFOAPP_R"]

# ISIS_POS = ["HF_ISIS"]

VCP_POS = ["VIRTUALCONTROLAPP_L", "VIRTUALCONTROLAPP_R"]

SYN_POS = [
    "SYNOPTICMENUAPP_L", "SYNOPTICMENUAPP_R", "SYNOPTICPAGEAPP_L",
    "SYNOPTICPAGEAPP_R"
]

FUNC_MAPPER = {
    "AUX": IDU_POS,
    "CNS": CNS_POS,
    "DMH": IDU_POS,
    "DMI": IMA_DM_POS,
    "EI": IDU_POS,
    "FDAS": FDAS_POS,
    "FDAS_DB": FDAS_POS,
    "HSI": IDU_POS,
    "HUD": IDU_POS,
    "INFO": INFO_POS,
    "INFO_DB": INFO_POS,
    "MAP": IDU_POS,
    "PFD": IDU_POS,
    "PIT": VCP_POS,
    "SYN": SYN_POS,
    "VCP": VCP_POS,
    "IDU":
    IDU_POS + IMA_DM_POS + CNS_POS + FDAS_POS + INFO_POS + VCP_POS + SYN_POS,
    "ALL":
    IDU_POS + IMA_DM_POS + CNS_POS + FDAS_POS + INFO_POS + VCP_POS + SYN_POS
}

SYN_LIST = [
    "AMS", "DOOR", "ELEC", "FCS", "FUEL", "HYD", "INIT", "DESIGN", "MENU",
    "GENERAL"
]

SSM_MAPPER = {
    "A429_SSM_BNR": {
        # 0=Failure Warning,1=No Computed Data,2=Functional Test,3=Normal Operation
        "valid": 3,
        "invalid": 0
    },
    "A429_SSM_DIS": {
        # 0=Verified Data,Normal Operation,1=No Computed Data,2=Functional Test,3=Failure Warning
        "valid": 0,
        "invalid": 3
    },
    "A429_SSM_BCD": {
        # 0=Plus,North,East,Right,To,Above ,1=No Computed Data,2=Functional Test,3=Minus,South,West,Left,From,Below
        "valid": 0,
        "invalid": 1
    }
}

CONDITION_KEY_WORDS = ["SET", "WAIT", "ACTION", "COMMENT", "RAMP", "MCDC SET"]

REAL_RDIU = [
    "RGW01_NonA664_In", "RGW02_NonA664_In", "RGW04_NonA664_In",
    "RGW05_NonA664_In"
]

FORBIDDEN_SDI_FUNC = ["FDAS_DB", "INFO_DB"]


class CaseIndex(Enum):
    # record case's index and name
    Case_ID = 0
    Description = auto()
    Requirement_ID = auto()
    Verification_Method = auto()
    Detail_Steps = auto()
    Expected_Result = auto()
    Function_Allocation = auto()
    Test_Type = auto()
    Verification_Procedure_ID = auto()
    Verification_Case_Approval_Status = auto()
    Verification_Site = auto()
    Verification_Status = auto()
    Coverage_Analysis = auto()

    def __str__(self):
        return self.name.replace("_", " ")


class SheetCfg:
    default_row_height: int = 14
    font_name: str = "GE Inspira"
    font_size: int = 10


class TCSheetCfg(SheetCfg):
    sheet_column_width_mapper: List[Tuple] = [("A:A", 15), ("B:B", 20),
                                              ("C:C", 15), ("D:D", 10),
                                              ("E:E", 50), ("F:F", 20),
                                              ("G:H", 10), ("I:I", 15),
                                              ("J:J", 15)]


class TPSheetCfg(SheetCfg):
    sheet_column_width_mapper: List[Tuple] = [
        ("A:B", 26),
        ("C:C", 90),
        ("D:E", 26),
        ("F:H", 8),
    ]

class CFGSheetCfg(SheetCfg):
    sheet_column_width_mapper: List[Tuple] = [
        ("A:B", 15),
        ("C:C", 20),
        ("D:D", 25),
        ("E:E", 15),
    ]

FUNC_KEYS = [
    "DS", "PFD", "EI", "HSI", "MAP", "DMI", "DMH", "AUX", "FDAS", "FDAS_DB",
    "STATUS", "AIR", "DOOR", "ELEC", "FLT_CTRL", "FUEL", "HYD", "A661", "PIT",
    "INFO", "INFO_DB", "VCP", "CNS", "HUD"
]
