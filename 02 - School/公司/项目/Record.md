---
created: 2026-07-21T14:17
updated: 2026-07-22T16:11
---
# 一、给定pdf生成本体demo（mode=im-bridge）
## 1、不能直接使用原始PDF文件作为 ontology-builder 的输入，因为原始Pdf字体编码导致乱码、公式和表格结构丢失
注意：就算是原生 PDF，也会存在页眉页脚、图表、公式无法正常提取的问题，先转成 md 人工清洗再生成本体，是更稳妥的工程方案；

## 2、Invalid JSON: EOF while parsing a value at line 1 column 0 \[type=json_invalid, input_value='', input_type=str]
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721142003764.png)

也就是说解析器收到的只有空白字符，并不是“返回了一段格式错误的JSON”。
原因基本可以确定为：
1. V4-Pro仍然进行了深度思考；
2. `BridgeIMExtractor` 默认只允许4096个输出Token；
3. 对整个 `reviewed.md` 生成Bridge IM JSON时，推理消耗了输出预算；
4. 模型尚未输出最终JSON，请求就结束了；
5. 项目没有检查 `finish_reason` 和 `reasoning_content`，最终只显示JSON解析错误。
修改：
```python
class BridgeIMExtractor:
	extract()->BridgeIMDraft:
	response = await service.chat(
		messages=[
			{"role": "system", "content": BRIDGE_IM_EXTRACTION_SYSTEM_PROMPT},
			{"role": "user", "content": prompt},
		],
		temperature=0.1,
		max_tokens=16384,
		enable_thinking=False,
	)
	if response.error:
		raise RuntimeError(
			f"DeepSeek request failed: {response.error}"
		)
	if not (response.content or "").strip():
		raise RuntimeError(
			"DeepSeek returned empty final content. "
			f"finish_reason={response.finish_reason}, "
			f"reason_length={len(response.reasoning_content or '')}, "
			f"usage={response.usage}"
		)
```
将`max_tokens`改成`16384`，`enable_thingking`改为`False`(测试使用，真实场景还是`True`)，并加入错误日志。
修改后结果：
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721143929223.png)


## 3、RuntimeError: DeepSeek request failed: LLM Error:
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721142636812.png)
修改`timeout=600.0`，延长超时时间
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721142929029.png)
结果：
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721143838514.png)
生成的sysml在语法和结构转换上没有明显错误，重视反映了JSON，但是LLM生成的JSON不够完整。
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721154035082.png)
## 4、修改`prompts`：BRIDGE_IM_EXTRACTION_SYSTEM_PROMPT
```
8. 本任务处理液体火箭发动机领域，RocketEngine 下应建立 LiquidRocketEngine，
   来源中的具体发动机型号应作为 LiquidRocketEngine 个体。
9. 对来源中每一个具体发动机型号、推进剂、循环方式、供应方式、用途和公式创建 individual。
   不要只创建个体名称，来源明确提供的事实必须写入 assertions。
10. individuals 中每项的结构为：
{
  "name": "rD170",
  "type": "LiquidRocketEngine",
  "anonymous": false,
  "assertions": [
    {
      "kind": "object",
      "property": "usesOxidizer",
      "value": "liquidOxygen"
    },
    {
      "kind": "data",
      "property": "vacuumThrustN",
      "value": "8060000",
      "datatype": "xsd:decimal"
    }
  ]
}
11. 对象之间的关系使用 kind="object"：
    - 发动机使用氧化剂：usesOxidizer
    - 发动机使用燃料：usesFuel
    - 发动机采用动力循环：hasCycle
    - 发动机采用供应方式：hasSupplySystemType
    - 发动机具有任务用途：hasMissionRole
12. 数值使用 kind="data"：
    - 真空推力统一换算为 N，属性名 vacuumThrustN
    - 真空比冲按来源单位 m/s，属性名 vacuumSpecificImpulseMPerS
    - 燃烧室压力使用 MPa，属性名 chamberPressureMPa
    - 密度使用 kg/m³，属性名 densityKgPerM3
    - 温度使用 K
13. 表格中的“—”、空白或来源未给出的数值必须省略，不得推测为0。
14. CycleType 只包含燃气发生器循环、补燃循环、膨胀循环等动力循环。
    挤压式和泵压式属于 SupplySystemType，不属于 CycleType。
15. MissionRole 表示一级发动机、二级发动机、上面级发动机、姿控发动机等用途。
    SSME 是具体发动机，不得建成 MissionRole。
16. 除非来源明确要求，关系基数不要设置为恰好1。
    hasCycle 使用 0..1，hasMissionRole、usesOxidizer、usesFuel 使用 0..*。
17. object assertion 的 value 必须对应已存在的 individual。
    data assertion 的 property 必须对应已存在的 data feature。
18. 公式个体必须包含 latexExpression、formulaNumber 和 sourcePage 断言。
19. 只提取来源明确陈述的事实，不得根据常识补充来源没有给出的性能参数。
```

