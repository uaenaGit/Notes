---
created: 2026-07-09T15:10
updated: 2026-07-21T16:36
---

# `ontology-builder/src/ontology_builder_agent/im.py`
## 01
```python
def safe_name(value: str, style: Literal["pascal", "camel"] = "pascal", fallback: str = "Concept") -> str:
    text = value.strip()
    if not text:
        return fallback if style == "pascal" else fallback[:1].lower() + fallback[1:]

    ascii_text = _IDENTIFIER_RE.sub(" ", text)
    parts = [part for part in ascii_text.split() if part]
    if not parts:
        # Keep deterministic but ASCII-only identifiers for non-Latin source terms.
        code = abs(hash(text)) % 100000
        parts = [f"{fallback}{code}"]

    pascal = "".join(part[:1].upper() + part[1:] for part in parts)
    pascal = re.sub(r"[^A-Za-z0-9_]", "", pascal)
    if not pascal:
        pascal = fallback
    if pascal[0].isdigit():
        pascal = f"{fallback}{pascal}"
    if style == "camel":
        return pascal[:1].lower() + pascal[1:]
    return pascal
```

### 一、函数整体介绍
#### 1.1 函数作用
输入任意一段混杂中文、符号、数字、空格的文本，清洗生成编程语言合法标识符，支持两种命名规范：
- `pascal`：大驼峰（类、SysML item 命名，首字母大写，如 `CarBattery`）
- `camel`：小驼峰（变量命名，首字母小写，如 `carBattery`）

内置多层容错逻辑：空白输入、纯中文无英文字符、清洗后空值、数字开头全部兜底处理，**无论什么输入都能返回合法名称，不会报错**。

#### 1.2 前置依赖
运行代码前必须导入对应库，同时提前定义正则常量 `_IDENTIFIER_RE`：
```python
import re
from typing import Literal

# 匹配所有非字母、数字、下划线的字符（中文、标点、横杠等都会命中）
_IDENTIFIER_RE = re.compile(r"[^A-Za-z0-9_]")
```

#### 1.3 函数参数说明
```python
def safe_name(value: str, style: Literal["pascal", "camel"] = "pascal", fallback: str = "Concept") -> str:
```
- `value: str`：必填，原始待清洗文本
- `style: Literal["pascal", "camel"] = "pascal"`：命名风格，默认大驼峰；`Literal` 限制只能传指定两个字符串，编辑器会做语法校验
- `fallback: str = "Concept"`：兜底基础词，转换完全失败时用来生成名称，可自定义
- 返回值：清洗完成的合法标识符字符串

### 二、逐行拆解代码逻辑
#### 2.1 去除首尾空格，空白输入兜底
```python
text = value.strip()
if not text:
    return fallback if style == "pascal" else fallback[:1].lower() + fallback[1:]
```
1. `strip()`：删除字符串开头、结尾所有空格、换行、制表符；
2. `if not text`：判断去空格后文本为空（输入全是空白字符）；
3. 三元表达式区分两种风格：
   - pascal 模式：直接返回兜底词 `Concept`
   - camel 模式：首字母转为小写，输出 `concept`

示例：输入 `""`，`style="camel"` → 返回 `concept`

#### 2.2 非法字符替换 + 提取有效单词片段
```python
ascii_text = _IDENTIFIER_RE.sub(" ", text)
parts = [part for part in ascii_text.split() if part]
```
1. `_IDENTIFIER_RE.sub(" ", text)`：把所有非法字符统一替换成空格，中文、顿号、感叹号全部清空；
2. `split()`：按任意空格切割文本，连续多个空格会自动合并；
3. 列表推导式 `if part`：过滤切割产生的空字符串，只保留有内容的单词片段。

示例输入：`"汽车-battery！123"` → 处理后 `parts = ["battery", "123"]`

#### 2.3 纯中文/无有效字符哈希兜底
```python
if not parts:
    # Keep deterministic but ASCII-only identifiers for non-Latin source terms.
    code = abs(hash(text)) % 100000
    parts = [f"{fallback}{code}"]
```
1. `if not parts`：列表为空，代表原文只有中文、符号，不存在字母/数字；
2. `hash(text)`：对原始文本生成哈希值，**同一文本每次运行哈希值固定**，保证结果稳定；
3. `abs()`：消除哈希可能出现的负数；`% 100000`：限制数字范围 0~99999，避免名称过长；
4. 拼接兜底词+数字存入列表，后续统一转驼峰。

