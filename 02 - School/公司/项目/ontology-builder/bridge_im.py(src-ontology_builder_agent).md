---
created: 2026-07-13T15:05
updated: 2026-07-13T16:09
---
# `ontology-builder/src/ontology_builder_agent/bridge_im.py`
## 01
```python
def bridge_im_from_ontology_model(model: OntologyModel) -> BridgeIMDraft:
    types = [
        BridgeIMType(
            name=ontology_class.name,
            kind="item",
            super_types=ontology_class.parents,
            description=ontology_class.description,
        )
        for ontology_class in model.classes
    ]
    features: list[BridgeIMFeature] = []
    for prop in model.object_properties:
        features.append(
            BridgeIMFeature(
                name=prop.name,
                kind="ref",
                owl_kind="object",
                owner_type=prop.domain,
                range_type=prop.range,
                min_cardinality=prop.min_cardinality,
                max_cardinality=prop.max_cardinality,
                description=prop.description,
            )
        )
    for prop in model.datatype_properties:
        features.append(
            BridgeIMFeature(
                name=prop.name,
                kind="attribute",
                owl_kind="data",
                owner_type=prop.domain,
                range_type=prop.range,
                description=prop.description,
                unit=prop.unit,
            )
        )
    individuals: list[BridgeIMIndividual] = []
    for individual in model.individuals:
        assertions = [
            BridgeIMAssertion(kind="data", property=name, value=value)
            for name, value in individual.properties.items()
        ]
        individuals.append(BridgeIMIndividual(name=individual.name, type=individual.type, assertions=assertions))
    annotations = [BridgeIMAnnotation(target=name, value=value) for name, value in model.annotations.items()]
    return BridgeIMDraft(
        base_iri=model.base_iri,
        name=model.name,
        types=types,
        features=features,
        individuals=individuals,
        annotations=annotations,
        metadata={"source_dto": "OntologyModel"},
    )
```
### 一、函数整体定位与作用
#### 1. 核心功能
这是**数据格式转换函数**：
输入：之前整套流程生成的 `OntologyModel`（OWL 风格本体内存模型）
输出：`BridgeIMDraft`（SysML/BridgeIM 中间草稿模型）
简单说：把语义本体（OWL）数据，翻译成桥梁建模框架 BridgeIM 能识别的标准化结构，实现「文本抽取本体 → 转换为工程建模模型」的数据流转。

#### 2. 前置依赖说明
代码依赖4个目标侧数据类（输出侧）：
- `BridgeIMType`：对应本体Class，建模里的 item 类型
- `BridgeIMFeature`：对应对象属性/数据属性，建模的关联、字段特征
- `BridgeIMIndividual`：本体实例个体
- `BridgeIMAssertion`：实例的属性赋值断言
- `BridgeIMAnnotation`：全局注解
- `BridgeIMDraft`：最终打包的完整建模草稿容器

### 二、函数入参、返回值总览
```python
def bridge_im_from_ontology_model(model: OntologyModel) -> BridgeIMDraft:
```
- 入参 `model: OntologyModel`：完整清洗校验后的本体对象（包含classes、properties、individuals、annotations）
- 返回 `BridgeIMDraft`：转换完成、适配BridgeIM建模规范的中间模型

### 三、分段逐行拆解转换逻辑
#### 3.1 转换本体类 OntologyClass → BridgeIMType
```python
types = [
    BridgeIMType(
        name=ontology_class.name,
        kind="item",
        super_types=ontology_class.parents,
        description=ontology_class.description,
    )
    for ontology_class in model.classes
]
```
1. 列表推导式，循环遍历本体所有概念类 `model.classes`；
2. 一一映射字段：
   - `name`：类名称；
   - `kind="item"`：固定标记为SysML item类型（和最开始生成SysML代码逻辑对应）；
   - `super_types`：父类列表，继承关系直接透传；
   - `description`：类描述注释；
3. 所有转换后的类型存入 `types` 列表，作为建模框架的基础类型库。

#### 3.2 转换 ObjectProperty（对象关系）→ BridgeIMFeature（关联特征）
```python
features: list[BridgeIMFeature] = []
for prop in model.object_properties:
    features.append(
        BridgeIMFeature(
            name=prop.name,
            kind="ref",
            owl_kind="object",
            owner_type=prop.domain,
            range_type=prop.range,
            min_cardinality=prop.min_cardinality,
            max_cardinality=prop.max_cardinality,
            description=prop.description,
        )
    )
```
1. `object_properties` 是类与类之间的关联（hasXxx）；
2. 标记区分类型：
   - `kind="ref"`：建模侧标记为**引用关系**；
   - `owl_kind="object"`：标记来源是OWL对象属性；
