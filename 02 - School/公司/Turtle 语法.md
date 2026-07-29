---
created: 2026-07-16T09:31
updated: 2026-07-29T16:28
---
# Turtle（Terse RDF Triple Language）阅读笔记
适配你当前 **SysMLv2 → OWL 火箭发动机本体（.ttl）**，结合你这份文件逐段对应讲解，所有例子全部取自你粘贴的代码，拿来直接对照看本体文件。
> 适用场景：读懂 ontology-builder 工具自动输出的 ttl、排查三元组、看懂类/属性/实例、理解SysML桥接生成规则

## 一、基础概念前置
1. **RDF 核心：三元组 `主语 谓语 宾语`**
   `Subject Predicate Object`
   所有 Turtle 文件本质就是批量写三元组。
2. **OWL = 在RDF基础上定义本体词汇（类、属性、约束）**
   - TBox：**模式层**（Class类、ObjectProperty对象属性、DatatypeProperty数据属性）
   - ABox：**实例层**（NamedIndividual个体/实例，发动机、推进剂具体对象）
> 你的文件结构严格遵循：前缀 → 注解属性 → 对象属性 → 数据属性 → 类(TBox) → 个体实例(ABox)，标准工程OWL输出结构。

## 二、前缀 `@prefix`（文件最顶部）
```turtle
@prefix : <http://example.org/rocket-engine/chapter01#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```
### 含义
把长URI起别名，简化书写
- `:CombustionChamber` 完整展开 = `<http://example.org/rocket-engine/chapter01#CombustionChamber>`
- `xsd:double` = XML标准数据类型
- `owl:` OWL本体标准词汇库
- `rdfs:` 注释、子类关系标准词汇

`@base <xxx#> .` ：设置默认基准URI，和上面默认前缀保持一致。

> ⚠️ 工程要点：你每个章节本体 `chapter01#`、chapter02# URI不一样，**跨章节实例引用会找不到实体**，也就是你之前遇到的`unknown object target`报错根源！

## 三、四种顶层元素（和你的ttl段落一一对应）
### 1. AnnotationProperty 注解属性
```turtle
<http://omg.org/sysml/v2#featureKind> rdf:type owl:AnnotationProperty .
```
**作用：附加备注元信息，不参与逻辑推理，仅用来记录来源（SysML桥接标记）**
你文件里：`<http://omg.org/sysml/v2#featureKind> "REFERENCE"`
含义：这条属性来源于SysMLv2的「Reference特性」，是**本体生成器自带的桥接注解**，不是业务语义。

常用通用注解属性（全局标准）
- `rdfs:comment "文字"` 中文注释、来源文件路径（你文件大量存在）

### 2. ObjectProperty 对象属性（关联【实体 ↔ 实体】）
```turtle
:hasCombustionChamber rdf:type owl:ObjectProperty ;
                      rdfs:range :CombustionChamber ;
                      <http://omg.org/sysml/v2#featureKind> "REFERENCE" ;
                      rdfs:comment "包含燃烧室" .
```
逐行拆解
1. `:hasCombustionChamber rdf:type owl:ObjectProperty .`
声明：`hasCombustionChamber` 是一条**对象关系**
2. `rdfs:range :CombustionChamber`
值域约束：这条关系指向的对象，必须是`CombustionChamber（燃烧室）`类的实例
> 通俗：A hasCombustionChamber B → B只能是燃烧室

符号规则：
- `;` ：主语复用，省略重复主语（最常用简写！）
- `.` 代表**一条完整三元组段落结束**

### 3. DatatypeProperty 数据属性（实体 ↔ 字面量/数值/字符串）
```turtle
:vacuumThrustN rdf:type owl:DatatypeProperty ;
                rdfs:range xsd:double ;
                rdfs:comment "真空推力" .
```
含义：用来存放**数字、文本**，不能指向实体
示例实例中使用：
```turtle
:f1 :vacuumThrustN "7776000.0"^^xsd:double .
```
`^^xsd:double` = 强制标记字面量数据类型，区分字符串和数字。

### 4. owl:Class 类定义（TBox，概念模板）
```turtle
:LiquidRocketEngine rdf:type owl:Class ;
                    rdfs:subClassOf :RocketEngine ;
                    rdfs:comment "液体火箭发动机" .
```
- `rdfs:subClassOf :RocketEngine`  **继承关系！子类**
LiquidRocketEngine（液体发动机） ⊆ RocketEngine（火箭发动机）
> 对应SysML：PartDef / ItemDef，由`<http://omg.org/sysml/v2#metaclass> "PART_DEF"`标记区分

