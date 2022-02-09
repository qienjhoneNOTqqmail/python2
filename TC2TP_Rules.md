# TC2TP规则

## 基本规则

### Case ID

测试用例的编号。

基本格式为：`C919-{Type}-{Func}-S{index}`

- `{Type}`: 测试类型，可以是 `TC`, `AC`, `IC`, `RC`，分别表示 Test, Analysis, Inspection, Review
- `{Func}`: 配置项名称，可以是 `DMH`, `DMI`, `EI`, `PFD`, `MAP`, `FDAS`, `SYN`, `HSI`, `VCP` 等
- `{index}`: case 的父级编号

例如：`C919-TC-DMH-S001`, `C919-IC-DMI-S010`

### Description

测试用例的描述信息。

如果是 `DELETE`，则表示，该用例已删除，但测试用例编号保留，在进行TC2TP转换时，将跳过该条用例。

如果是符合 `Verify {input_param} source selection{pos}` 规则，则代表该用例为源选择类型，将按照源选择规则进行解析。

- `{input_param}`: 需要进行源选择的输入参数
- `{pos}`: 表示主驾或副驾位置，值可以是 `(pilot)`, `(copilot)` 或 留空，分别表示主驾，副驾，不区分主副驾

例如：`Verify ipAltitudeCapture Source Selection(copilot)` 表示对 `ipAltitudeCapture` 的副驾进行源选择测试

### Requirement ID

表示该用例所对应的需求号，如对应多个，用换行符分隔。

例如：`DMH:103`, `DMH_DD_IN:10`

### Verification Method

验证方法，包括四种：`Test`, `Analysis`, `Inspection`, `Review`

### Detail Steps

测试步骤。由两部分组成，关键字和具体步骤。

当前支持的关键字有：

- `SET`: 对输入参数设值
- `WAIT`: 等待
- `ACTION`: 手动操作
- `COMMENT`: 用于注释
- `RAMP`: 区间设值

#### SET and RAMP

对于 `SET` 和 `RAMP` 设值指令而言，步骤符合格式 `{param_name}{extra_param} = {param_value} and {validity}`，多个步骤用关键字 `-AND-` 或者 `-OR-` 进行分隔。当存在 `-OR-` 时，将拆分为多个用例

```
SET:
stepA
-OR-
stepB
-AND-
stepC
```

将拆分为两个用例，一个为

```
SET:
stepA
```

另一个为

```
SET:
stepB
-AND-
stepC
```

对于步骤中几部分做如下说明：

- `{param_name}`: 表示设值的 ip 参数
- `{extra_param}`: 表示对参数的补充信息
    - 基本格式为 `(RP:{rp_value}, HF:{hf_value})`，表示查找该 `{param_name}` RP 为 `{rp_value}` HF 为 `{hf_value}` 的源，对其进行设值，也可以是 `(RP:{rp_value})` 或 `(HF:{hf_value})`
    - 该部分可省略，则表示查找该 `{param_name}` 所有的源，对其进行设值
- `{param_value}`: 表示参数的值，三种格式
    - `1`: 单个值
    - `[1, 2, 3]`: 多个值，如果是`SET`指令，对于一般用例而言，则会拆成多个子用例，对于源选择用例而言，目标参数源的个数个值的个数必须相同，如果是 `RAMP` 指令，则必须为 `[start, end, step, freq]` 四个值的格式
    - `{dp_name_1: dp_value_1, dp_name_1: dp_value_2}`: 如果输入参数为 `429转664` 类型，则必须使用该格式进行设值，其中 dp_value 支持多个值的形式，会拆分为多个子用例
- `{validity}`: 表示参数值的有效性设置
    - 基本格式为 `valid(FSB:3)`，表示该参数有效，且将其 fsb 设为 3
    - `invalid(FSB: 0)`: 表示该参数无效，且将其 fsb 设为 0
    - 对于429类型的参数，还支持 ssm 的设值，例如 `valid(SSM: 3, FSB: 3)`

例如

1. `ipAOTFuelQuantityUnit(RP: AOT_1_FUEL_QUANTITY_UNIT) = 1 and valid(FSB: 3)` 表示将参数 `ipAOTFuelQuantityUnit`，RP为 `AOT_1_FUEL_QUANTITY_UNIT`的源设为fbs为3的有效值1
2. `ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1} and valid` 表示将429参数 `ipFuelRightWingTankFuelQuantityKg_A`所有源中，A429Word中 `RWingTank_FuelQuantity_KGS`字段的值设为有效的-1

#### WAIT

等待指令，默认单位为秒，同时可支持 `min`, `m`, `h`, `hour`

```
WAIT:
10
```

表示等待10s后执行接下来的步骤

```
WAIT:
0.5min
```

表示等待30s后执行接下来的步骤

#### ACTION

手动操作步骤

```
ACTION:
step1...
step2...
```

#### COMMENT

用于步骤中的注释信息

```
COMMENT:
msg...
```

### Expected Result

预期结果。

关键字为 `VERIFY` 和 `CHECK`

支持多个 `VERIFY`，与可拆分为多个用例的 `Detail Steps`配合使用，表示将拆分出的多个子用例的各个预期结果。

```
VERIFY:
result1...
CHECK:
[func]check1...
VERIFY:
result2...
```

表示该条用例将拆分为两个子用例，预期结果分别为

```
VERIFY:
result1...
CHECK:
[func]check1...
```

和

```
VERIFY:
result2...
```

### Function Allocation