示例输入：`"自动驾驶控制器"` → `parts = ["Concept45216"]`

#### 2.4 拼接基础大驼峰字符串
```python
pascal = "".join(part[:1].upper() + part[1:] for part in parts)
```
遍历每一个单词片段做处理：
- `part[:1].upper()`：片段第一个字符转大写
- `part[1:]`：片段剩余字符保持原样
最后用 `join` 无缝拼接所有片段，形成标准大驼峰。

示例：`["battery", "48v"]` → `Battery48v`

#### 2.5 二次清理残留非法字符
```python
pascal = re.sub(r"[^A-Za-z0-9_]", "", pascal)
```
极端场景防护，彻底删除字符串里所有不属于字母、数字、下划线的字符，保证标识符合编程语言规范。

#### 2.6 清洗后空字符串兜底
```python
if not pascal:
    pascal = fallback
```
如果多层清洗后字符串变成空，直接赋值兜底词 `Concept`，避免后续索引报错。

#### 2.7 修复数字开头标识符（语法违规）
```python
if pascal[0].isdigit():
    pascal = f"{fallback}{pascal}"
```
编程语言、SysML 标识符**禁止以数字开头**；
`isdigit()` 判断首字符是否为数字，若是则在前面拼接兜底词。

示例：`99Battery` → `Concept99Battery`

#### 2.8 根据风格返回大/小驼峰
```python
if style == "camel":
    return pascal[:1].lower() + pascal[1:]
return pascal
```
- `camel` 分支：大驼峰首字母转小写，其余不变，输出小驼峰；
- 默认 `pascal`：直接返回处理完成的大驼峰字符串。

### 三、完整运行测试示例
#### 示例1：中英文混合文本，默认大驼峰
```python
text = "动力电池-battery 48v！"
print(safe_name(text))
```
执行流程：提取片段 `["battery", "48v"]` → 拼接 `Battery48v`，首字符非数字直接返回
输出：`Battery48v`

#### 示例2：指定小驼峰 camel
```python
text = "电机-motor"
print(safe_name(text, style="camel"))
```
输出：`batteryMotor`

#### 示例3：纯中文文本（哈希兜底）
```python
text = "自动驾驶控制器"
print(safe_name(text))
```
无有效英文片段，生成哈希数字后缀，输出类似：`Concept72419`

#### 示例4：数字开头文本
```python
text = "99发动机"
print(safe_name(text))
```
清洗结果以数字开头，自动拼接兜底词
输出：`Concept99`

#### 示例5：输入全空白，小驼峰模式
```python
text = "    "
print(safe_name(text, style="camel"))
```
输出：`concept`

### 四、与之前 `_to_pascal_case` 函数核心区别
1. 双风格支持：同时输出大驼峰、小驼峰，旧函数仅支持大驼峰；
2. 纯中文处理升级：不再返回空字符串，使用固定哈希生成唯一名称，结果可复现；
3. 二次字符过滤：严格只保留字母、数字、下划线，合规性更强；
4. 可自定义兜底词 `fallback`，适配不同建模场景；
5. 分层容错更完善：单独区分空白输入、无有效字符、清洗为空、数字开头四类异常。

### 五、初学者核心知识点总结
1. 正则操作：`re.compile` 预编译正则、`re.sub` 字符批量替换、字符集取反 `[^xxx]`；
2. 字符串基础：`strip()` 去空格、切片 `[:1]`/`[1:]`、`upper()`/`lower()` 大小写转换；
3. 列表推导式：快速过滤列表内空字符串；
4. 哈希运算：`hash()` + `abs()` + `%` 生成稳定数字后缀；
5. 类型注解：`Literal` 限制参数可选值，代码更规范；
6. 防御式编程：多层兜底判断，杜绝空字符串、非法标识符导致程序崩溃。

