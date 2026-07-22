---
created: 2026-07-22T11:31
updated: 2026-07-22T11:31
---
# BridgeIM JSON ↔ SysML v2 Text ↔ OWL(Turtle) 完整映射清单
> 适配项目链路：LLM输出 → BridgeIM(JSON) → SysML渲染 → sysml-owl-bridge → OWL本体
> 可直接复制进 Obsidian

## 0. 顶层全局配置映射
| BridgeIM JSON | SysML v2 | OWL(Turtle) | 说明 |
| ---- | ---- | ---- | ---- |
| `"base_iri": "http://ex.org/engine#"` | 隐式全局命名空间 | `@prefix : <http://ex.org/engine#> .` | 所有实体URI根前缀 |
| `"prefixes": {"xsd":"http://www.w3.org/2001/XMLSchema#"}` | 隐式导入xsd类型 | `@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .` | 标准数据类型命名空间 |
| `"name": "Chapter01Model"` | `package Chapter01Model{}`（近似） | `:Chapter01Model rdf:type owl:Ontology` | 模型标识名称 |

## 1. 类型定义 `types[]`（对应 OWL Class / SysML item def）
JSON模板
```json
{
  "name": "LiquidRocketEngine",
  "kind": "item",
  "super_types": ["RocketEngine"],
  "equivalent_expression": null,
  "description": "液体火箭发动机"
}
```

| BridgeIM JSON | SysML v2 | OWL Turtle |
| ---- | ---- | ---- |
| `"name":"LiquidRocketEngine"` | `item def LiquidRocketEngine` | `:LiquidRocketEngine rdf:type owl:Class .` |
| `"kind":"item"` | `item def XXX` | `owl:Class`（系统/物理实体类） |
| `"super_types":["RocketEngine"]` | `item def LiquidRocketEngine :> RocketEngine` | `:LiquidRocketEngine rdfs:subClassOf :RocketEngine .` |
| `"description":"xxx"` | `// 液体火箭发动机`（注释） | `:LiquidRocketEngine rdfs:label "液体火箭发动机" .` |
| `"equivalent_expression":["A"]` | 无原生语法 | `:LiquidRocketEngine owl:equivalentClass :A .` |

## 2. 属性定义 `features[]`
### 2.1 对象关联属性 `kind":"ref"` → OWL ObjectProperty
```json
{
  "name": "usesOxidizer",
  "kind": "ref",
  "owl_kind": "object",
  "owner_type": "LiquidRocketEngine",
  "range_type": "Oxidizer",
  "min_cardinality": 0,
  "max_cardinality": null
}
```

| BridgeIM JSON | SysML v2 | OWL Turtle |
| ---- | ---- | ---- |
| `"name":"usesOxidizer"` | `ref usesOxidizer : Oxidizer [0..*];` | `:usesOxidizer rdf:type owl:ObjectProperty .` |
| `"owner_type":"LiquidRocketEngine"` | 写在`item def LiquidRocketEngine{}`内部 | `:usesOxidizer rdfs:domain :LiquidRocketEngine .` |
| `"range_type":"Oxidizer"` | `ref ... : Oxidizer` | `:usesOxidizer rdfs:range :Oxidizer .` |
| min=0,max=null | `[0..*]` | 默认无强制基数公理 |
| min=1,max=1 | `[1..1]` | 基数约束 Restriction |
| `"sub_property_of":"hasConsumable"` | 无原生语法 | `:usesOxidizer rdfs:subPropertyOf :hasConsumable .` |

### 2.2 数据属性 `kind":"attribute"` → OWL DatatypeProperty
```json
{
  "name": "vacuumThrustN",
  "kind": "attribute",
  "owl_kind": "datatype",
  "owner_type": "LiquidRocketEngine",
  "range_datatype": "xsd:Decimal"
}
```

| BridgeIM JSON | SysML v2 | OWL Turtle |
| ---- | ---- | ---- |
| `"name":"vacuumThrustN"` | `attribute vacuumThrustN : xsd:Decimal;` | `:vacuumThrustN rdf:type owl:DatatypeProperty .` |
| `"owner_type":"LiquidRocketEngine"` | 位于`item def LiquidRocketEngine{}` | `:vacuumThrustN rdfs:domain :LiquidRocketEngine .` |
| `"range_datatype":"xsd:Decimal"` | `: xsd:Decimal` | `:vacuumThrustN rdfs:range xsd:decimal .` |

## 3. 实例个体 `features[]` 内带 `"type":"XXX"` 的条目（NamedIndividual）
```json
{
  "name": "liquidOxygen",
  "type": "Oxidizer",
  "anonymous": false,
  "assertions": [
    {
      "kind": "data",
      "property": "molecularWeight",
      "value": "32",
      "datatype": "xsd:decimal"
    }
  ]
}
```