结果：
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260722095636949.png)
修改提示词后，模型开始为大量发动机生成 `assertions`，输出从原来的“70个空个体”变成“70个带多个事实的个体”，所以16384 Token仍然可能不足。
## 5、Invalid JSON: EOF while parsing a string at line 231 column 45

提高输出上限`max_tokens=32768`，`timeout=900.0`，添加报错打印和完善提示词
```
12. 本任务处理液体火箭发动机领域，RocketEngine 下应建立 LiquidRocketEngine，
   来源中的具体发动机型号应作为 LiquidRocketEngine 个体。
13. 对来源中每一个具体发动机型号、推进剂、循环方式、供应方式、用途和公式创建 individual。
   不要只创建个体名称，来源明确提供的事实必须写入 assertions。
14. individuals 中每项的结构为：
{
  "name": "rD170",
  "type": "LiquidRocketEngine",
  "anonymous": false,
  "assertions": [
    {
      "kind": "object",
      "property": "usesOxidizer",
      "value": "liquidOxygen"
    },
    {
      "kind": "data",
      "property": "vacuumThrustN",
      "value": "8060000",
      "datatype": "xsd:decimal"
    }
  ]
}
15. 对象之间的关系使用 kind="object"：
    - 发动机使用氧化剂：usesOxidizer
    - 发动机使用燃料：usesFuel
    - 发动机采用动力循环：hasCycle
    - 发动机采用供应方式：hasSupplySystemType
    - 发动机具有任务用途：hasMissionRole
16. 数值使用 kind="data"：
    - 真空推力统一换算为 N，属性名 vacuumThrustN
    - 真空比冲按来源单位 m/s，属性名 vacuumSpecificImpulseMPerS
    - 燃烧室压力使用 MPa，属性名 chamberPressureMPa
    - 密度使用 kg/m³，属性名 densityKgPerM3
    - 温度使用 K
17. 表格中的“—”、空白或来源未给出的数值必须省略，不得推测为0。
18. CycleType 只包含燃气发生器循环、补燃循环、膨胀循环等动力循环。
    挤压式和泵压式属于 SupplySystemType，不属于 CycleType。
19. MissionRole 表示一级发动机、二级发动机、上面级发动机、姿控发动机等用途。
    SSME 是具体发动机，不得建成 MissionRole。
20. 除非来源明确要求，关系基数不要设置为恰好1。
    hasCycle 使用 0..1，hasMissionRole、usesOxidizer、usesFuel 使用 0..*。
21. object assertion 的 value 必须对应已存在的 individual。
    data assertion 的 property 必须对应已存在的 data feature。
22. 公式个体必须包含 latexExpression、formulaNumber 和 sourcePage 断言。
23. 只提取来源明确陈述的事实，不得根据常识补充来源没有给出的性能参数。
24. 输出紧凑JSON，不要为了排版添加大量空行或缩进。
25. 除非来源中确实需要，不要填写description、rules、keys和高级OWL字段。
26. 所有顶层数组必须完整闭合，即使为空也输出[]；输出结束前检查JSON括号和引号是否闭合。
```
结果：
### 必须修正1：数据类型不兼容Java bridge

当前SysML声明：

```sysml
attribute vacuumThrustN : xsd:Decimal;
attribute latexExpression : xsd:String;
```

问题是Java bridge明确支持：

```text
Real
Integer
String
Boolean
xsd:double
xsd:integer
xsd:string
```

但没有把 `xsd:Decimal` 作为标准映射。大小写后的 `xsd:Decimal` 也不是标准XSD名称，存在转换失败或被错误当成自定义数据类型的风险。

修改提示词，明确规定：

```text
23. feature的range_type只能使用Java bridge支持的名称：
    - 小数和一般数值使用Real
    - 整数使用Integer
    - 文本使用String
    - 布尔值使用Boolean
    feature的range_type不得使用xsd:Decimal、xsd:String。

24. 数值断言的datatype使用xsd:double，
    整数断言使用xsd:integer，
    文本断言使用xsd:string。
```