---
## 02
```python
class OntologyModel(BaseModel):
    base_iri: str
    name: str = "GeneratedOntology"
    classes: list[OntologyClass] = Field(default_factory=list)
    object_properties: list[ObjectProperty] = Field(default_factory=list)
    datatype_properties: list[DatatypeProperty] = Field(default_factory=list)
    individuals: list[Individual] = Field(default_factory=list)
    annotations: dict[str, str] = Field(default_factory=dict)
    sources: list[SourceReference] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_model_name(cls, value: Any) -> str:
        return safe_name(str(value or "GeneratedOntology"), style="pascal")

    @model_validator(mode="after")
    def normalize_model(self) -> "OntologyModel":
        deduplicate_model(self)
        validate_references(self, repair=True)
        return self
```
### 一、整体前置说明
#### 1. 依赖库
这个类基于 **Pydantic v2** 的 `BaseModel`（数据校验、数据建模库），必须导入：
```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any
```
配套用到的外部工具/实体类：
1. `safe_name`：之前讲解的名称标准化函数，生成合法大/小驼峰标识符
2. `deduplicate_model(self)`：自定义工具函数，对本体内部所有类、属性、实例做去重
3. `validate_references(self, repair=True)`：自定义校验函数，检查关系引用是否存在、自动修复缺失引用
4. 配套实体类型：`OntologyClass` / `ObjectProperty` / `DatatypeProperty` / `Individual` / `SourceReference`

#### 2. 类功能总述
`OntologyModel` 是**完整领域本体的数据载体**，存储一套本体全部组成要素；
同时内置两套自动校验逻辑：
1. 本体名称自动清洗为合法大驼峰；
2. 实例构建完成后自动去重、自动校验/修复实体引用关系，保证本体数据合法、无冗余、无断裂关联。

### 二、类字段逐行解析
```python
class OntologyModel(BaseModel):
    base_iri: str
    name: str = "GeneratedOntology"
    classes: list[OntologyClass] = Field(default_factory=list)
    object_properties: list[ObjectProperty] = Field(default_factory=list)
    datatype_properties: list[DatatypeProperty] = Field(default_factory=list)
    individuals: list[Individual] = Field(default_factory=list)
    annotations: dict[str, str] = Field(default_factory=dict)
    sources: list[SourceReference] = Field(default_factory=list)
```
#### 2.1 base_iri: str
- 无默认值，**必填参数**
- 本体全局唯一资源标识符（OWL标准），形如 `https://domain/ontology#`，用来区分不同本体，不可为空。

#### 2.2 name: str = "GeneratedOntology"
- 本体名称，默认值 `GeneratedOntology`；
- 下方有校验器，无论传入什么文本，都会自动转为**大驼峰合法名称**。

#### 2.3 classes: list\[OntologyClass] = Field(default_factory=list)
`Field(default_factory=list)` 是Pydantic规范写法，区别直接写 `= []`：
- 不会出现多个实例共享同一个列表的坑；
- 对象创建时自动生成全新空列表。
含义：存储本体所有**概念类**（实体类型，如汽车、电池、电机）。

#### 2.4 object_properties: list[ObjectProperty]
存储**对象属性**：类与类之间的关联关系，例如 `hasBattery`（汽车→动力电池）。

#### 2.5 datatype_properties: list[DatatypeProperty]
存储**数据属性**：类自身的基础字段，值域为字符串/数字等基础类型，例如 `weight`、`voltage`。

#### 2.6 individuals: list[Individual]
本体**实例个体**：类的具体实例。
例：类=汽车，个体=“比亚迪汉EV”。

#### 2.7 annotations: dict[str, str] = Field(default_factory=dict)
本体注解字典，存储描述、标签、备注等元数据。
键：注解类型（label/comment），值：文本内容。
示例：`{"label": "车辆领域本体", "comment": "自动从文本抽取生成"}`

#### 2.8 sources: list[SourceReference]
来源引用列表，记录每条实体/关系来自哪一段原始文本，用于溯源。

### 三、字段校验器：normalize_model_name（name 预处理）
```python
@field_validator("name", mode="before")
@classmethod
def normalize_model_name(cls, value: Any) -> str:
    return safe_name(str(value or "GeneratedOntology"), style="pascal")
```
#### 3.1 装饰器解释
1. `@field_validator("name", mode="before")`
   - 作用范围：仅针对字段 `name`；
   - `mode="before"`：**在参数转类型之前执行校验**，允许传入任意类型（数字、空值、中文、符号文本）。