表示功能所属配置项，如果有多个，以换行符隔开，`Detail Steps`中的参数将在所给功能配置项的DDIN表中进行查找。

### Test Type

测试类型，对应4种验证方法，分别对应 `Test Procedure`，`Inspection Checklist`, `Review Comments`, `Analysis Report`

### Verification Procedure ID

该测试用例链接的验证程序号，将以该号生成对应的测试程序，该号一致的用例将生成在同一个文件中。

基本格式为：`C919-{Type}-{Func}-S{index}`

- `{Type}`: 测试类型，可以是 `TP`, `AP`, `IP`, `RP`，分别表示 Test, Analysis, Inspection, Review
- `{Func}`: 配置项名称，可以是 `DMH`, `DMI`, `EI`, `PFD`, `MAP`, `FDAS`, `SYN`, `HSI`, `VCP` 等
- `{index}`: procedure 的编号

> 配置项名称需要与 Case ID 中的配置项名称相对应

例如：`C919-TP-DMH-S001`, `C919-IP-DMI-S010`

### Verification Case Approval Status

Status of the approval of the Case

可选的状态有：`Development`, `In Review`, `On Hold`, `Open PR`, `Verified`

### Verification Site

Location where the requirement will be tested

可选的环境有：`Aircraft`, `COMAC SIVB`, `AVIAGE SIVB`, `Iron Bird`, `SAVIC SSDL`, `SAVIC SDIB`, `SAVIC CPTD`, `SAVIC ISISTD`

### Verification Status

Status of the verification activity for the requirement

可选的状态有：`Development`, `Dry Run`, `In Review`, `Ready for TRR`, `For Credit`, `On Hold`, `Open PR`, `Passed`, `Failed`

### Coverage Analysis

Status of the coverage analysis for the requirement

可选值有：`In Work`, `In Review`, `Complete`

## 示例

### 和输入参数源相关

#### case 1

INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                              Detail Steps                               |     Expected Result     | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| --------------- | ----------- | -------------- | ------------------- | ----------------------------------------------------------------------- | ----------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-EI-S001 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = 1 and valid<br>COMMENT:<br>four sources | verify:<br>four sources | EI                  | Test Procedure | C919-TP-EI-S001           | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TC:

|     Case ID     | Description | Requirement ID | Verification Method |                              Detail Steps                               |     Expected Result     | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| --------------- | ----------- | -------------- | ------------------- | ----------------------------------------------------------------------- | ----------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-EI-S001 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = 1 and valid<br>COMMENT:<br>four sources | Verify:<br>four sources | EI                  | Test Procedure | C919-TP-EI-S001           | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TP:

| START OF TEST SCRIPT |        |                                                              |     |
| -------------------- | ------ | ------------------------------------------------------------ | --- |
| 1                    | SET    | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 2                    | SET    | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 3                    | SET    | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 4                    | SET    | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 5                    | SET    | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 6                    | SET    | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 7                    | SET    | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 8                    | SET    | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 9                    | verify | four sources                                                 |     |
| END OF TEST SCRIPT   |        |                                                              |     |

#### case 2

INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                                                                                 Detail Steps                                                                                 |         Expected Result         | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| --------------- | ----------- | -------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-EI-S002 | test desc   | EI:679         | Test                | SET:<br>1. ipAOTFuelQuantityUnit(RP:AOT_1_FUEL_QUANTITY_UNIT) = 1 and valid<br>-AND-<br>2. ipAOTFuelQuantityUnit(HF:AOT_2) = 0 and valid<br>COMMENT:<br>set specified source | verify:<br>set specified source | EI                  | Test Procedure | C919-TP-EI-S002           | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TC:

|     Case ID     | Description | Requirement ID | Verification Method |                                                                               Detail Steps                                                                               |         Expected Result         | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| --------------- | ----------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-EI-S002 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit(RP: AOT_1_FUEL_QUANTITY_UNIT) = 1 and valid<br>-AND-<br>ipAOTFuelQuantityUnit(HF: AOT_2) = 0 and valid<br>COMMENT:<br>set specified source | Verify:<br>set specified source | EI                  | Test Procedure | C919-TP-EI-S002           | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TP:

| START OF TEST SCRIPT |        |                                                              |     |
| -------------------- | ------ | ------------------------------------------------------------ | --- |
| 1                    | SET    | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 2                    | SET    | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 3                    | SET    | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 4                    | SET    | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 0   |
| 5                    | verify | set specified source                                         |     |
| END OF TEST SCRIPT   |        |                                                              |     |

### 和输入参数有效性相关

#### case 1

INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                                                          Detail Steps                                                           |       Expected Result       | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ----------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S003 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1} and valid(FSB:3)<br>COMMENT:<br>set fsb of param | verify:<br>set fsb of param | EI                  | Test Procedure | C919-TP-EI-S003           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|     Case ID     | Description | Requirement ID | Verification Method |                                                          Detail Steps                                                           |       Expected Result       | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| --------------- | ----------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-EI-S003 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1} and valid(FSB:3)<br>COMMENT:<br>set fsb of param | Verify:<br>set fsb of param | EI                  | Test Procedure | C919-TP-EI-S003           | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TP:

| START OF TEST SCRIPT |        |                                                                                                                                       |     |
| -------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------- | --- |
| 1                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 2                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 3                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 4                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 5                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 6                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 7                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 8                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 9                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 10                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 11                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 12                   | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 13                   | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 14                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 15                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 16                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 17                   | verify | set fsb of param                                                                                                                      |     |
| END OF TEST SCRIPT   |        |                                                                                                                                       |     |

