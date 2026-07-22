---
created: 2026-07-22T10:55
updated: 2026-07-22T10:58
---
# SysML v2 文本语法速查表（适配你的本体项目，初学者版）
> 适用场景：`ontology-builder`自动生成、`sysml-owl-bridge`转换OWL，**重点聚焦结构建模**，行为建模仅作拓展

## 一、基础区分（重中之重，最容易混淆）
| 写法                | 含义                         | 类比            | 对应OWL             | 使用位置      |
| ----------------- | -------------------------- | ------------- | ----------------- | --------- |
| `item def XXX`    | **类型定义（蓝图/模板）**，描述一类事物共有特征 | `class XXX`   | `owl:Class`       | 顶层，定义概念   |
| `item xxx : Type` | **独立实例**，独立存在的实体           | `obj = XXX()` | `NamedIndividual` | 模板之外，独立个体 |
| `part xxx : Type` | **部件实例**，属于某个系统内部组成部分      | 复合对象内部成员      | `NamedIndividual` | 系统内部的组件   |

> 口诀：带`def`是模板；不带def是实物；`part`强调「整体包含部分」。

## 二、包管理 `package`
作用：命名空间，区分领域，防止名字冲突
```sysml
package RocketEngineDomain {
  // 所有类型、实例写在这里
}
```

## 三、泛化（继承 `:>`）
语义：**is-a （是一种）**
```sysml
item def LiquidEngine :> RocketEngine {
}
```
翻译：液体发动机 是一种 火箭发动机
映射OWL：`LiquidEngine rdfs:subClassOf RocketEngine`

## 四、模板内部成员（写在 `XXX def {}` 大括号内）
### 1. `ref` 对象关联（关系声明）
语法：
```sysml
ref 关系名 : 目标类型 [多重度];
```
语义：该类型**可以关联其他类型**，只定义“允许有什么关系”，不填具体值。

#### 多重度基数速查
| 写法 | 含义 |
| ---- | ---- |
| `[0..1]` | 可选，最多1个，可以为空 |
| `[1..1]` | 必填，恰好1个 |
| `[0..*]` | 0个或任意多个（最常用） |
| `[1..*]` | 至少1个 |

示例：
```sysml
ref hasCycle : CycleType [0..1];
```

### 2. `attribute` 数据属性（参数声明）
语法：
```sysml
attribute 参数名 : 数据类型;
```
示例：
```sysml
attribute chamberPressureMPa : xsd:Decimal;
```

## 五、实例内部赋值（写在 `part / item {}` 内部）
> `def`里只声明结构；**实例内部填写具体取值**
### 1. 关联赋值（绑定别的实例）
```sysml
part usesOxidizer = liquidOxygen;
```
### 2. 属性赋值（xsd字面量语法）
格式：`"数值"^^xsd:类型`
```sysml
attribute vacuumThrustN = "1000000"^^xsd:decimal;
```

## 六、常用XSD基础数据类型（SysML ↔ OWL通用）
```
xsd:String     字符串
xsd:Integer    整数
xsd:Decimal    小数（推力、压力优先用，比float精度高）
xsd:Boolean    布尔 true/false
xsd:Float
xsd:Double
```

## 七、连接关系 `connect`（部件接口交互）
表达两个部件之间存在流体/电气接口
```sysml
connect engine.fuelInlet to tank.outlet;
```

## 八、约束（拓展，本体可映射规则公理）
```sysml
constraint def PositiveThrust {
    vacuumThrustN > 0;
}
```

## 九、完整标准模板范例（直接参考格式）
```sysml
package EngineDomain {
    // 1. 定义父类模板
    item def RocketEngine;

    // 2. 定义子类模板（继承）
    item def LiquidRocketEngine :> RocketEngine {
        ref usesOxidizer : Oxidizer [0..*];
        ref usesFuel : Fuel [0..*];
        attribute vacuumThrustN : xsd:Decimal;
    }

    // 3. 基础概念模板
    item def Oxidizer;
    item def Fuel;

    // 4. 独立实例
    item liquidOxygen : Oxidizer;
    item kerosene : Fuel;

    // 5. 部件实例（你代码自动生成的样式）
    part rD107 : LiquidRocketEngine {
        part usesOxidizer = liquidOxygen;
        part usesFuel = kerosene;
        attribute vacuumThrustN = "1000000"^^xsd:decimal;
    };
}
```

## 十、初学者高频易错清单
1. ❌ `:>` 不是大于号，是SysML专属继承符号
2. ❌ 不要在 `item def{}` 里面写 `part xxx = xxx`
   → def只声明结构，赋值只能写在实例（part/item）中
3. ❌ 多重度不能丢：`ref` 必须带 `[a..b]`
4. ❌ `"123"^^xsd:decimal` 引号不能省略，是标准字面量格式
5. ✅ 转换链路记忆：
文档文本 → BridgeIM → 生成`item def`（类）+`part`（实例） → sysml-owl-bridge → TTL本体

## 十一、和你项目命令链路对应
`render_bridge_im_to_sysml()`
1. BridgeIM里的概念 → 输出 `item def`
2. BridgeIM里具体装备实例 → 输出 `part xxx : Type { ... }`