2. `@classmethod`：校验器是类方法，第一个参数为 `cls`（本体类本身）。

#### 3.2 内部逻辑拆解
```python
value or "GeneratedOntology"
```
如果传入 `None`、空字符串、空值，自动替换为默认本体名。
```python
str(value or "GeneratedOntology")
```
强制转为字符串，兼容数字、布尔等非法输入。
```python
safe_name(..., style="pascal")
```
调用命名工具，统一转为**大驼峰合法标识符**。

#### 示例
- 输入 `name="车辆本体！"` → 输出 `DomainConceptxxxx`
- 输入 `name=99汽车` → 输出 `Concept99Car`
- 输入 `name=None` → 使用默认值 `GeneratedOntology`

### 四、实例后置校验器：normalize_model
```python
@model_validator(mode="after")
def normalize_model(self) -> "OntologyModel":
    deduplicate_model(self)
    validate_references(self, repair=True)
    return self
```
#### 4.1 装饰器说明
`@model_validator(mode="after")`
- `mode="after"`：**所有字段初始化完成、对象实例创建完毕后**执行；
- 第一个参数是 `self`（当前本体实例），可以直接修改本体内部数据；
- 最后必须返回 `self`，完成标准化修复。

#### 4.2 两步标准化逻辑
1. `deduplicate_model(self)`
    自定义去重函数，遍历本体全部内容：
    - classes 去重、object_properties 去重、datatype_properties 去重、个体/注解/来源去重；
    删除重复定义的类、关系，精简本体。
2. `validate_references(self, repair=True)`
    校验所有关系的定义域domain、值域range是否存在对应的Class：
    - `repair=True`：自动修复，引用的类不存在则自动创建空Class，防止关系悬空；
    - 避免出现“有关系，但两端实体不存在”的非法本体结构。

#### 4.3 返回 self
修复、去重完成后，返回标准化后的本体实例。

### 五、整体代码设计优势
1. **类型安全**：基于Pydantic强类型约束，赋值类型错误会直接抛出清晰报错；
2. **自动命名清洗**：本体名称无需人工规范，任意文本自动转为合法标识符；
3. **容器安全初始化**：全部列表/字典使用 `default_factory`，规避可变默认值经典bug；
4. **自动数据清洗**：实例创建后自动去重，自动修复断裂的实体引用；
5. **结构完整**：一次性承载本体所有标准组件（类、对象属性、数据属性、实例、注解、溯源来源），是完整OWL本体的内存模型。

### 六、初学者重点知识点总结
1. Pydantic 基础：`BaseModel` 数据模型、`Field(default_factory)` 安全初始化容器；
2. 两种校验器区别：
   - `field_validator(mode="before")`：单个字段赋值前预处理；
   - `model_validator(mode="after")`：整个对象构建完成后批量校验/修改；
3. 可变默认值陷阱：禁止直接 `list = []`，必须用 `default_factory=list`；
4. 本体工程思想：自动标准化、自动去重、自动修复引用，减少人工校验成本；
5. 工具函数配合：和前文 `safe_name`、`fallback_im_from_text` 整套流水线打通，文本抽取 → 实例化本体 → 自动清洗修复。
## 03 
```python
def _dedupe_by_name(items: list[Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items:
        if item.name not in result:
            result[item.name] = item
    return result


def deduplicate_model(model: OntologyModel) -> OntologyModel:
    model.classes = list(_dedupe_by_name(model.classes).values())
    model.object_properties = list(_dedupe_by_name(model.object_properties).values())
    model.datatype_properties = list(_dedupe_by_name(model.datatype_properties).values())
    model.individuals = list(_dedupe_by_name(model.individuals).values())
    return model


def validate_references(model: OntologyModel, repair: bool = False) -> list[str]:
    known_classes = {item.name for item in model.classes}
    issues: list[str] = []

    def missing_class(name: str, context: str) -> None:
        if name not in known_classes:
            issues.append(f"Unknown class reference {name!r} in {context}")
            if repair:
                model.classes.append(OntologyClass(name=name))
                known_classes.add(name)

    for ontology_class in model.classes:
        for parent in ontology_class.parents:
            missing_class(parent, f"class {ontology_class.name}.parents")

    for prop in model.object_properties:
        missing_class(prop.domain, f"object property {prop.name}.domain")
        missing_class(prop.range, f"object property {prop.name}.range")

    for prop in model.datatype_properties:
        missing_class(prop.domain, f"datatype property {prop.name}.domain")
        if prop.range not in _BUILTIN_DATATYPES:
            issues.append(f"Unknown datatype {prop.range!r} in datatype property {prop.name}")
            if repair:
                prop.range = "string"

    for individual in model.individuals:
        missing_class(individual.type, f"individual {individual.name}.type")

    return issues

```