#### case 2

INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                                                                     Detail Steps                                                                      |           Expected Result           | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ----------- | -------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S004 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1, SDI:1} and valid(FSB:3, SSM:3)<br>COMMENT:<br>set fsb and ssm of param | verify:<br>set fsb and ssm of param | EI                  | Test Procedure | C919-TP-EI-S004           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|     Case ID     | Description | Requirement ID | Verification Method |                                                                      Detail Steps                                                                      |           Expected Result           | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| --------------- | ----------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-EI-S004 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1, SDI: 1} and valid(FSB:3, SSM:3)<br>COMMENT:<br>set fsb and ssm of param | Verify:<br>set fsb and ssm of param | EI                  | Test Procedure | C919-TP-EI-S004           | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TP:

| START OF TEST SCRIPT |        |                                                                                                                                       |     |
| -------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------- | --- |
| 1                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 2                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 3                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 4                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 5                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 6                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 7                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 8                    | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 9                    | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 10                   | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 11                   | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 12                   | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 13                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 14                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 15                   | SET    | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 16                   | SET    | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 17                   | verify | set fsb and ssm of param                                                                                                              |     |
| END OF TEST SCRIPT   |        |                                                                                                                                       |     |

### 和子 case 相关

#### case 1

INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                                 Detail Steps                                  |                         Expected Result                          | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ----------- | -------------- | ------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S005 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = [1, 2, 3] and valid<br>COMMENT:<br>664 signal | verify<br>case1: 1<br>verify:<br>case2: 2<br>verify:<br>case3: 3 | EI                  | Test Procedure | C919-TP-EI-S005           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID       | Description | Requirement ID | Verification Method |                             Detail Steps                              |   Expected Result   | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ------------------- | ----------- | -------------- | ------------------- | --------------------------------------------------------------------- | ------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S005-001 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = 1 and valid<br>COMMENT:<br>664 signal | Verify:<br>case1: 1 | EI                  | Test Procedure | C919-TP-EI-S005           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S005-002 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = 2 and valid<br>COMMENT:<br>664 signal | Verify:<br>case2: 2 | EI                  | Test Procedure | C919-TP-EI-S005           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S005-003 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = 3 and valid<br>COMMENT:<br>664 signal | Verify:<br>case3: 3 | EI                  | Test Procedure | C919-TP-EI-S005           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-EI-S005-001  |                                                              |     |
| -------------------- | -------------------- | ------------------------------------------------------------ | --- |
| START OF TEST PROMPT | TESTING:             | test desc                                                    |     |
|                      |                      |                                                              |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                       |     |
|                      |                      |                                                              |     |
|                      | ACTION:              |                                                              |     |
|                      |                      |                                                              |     |
|                      | ENSURE:              |                                                              |     |
| END OF TEST PROMPT   |                      |                                                              |     |
|                      |                      |                                                              |     |
| START OF TEST SCRIPT |                      |                                                              |     |
| 1                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 2                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 3                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 4                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 5                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 6                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 7                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 8                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 1   |
| 9                    | verify               | case1: 1                                                     |     |
| END OF TEST SCRIPT   |                      |                                                              |     |
| END OF TEST CASE     |                      |                                                              |     |
|                      |                      |                                                              |     |
| START OF TEST CASE   | C919-TC-EI-S005-002  |                                                              |     |
| START OF TEST PROMPT | TESTING:             | test desc                                                    |     |
|                      |                      |                                                              |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                       |     |
|                      |                      |                                                              |     |
|                      | ACTION:              |                                                              |     |
|                      |                      |                                                              |     |
|                      | ENSURE:              |                                                              |     |
| END OF TEST PROMPT   |                      |                                                              |     |
|                      |                      |                                                              |     |
| START OF TEST SCRIPT |                      |                                                              |     |
| 1                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 2                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 2   |
| 3                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 4                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 2   |
| 5                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 6                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 2   |
| 7                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 8                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 2   |
| 9                    | verify               | case2: 2                                                     |     |
| END OF TEST SCRIPT   |                      |                                                              |     |
| END OF TEST CASE     |                      |                                                              |     |
|                      |                      |                                                              |     |
| START OF TEST CASE   | C919-TC-EI-S005-003  |                                                              |     |
| START OF TEST PROMPT | TESTING:             | test desc                                                    |     |
|                      |                      |                                                              |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                       |     |
|                      |                      |                                                              |     |
|                      | ACTION:              |                                                              |     |
|                      |                      |                                                              |     |
|                      | ENSURE:              |                                                              |     |
| END OF TEST PROMPT   |                      |                                                              |     |
|                      |                      |                                                              |     |
| START OF TEST SCRIPT |                      |                                                              |     |
| 1                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 2                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 3   |
| 3                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 4                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 3   |
| 5                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 6                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 3   |
| 7                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__ | 3   |
| 8                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit         | 3   |
| 9                    | verify               | case3: 3                                                     |     |
| END OF TEST SCRIPT   |                      |                                                              |     |
| END OF TEST CASE     |                      |                                                              |     |

#### case 2

INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                                                              Detail Steps                                                               |                         Expected Result                          | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ----------- | -------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S006 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: [1, 2, 3]} and valid<br>COMMENT:<br>429 or 429 in 664 signal | verify<br>case1: 1<br>verify:<br>case2: 2<br>verify:<br>case3: 3 | EI                  | Test Procedure | C919-TP-EI-S006           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID       | Description | Requirement ID | Verification Method |                                                          Detail Steps                                                           |   Expected Result   | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ------------------- | ----------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S006-001 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: 1} and valid<br>COMMENT:<br>429 or 429 in 664 signal | Verify:<br>case1: 1 | EI                  | Test Procedure | C919-TP-EI-S006           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S006-002 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: 2} and valid<br>COMMENT:<br>429 or 429 in 664 signal | Verify:<br>case2: 2 | EI                  | Test Procedure | C919-TP-EI-S006           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S006-003 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: 3} and valid<br>COMMENT:<br>429 or 429 in 664 signal | Verify:<br>case3: 3 | EI                  | Test Procedure | C919-TP-EI-S006           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-EI-S006-001  |                                                                                                                                       |     |
| -------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | test desc                                                                                                                             |     |
|                      |                      |                                                                                                                                       |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                                                                                                |     |
|                      |                      |                                                                                                                                       |     |
|                      | ACTION:              |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
|                      | ENSURE:              |                                                                                                                                       |     |
| END OF TEST PROMPT   |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST SCRIPT |                      |                                                                                                                                       |     |
| 1                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 2                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 3                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 4                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 1   |
| 5                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 6                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 7                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 8                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 9                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 1   |
| 10                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 11                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 12                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 13                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 14                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 15                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 16                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 17                   | verify               | case1: 1                                                                                                                              |     |
| END OF TEST SCRIPT   |                      |                                                                                                                                       |     |
| END OF TEST CASE     |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST CASE   | C919-TC-EI-S006-002  |                                                                                                                                       |     |
| START OF TEST PROMPT | TESTING:             | test desc                                                                                                                             |     |
|                      |                      |                                                                                                                                       |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                                                                                                |     |
|                      |                      |                                                                                                                                       |     |
|                      | ACTION:              |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
|                      | ENSURE:              |                                                                                                                                       |     |
| END OF TEST PROMPT   |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST SCRIPT |                      |                                                                                                                                       |     |
| 1                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 2                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 3                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 4                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 2   |
| 5                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 6                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 7                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 8                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 9                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 10                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 2   |
| 11                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 12                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 13                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 14                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 15                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 16                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 17                   | verify               | case2: 2                                                                                                                              |     |
| END OF TEST SCRIPT   |                      |                                                                                                                                       |     |
| END OF TEST CASE     |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST CASE   | C919-TC-EI-S006-003  |                                                                                                                                       |     |
| START OF TEST PROMPT | TESTING:             | test desc                                                                                                                             |     |
|                      |                      |                                                                                                                                       |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                                                                                                |     |
|                      |                      |                                                                                                                                       |     |
|                      | ACTION:              |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
|                      | ENSURE:              |                                                                                                                                       |     |
| END OF TEST PROMPT   |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST SCRIPT |                      |                                                                                                                                       |     |
| 1                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 2                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 3                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 4                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 3   |
| 5                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 6                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 7                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 8                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 9                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 10                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 3   |
| 11                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 12                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 13                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 14                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 15                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 16                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 17                   | verify               | case3: 3                                                                                                                              |     |
| END OF TEST SCRIPT   |                      |                                                                                                                                       |     |
| END OF TEST CASE     |                      |                                                                                                                                       |     |

#### case 3
INPUT:

|     Case ID     | Description | Requirement ID | Verification Method |                                                                                                                                                                                                               Detail Steps                                                                                                                                                                                                                |           Expected Result            | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ----------- | -------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S007 | test desc   | EI:679         | Test                | SET:<br>1. ipAOTFuelQuantityUnit = 1 and valid<br>-AND-<br>2. ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1} and valid<br>-AND-<br>3. ipFuelRightWingTankFuelQuantityKg_B ={RWingTank_FuelQuantity_KGS: -1 } and valid<br>-OR-<br>1. ipFuelRightWingTankFuelQuantityKg_A ={RWingTank_FuelQuantity_KGS: 3} and valid<br>-AND-<br>2. ipFuelRightWingTankFuelQuantityKg_B ={RWingTank_FuelQuantity_KGS: 3} and valid | verify:<br>case1<br>verify:<br>case2 | EI                  | Test Procedure | C919-TP-EI-S007           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID       | Description | Requirement ID | Verification Method |                                                                                                             Detail Steps                                                                                                              | Expected Result  | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ------------------- | ----------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S007-001 | test desc   | EI:679         | Test                | SET:<br>ipAOTFuelQuantityUnit = 1 and valid<br>-AND-<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: -1} and valid<br>-AND-<br>ipFuelRightWingTankFuelQuantityKg_B = {RWingTank_FuelQuantity_KGS: -1} and valid | Verify:<br>case1 | EI                  | Test Procedure | C919-TP-EI-S007           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S007-002 | test desc   | EI:679         | Test                | SET:<br>ipFuelRightWingTankFuelQuantityKg_A = {RWingTank_FuelQuantity_KGS: 3} and valid<br>-AND-<br>ipFuelRightWingTankFuelQuantityKg_B = {RWingTank_FuelQuantity_KGS: 3} and valid                                                   | Verify:<br>case2 | EI                  | Test Procedure | C919-TP-EI-S007           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-EI-S007-001  |                                                                                                                                       |     |
| -------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | test desc                                                                                                                             |     |
|                      |                      |                                                                                                                                       |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                                                                                                |     |
|                      |                      |                                                                                                                                       |     |
|                      | ACTION:              |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
|                      | ENSURE:              |                                                                                                                                       |     |
| END OF TEST PROMPT   |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST SCRIPT |                      |                                                                                                                                       |     |
| 1                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__                                                                          | 3   |
| 2                    | SET                  | AOT_1.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit                                                                                  | 1   |
| 3                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__                                                                          | 3   |
| 4                    | SET                  | AOT_2.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit                                                                                  | 1   |
| 5                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__                                                                          | 3   |
| 6                    | SET                  | AOT_3.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit                                                                                  | 1   |
| 7                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit.__fsb__                                                                          | 3   |
| 8                    | SET                  | AOT_4.AOT_Distributed_Message.DS6.Fuel_Quantity_Unit                                                                                  | 1   |
| 9                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 10                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 11                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 12                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 13                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 14                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 15                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 16                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 17                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 18                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 19                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 20                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 21                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 22                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 23                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 24                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 25                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 26                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 2   |
| 27                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 28                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 29                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 30                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 2   |
| 31                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 32                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | -1  |
| 33                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 34                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 35                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 36                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 37                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 38                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 39                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 40                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 41                   | verify               | case1                                                                                                                                 |     |
| END OF TEST SCRIPT   |                      |                                                                                                                                       |     |
| END OF TEST CASE     |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST CASE   | C919-TC-EI-S007-002  |                                                                                                                                       |     |
| START OF TEST PROMPT | TESTING:             | test desc                                                                                                                             |     |
|                      |                      |                                                                                                                                       |     |
|                      | REQUIREMENTS TESTED: | EI:679                                                                                                                                |     |
|                      |                      |                                                                                                                                       |     |
|                      | ACTION:              |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
|                      | ENSURE:              |                                                                                                                                       |     |
| END OF TEST PROMPT   |                      |                                                                                                                                       |     |
|                      |                      |                                                                                                                                       |     |
| START OF TEST SCRIPT |                      |                                                                                                                                       |     |
| 1                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 2                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 3                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 4                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 3   |
| 5                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 6                    | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 7                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 8                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 1   |
| 9                    | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 10                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 3   |
| 11                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 12                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 13                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 14                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 15                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 16                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_A1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 17                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 18                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 2   |
| 19                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 20                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 3   |
| 21                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM                                | 3   |
| 22                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI                                | 2   |
| 23                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 24                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS         | 3   |
| 25                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 26                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SSM.__fsb__                        | 3   |
| 27                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 28                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.PARITY.__fsb__                     | 3   |
| 29                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.RWingTank_FuelQuantity_KGS.__fsb__ | 3   |
| 30                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.LABEL.__fsb__                      | 3   |
| 31                   | SET                  | RGW07_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 32                   | SET                  | RGW09_NonA664_In.poHFS_DISPLAY_IDU_Msg2_1.HF_FUEL_LRM.po429_B1_Msg.L252_RWingTank_FuelQuantity_KGS.SDI.__fsb__                        | 3   |
| 33                   | verify               | case2                                                                                                                                 |     |
| END OF TEST SCRIPT   |                      |                                                                                                                                       |     |
| END OF TEST CASE     |                      |                                                                                                                                       |     |

### 源选择相关

#### case 1

INPUT:

|     Case ID     |                Description                 |                Requirement ID                | Verification Method |                       Detail Steps                        |                                                                                                Expected Result                                                                                                | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ------------------------------------------ | -------------------------------------------- | ------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S008 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos = [1, 15,20] and Valid<br><br> | VERIFY:<br>1.The rudder trim position readout as 1 in white color<br>VERIFY:<br>2.The rudder trim position readout as 15 in white color<br>VERIFY:<br>3.The rudder trim position readout as 20 in white color | EI                  | Test Procedure | C919-TP-EI-S008           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID       |                Description                 |                Requirement ID                | Verification Method |                                                                                                    Detail Steps                                                                                                     |                          Expected Result                           | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ------------------- | ------------------------------------------ | -------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S008-001 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos(RP: FCM_1_RudderTrimPos) = 1 and valid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_2_RudderTrimPos) = 15 and valid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_3_RudderTrimPos) = 20 and valid     | Verify:<br>1.The rudder trim position readout as 1 in white color  | EI                  | Test Procedure | C919-TP-EI-S008           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S008-002 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos(RP: FCM_1_RudderTrimPos) = 1 and invalid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_2_RudderTrimPos) = 15 and valid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_3_RudderTrimPos) = 20 and valid   | Verify:<br>2.The rudder trim position readout as 15 in white color | EI                  | Test Procedure | C919-TP-EI-S008           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S008-003 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos(RP: FCM_1_RudderTrimPos) = 1 and invalid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_2_RudderTrimPos) = 15 and invalid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_3_RudderTrimPos) = 20 and valid | Verify:<br>3.The rudder trim position readout as 20 in white color | EI                  | Test Procedure | C919-TP-EI-S008           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-EI-S008-001  |                                                            |     |
| -------------------- | -------------------- | ---------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | Verify ipFCSRudderTrimPos Source Selection                 |     |
|                      |                      |                                                            |     |
|                      | REQUIREMENTS TESTED: | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329               |     |
|                      |                      |                                                            |     |
|                      | ACTION:              |                                                            |     |
|                      |                      |                                                            |     |
|                      | ENSURE:              |                                                            |     |
| END OF TEST PROMPT   |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST SCRIPT |                      |                                                            |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 1   |
| 3                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 15  |
| 5                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 20  |
| 7                    | verify               | 1.The rudder trim position readout as 1 in white color     |     |
| END OF TEST SCRIPT   |                      |                                                            |     |
| END OF TEST CASE     |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST CASE   | C919-TC-EI-S008-002  |                                                            |     |
| START OF TEST PROMPT | TESTING:             | Verify ipFCSRudderTrimPos Source Selection                 |     |
|                      |                      |                                                            |     |
|                      | REQUIREMENTS TESTED: | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329               |     |
|                      |                      |                                                            |     |
|                      | ACTION:              |                                                            |     |
|                      |                      |                                                            |     |
|                      | ENSURE:              |                                                            |     |
| END OF TEST PROMPT   |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST SCRIPT |                      |                                                            |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 0   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 1   |
| 3                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 15  |
| 5                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 20  |
| 7                    | verify               | 2.The rudder trim position readout as 15 in white color    |     |
| END OF TEST SCRIPT   |                      |                                                            |     |
| END OF TEST CASE     |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST CASE   | C919-TC-EI-S008-003  |                                                            |     |
| START OF TEST PROMPT | TESTING:             | Verify ipFCSRudderTrimPos Source Selection                 |     |
|                      |                      |                                                            |     |
|                      | REQUIREMENTS TESTED: | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329               |     |
|                      |                      |                                                            |     |
|                      | ACTION:              |                                                            |     |
|                      |                      |                                                            |     |
|                      | ENSURE:              |                                                            |     |
| END OF TEST PROMPT   |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST SCRIPT |                      |                                                            |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 0   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 1   |
| 3                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 0   |
| 4                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 15  |
| 5                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 20  |
| 7                    | verify               | 3.The rudder trim position readout as 20 in white color    |     |
| END OF TEST SCRIPT   |                      |                                                            |     |
| END OF TEST CASE     |                      |                                                            |     |

