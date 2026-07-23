---
created: 2026-07-22T15:36
updated: 2026-07-23T16:19
---
有。最合适的做法是增加一次 `--prompt-file` 扩展能力，把领域规则放在项目外的 Markdown 文件中。以后换发动机类型只换参数，不再修改 [prompts.py](D:/Work/projects/ontology-builder/src/ontology_builder_agent/prompts.py)。

注意：下面的 `--prompt-file` 是建议新增的功能，当前 CLI 还不能直接执行。

## 推荐结构

```
D:\Work\projects\ontology-builder-work\
└─ prompt-profiles\
   ├─ bridge-common.md
   ├─ liquid-rocket-engine.md
   ├─ solid-rocket-engine.md
   ├─ diesel-engine.md
   └─ aero-engine.md
```

职责分开：

- `prompts.py`：稳定的 JSON 格式、字段结构等基础规则。
- `bridge-common.md`：Java bridge 数据类型、命名、引用完整性等通用规则。
- 各领域文件：该发动机领域自己的分类、属性和语义约束。
- `reviewed.md`/`faithful.md`：只放文献事实，不混入建模规则。

## 命令最终应当这样使用

液体火箭发动机：

```
python -m ontology_builder_agent from-file `
  "D:\Work\projects\ontology-builder-work\rocket-engine-ontology\per-document\chapter01-reviewed.md" `
  --out "D:\Work\projects\ontology-builder-work\rocket-engine-ontology\reports\v3\chapter01.ttl" `
  --emit-bridge-im "D:\Work\projects\ontology-builder-work\rocket-engine-ontology\reports\v3\chapter01.bridge-im.json" `
  --emit-sysml "D:\Work\projects\ontology-builder-work\rocket-engine-ontology\reports\v3\chapter01.sysml" `
  --base-iri "http://example.org/rocket-engine/chapter01#" `
  --mode im-bridge `
  --prompt-file "D:\Work\projects\ontology-builder-work\prompt-profiles\bridge-common.md" `
  --prompt-file "D:\Work\projects\ontology-builder-work\prompt-profiles\liquid-rocket-engine.md" `
  --dry-run
```

以后处理柴油发动机只需要替换：

```
--prompt-file ...\diesel-engine.md
```

不需要修改 Python 源码。

## 通用规则文件示例

`bridge-common.md`：

```
# Bridge 通用抽取约束

1. 只输出符合 BridgeIMDraft 的完整 JSON object。
2. feature.range_type 只使用：
   - Real
   - Integer
   - String
   - Boolean
   - 或已声明的本体类型名称
3. 数据断言的 datatype 使用：
   - xsd:double
   - xsd:integer
   - xsd:string
   - xsd:boolean
4. sourcePage 使用 Integer 和 xsd:integer。
5. object assertion 的 property 必须是已声明的 object feature。
6. data assertion 的 property 必须是已声明的 data feature。
7. object assertion 的 target 必须是已声明的 individual。
8. 不得根据常识补充原文没有提供的型号、性能和组成信息。
9. 无法确认的事实省略，不得猜测。
10. 输出紧凑 JSON，不输出 Markdown 代码围栏和解释。
```

## 液体火箭发动机规则示例

`liquid-rocket-engine.md`：

```
# 液体火箭发动机领域规则

## 核心类型

- RocketEngine
- LiquidRocketEngine，继承 RocketEngine
- EngineComponent
- ThrustChamber，继承 EngineComponent
- CombustionChamber，继承 EngineComponent
- Nozzle，继承 EngineComponent
- Valve，继承 EngineComponent
- Regulator，继承 EngineComponent
- Propellant
- Oxidizer，继承 Propellant
- Fuel，继承 Propellant
- Monopropellant，继承 Propellant
- CycleType
- SupplySystemType
- MissionRole
- Formula

## 对象属性

- usesOxidizer：LiquidRocketEngine → Oxidizer
- usesFuel：LiquidRocketEngine → Fuel
- usesMonopropellant：LiquidRocketEngine → Propellant
- hasCycle：LiquidRocketEngine → CycleType
- hasSupplySystemType：LiquidRocketEngine → SupplySystemType
- hasMissionRole：LiquidRocketEngine → MissionRole
- hasComponent：LiquidRocketEngine → EngineComponent
- hasThrustChamber：LiquidRocketEngine → ThrustChamber
- hasCombustionChamber：LiquidRocketEngine → CombustionChamber
- hasNozzle：LiquidRocketEngine → Nozzle

## 语义约束

- 单组元发动机使用 usesMonopropellant，不使用 usesFuel 表达推进剂。
- staged combustion、gas generator 等属于 CycleType。
- pressure-fed、pump-fed 等属于 SupplySystemType。
- space shuttle main propulsion 等用途属于 MissionRole。
- “三组元发动机”是推进剂组合分类，不是 MissionRole。
- 不要假设每台发动机恰好有一个推力室、燃烧室或喷管。
```

其他领域文件同理。例如柴油发动机中定义：

```
DieselEngine
Cylinder
Piston
Crankshaft
FuelInjector
Turbocharger
usesFuel
hasCylinder
hasCompressionRatio
ratedPowerKW
ratedSpeedRpm
```

不要把液体火箭的 `usesOxidizer`、`hasCycle` 等约束带入柴油机。

## 代码只需要改一次

建议增加：

```
--prompt-file PATH
```

并允许多次传入。处理链为：

```
内置基础 prompt
    + bridge-common.md
    + 当前领域 profile
    + 原始文档内容
```

领域规则必须附加到 system message，而不是拼进 `reviewed.md`。这样模型能区分：

- 哪些是抽取规则；
- 哪些是 PDF 中的事实。

还建议把所用 profile 的路径和 SHA-256 写入生成 JSON 的 `metadata`，例如：

```
{
  "metadata": {
    "prompt_profiles": [
      {
        "path": "bridge-common.md",
        "sha256": "..."
      },
      {
        "path": "liquid-rocket-engine.md",
        "sha256": "..."
      }
    ]
  }
}
```

这样过几个月也能知道某份本体是根据哪版规则生成的。

## 当前源码中的规则怎么处理

你已经加在 `prompts.py` 中的规则需要分类迁移：

- JSON 格式、bridge 数据类型、禁止编造、引用完整性：移到 `bridge-common.md`，或者保留为项目通用基础规则。
- `LiquidRocketEngine`、推进剂、循环、推力室、RD-701 等：移到 `liquid-rocket-engine.md`。
- 不要把具体型号事实写进 profile；型号性能应当只来自输入文献。

这套方案既能避免每次修改源代码，也能显著减少以后更新 `ontology-builder` 时的 Git 冲突。`enable_thinking=False`、`max_tokens` 和 `timeout` 属于 LLM 运行参数，与领域 profile 无关，不需要随发动机类型改变。