3. 关键字段映射：
   - `owner_type = domain`：归属的主体类；
   - `range_type = range`：关联指向的目标类；
   - `min_cardinality/max_cardinality`：基数约束（最少/最多关联几个对象）；
4. 全部关联特征统一放入 `features` 列表。

#### 3.3 转换 DatatypeProperty（数据字段）→ BridgeIMFeature（属性特征）
```python
for prop in model.datatype_properties:
    features.append(
        BridgeIMFeature(
            name=prop.name,
            kind="attribute",
            owl_kind="data",
            owner_type=prop.domain,
            range_type=prop.range,
            description=prop.description,
            unit=prop.unit,
        )
    )
```
1. 遍历本体数据属性（实体的字符串/数字字段）；
2. 区分标识：
   - `kind="attribute"`：建模侧普通属性字段；
   - `owl_kind="data"`：标记来源是OWL数据属性；
3. 独有字段 `unit=prop.unit`：数据单位（如kg、V），对象关系没有这个字段；
4. 和上面的对象ref共用同一个 `features` 列表，框架统一管理所有特征。

#### 3.4 转换 Individual 实例个体 → BridgeIMIndividual
```python
individuals: list[BridgeIMIndividual] = []
for individual in model.individuals:
    assertions = [
        BridgeIMAssertion(kind="data", property=name, value=value)
        for name, value in individual.properties.items()
    ]
    individuals.append(BridgeIMIndividual(name=individual.name, type=individual.type, assertions=assertions))
```
1. 遍历本体实例（如：类=电池，实例=48V锂电池）；
2. 内层列表推导式：把实例的 `properties` 键值对转为 `BridgeIMAssertion` 断言；
   - `kind="data"`：代表给数据属性赋值；
   - `property`：属性名，`value`：属性具体值；
3. 组装实例：
   - `name`：实例名称；
   - `type`：归属的本体类名；
   - `assertions`：该实例所有属性赋值记录；
4. 存入 `individuals` 列表。

#### 3.5 全局注解 annotations 转换
```python
annotations = [BridgeIMAnnotation(target=name, value=value) for name, value in model.annotations.items()]
```
本体顶层注解字典，批量转为建模注解对象：
- `target`：注解标识key（label/comment等）
- `value`：注解文本内容

#### 3.6 组装并返回完整 BridgeIMDraft
```python
return BridgeIMDraft(
    base_iri=model.base_iri,
    name=model.name,
    types=types,
    features=features,
    individuals=individuals,
    annotations=annotations,
    metadata={"source_dto": "OntologyModel"},
)
```
1. 把上面所有转换好的集合全部塞进目标模型；
2. 保留本体原始 `base_iri`、本体名称；
3. 额外增加 `metadata` 元数据，标记这份建模草稿来源于 `OntologyModel`，方便日志、溯源区分数据源；
4. 返回完整可用于生成SysML代码、导出建模文件的中间对象。

### 四、完整数据流串联（整套代码链路）
1. 输入自然文本 → `fallback_im_from_text` 抽取实体、关系、属性 → 生成原始 `OntologyModel`；
2. `OntologyModel` 内置校验器自动执行 `deduplicate_model`、`validate_references`，清洗修复本体；
3. 调用本函数 `bridge_im_from_ontology_model`：**OWL本体 → BridgeIM工程建模模型**；
4. 拿到 `BridgeIMDraft` 后，后续代码可基于它生成标准SysML文本、导出建模文件。

### 五、核心映射对照表（一眼看懂两边对应关系）
| OntologyModel 本体结构 | BridgeIMDraft 建模结构 | 类型标记 |
| ---- | ---- | ---- |
| OntologyClass | BridgeIMType | kind="item" |
| ObjectProperty | BridgeIMFeature | kind="ref", owl_kind="object" |
| DatatypeProperty | BridgeIMFeature | kind="attribute", owl_kind="data" |
| Individual | BridgeIMIndividual | 携带属性断言 Assertion |
| annotations 字典 | BridgeIMAnnotation 列表 | 全局备注 |

### 六、初学者重点知识点
1. **DTO转换思想**：两套不同业务模型之间做字段映射，无业务逻辑，只做结构翻译；
2. 列表推导式简化批量实例化代码；
3. 同一目标载体区分来源类型（owl_kind / kind），上层渲染代码可以根据标记生成不同SysML语法；
4. 元数据 metadata 用于溯源，区分数据来源；
5. 字段透传设计：描述、基数、单位、父类等元信息完整保留，不丢失本体原有信息；
6. 分层存储：类型、特征、实例、注解完全分离，符合建模软件分层结构。