#### case 2

INPUT:

|     Case ID     |                Description                 |                Requirement ID                | Verification Method |                                                                        Detail Steps                                                                         |                                                                                                Expected Result                                                                                                | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| --------------- | ------------------------------------------ | -------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S009 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos = 0 and Valid<br>COMMENT:<br>init ipFCSRudderTrimPos<br>WAIT:<br>10<br>SET:<br>ipFCSRudderTrimPos = [1, 15,20] and Valid<br><br> | VERIFY:<br>1.The rudder trim position readout as 1 in white color<br>VERIFY:<br>2.The rudder trim position readout as 15 in white color<br>VERIFY:<br>3.The rudder trim position readout as 20 in white color | EI                  | Test Procedure | C919-TP-EI-S009           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID       |                Description                 |                Requirement ID                | Verification Method |                                                                                                                                                     Detail Steps                                                                                                                                                      |                          Expected Result                           | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ------------------- | ------------------------------------------ | -------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-EI-S009-001 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos = 0 and valid<br>COMMENT:<br>init ipFCSRudderTrimPos<br>WAIT:<br>10<br>SET:<br>ipFCSRudderTrimPos(RP: FCM_1_RudderTrimPos) = 1 and valid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_2_RudderTrimPos) = 15 and valid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_3_RudderTrimPos) = 20 and valid     | Verify:<br>1.The rudder trim position readout as 1 in white color  | EI                  | Test Procedure | C919-TP-EI-S009           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S009-002 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos = 0 and valid<br>COMMENT:<br>init ipFCSRudderTrimPos<br>WAIT:<br>10<br>SET:<br>ipFCSRudderTrimPos(RP: FCM_1_RudderTrimPos) = 1 and invalid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_2_RudderTrimPos) = 15 and valid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_3_RudderTrimPos) = 20 and valid   | Verify:<br>2.The rudder trim position readout as 15 in white color | EI                  | Test Procedure | C919-TP-EI-S009           | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-EI-S009-003 | Verify ipFCSRudderTrimPos Source Selection | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329 | Test                | SET:<br>ipFCSRudderTrimPos = 0 and valid<br>COMMENT:<br>init ipFCSRudderTrimPos<br>WAIT:<br>10<br>SET:<br>ipFCSRudderTrimPos(RP: FCM_1_RudderTrimPos) = 1 and invalid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_2_RudderTrimPos) = 15 and invalid<br>-AND-<br>ipFCSRudderTrimPos(RP: FCM_3_RudderTrimPos) = 20 and valid | Verify:<br>3.The rudder trim position readout as 20 in white color | EI                  | Test Procedure | C919-TP-EI-S009           | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-EI-S009-001  |                                                            |     |
| -------------------- | -------------------- | ---------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | Verify ipFCSRudderTrimPos Source Selection                 |     |
|                      |                      |                                                            |     |
|                      | REQUIREMENTS TESTED: | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329               |     |
|                      |                      |                                                            |     |
|                      | ACTION:              |                                                            |     |
|                      |                      |                                                            |     |
|                      | ENSURE:              |                                                            |     |
| END OF TEST PROMPT   |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST SCRIPT |                      |                                                            |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 3                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 5                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 7                    | WAIT                 | 10                                                         |     |
| 8                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 9                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 1   |
| 10                   | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 11                   | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 15  |
| 12                   | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 13                   | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 20  |
| 14                   | verify               | 1.The rudder trim position readout as 1 in white color     |     |
| END OF TEST SCRIPT   |                      |                                                            |     |
| END OF TEST CASE     |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST CASE   | C919-TC-EI-S009-002  |                                                            |     |
| START OF TEST PROMPT | TESTING:             | Verify ipFCSRudderTrimPos Source Selection                 |     |
|                      |                      |                                                            |     |
|                      | REQUIREMENTS TESTED: | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329               |     |
|                      |                      |                                                            |     |
|                      | ACTION:              |                                                            |     |
|                      |                      |                                                            |     |
|                      | ENSURE:              |                                                            |     |
| END OF TEST PROMPT   |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST SCRIPT |                      |                                                            |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 3                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 5                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 7                    | WAIT                 | 10                                                         |     |
| 8                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 0   |
| 9                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 1   |
| 10                   | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 11                   | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 15  |
| 12                   | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 13                   | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 20  |
| 14                   | verify               | 2.The rudder trim position readout as 15 in white color    |     |
| END OF TEST SCRIPT   |                      |                                                            |     |
| END OF TEST CASE     |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST CASE   | C919-TC-EI-S009-003  |                                                            |     |
| START OF TEST PROMPT | TESTING:             | Verify ipFCSRudderTrimPos Source Selection                 |     |
|                      |                      |                                                            |     |
|                      | REQUIREMENTS TESTED: | EI_DD_IN:327<br>EI_DD_IN:328<br>EI_DD_IN:329               |     |
|                      |                      |                                                            |     |
|                      | ACTION:              |                                                            |     |
|                      |                      |                                                            |     |
|                      | ENSURE:              |                                                            |     |
| END OF TEST PROMPT   |                      |                                                            |     |
|                      |                      |                                                            |     |
| START OF TEST SCRIPT |                      |                                                            |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 3                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 5                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 0   |
| 7                    | WAIT                 | 10                                                         |     |
| 8                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 0   |
| 9                    | SET                  | HF_FCM_1.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 1   |
| 10                   | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 0   |
| 11                   | SET                  | HF_FCM_2.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 15  |
| 12                   | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position.__fsb__ | 3   |
| 13                   | SET                  | HF_FCM_3.FCS_Output_PF20.DS63.Rudder_Trim_Position         | 20  |
| 14                   | verify               | 3.The rudder trim position readout as 20 in white color    |     |
| END OF TEST SCRIPT   |                      |                                                            |     |
| END OF TEST CASE     |                      |                                                            |     |