期望SysML变成：

```sysml
attribute vacuumThrustN : Real;
attribute formulaNumber : String;
attribute sourcePage : Integer;
```

数据断言变成：

```json
{
  "kind": "data",
  "property": "vacuumThrustN",
  "value": "8060000",
  "datatype": "xsd:double"
}
```

### 必须修正2：单组元发动机被错误建成“使用燃料”

当前存在：

```text
DOT-25 usesFuel hydrazine
FY-81 usesFuel hydrazine
FY-82 usesFuel hydrazine
FY-83 usesFuel singlePushThree
FY-84 usesFuel singlePushThree
Ariane5USC usesFuel hydrazine
```

这些是单组元/挤压式发动机。单组元推进剂不能简单等同于“燃料”。

而且存在明确的类型冲突：

```text
FY83 usesFuel singlePushThree
singlePushThree : Monopropellant
usesFuel的range要求Fuel
```

应增加属性：

```json
{
  "name": "usesMonopropellant",
  "kind": "ref",
  "owl_kind": "object",
  "owner_type": "LiquidRocketEngine",
  "range_type": "Propellant",
  "min_cardinality": 0,
  "max_cardinality": 1
}
```

然后改成：

```text
FY81 usesMonopropellant hydrazine
FY82 usesMonopropellant hydrazine
FY83 usesMonopropellant singlePushThree
FY84 usesMonopropellant singlePushThree
```

在提示词增加：

```text
25. 对单组元发动机使用usesMonopropellant，不得使用usesFuel。
    usesMonopropellant的range_type为Propellant。
    肼作为单组元推进剂使用时，也必须通过usesMonopropellant关联。
```

### 必须修正3：三组元发动机被误当成任务用途

当前：

```text
tripropellantLiquidRocketEngine : MissionRole

RD701第一工况
  hasMissionRole tripropellantLiquidRocketEngine
```

“三组元液体火箭发动机”是发动机分类，不是任务用途。

最简单的修正方法是删掉RD-701两个工况的这条：

```text
hasMissionRole tripropellantLiquidRocketEngine
```

因为：

```text
usesOxidizer liquidOxygen
usesFuel kerosene
usesFuel liquidHydrogen
```

已经足以表达第一工况使用三组元。

提示词增加：

```text
26. “三组元液体火箭发动机”是按推进剂组元数量进行的发动机分类，
    不是MissionRole。不得创建tripropellantLiquidRocketEngine类型的
    MissionRole，也不得通过hasMissionRole关联。
```

更正式的版本可以建立：

```text
PropellantComponentCountCategory
├── MonopropellantEngineCategory
├── BipropellantEngineCategory
└── TripropellantEngineCategory
```

但试验版可以先不建，避免复杂化。

### 必须修正4：部件结构从第二版中消失了

上一版至少包含：

```text
ThrustChamber
CombustionChamber
Nozzle
Valve
Regulator
```

这一版只剩发动机、推进剂、循环、用途和公式，丢失了第一章正文明确陈述的结构：

```text
推力室由燃烧室和喷管组成
```

因此当前本体能回答发动机性能，但不能回答：

```text
液体火箭发动机有哪些部件？
推力室由什么组成？
```

提示词增加：

```text
27. 必须提取来源中明确给出的发动机组成结构，至少包括：
    EngineComponent、ThrustChamber、CombustionChamber、Nozzle、
    Valve、Regulator、PropellantSupplySystem。

28. 建立下列组成关系：
    LiquidRocketEngine hasThrustChamber ThrustChamber
    LiquidRocketEngine hasComponent EngineComponent
    ThrustChamber hasCombustionChamber CombustionChamber
    ThrustChamber hasNozzle Nozzle

29. hasThrustChamber允许0..*，因为部分发动机具有多个推力室。
```

### 建议优化项

#### `shuttleMainEngine`名称不够明确

当前：

```text
ssme : LiquidRocketEngine
shuttleMainEngine : MissionRole
ssme hasMissionRole shuttleMainEngine
```

逻辑上已经不再把SSME误建成任务类型，但名称容易混淆。建议改为：

```text
spaceShuttleMainPropulsionRole
```

#### `hasSupplySystemType`建议限制为0..1

当前允许多个：

```text
hasSupplySystemType [0..*]
```

对于本章试验模型建议：

```text
hasSupplySystemType [0..1]
```