### 5. NamedIndividual 实例/个体（ABox，真实对象）
```turtle
:f1 rdf:type owl:NamedIndividual ,
               :LiquidRocketEngine ;
    :chamberPressureMPa "6.67"^^xsd:double ;
    rdfs:comment "F-1" .
```
解读：
1. `:f1` 是一个实例
2. 类型是 `LiquidRocketEngine`（液体火箭发动机类）
3. 拥有属性：燃烧室压力 = 6.67 MPa
> `,` 逗号：同一个主语，**多个类型**，等价多条rdf:type三元组

## 四、高频语法符号速查表（重点！查询ttl必备）
| 符号 | 作用 | 示例 |
|------|------|------|
| `.` | 段落终止，三元组组结束 | `:a rdfs:comment "xxx" .` |
| `;` | 主语复用，谓语宾语续写 | `:a rdf:type owl:Class ; rdfs:label "A类" .` |
| `,` | 谓语不变，多个宾语 | `:a rdf:type :B , :C .` |
| `"文本"` | 字符串字面量 | `"真空推力"` |
| `"123"^^xsd:double` | 带类型的数值 | 本体所有物理参数都采用这种写法 |
| `<完整URI>` | 原始URI | 不使用前缀简写 |

## 五、最常用标准谓词词典（直接检索ttl用）
### rdfs 系列（本体基础语义）
1. `rdf:type` 【最重要】
`X rdf:type Y` → X 属于 Y 类型
例子：`:f1 rdf:type :LiquidRocketEngine`
👉 F1发动机 是 液体火箭发动机 的实例

2. `rdfs:subClassOf`
`A rdfs:subClassOf B` → A是B的子类（继承）

3. `rdfs:comment`
中文说明、备注、文件来源路径（你文件大量存在）

### owl 系列（本体类型声明）
1. `owl:Class` 类
2. `owl:ObjectProperty` 对象关系
3. `owl:DatatypeProperty` 数值/文本属性
4. `owl:NamedIndividual` 实体实例

## 六、结合你的项目常见查询句式（复制到Protegé / rdflib直接检索）
### 场景1：查询所有液体火箭发动机实例（ABox查询）
```sparql
PREFIX : <http://example.org/rocket-engine/chapter01#>
SELECT ?engine WHERE {
    ?engine rdf:type :LiquidRocketEngine .
}
```
### 场景2：查找真空推力大于1000000N的发动机
```sparql
PREFIX : <http://example.org/rocket-engine/chapter01#>
SELECT ?engine ?thrust WHERE {
    ?engine rdf:type :LiquidRocketEngine ;
            :vacuumThrustN ?thrust .
    FILTER(?thrust > 1000000)
}
```

## 七、踩坑清单（贴合你ontology-builder生成的ttl）
1. ❌ 不要混淆 `ObjectProperty` 和 `DatatypeProperty`
对象属性只能指向`:xxx`实体，不能写数字；数据属性只能放数字/字符串
2. ❌ 章节隔离问题
`chapter01#` 实例无法引用 `chapter02#` 的实体 → 产生`引用校验失败`
3. ❌ 不要忽略 `^^xsd:xxx`
没有类型标记，SPARQL数值比较会失效，字符串无法和数字对比
4. 桥接注解区分
`<http://omg.org/sysml/v2#xxxx>` 全部是生成器附加标记，**不属于业务本体语义**，推理可以忽略

## 八、快速阅读模板（拿到任意一条TTL套用）
通用阅读公式：
`主语 谓语 宾语 .`
1. 找到第一个标识符=主语
2. `;` 后面全部共用这个主语
3. 判断谓语：
   - rdf:type → 【类型】
   - rdfs:subClassOf → 【继承】
   - rdfs:comment → 【注释】
   - :xxx（自定义名称）→ 业务属性
4. 宾语区分：
   - 以`:`开头 → **实体（类/实例）**
   - 带`""` → **字面量（文本、数值）**

如果你需要，我可以把这份笔记精简成 **Obsidian Markdown纯净版本**，方便你本地永久保存，后续调试ttl随时查阅。