#### case 3

INPUT:

|     Case ID      |                   Description                    |                 Requirement ID                  | Verification Method |                  Detail Steps                   |                          Expected Result                          | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ---------------- | ------------------------------------------------ | ----------------------------------------------- | ------------------- | ----------------------------------------------- | ----------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-PFD-S001 | Verify ipAltitudeCapture Source Selection(pilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture = [1, 2, 3] and valid | Verify:<br>FCM_1: 1<br>Verify:<br>FCM_3: 2<br>Verify:<br>FCM_2: 3 | PFD                 | Test Procedure | C919-TP-PFD-S001          | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID        |                   Description                    |                 Requirement ID                  | Verification Method |                                                                                                      Detail Steps                                                                                                       |   Expected Result   | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| -------------------- | ------------------------------------------------ | ----------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-PFD-S001-001 | Verify ipAltitudeCapture Source Selection(pilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 1 and valid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 3 and valid     | Verify:<br>FCM_1: 1 | PFD                 | Test Procedure | C919-TP-PFD-S001          | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-PFD-S001-002 | Verify ipAltitudeCapture Source Selection(pilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 1 and invalid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 3 and valid   | Verify:<br>FCM_3: 2 | PFD                 | Test Procedure | C919-TP-PFD-S001          | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-PFD-S001-003 | Verify ipAltitudeCapture Source Selection(pilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 1 and invalid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and invalid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 3 and valid | Verify:<br>FCM_2: 3 | PFD                 | Test Procedure | C919-TP-PFD-S001          | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-PFD-S001-001 |                                                             |     |
| -------------------- | -------------------- | ----------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(pilot)            |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_1: 1                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S001-002 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(pilot)            |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 0   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_3: 2                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S001-003 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(pilot)            |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 0   |
| 2                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 0   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_2: 3                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |

#### case 4

INPUT:

|     Case ID      |                    Description                     |                 Requirement ID                  | Verification Method |                  Detail Steps                   |                          Expected Result                          | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ---------------- | -------------------------------------------------- | ----------------------------------------------- | ------------------- | ----------------------------------------------- | ----------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-PFD-S002 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture = [1, 2, 3] and valid | Verify:<br>FCM_2: 1<br>Verify:<br>FCM_3: 2<br>Verify:<br>FCM_1: 3 | PFD                 | Test Procedure | C919-TP-PFD-S002          | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID        |                    Description                     |                 Requirement ID                  | Verification Method |                                                                                                      Detail Steps                                                                                                       |   Expected Result   | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| -------------------- | -------------------------------------------------- | ----------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-PFD-S002-001 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and valid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid     | Verify:<br>FCM_2: 1 | PFD                 | Test Procedure | C919-TP-PFD-S002          | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-PFD-S002-002 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and invalid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid   | Verify:<br>FCM_3: 2 | PFD                 | Test Procedure | C919-TP-PFD-S002          | Development                       | SAVIC SSDL        | Development         | In Work           |     |
| C919-TC-PFD-S002-003 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and invalid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and invalid<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid | Verify:<br>FCM_1: 3 | PFD                 | Test Procedure | C919-TP-PFD-S002          | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-PFD-S002-001 |                                                             |     |
| -------------------- | -------------------- | ----------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_2: 1                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S002-002 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 0   |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_3: 2                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S002-003 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 0   |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 0   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_1: 3                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |

#### case 5

INPUT:

|     Case ID      |                    Description                     |                 Requirement ID                  | Verification Method |                              Detail Steps                               |                          Expected Result                          | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ---------------- | -------------------------------------------------- | ----------------------------------------------- | ------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-PFD-S003 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture = [1, 2, 3] and valid(FSB:3); invalid(FSB:12) | Verify:<br>FCM_2: 1<br>Verify:<br>FCM_3: 2<br>Verify:<br>FCM_1: 3 | PFD                 | Test Procedure | C919-TP-PFD-S003          | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID        |                    Description                     |                 Requirement ID                  | Verification Method |                                                                                                                  Detail Steps                                                                                                                  |   Expected Result   | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| -------------------- | -------------------------------------------------- | ----------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-PFD-S003-001 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and valid(FSB:3)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid(FSB:3)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid(FSB:3)       | Verify:<br>FCM_2: 1 | PFD                 | Test Procedure | C919-TP-PFD-S003          | Development                       | SAVIC SSDL        | Development         | In Work           |
| C919-TC-PFD-S003-002 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and invalid(FSB:12)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid(FSB:3)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid(FSB:3)    | Verify:<br>FCM_3: 2 | PFD                 | Test Procedure | C919-TP-PFD-S003          | Development                       | SAVIC SSDL        | Development         | In Work           |
| C919-TC-PFD-S003-003 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and invalid(FSB:12)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and invalid(FSB:12)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid(FSB:3) | Verify:<br>FCM_1: 3 | PFD                 | Test Procedure | C919-TP-PFD-S003          | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-PFD-S003-001 |                                                             |     |
| -------------------- | -------------------- | ----------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_2: 1                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S003-002 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 12  |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_3: 2                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S003-003 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 12  |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 12  |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_1: 3                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |

#### case 6

INPUT:

|     Case ID      |                    Description                     |                 Requirement ID                  | Verification Method |                                     Detail Steps                                      |                          Expected Result                          | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |     |
| ---------------- | -------------------------------------------------- | ----------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- | --- |
| C919-TC-PFD-S004 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture = [1, 2, 3] and valid(FSB:3); [4, 5, 6] and invalid(FSB:12) | Verify:<br>FCM_2: 1<br>Verify:<br>FCM_3: 2<br>Verify:<br>FCM_1: 3 | PFD                 | Test Procedure | C919-TP-PFD-S004          | Development                       | SAVIC SSDL        | Development         | In Work           |     |

OUTPUT TC:

|       Case ID        |                    Description                     |                 Requirement ID                  | Verification Method |                                                                                                                  Detail Steps                                                                                                                  |   Expected Result   | Function Allocation |   Test Type    | Verification Procedure ID | Verification Case Approval Status | Verification Site | Verification Status | Coverage Analysis |
| -------------------- | -------------------------------------------------- | ----------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------- | ------------------------- | --------------------------------- | ----------------- | ------------------- | ----------------- |
| C919-TC-PFD-S004-001 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 1 and valid(FSB:3)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid(FSB:3)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid(FSB:3)       | Verify:<br>FCM_2: 1 | PFD                 | Test Procedure | C919-TP-PFD-S004          | Development                       | SAVIC SSDL        | Development         | In Work           |
| C919-TC-PFD-S004-002 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 4 and invalid(FSB:12)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 2 and valid(FSB:3)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid(FSB:3)    | Verify:<br>FCM_3: 2 | PFD                 | Test Procedure | C919-TP-PFD-S004          | Development                       | SAVIC SSDL        | Development         | In Work           |
| C919-TC-PFD-S004-003 | Verify ipAltitudeCapture Source Selection(copilot) | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292 | Test                | SET:<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_2) = 4 and invalid(FSB:12)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_3) = 5 and invalid(FSB:12)<br>-AND-<br>ipAltitudeCapture(RP: Altitude_Capture_FCM_1) = 3 and valid(FSB:3) | Verify:<br>FCM_1: 3 | PFD                 | Test Procedure | C919-TP-PFD-S004          | Development                       | SAVIC SSDL        | Development         | In Work           |

OUTPUT TP:

|  START OF TEST CASE  | C919-TC-PFD-S004-001 |                                                             |     |
| -------------------- | -------------------- | ----------------------------------------------------------- | --- |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 1   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_2: 1                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S004-002 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 12  |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 4   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 2   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_3: 2                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST CASE   | C919-TC-PFD-S004-003 |                                                             |     |
| START OF TEST PROMPT | TESTING:             | Verify ipAltitudeCapture Source Selection(copilot)          |     |
|                      |                      |                                                             |     |
|                      | REQUIREMENTS TESTED: | PFD_DD_IN:290<br>PFD_DD_IN:291<br>PFD_DD_IN:292             |     |
|                      |                      |                                                             |     |
|                      | ACTION:              |                                                             |     |
|                      |                      |                                                             |     |
|                      | ENSURE:              |                                                             |     |
| END OF TEST PROMPT   |                      |                                                             |     |
|                      |                      |                                                             |     |
| START OF TEST SCRIPT |                      |                                                             |     |
| 1                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 12  |
| 2                    | SET                  | HF_FCM_2.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 4   |
| 3                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 12  |
| 4                    | SET                  | HF_FCM_3.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 5   |
| 5                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture.__fsb__ | 3   |
| 6                    | SET                  | HF_FCM_1.FCS_Output_Data_AF20.DS13.Altitude_Capture         | 3   |
| 7                    | verify               | FCM_1: 3                                                    |     |
| END OF TEST SCRIPT   |                      |                                                             |     |
| END OF TEST CASE     |                      |                                                             |     |
