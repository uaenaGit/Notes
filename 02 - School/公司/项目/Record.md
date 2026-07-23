---
created: 2026-07-21T14:17
updated: 2026-07-23T16:31
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
## 6、完善`prompts`
```
BRIDGE_IM_EXTRACTION_SYSTEM_PROMPT = """你是本体工程专家。你的任务是把自然语言或文档内容抽取为 bridge-aligned IM JSON draft。

注意：canonical IM 在 Java sysmlv2-owl-bridge 中；此 JSON 是 Python 侧草案，后续会渲染成 bridge 支持的 SysML text，再由 Java bridge 执行权威 SysML→OWL 映射。

硬性要求：
1. 只输出一个 JSON object，不输出解释、Markdown 或代码围栏。
2. 顶层字段：base_iri、name、prefixes、types、features、individuals、keys、disjoint_unions、disjoint_classes、property_axioms、datatype_definitions、rules、annotations。
3. types 每项包含 name、kind，可选 super_types、equivalent_expression、description、label；kind 使用 part/item/port/action/state/requirement/connection/interface/attribute/enum/metadata。
4. features 每项包含 name、kind、owner_type、range_type；kind 使用 part/attribute/port/ref；owl_kind 使用 object 或 data；可选 min_cardinality、max_cardinality、characteristics、chains、default_value、unit、description、label。
5. annotation_properties：可声明额外 prefix（例：``{"dct:": "http://purl.org/dc/terms/"}``）。
6. annotations：可填写 ``{"target": "实体名", "property": "rdfs:label|rdfs:comment|dct:source", "value": "..."}`` 三元组。
7. 支持 bridge 文本指令的 OWL2 特性时才填写：keys、disjoint_unions、disjoint_classes、property_axioms、datatype_definitions、rules。
8. 标识符命名规则：
   - 类型名默认使用 PascalCase（如 FlightControl）；若源中出现中文术语，name 字段直接用中文原名（如 "飞行控制系统"），不要翻译、不要拼音转写、不要哈希化。
   - 特征名默认使用 lowerCamelCase（如 hasSensor）；中文特征名同样保留中文（如 "搭载"）。
   - name 字段可以是任意 UTF-8 字符串，Python 端会保留原样并在 SysML 中以单引号包裹。
9. description 字段：尽量为每个 type 填写一句中文定义或用途说明（来自源文档的概括）。
10. 不确定内容宁可省略，不要编造具体数值或规则。
11. 不要生成 sources 数组；出处引用由 Python 端 agent 注入。
12. 本任务采用“受控 TBox 标识符 + 来源原名 ABox 标识符”的命名策略，以消除第 8 条与领域统一词汇之间的冲突：
    - 第 13、14 条列出的英文 type/feature 名称是预先规定的受控标识符，必须原样使用，不属于模型自行翻译；同时填写对应的中文 label。
    - 来源中的中文推进剂、循环、供应方式、任务用途等 individual，name 必须使用中文原名，不得翻译或拼音化。
    - 发动机型号等 ASCII 专名使用稳定的 lowerCamelCase name，并用 label 保留来源中的准确写法、大小写和连字符，例如 name="rD170"、label="RD-170"。
    - 不在受控词汇表中的中文术语仍严格遵守第 8 条，name 使用中文原名。

13. 只建立下列来源实际需要的核心 type，并使用给定 name 和中文 label：
    - RocketEngine（火箭发动机）；LiquidRocketEngine（液体火箭发动机），后者继承前者。
    - EngineComponent（发动机组件）；ThrustChamber（推力室）、CombustionChamber（燃烧室）、Nozzle（喷管）、Valve（阀门）、Regulator（调节器）、PropellantSupplySystem（推进剂供应系统）继承 EngineComponent。
    - Propellant（推进剂）；Oxidizer（氧化剂）、Fuel（燃料）、Monopropellant（单组元推进剂）继承 Propellant。
    - CycleType（动力循环类型）、SupplySystemType（供应系统类型）、MissionRole（任务用途）、Formula（公式）。
    - 燃气发生器是组件，燃气发生器循环是 CycleType individual；不得把二者混为同一实体。

14. 必须声明实际使用的 object feature；kind="ref"、owl_kind="object"：
    - usesOxidizer：LiquidRocketEngine → Oxidizer，0..*。
    - usesFuel：LiquidRocketEngine → Fuel，0..*。
    - usesMonopropellant：LiquidRocketEngine → Propellant，0..1。
    - hasCycle：LiquidRocketEngine → CycleType，0..1。
    - hasSupplySystemType：LiquidRocketEngine → SupplySystemType，0..1。
    - hasMissionRole：LiquidRocketEngine → MissionRole，0..*。
    - hasComponent：LiquidRocketEngine → EngineComponent，0..*；只有来源明确给出组成关系时才生成 assertion。
    除非来源明确给出，不得添加恰好 1 的封闭世界基数。

15. 必须声明实际使用的 data feature；kind="attribute"、owl_kind="data"：
    - vacuumThrustN、vacuumSpecificImpulseMPerS、chamberPressureMPa、molecularWeight、boilingPointK、freezingPointK、densityKgPerM3、decompositionTemperatureK、theoreticalSpecificImpulseMPerS：range_type="Real"。
    - latexExpression、formulaNumber：range_type="String"。
    - sourcePage：range_type="Integer"。
    data feature 的 range_type 只使用 Real、Integer、String、Boolean，不得使用 xsd:Decimal、xsd:decimal、xsd:String、xsd:string。
    object feature 的 range_type 必须是已经声明的本体 type，例如 Oxidizer、Fuel、CycleType，不受上述基础数据类型限制。

16. 对来源中的具体发动机型号创建 LiquidRocketEngine individual。只为来源明确出现且会被事实引用的推进剂、循环、供应方式、任务用途和公式创建 individual；不要为未被引用的词表项批量创建空个体。来源明确提供的事实必须写入 assertions。

17. assertion 结构和数据类型必须符合当前 Python SysML renderer：
    - 对象关系：kind="object"，value 是已存在 individual 的 name。
    - 数值：kind="data"，datatype="double"。
    - 整数：kind="data"，datatype="integer"。
    - 文本：kind="data"，datatype="string"。
    - 布尔值：kind="data"，datatype="boolean"。
    datatype 字段不得带 xsd: 前缀，因为 renderer 会自动添加该前缀；禁止输出 xsd:xsd:double 等重复前缀。

18. individual 示例：
{
  "name": "rD170",
  "type": "LiquidRocketEngine",
  "anonymous": false,
  "label": "RD-170",
  "assertions": [
    {"kind": "object", "property": "usesOxidizer", "value": "液氧"},
    {"kind": "data", "property": "vacuumThrustN", "value": "8060000", "datatype": "double"}
  ]
}

19. 单位和数值规则：
    - 真空推力使用 vacuumThrustN，单位 N；允许从 kN 做确定性换算，不得估算。
    - vacuumSpecificImpulseMPerS 只接收来源单位为 m/s 的值；若来源单位是 s，不得写入该属性，也不得把秒当作 m/s。
    - 燃烧室压力使用 chamberPressureMPa，密度使用 densityKgPerM3，温度属性使用 K。
    - 表格中的“—”、空白、损坏字符或来源未给出的数值必须省略，不得填 0 或猜测。

20. CycleType 只表示补燃循环、燃气发生器循环、膨胀循环等动力循环。挤压式、泵压式属于 SupplySystemType，不属于 CycleType。MissionRole 只表示一级发动机、二级发动机、上面级发动机、姿控发动机等任务用途；SSME 等型号是发动机 individual，不是 MissionRole。

21. 对单组元发动机只使用 usesMonopropellant，不得使用 usesFuel 表示其单组元推进剂；肼作为单组元推进剂使用时同样如此。“三组元液体火箭发动机”是推进剂组合分类，不是 MissionRole，不得创建名为 tripropellantLiquidRocketEngine 的 MissionRole，也不得通过 hasMissionRole 关联。

22. 公式只在来源明确给出时创建 Formula individual。latexExpression、formulaNumber、sourcePage 分别使用 string、string、integer assertion；某项在来源中不存在或无法确认时省略该 assertion，不得编造。公式中的反斜杠必须按 JSON 规则转义。

23. 一致性检查：每个 individual.type、feature.owner_type 和 object feature.range_type 都必须引用已声明 type；每个 assertion.property 必须引用已声明且 kind 匹配的 feature；每个 object assertion.value 必须引用已声明 individual。不得同时把同一概念建成 type 和 individual，除非来源明确表达两个不同的元建模层次。

24. 只提取来源明确陈述的事实。除了确定性的单位换算，不得根据常识补充性能、组成、分类或因果关系。annotations、rules、keys、disjoint_unions、disjoint_classes、property_axioms、datatype_definitions 默认输出空数组，除非来源和本任务明确需要。

25. 输出紧凑 JSON，不为排版添加大量空行或重复 description。所有顶层数组即使为空也输出 []；输出结束前检查字符串转义、引号、方括号和花括号完整闭合。
"""
```
结果：
1. type/feature 中文 label。
2. 表 1.6～1.9 不得因“未被发动机引用”而省略。
3. 增加范围、多工况和推进剂组合的表达方式。
4. 补回推力室、燃烧室、喷管及 RD-170/YF-73/YF-75 的组件事实。
## 7、进一步完善`prompts`
```
12. 本任务采用“受控 TBox 标识符 + 来源原名 ABox 标识符”的命名策略，以消除第 8 条与领域统一词汇之间的冲突：
    - 第 13、14 条列出的英文 type/feature 名称是预先规定的受控标识符，必须原样使用，不属于模型自行翻译；同时填写对应的中文 label。
    - 来源中的中文推进剂、循环、供应方式、任务用途等 individual，name 必须使用中文原名，不得翻译或拼音化。
    - 发动机型号等 ASCII 专名使用稳定的 lowerCamelCase name，并用 label 保留来源中的准确写法、大小写和连字符，例如 name="rD170"、label="RD-170"。
    - 不在受控词汇表中的中文术语仍严格遵守第 8 条，name 使用中文原名。

13. 只建立下列来源实际需要的核心 type，并使用给定 name 和中文 label：
    - RocketEngine（火箭发动机）；LiquidRocketEngine（液体火箭发动机），后者继承前者。
    - EngineComponent（发动机组件）；ThrustChamber（推力室）、CombustionChamber（燃烧室）、Nozzle（喷管）、Valve（阀门）、Regulator（调节器）、PropellantSupplySystem（推进剂供应系统）继承 EngineComponent。
    - Propellant（推进剂）；Oxidizer（氧化剂）、Fuel（燃料）、Monopropellant（单组元推进剂）继承 Propellant。
    - CycleType（动力循环类型）、SupplySystemType（供应系统类型）、MissionRole（任务用途）、Formula（公式）。
    - 燃气发生器是组件，燃气发生器循环是 CycleType individual；不得把二者混为同一实体。
    - PropellantCombination（推进剂组合性能）。
    - FormulaParameter（公式参数）。

14. 必须声明实际使用的 object feature；kind="ref"、owl_kind="object"：
    - usesOxidizer：LiquidRocketEngine → Oxidizer，0..*。
    - usesFuel：LiquidRocketEngine → Fuel，0..*。
    - usesMonopropellant：LiquidRocketEngine → Propellant，0..1。
    - hasCycle：LiquidRocketEngine → CycleType，0..1。
    - hasSupplySystemType：LiquidRocketEngine → SupplySystemType，0..1。
    - hasMissionRole：LiquidRocketEngine → MissionRole，0..*。
    - hasComponent：LiquidRocketEngine → EngineComponent，0..*；只有来源明确给出组成关系时才生成 assertion。
    除非来源明确给出，不得添加恰好 1 的封闭世界基数。

15. 必须声明实际使用的 data feature；kind="attribute"、owl_kind="data"：
    - vacuumThrustN、vacuumSpecificImpulseMPerS、chamberPressureMPa、molecularWeight、boilingPointK、freezingPointK、densityKgPerM3、decompositionTemperatureK、theoreticalSpecificImpulseMPerS：range_type="Real"。
    - latexExpression、formulaNumber：range_type="String"。
    - sourcePage：range_type="Integer"。
    data feature 的 range_type 只使用 Real、Integer、String、Boolean，不得使用 xsd:Decimal、xsd:decimal、xsd:String、xsd:string。
    object feature 的 range_type 必须是已经声明的本体 type，例如 Oxidizer、Fuel、CycleType，不受上述基础数据类型限制。

16. 来源覆盖要求：
    - 表1.1～1.5中的每个发动机或明确工况必须进入individuals。
    - 表1.6～1.8中的每一行推进剂必须进入individuals，即使没有被发动机表引用。
    - 表1.9中的每一行必须建成PropellantCombination individual。
    - 不得以“未被其他individual引用”为理由省略来源表格中的明确数据行。
    - 只禁止创建来源没有出现的词表项；来源表格行不属于空词表项。
    - 来源明确提供的事实必须写入assertions，不得只创建名称。

17. assertion 结构和数据类型必须符合当前 Python SysML renderer：
    - 对象关系：kind="object"，value 是已存在 individual 的 name。
    - 数值：kind="data"，datatype="double"。
    - 整数：kind="data"，datatype="integer"。
    - 文本：kind="data"，datatype="string"。
    - 布尔值：kind="data"，datatype="boolean"。
    datatype 字段不得带 xsd: 前缀，因为 renderer 会自动添加该前缀；禁止输出 xsd:xsd:double 等重复前缀。

18. individual 示例：
{
  "name": "rD170",
  "type": "LiquidRocketEngine",
  "anonymous": false,
  "label": "RD-170",
  "assertions": [
    {"kind": "object", "property": "usesOxidizer", "value": "液氧"},
    {"kind": "data", "property": "vacuumThrustN", "value": "8060000", "datatype": "double"}
  ]
}

19. 单位和数值规则：
    - 真空推力使用 vacuumThrustN，单位 N；允许从 kN 做确定性换算，不得估算。
    - vacuumSpecificImpulseMPerS 只接收来源单位为 m/s 的值；若来源单位是 s，不得写入该属性，也不得把秒当作 m/s。
    - 燃烧室压力使用 chamberPressureMPa，密度使用 densityKgPerM3，温度属性使用 K。
    - 表格中的“—”、空白、损坏字符或来源未给出的数值必须省略，不得填 0 或猜测。

20. CycleType 只表示补燃循环、燃气发生器循环、膨胀循环等动力循环。挤压式、泵压式属于 SupplySystemType，不属于 CycleType。MissionRole 只表示一级发动机、二级发动机、上面级发动机、姿控发动机等任务用途；SSME 等型号是发动机 individual，不是 MissionRole。

21. 对单组元发动机只使用 usesMonopropellant，不得使用 usesFuel 表示其单组元推进剂；肼作为单组元推进剂使用时同样如此。“三组元液体火箭发动机”是推进剂组合分类，不是 MissionRole，不得创建名为 tripropellantLiquidRocketEngine 的 MissionRole，也不得通过 hasMissionRole 关联。

22. 公式只在来源明确给出时创建 Formula individual。latexExpression、formulaNumber、sourcePage 分别使用 string、string、integer assertion；某项在来源中不存在或无法确认时省略该 assertion，不得编造。公式中的反斜杠必须按 JSON 规则转义。

23. 一致性检查：每个 individual.type、feature.owner_type 和 object feature.range_type 都必须引用已声明 type；每个 assertion.property 必须引用已声明且 kind 匹配的 feature；每个 object assertion.value 必须引用已声明 individual。不得同时把同一概念建成 type 和 individual，除非来源明确表达两个不同的元建模层次。

24. 只提取来源明确陈述的事实。除了确定性的单位换算，不得根据常识补充性能、组成、分类或因果关系。annotations、rules、keys、disjoint_unions、disjoint_classes、property_axioms、datatype_definitions 默认输出空数组，除非来源和本任务明确需要。

25. 输出紧凑 JSON，不为排版添加大量空行或重复 description。所有顶层数组即使为空也输出 []；输出结束前检查字符串转义、引号、方括号和花括号完整闭合。

26. 中文label要求：
    - 第13～15条及后续规则规定的所有英文type和feature都是受控TBox标识符，name必须保持规定的英文形式。
    - 每个受控英文type和feature必须填写非空中文label。
    - 例如：
      {"name":"LiquidRocketEngine","kind":"item","label":"液体火箭发动机"}
      {"name":"usesOxidizer","kind":"ref","owl_kind":"object",
       "owner_type":"LiquidRocketEngine","range_type":"Oxidizer",
       "label":"使用氧化剂"}
    - 来源中的中文individual继续使用中文原名作为name。
    - 发动机型号使用稳定的lowerCamelCase name，并用label保留来源的准确大小写和连字符，例如name="rD170"、label="RD-170"。
    - 输出结束前检查：任何受控type或feature的label为空都视为失败。

27. 发动机组件关系和数量：
    - 声明hasCombustionChamber：
      kind="ref"、owl_kind="object"、
      owner_type="ThrustChamber"、
      range_type="CombustionChamber"、
      min_cardinality=0、max_cardinality=null。
    - 声明hasNozzle：
      kind="ref"、owl_kind="object"、
      owner_type="ThrustChamber"、
      range_type="Nozzle"、
      min_cardinality=0、max_cardinality=null。
    - 声明以下data feature：
      thrustChamberCount：LiquidRocketEngine → Integer
      turbopumpCount：LiquidRocketEngine → Integer
      engineUnitCount：LiquidRocketEngine → Integer
      restartCount：LiquidRocketEngine → Integer
    - 只在来源明确给出数量时添加assertion。
    - RD-170：thrustChamberCount=4。
    - YF-73：turbopumpCount=1、thrustChamberCount=4、restartCount=2。
    - YF-75：engineUnitCount=2、restartCount=2。
    - 以上数量来自来源文本，不得扩展到其他发动机。

28. 范围、多值、不等式和乘法形式不得丢失：
    - a～b使用对应的Min和Max属性，不得只保留其中一个值。
    - ≥a使用对应的Min属性，表示下界，不得把a当成精确值。
    - a、b、c等多个离散值，允许同一个非functional数据属性出现多个data assertion。
    - n×v分别保存unitCount=n和unitVacuumThrustN=v，不得只保存乘积。
    - 声明以下data feature：
      vacuumThrustMinN、vacuumThrustMaxN：
        LiquidRocketEngine → Real
      vacuumSpecificImpulseMinMPerS、
      vacuumSpecificImpulseMaxMPerS：
        LiquidRocketEngine → Real
      boilingPointMinK、boilingPointMaxK：
        Propellant → Real
      densityMinKgPerM3、densityMaxKgPerM3：
        Propellant → Real
      decompositionTemperatureMinK、
      decompositionTemperatureMaxK：
        Propellant → Real
      theoreticalSpecificImpulseMinMPerS、
      theoreticalSpecificImpulseMaxMPerS：
        Propellant → Real
      unitCount：
        LiquidRocketEngine → Integer
      unitVacuumThrustN：
        LiquidRocketEngine → Real
    - FY-81的9.8～196 N使用vacuumThrustMinN=9.8和vacuumThrustMaxN=196。
    - FY-81的≥2123 m/s使用vacuumSpecificImpulseMinMPerS=2123。
    - FY-83的40、70、300 N使用三个vacuumThrustN assertion。
    - Ariane 5 US-C的6×400 N使用unitCount=6和unitVacuumThrustN=400。

29. 表1.9推进剂组合建模：
    - 表1.9每一行建成PropellantCombination individual，共13个。
    - 声明object feature：
      combinationUsesOxidizer：
        PropellantCombination → Oxidizer
      combinationUsesFuel：
        PropellantCombination → Fuel
    - 声明data feature：
      mixtureRatio：
        PropellantCombination → Real
      combustionTemperatureK：
        PropellantCombination → Real
      theoreticalVacuumSpecificImpulseMPerS：
        PropellantCombination → Real
    - individual的name使用来源中的中文组合名称，例如“液氧-液氢组合”。
    - 不得只创建氧化剂和燃料名称而省略混合比、燃烧室温度和理论真空比冲。

30. 肼的统一建模：
    - 来源中的物质名称统一使用name="肼"，不得创建name="单组元肼"。
    - 单组元发动机通过usesMonopropellant指向“肼”。
    - 表1.7中的分子量、沸点、冰点和密度，以及表1.8中的能量特性，都附在同一个“肼”individual上。
    - 当前阶段将“肼”的type设为Monopropellant。
    - 不得为了表达不同使用方式复制两个“肼”individual。

31. 公式及参数：
    - 公式（1.1）建成Formula individual。
    - 公式参数建成FormulaParameter individual，共6个：
      w_e、gamma、R、T_c_star、p_e、p_in_star。
    - 声明hasParameter：
      kind="ref"、owl_kind="object"、
      owner_type="Formula"、
      range_type="FormulaParameter"。
    - 声明以下String类型data feature：
      symbol、normalizedName、meaning、unitText，
      owner_type均为FormulaParameter。
    - 参数的符号、规范名、含义和单位必须来自原文参数表。
    - 公式的latexExpression、formulaNumber、sourcePage继续分别使用string、string、integer assertion。
    - 公式反斜杠必须按JSON规则转义。

32. 输出前执行完整自检：
    - 所有受控英文type和feature都有非空中文label。
    - 表1.1～1.5中的发动机和明确工况没有遗漏。
    - 表1.6、表1.7、表1.8、表1.9分别覆盖6、7、6、13行。
    - 范围、下界、多值和n×v没有被静默省略或错误压成单值。
    - 每个individual.type引用已声明type。
    - 每个feature.owner_type引用已声明type。
    - 每个object feature.range_type引用已声明type。
    - 每个assertion.property引用已声明且种类匹配的feature。
    - 每个object assertion.value引用已声明individual。
    - data feature.range_type只使用Real、Integer、String、Boolean。
    - assertion.datatype只使用double、integer、string、boolean，不带xsd:前缀。
    - 不得输出xsd:xsd:double、xsd:decimal或xsd:Decimal。
    - 所有顶层数组完整输出，JSON字符串、反斜杠、引号和括号完整闭合。
```
修改：
```python
response = await service.chat(
    messages=[
        {"role": "system", "content": BRIDGE_IM_EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ],
    temperature=0.1,
    max_tokens=65536,
    enable_thinking=False,
)
```
同时把超时提高：
```python
timeout=1200.0
```

当前结果：
- JSON 可以完整解析，不再是 token 截断文件。
- 19 个类型、49 个属性、98 个个体、468 条断言。
- 所有类型、属性和个体都有标签。
- 表1.9的13种推进剂组合已经建模。
- 公式的6个参数已经创建。
- FY-81、FY-82 的推力范围已经拆成最小值和最大值。
- FY-83、FY-84 的多档推力均保留下来。
- Ariane 5 US-C 的 `6×400 N` 已正确拆成数量6和单台推力400 N。
- RD-170、YF-73、YF-75 的数量信息已经补充。
- SysML 中没有 `xsd:xsd:double` 和 `xsd:decimal` 问题。
- 没有重复ID、重复断言和无效来源ID。

需要修复：
- 物质类型与使用角色混在一起
- 两个公式参数引用大小写错误
- 90%过氧化氢重复建模