### 一、整体说明
这两个函数是配套 `OntologyModel` 的本体清洗校验工具：
1. `deduplicate_model`：给本体内部所有概念、属性、实例**按名称去重**，删除重复定义；
2. `validate_references`：校验本体里所有引用的类是否真实存在，收集异常日志；开启自动修复时会补全缺失类、修正非法数据类型；
两个函数会在 `OntologyModel` 实例化完成后自动执行（`@model_validator(mode="after")`），保证本体结构合法无冗余。

### 二、第一个函数：deduplicate_model 本体去重
```python
def deduplicate_model(model: OntologyModel) -> OntologyModel:
    model.classes = list(_dedupe_by_name(model.classes).values())
    model.object_properties = list(_dedupe_by_name(model.object_properties).values())
    model.datatype_properties = list(_dedupe_by_name(model.datatype_properties).values())
    model.individuals = list(_dedupe_by_name(model.individuals).values())
    return model
```
#### 2.1 参数与返回
- 入参：`model: OntologyModel`，完整本体实例
- 返回：处理完成后的本体对象（直接修改原对象再返回）

#### 2.2 核心逻辑拆解
1. `_dedupe_by_name(列表)`
   这是外部依赖的辅助函数，逻辑规则：
   - 接收一批拥有 `name` 属性的对象（OntologyClass / ObjectProperty / Individual 等）
   - 用对象的 `name` 作为字典 key，同名对象只保留**第一个**，覆盖后面重复项
   - 返回 `{名称: 唯一对象}` 格式字典，天然完成去重

2. `list(xxx.values())`
   提取字典里去重后的唯一对象，重新赋值给本体对应字段：
   - `model.classes`：去重所有概念类，同名类只留一条
   - `model.object_properties`：去重对象关联关系
   - `model.datatype_properties`：去重数据属性
   - `model.individuals`：去重实体实例

3. `return model`
   原本体对象已原地修改，直接返回。

#### 2. 示例场景
文本解析重复提取两次 `Car` 类，去重后列表只会保留一个 `OntologyClass(name="Car")`。

### 三、第二个函数：validate_references 引用校验&自动修复
```python
def validate_references(model: OntologyModel, repair: bool = False) -> list[str]:
    # 1. 收集所有已存在类名称集合，快速查找
    known_classes = {item.name for item in model.classes}
    issues: list[str] = []

    # 内部嵌套函数：统一处理缺失类逻辑
    def missing_class(name: str, context: str) -> None:
        if name not in known_classes:
            # 记录异常日志
            issues.append(f"Unknown class reference {name!r} in {context}")
            # 开启修复则自动新建缺失类
            if repair:
                model.classes.append(OntologyClass(name=name))
                known_classes.add(name)

    # 校验1：类的父类引用
    for ontology_class in model.classes:
        for parent in ontology_class.parents:
            missing_class(parent, f"class {ontology_class.name}.parents")

    # 校验2：对象属性 domain、range 引用
    for prop in model.object_properties:
        missing_class(prop.domain, f"object property {prop.name}.domain")
        missing_class(prop.range, f"object property {prop.name}.range")

    # 校验3：数据属性 domain + 数据类型合法性
    for prop in model.datatype_properties:
        missing_class(prop.domain, f"datatype property {prop.name}.domain")
        # range 不是内置基础类型则报错
        if prop.range not in _BUILTIN_DATATYPES:
            issues.append(f"Unknown datatype {prop.range!r} in datatype property {prop.name}")
            # 自动修复：非法类型统一改为 string
            if repair:
                prop.range = "string"

    # 校验4：实例所属类型引用
    for individual in model.individuals:
        missing_class(individual.type, f"individual {individual.name}.type")

    # 返回所有检测到的问题日志
    return issues
```
#### 3.1 参数说明
- `model`：待校验本体实例
- `repair: bool = False`：是否自动修复错误，默认关闭；前文本体校验器传入 `repair=True` 自动修复
- 返回值：字符串列表，存储所有检测出的异常描述，可供打印、日志输出