| BridgeIM JSON | SysML v2 | OWL Turtle |
| ---- | ---- | ---- |
| `"name":"liquidOxygen"` | `item liquidOxygen : Oxidizer;` | `:liquidOxygen rdf:type owl:NamedIndividual .` |
| `"type":"Oxidizer"` | `item liquidOxygen : Oxidizer` | `:liquidOxygen rdf:type :Oxidizer .` |
| `"anonymous":false` | 具名 `item / part` | NamedIndividual；true=空白节点`[]` |

### 3.1 实例内部：数据断言 `kind:"data"`
BridgeIM
```json
{
  "kind": "data",
  "property": "molecularWeight",
  "value": "32",
  "datatype": "xsd:decimal"
}
```
SysML
```sysml
attribute molecularWeight = "32"^^xsd:decimal;
```
OWL
```turtle
:liquidOxygen :molecularWeight "32"^^xsd:decimal .
```

### 3.2 实例内部：对象关联断言（实体之间相互引用）
BridgeIM逻辑：个体`YF100` → 属性`usesOxidizer` → 个体`liquidOxygen`
SysML
```sysml
part YF100 : LiquidRocketEngine {
    part usesOxidizer = liquidOxygen;
}
```
OWL
```turtle
:YF100 :usesOxidizer :liquidOxygen .
```

## 4. 多重度对照表
| JSON min/max | SysML多重度 | 业务含义 |
| ---- | ---- | ---- |
| min=0, max=null | `[0..*]` | 0个或多个 |
| min=1, max=null | `[1..*]` | 至少1个 |
| min=0, max=1 | `[0..1]` | 可选，最多1个 |
| min=1, max=1 | `[1..1]` | 必须恰好1个 |

## 5. 高级本体公理映射
| BridgeIM JSON Key | SysML v2 | OWL Turtle |
| ---- | ---- | ---- |
| `"disjoint_classes": [["A","B"]]` | 无原生语法支持 | `:A owl:disjointWith :B .` |
| `"disjoint_unions"` | 无原生支持 | `owl:disjointUnionOf` |
| `"property_axioms": {"transitive":["propA"]}` | 无原生支持 | `:propA rdf:type owl:TransitiveProperty .` |
| `"rules":[]` | 无原生支持 | SWRL推理规则 |
| `"annotations":[]` | `// 注释文本` | `rdfs:comment, rdfs:label` |

## 6. 完整三合一最小示例（可直接测试）
### BridgeIM JSON
```json
{
  "base_iri":"http://example.org/engine#",
  "types":[
    {"name":"RocketEngine","kind":"item","super_types":[]},
    {"name":"LiquidRocketEngine","kind":"item","super_types":["RocketEngine"]},
    {"name":"Oxidizer","kind":"item","super_types":[]}
  ],
  "features":[
    {
      "name":"usesOxidizer",
      "kind":"ref",
      "owl_kind":"object",
      "owner_type":"LiquidRocketEngine",
      "range_type":"Oxidizer",
      "min_cardinality":0,
      "max_cardinality":null
    },
    {
      "name":"liquidOxygen",
      "type":"Oxidizer",
      "anonymous":false,
      "assertions":[]
    },
    {
      "name":"YF100",
      "type":"LiquidRocketEngine",
      "anonymous":false,
      "assertions":[]
    }
  ]
}
```

### 渲染输出 SysML v2
```sysml
package Model {
item def RocketEngine;
item def Oxidizer;
item def LiquidRocketEngine :> RocketEngine {
    ref usesOxidizer : Oxidizer [0..*];
}

item liquidOxygen : Oxidizer;
part YF100 : LiquidRocketEngine {
    part usesOxidizer = liquidOxygen;
}
}
```

### sysml-owl-bridge 输出 Turtle
```turtle
@prefix : <http://example.org/engine#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

:RocketEngine rdf:type owl:Class .
:Oxidizer rdf:type owl:Class .
:LiquidRocketEngine rdf:type owl:Class ;
    rdfs:subClassOf :RocketEngine .

:usesOxidizer rdf:type owl:ObjectProperty ;
    rdfs:domain :LiquidRocketEngine ;
    rdfs:range :Oxidizer .

:liquidOxygen rdf:type owl:NamedIndividual, :Oxidizer .
:YF100 rdf:type owl:NamedIndividual, :LiquidRocketEngine ;
    :usesOxidizer :liquidOxygen .
```

## ⚠️ 重要工程提示
1. 流向单向：**BridgeIM → SysML**；SysML文本无法无损还原全部BridgeIM公理（传递属性、不相交类等信息会丢失）；
2. SysML v2 侧重结构建模，缺少大量OWL本体公理表达能力；
3. 所有数值字面量统一格式 `"数值"^^xsd:Decimal`，三者互通；
4. 你项目中 `--mode im-bridge` 整条链路就是基于这套映射规则执行。