---
## 02
```python
class BridgeIMDraft(BaseModel):
    """Bridge-aligned Python DTO.

    This is intentionally a draft/adaptor DTO: the canonical IM implementation remains
    the Java IM in sysmlv2-owl-bridge. The builder renders this DTO to bridge-supported
    SysML text and lets BridgeCli perform the authoritative SysML→OWL mapping.
    """

    base_iri: str
    name: str = "GeneratedOntology"
    prefixes: dict[str, str] = Field(default_factory=dict)
    types: list[BridgeIMType] = Field(default_factory=list)
    features: list[BridgeIMFeature] = Field(default_factory=list)
    individuals: list[BridgeIMIndividual] = Field(default_factory=list)
    keys: list[BridgeIMKey] = Field(default_factory=list)
    disjoint_unions: list[BridgeIMDisjointUnion] = Field(default_factory=list)
    disjoint_classes: list[list[str]] = Field(default_factory=list)
    property_axioms: list[BridgeIMPropertyAxiom] = Field(default_factory=list)
    datatype_definitions: list[BridgeIMDatatypeDefinition] = Field(default_factory=list)
    rules: list[BridgeIMRule] = Field(default_factory=list)
    annotations: list[BridgeIMAnnotation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> str:
        return safe_name(str(value or "GeneratedOntology"), "pascal")

    @field_validator("disjoint_classes", mode="before")
    @classmethod
    def normalize_disjoint_classes(cls, value: Any) -> list[list[str]]:
        if value is None:
            return []
        normalized: list[list[str]] = []
        for group in value:
            if isinstance(group, str):
                members = [item.strip() for item in group.split(",") if item.strip()]
            else:
                members = list(group)
            refs = [bridge_ref(item, "pascal") for item in members]
            if len(refs) >= 2:
                normalized.append(refs)
        return normalized

    @model_validator(mode="after")
    def normalize_model(self) -> "BridgeIMDraft":
        if "xsd" not in {key.rstrip(":") for key in self.prefixes}:
            self.prefixes.setdefault("xsd:", "http://www.w3.org/2001/XMLSchema#")
        self.types = list(_dedupe_by_name(self.types).values())
        self.features = list(_dedupe_by_name(self.features).values())
        self.individuals = list(_dedupe_by_name(self.individuals).values())
        known_types = {item.name for item in self.types}
        for feature in self.features:
            if feature.owner_type and feature.owner_type not in known_types and not _is_external_ref(feature.owner_type):
                self.types.append(BridgeIMType(name=feature.owner_type))
                known_types.add(feature.owner_type)
            if feature.owl_kind == "object" and feature.range_type not in known_types and not _is_external_ref(feature.range_type):
                self.types.append(BridgeIMType(name=feature.range_type))
                known_types.add(feature.range_type)
        for individual in self.individuals:
            if individual.type not in known_types and not _is_external_ref(individual.type):
                self.types.append(BridgeIMType(name=individual.type))
                known_types.add(individual.type)
        return self
```
### 一、整体定位：这是个什么类？
#### 1. 核心一句话
`BridgeIMDraft` 是**Pydantic数据传输模型（DTO）**，作为中间适配层，用来承载「从OWL本体转换过来、专门对接SysMLv2-Owl-Bridge工具链」的建模数据。
文档注释关键信息翻译：
- 这只是**草稿/适配临时模型**，官方标准IM实现在Java端；
- 程序会把这个DTO渲染成Bridge可识别的SysML文本；
- 再交给命令行工具 BridgeCli 完成最终 SysML ↔ OWL 双向转换。

#### 2. 上下游链路
前文完整数据流：
自然文本 → `fallback_im_from_text` → `OntologyModel`（OWL本体模型）→ `bridge_im_from_ontology_model()` → **BridgeIMDraft** → 导出SysML代码/交给Bridge工具

`OntologyModel` 是OWL语义本体结构；`BridgeIMDraft` 是专门适配SysML桥梁工具的结构，两者字段、约束、校验规则不一样，所以单独定义一套模型。