#### 3.2 前置集合 known_classes
```python
known_classes = {item.name for item in model.classes}
```
集合推导式，把所有类的名称存入集合；集合查找 `in` 速度远快于列表，用来快速判断某个类是否存在。

#### 3.3 内部工具函数 missing_class（复用逻辑）
统一封装「检测缺失类、记录异常、自动补全类」逻辑，避免重复写代码：
1. 判断目标类名不在 `known_classes`；
2. 拼接报错信息存入 `issues`；
3. 开启 `repair=True` 时：
   - 新建空 `OntologyClass` 加入本体类列表
   - 同步更新 `known_classes` 集合，避免重复新增

`{name!r}`：Python格式化写法，给名称加上引号，日志可读性更高。

#### 3.4 4轮全量校验逻辑
##### 3.4.1 校验类的父类继承关系
```python
for ontology_class in model.classes:
    for parent in ontology_class.parents:
        missing_class(parent, f"class {ontology_class.name}.parents")
```
每个类可以有多个父类，如果父类名称不存在于本体，判定引用缺失。

##### 3.4.2 校验对象属性（实体关联）
`ObjectProperty` 有 `domain`（定义域）、`range`（值域），二者都必须是已定义的类：
- 例：`hasBattery` 的 domain=Car、range=Battery；如果Car不存在，标记异常并自动创建。

##### 3.4.3 校验数据属性（字段）
1. `domain`：该属性归属的类，不存在则修复；
2. `range`：数据类型，只能是内置合法类型（`_BUILTIN_DATATYPES` 一般包含 string、int、float、bool 等）；
   - 类型非法时记录问题，自动修复统一替换为 `string`。

##### 3.4.4 校验实例个体 type
每个 `Individual`（实体实例）必须归属一个类，`individual.type` 是类名，缺失则自动新建对应类。

#### 3.5 返回异常列表
所有检测到的缺失类、非法数据类型都会收集到 `issues`，函数执行完毕全部返回，外部可以打印查看本体缺陷。

### 四、两个函数在整套代码中的运行时机
在 `OntologyModel` 的后置校验器里自动串行执行：
```python
@model_validator(mode="after")
def normalize_model(self) -> "OntologyModel":
    deduplicate_model(self)          # 第一步：先去重
    validate_references(self, repair=True)  # 第二步：校验+自动修复所有引用
    return self
```
流程固定：**先删重复，再校验修复引用**。

### 五、完整运行示例
假设解析文本生成有缺陷的本体：
1. 重复两条 `Car` 类；
2. 对象属性 `hasMotor` 的 range=Motor，但本体没有 Motor 类；
3. 数据属性 `voltage` range=number123（非法类型）

执行流程：
1. `deduplicate_model`：删掉重复的 Car，只保留一条；
2. `validate_references(repair=True)`：
   - 检测到 Motor 类缺失，自动追加 `OntologyClass(name="Motor")`；
   - 检测到 `number123` 非法，修改 range="string"；
   - issues 列表存入两条异常日志；
3. 输出干净、无重复、无悬空引用的合法本体。

### 六、初学者核心知识点总结
1. 集合推导式快速构建查找池，提升成员判断效率；
2. 嵌套函数封装重复逻辑，减少冗余代码；
3. 原地修改对象：函数直接修改传入的 `model` 内部字段，再返回；
4. 防御式本体校验：两层能力——问题检测 + 自动修复；
5. 命名去重机制：依靠 `name` 作为唯一标识，同名实体自动合并；
6. 格式化字符串 `!r` 用于日志美化输出。