### 二、所有字段逐行说明
```python
class BridgeIMDraft(BaseModel):
    base_iri: str
    name: str = "GeneratedOntology"
    prefixes: dict[str, str] = Field(default_factory=dict)
    types: list[BridgeIMType] = Field(default_factory=list)
    features: list[BridgeIMFeature] = Field(default_factory=list)
    individuals: list[BridgeIMIndividual] = Field(default_factory=list)
    keys: list[BridgeIMKey] = Field(default_factory=list)
    disjoint_unions: list[BridgeIMDisjointUnion] = Field(default_factory=list)
    disjoint_classes: list[list[str]] = Field(default_factory=list)
    property_axioms: list[BridgeIMPropertyAxiom] = Field(default_factory=list)
    datatype_definitions: list[BridgeIMDatatypeDefinition] = Field(default_factory=list)
    rules: list[BridgeIMRule] = Field(default_factory=list)
    annotations: list[BridgeIMAnnotation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
```
1. `base_iri: str`
   本体全局唯一资源地址，必填，OWL/SysML建模标准必填标识。
2. `name`
   建模包/本体名称，默认 `GeneratedOntology`，自带校验器自动清洗为合法大驼峰。
3. `prefixes` 命名空间前缀字典
   键：前缀（如`xsd:`），值：对应标准URL，用于XML/OWL类型解析。
4. `types: list[BridgeIMType]`
   对应SysML item，等价OWL Class，存储所有领域实体类型。
5. `features: list[BridgeIMFeature]`
   统一存放两类内容：
   - `kind=ref`：对象属性（类之间关联关系）
   - `kind=attribute`：数据属性（类自身字段）
6. `individuals`
   本体实例，某个Type的具体个体，附带属性赋值断言。
7. `keys`
   唯一键约束，类似数据库主键，标识类型中唯一标识字段。
8. `disjoint_unions / disjoint_classes`
   OWL互斥类约束：两个类的实例完全不重叠、无交集。
   - `disjoint_classes` 二维字符串列表：每一组内的类两两互斥。
9. `property_axioms`
   属性公理：传递性、对称性、函数性等OWL属性约束。
10. `datatype_definitions`
    自定义数据类型定义（枚举、限制数值区间等）。
11. `rules`
    语义推理规则，用于自动推导隐含关系。
12. `annotations`
    全局注释、标签、描述文本。
13. `metadata`
    自定义元数据，记录来源、版本、转换日志等溯源信息。

> 所有列表/字典都用 `Field(default_factory=xxx)` 初始化，规避Python可变默认值共享bug。

### 三、三个内置校验器逐段拆解
#### 3.1 name 字段前置校验：normalize_name
```python
@field_validator("name", mode="before")
@classmethod
def normalize_name(cls, value: Any) -> str:
    return safe_name(str(value or "GeneratedOntology"), "pascal")
```
- `mode="before"`：字段赋值前执行；
- 空/None自动替换默认本体名；
- 强制转字符串，调用 `safe_name` 标准化为大驼峰合法标识符；
和 `OntologyModel` 的名称清洗逻辑完全统一。

#### 3.2 disjoint_classes 前置校验：normalize_disjoint_classes
```python
@field_validator("disjoint_classes", mode="before")
@classmethod
def normalize_disjoint_classes(cls, value: Any) -> list[list[str]]:
    if value is None:
        return []
    normalized: list[list[str]] = []
    for group in value:
        # 如果传入字符串 "Car,Battery,Motor"，按逗号分割
        if isinstance(group, str):
            members = [item.strip() for item in group.split(",") if item.strip()]
        else:
            members = list(group)
        # 批量标准化类名
        refs = [bridge_ref(item, "pascal") for item in members]
        # 互斥组至少2个类才有意义，过滤单类组
        if len(refs) >= 2:
            normalized.append(refs)
    return normalized
```
功能：统一兼容两种输入格式，标准化互斥类名称、过滤无效分组：
1. 输入为 `None` → 返回空列表；
2. 单组输入是逗号分隔字符串，自动切割、去空格；
3. 每组内所有类名通过 `bridge_ref` 清洗为规范驼峰名称；
4. 只保留包含≥2个类的分组（单个类不存在互斥关系，直接丢弃）。

#### 3.3 全局后置模型校验 normalize_model（最重要）
`@model_validator(mode="after")`：**所有字段赋值完成、对象创建成功后**执行一整套自动清洗修复流程。
```python
@model_validator(mode="after")
def normalize_model(self) -> "BridgeIMDraft":
    # 1. 强制插入xsd标准命名空间前缀（建模必须）
    if "xsd" not in {key.rstrip(":") for key in self.prefixes}:
        self.prefixes.setdefault("xsd:", "http://www.w3.org/2001/XMLSchema#")

    # 2. types、features、individuals 按名称去重
    self.types = list(_dedupe_by_name(self.types).values())
    self.features = list(_dedupe_by_name(self.features).values())
    self.individuals = list(_dedupe_by_name(self.individuals).values())

    # 构建已存在类型集合，快速查询
    known_types = {item.name for item in self.types}

    # 3. 遍历所有特征，自动补全缺失的类型定义
    for feature in self.features:
        # 特征归属类不存在，且不是外部引用 → 自动新建空Type
        if feature.owner_type and feature.owner_type not in known_types and not _is_external_ref(feature.owner_type):
            self.types.append(BridgeIMType(name=feature.owner_type))
            known_types.add(feature.owner_type)
        # 对象属性的值域类不存在，自动新建
        if feature.owl_kind == "object" and feature.range_type not in known_types and not _is_external_ref(feature.range_type):
            self.types.append(BridgeIMType(name=feature.range_type))
            known_types.add(feature.range_type)

    # 4. 所有实例对应的类型缺失，自动补充
    for individual in self.individuals:
        if individual.type not in known_types and not _is_external_ref(individual.type):
            self.types.append(BridgeIMType(name=individual.type))
            known_types.add(individual.type)
    return self
```
分步功能拆解：
1. **强制补全xsd前缀**
   XSD是标准XML数据类型命名空间（string/int/float），建模必须存在，不存在则自动插入。
2. **全局去重**
   复用 `_dedupe_by_name` 工具，同名Type、Feature、Individual只保留一份，删除重复定义。
3. **自动修复悬空引用（核心能力）**
   遍历所有关联特征、实例：
   - 特征的 `owner_type`（归属类）不存在；
   - 对象属性的 `range_type`（关联目标类）不存在；
   - 实例 `type`（所属概念类）不存在；
   同时判断不是外部第三方引用（外部类不用新建），自动创建空 `BridgeIMType` 加入types列表，避免SysML代码出现无定义的类型报错。
4. `known_types` 集合：缓存所有已存在类型名，`in` 查询效率远高于列表。

### 四、该类的整体设计作用总结
#### 1. 数据转换中间载体
承接上游 `OntologyModel`，统一转换成符合SysML Bridge工具要求的数据结构，补齐SysML专属字段（前缀、互斥类、公理、推理规则等OWL模型没有的字段）。

#### 2. 多层自动数据标准化
- 名称统一驼峰规范；
- 互斥类分组格式自动兼容、清洗；
- 强制内置标准xsd命名空间；
- 全局自动去重，删除重复类型/特征/实例。

#### 3. 自动修复断裂引用（核心容错）
只要是内部自定义类型，出现「有属性/实例，但对应类没定义」的悬空引用，自动新建空白类型补齐，保证输出的SysML语法完全合法，不会出现未定义标识符。

#### 4. 兼容下游Bridge工具链
字段完全匹配Java端IM规范，后续可直接序列化、渲染为标准SysML文本，交给BridgeCli完成本体与SysML模型互转。

### 五、和 OntologyModel 的关键区别
1. **定位不同**
   - `OntologyModel`：纯粹OWL语义本体模型；
   - `BridgeIMDraft`：面向SysML工程建模工具的适配草稿模型。
2. **字段范围不同**
   BridgeIMDraft多出建模专用字段：命名空间前缀、互斥类、属性公理、推理规则、数据类型定义等SysML/Bridge工具需要的结构。
3. **自动修复逻辑差异**
   - OntologyModel只校验OWL类引用；
   - BridgeIMDraft额外区分「内部类型/外部引用」，只自动补全内部缺失类型，外部第三方类型不处理；强制注入xsd命名空间。
4. 用途分层
   OntologyModel：文本抽取、语义校验；
   BridgeIMDraft：建模导出、对接SysML转换工具。

### 六、初学者核心知识点
1. Pydantic双类型校验器：
   - `field_validator(mode="before")`：单个字段赋值前预处理；
   - `model_validator(mode="after")`：整个对象构建完成后批量清洗、修复数据；
2. 集合推导式快速构建查询池，提升成员判断性能；
3. 防御式编程：自动补全缺失定义、去重、补齐标准命名空间，保证下游输出无语法错误；
4. 分层DTO设计思想：不同业务阶段使用专属数据模型，上游语义本体、下游建模适配模型解耦；
5. 外部引用区分：通过 `_is_external_ref` 判断第三方类型，避免无意义自动创建空白类。
---

