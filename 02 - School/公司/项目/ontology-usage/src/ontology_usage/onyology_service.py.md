---
created: 2026-07-31T11:01
updated: 2026-08-06T16:08
---
# `build_ontology` 函数详解

> 本篇假定读者对 Python 异步编程、类型注解等特性不熟悉，会在关键节点展开解释。

---

## 1. 函数签名

```
async def build_ontology(source_text: str, *, include_props: bool = True) -> dict[str, Any]:
```

先从这行拆起：

- **`async def`**：这是 Python 的**异步函数**。普通函数（`def`）执行时会一直跑到结束才把控制权交还给调用者；异步函数运行到 `await` 语句时会主动暂停，把 CPU 让给其他任务，等 I/O 操作（比如网络请求）完成后再恢复。这里用 `async` 是因为函数内部要通过网络调用 LLM，等待期间不希望整个程序卡住。
- **`source_text: str`**：类型注解。告诉你（和编辑器）这个参数应该传字符串，传错了 IDE 会标红。
- **`*`**：孤立的星号。它的意思是"星号后面的参数只能用**关键字**方式传递，不能按位置传递"。比如调用时只能写 `build_ontology(text, include_props=False)`，不能写 `build_ontology(text, False)`——后者会被拒绝。这是 Python 强制代码可读性的手段。
- **`include_props: bool = True`**：布尔型参数，默认值 `True`。`include_props` 是"是否包含属性"的缩写。
- **`-> dict[str, Any]`**：返回值类型注解。`dict[str, Any]` 意思是返回一个字典，键是字符串，值可以是任意类型。

---

## 2. 整体职责

把一段**自由文本**（比如某系统的技术文档、需求描述）喂给 LLM，让它从文本中提取出结构化的**本体**（ontology）。

本体是什么？简单说就是一张"知识地图"：

- 有哪些**类型**（比如"系统"、"组件"、"参数"）
- 有哪些**具体实例**（比如"发动机"、"涡轮控制器"、"推力参数"）
- 实例之间有什么**关系**（比如"发动机 包含 涡轮控制器"）
- 实例有哪些**属性**（比如"推力=5000 kN"、"重量=1200 kg"）

函数返回一个字典，把这些信息都打包在一起。

---

## 3. 执行流程（5 步）

### 步骤 1：估算 Token 预算

```
source_chars = len(source_text)
if source_chars > 30000:
    max_tokens = 32768
elif source_chars > 15000:
    max_tokens = 24576
elif source_chars > 7000:
    max_tokens = 16384
else:
    max_tokens = 8192
```

**为什么需要这一步？** LLM 的输出有长度限制。输入文本越长，需要输出的本体结构也越大，所以要给 LLM 预留足够的输出空间。`max_tokens` 就是告诉 LLM"你最多可以输出多少个 token"。这里的逻辑是：输入越长，给越多的输出额度。

> **Token** 不是字符。一个中文字大约 1-2 个 token，一个英文单词大约 1-3 个 token。`max_tokens` 控制的是 LLM 输出长度的上限，不是输入。

### 步骤 2：调用 LLM

```
system = ONTOLOGY_BUILD_SYSTEM if include_props else ONTOLOGY_BUILD_SYSTEM_NO_PROPS
messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": ONTOLOGY_BUILD_USER.format(source_text=source_text)},
]
raw = await llm_service.chat(messages, temperature=0.1, max_tokens=max_tokens)
```

逐行解释：

- **`ONTOLOGY_BUILD_SYSTEM if include_props else ONTOLOGY_BUILD_SYSTEM_NO_PROPS`**：这是 Python 的**三元表达式**，等价于"如果 `include_props` 为真，就用 A；否则用 B"。两种提示词的区别：一种要求 LLM 同时抽取实例的属性（props），另一种只抽取实例的基本信息（id/name/desc），属性留给后续阶段补充。
- **`messages`**：一个列表，包含两条消息。`system` 消息告诉 LLM"你是什么角色、要做什么"，`user` 消息是具体任务。这是 LLM API 的标准对话格式。
- **`.format(source_text=source_text)`**：Python 字符串的格式化方法。`ONTOLOGY_BUILD_USER` 是一个模板字符串，里面有一个 `{source_text}` 占位符，`.format()` 把它替换成实际的源文本内容。
- **`await`**：这是异步编程的关键字。`llm_service.chat()` 是一个异步函数（发网络请求），`await` 的意思是"等这个网络请求完成，拿到结果后再继续往下走"。在等待期间，Python 的事件循环可以处理其他任务，不会白白浪费 CPU。
- **`temperature=0.1`**：控制 LLM 输出的"随机性"。0 到 1 之间，越低越确定（每次输出几乎一样），越高越有创造性。本体抽取是确定性任务，所以用 0.1 这个极低值。
- **`raw`**：LLM 返回的原始文本字符串。

**`llm_service.chat()` 内部做了什么？**[[llm_service.py#`async def chat` 函数详解]] 它在 `src/ontology_usage/llm_service.py:85`，通过 HTTP POST 请求调用 MiniMax 大模型 API（`/chat/completions` 端点），需要提前配置 `MINIMAX_API_KEY` 环境变量。返回的是 LLM 生成的完整文本。

### 步骤 3：从 LLM 输出中提取 JSON

```
data = llm_service.extract_json(raw)
```

LLM 的输出不一定是纯 JSON——它可能被 markdown 代码块包裹（` ```json ... ``` `），或者前后有额外的解释文字。`extract_json()`（在 `llm_service.py:213`）做三件事：

1. 清除 `think` 标签（某些模型会在输出中插入思考过程）
2. 去掉 markdown 代码围栏
3. 找到第一个 `{` 或 `[`，按括号匹配找到完整的 JSON 文本，然后用 `json.loads()` 解析成 Python 字典

如果解析失败，或者结果里没有 `instances` 字段，就抛出 `ValueError`（一种 Python 异常，表示"你给我的值不对"）。

### 步骤 4：后处理链

LLM 的输出不可靠，以下四个步骤逐一修复和补充：

#### 4a. 分配颜色

```
data = _ensure_colors(data)
```

遍历 `ontoTypes`，为每个没有颜色的类型从预定义的色池 `_COLOR_POOL` 中按顺序取一个颜色（如 `#2563eb`、`#0891b2` 等）。这个函数不会覆盖已有的颜色，只补缺失的。颜色用于前端可视化。

#### 4b. 校验引用完整性

```
data = _validate_references(data)
```

([[#`_validate_references(data dict)` 解析]])LLM 可能生成指向不存在实例的 relations（比如 `from: "FOO"` 但 `FOO` 这个实例根本不存在），或者实例的 `type` 指向一个不存在的 `ontoType`。这个函数：

- 过滤掉无效的 relations（`from` 或 `to` 在实例 ID 集合中找不到的）
- 把 `type` 无效的实例修正为第一个有效类型

#### 4c. 推导数据属性与约束

```
dpp, axioms = derive_datatype_properties_and_constraints(instances, valid_types)
data["datatypeProperties"] = dpp
data["constraints"] = axioms
```

这个函数([[#`derive_datatype_properties_and_constraints` 代码详解]])遍历所有实例的 `props`（属性字典），做两件事：

**推导 `datatypeProperties`**：从属性值中推断属性类型。比如值是 `"5000 kN"`，它识别出 `5000` 是整数，单位为 `kN`，类型就是 `Integer`。值是 `"100~300 MHz"`，识别出这是一个范围，类型是 `Real`。它还记录每个属性适用于哪些类型（`appliesTo`）。

**推导 `constraints`**：每个属性值变成一条约束。比如 `"5000 kN"` → `{subject: "ENG", property: "推力", operator: "=", value: "5000", unit: "kN"}`。范围值 `"100~300 MHz"` → `{operator: "range", value: "100~300", unit: "MHz"}`。

#### 4d. 推导类型级关系

```
data["typeRelations"] = infer_type_relations(types, instances, relations)
```

从实例级别的 relations 反推类型级别的关系。比如：发动机（类型=system）→ 涡轮控制器（类型=component），标签是"组成 part"。如果多个 system 实例都通过"组成 part"指向 component 实例，就推断出 `{from: "system", to: "component", label: "组成 part"}` 这条类型级关系。

### 步骤 5：计时与日志

```
logger.info(
    "[ontology.build] llm=%.2fs parse=%.2fs total=%.2fs instances=%d",
    llm_done - t0, parse_done - llm_done, total, len(data.get("instances", [])),
)
```

记录三个耗时（LLM 调用、JSON 解析、总耗时）和最终实例数量，方便排查性能问题。`%.2fs` 是格式化占位符，保留两位小数，后面跟 `s`（秒）。

---

## 4. 返回值结构

```
{
    "ontoTypes": [
        {"key": "system", "name": "系统", "color": "#2563eb"},
        {"key": "component", "name": "组件", "color": "#0891b2"},
        ...
    ],
    "instances": [
        {
            "id": "ENG",           # 大写英文缩写，唯一标识
            "type": "system",      # 对应 ontoTypes 中的 key
            "name": "发动机",
            "desc": "提供推力的主推进系统",
            "props": {             # 仅 include_props=True 时有
                "推力": "5000 kN",
                "重量": "1200 kg"
            }
        },
        ...
    ],
    "relations": [
        {"from": "ENG", "to": "TC", "label": "组成 part", "key": 1},
        ...
    ],
    "datatypeProperties": [        # 由步骤 4c 派生
        {"name": "推力", "type": "Integer", "unit": "kN",
         "appliesTo": ["system"]},
        ...
    ],
    "constraints": [               # 由步骤 4c 派生
        {"subject": "ENG", "property": "推力", "operator": "=",
         "value": "5000", "unit": "kN"},
        ...
    ],
    "typeRelations": [             # 由步骤 4d 派生
        {"from": "system", "to": "component", "label": "组成 part"},
        ...
    ]
}
```

六个字段的职责：

|字段|来源|含义|
|---|---|---|
|`ontoTypes`|LLM 生成 + 步骤 4a 补色|有哪些类型分类|
|`instances`|LLM 生成|有哪些具体实例|
|`relations`|LLM 生成 + 步骤 4b 过滤|实例之间有什么关联|
|`datatypeProperties`|步骤 4c 派生|每个属性叫什么、什么类型、什么单位|
|`constraints`|步骤 4c 派生|每个实例的每个属性具体等于多少|
|`typeRelations`|步骤 4d 派生|类型与类型之间有什么关系|

---

## 5. 调用链全景图

```
build_ontology(source_text)
 │
 ├─ 估算 max_tokens（根据输入长度）
 │
 ├─ await llm_service.chat(messages)     ← 异步网络请求，调用 MiniMax API
 │   └─ 返回 raw 文本
 │
 ├─ llm_service.extract_json(raw)        ← 从文本中提取 JSON
 │   └─ 返回 Python 字典
 │
 ├─ _ensure_colors(data)                 ← 补颜色
 ├─ _validate_references(data)           ← 过滤无效引用
 ├─ derive_datatype_properties_and_constraints() ← 派生数据属性+约束
 ├─ infer_type_relations()               ← 派生类型级关系
 │
 └─ 返回完整的本体字典
```

---

## 6. 关键设计决策

- **LLM 做"脏活"**：ontoTypes、instances、relations 的初步抽取完全交给 LLM，代码只做校验和派生。这是因为从自然语言中识别实体和关系是 LLM 的强项，代码做不好。
- **后处理补"漏"**：LLM 输出不稳定（颜色缺失、引用断裂、类型不匹配），后处理链逐一修复，确保下游拿到合法数据。这是"信任但验证"的策略。
- **`include_props` 开关**：当属性由外部系统（如 Excel 解析）补充时，可以跳过 LLM 的属性抽取，减少 token 消耗和"幻觉"（LLM 编造不存在的属性值）。
- **`temperature=0.1`**：极低温度保证输出结构稳定。本体抽取是确定性任务，不需要创造性。
- **`*` 强制关键字参数**：`include_props` 只能按关键字传递，防止调用者搞混参数顺序。

# `_validate_references(data: dict)` 解析
## 整体功能定位
这是一份**本体实例数据的合法性校验+自动修复函数**。
针对结构化数据（本体类型ontoTypes、实例instances、关联关系relations）做两件核心事：
1. 修正实例非法的 `type`（实例类型不存在时自动兜底）
2. **清理无效关联关系**：如果一条关系的起点/终点实例不存在，直接删掉这条关系
> 业务背景：你前面一直在处理本体 Ontology 相关代码，这份函数就是用于知识图谱/本体导入前的数据清洗，防止出现「悬空引用」。

## 假设数据结构（先约定输入data长什么样，方便理解）
```python
data = {
    "ontoTypes": [   # 本体允许的类型列表
        {"key": "Engine", "label": "发动机"},
        {"key": "Pump", "label": "泵体"}
    ],
    "instances": [   # 实体实例
        {"id": "inst_001", "type": "Engine", "name": "一号发动机"},
        {"id": "inst_002", "type": "XXX", "name": "非法类型实例"}
    ],
    "relations": [   # 实例之间的关联关系 from/to 对应实例id
        {"from": "inst_001", "to": "inst_002", "relation": "hasPart"},
        {"from": "inst_001", "to": "inst_999", "relation": "connect"} # inst_999不存在
    ]
}
```

## 代码逐段拆解
```python
# 获取所有合法类型key集合
valid_types = {t["key"] for t in data.get("ontoTypes", [])}
# 获取所有实例id集合
inst_ids = {i["id"] for i in data.get("instances", [])}
```
- `data.get("ontoTypes", [])`：如果字典没有`ontoTypes`键，不会报错，返回空列表
- 集合推导式：快速收集**合法类型名**、**所有实例ID**
集合查询 `x in 集合` 速度远快于列表，用于后续快速校验。

```python
# 修复 instance type
for inst in data.get("instances", []):
    # 条件1：实例的type不在合法类型集合
    # 条件2：valid_types 非空（有可用的合法类型兜底）
    if inst["type"] not in valid_types and valid_types:
        # 强制修改为第一个合法类型
        inst["type"] = list(valid_types)[0]
```
### 逻辑说明
实例的 `type` 必须来自 `ontoTypes` 里面定义的key。
- 如果实例写了不存在的类型（比如`"XXX"`）
- 同时系统存在合法类型列表
→ 自动兜底，改成**第一个合法类型**

⚠️ 小缺陷：`set` 集合是无序的！`list(valid_types)[0]` 获取的“第一个元素”顺序不稳定。
> 如果业务要求稳定顺序，不能用集合存储 `valid_types`，要改用列表。

```python
    # 过滤无效 relations
    data["relations"] = [
        r for r in data.get("relations", [])
        if r.get("from") in inst_ids and r.get("to") in inst_ids
    ]
```
列表推导式筛选关系：
保留一条关系的**唯一条件**：
`from` 对应的实例ID **存在** 并且 `to` 对应的实例ID **存在**
只要任意一端实例不存在 → 直接丢弃这条relation，避免悬空引用。

`r.get("from")` 安全写法：防止relation字典没有`from`键，避免`KeyError`。

```python
return data
```
注意：**直接原地修改传入的data字典（可变对象），同时返回自身**。
Python字典是引用传递，函数外部的原始字典也会被改动。

## 使用上面示例数据演示运行效果
原始实例：`{"id": "inst_002", "type": "XXX", "name": "非法类型实例"}`
`XXX` 不在 `{"Engine","Pump"}`，自动修改为 `Engine`（集合无序，也可能是Pump）

原始两条关系：
1. `from:inst_001 → to:inst_002`：两端实例都存在，保留
2. `from:inst_001 → to:inst_999`：inst_999不存在，直接删除

最终 `data["relations"]` 只剩第一条。

## 边界情况梳理
1. `ontoTypes` 为空列表 → `valid_types`为空，不会执行type自动修复（防止强行赋值）
2. `instances` 为空 → `inst_ids`为空，**所有relations全部清空**
3. relation缺少`from` 或者 `to` 字段 → `r.get()`得到`None`，必然不在inst_ids，这条关系被过滤
4. 实例type大小写不一致（`engine` vs `Engine`）：代码不会自动兼容，需要额外统一大小写

## 潜在优化点（你后续开发可以参考）
1. 不要使用set存放valid_types，解决`list(valid_types)[0]`顺序随机问题；
2. 非法type不要静默覆盖，可以增加日志告警，方便排查脏数据；
3. 区分「原地修改」，如果不想改动原始入参，可以先深拷贝一份data再处理。

如果你需要，我可以写一段测试代码，复制就能运行，直观看到修复前后的数据变化。

# `derive_datatype_properties_and_constraints` 代码详解
## 一、函数整体功能
该函数面向本体工程（ABox/TBox）场景，**扫描实例列表中的自定义属性props，自动反向派生两类数据**：
1. `datatypeProperties`：数据属性定义（归属TBox术语层，描述属性元信息）
2. `constraints`：实例属性约束公理（归属ABox实例层，描述每个实体的属性取值）

调用时机：`store.set_abox()`、`build_abox()` 流程收尾。
业务价值：仅导入实例数据（ABox）时，无需提前人工建模属性定义，程序自动提取生成数据属性。

入参说明：
- `instances`：实例字典列表，每个实例包含id、type、props等字段
- `valid_types`：合法本体类集合；传`None`代表纯ABox场景，不校验实例类型

返回：`(datatypeProperties, constraints)`

## 二、逐段源码解析
```python
def derive_datatype_properties_and_constraints(instances: list[dict], valid_types: set[str] | None = None) -> tuple[list[dict], list[dict]]:
    """从实例 props 推导 datatype property + instance axiom。

    返回 (datatypeProperties, constraints) 两份列表。
    valid_types 为 None 时不限制 inst.type（ABox-only 上下文中所有 instance 视为合法）。
    用于 store.set_abox() 自动派生、build_abox() 收尾时被调用。
    """
    dp_map: dict[str, dict] = {}   # 临时聚合所有推导出来的数据属性，key=属性名
    constraints: list[dict] = []   # 存放所有实例属性约束
    valid_types = valid_types or set() # 空兼容：外部传入None则初始化为空集合
```

```python
    for inst in instances:
        raw_type = inst.get("type")
        # 判定当前实例类型是否合法
        # 无合法类型限制 或者 实例type在合法集合内 → 保留类型；否则置为None
        inst_type = raw_type if (not valid_types or raw_type in valid_types) else None
```
- 如果`inst_type = None`：后续不会把该类型加入属性的`appliesTo`（属性不认为适用于该非法类）

```python
        # 遍历实例下所有自定义属性 props
        for name, raw_value in (inst.get("props") or {}).items():
            # 工具函数：拆分【数值文本】和【单位】
            # 示例："10~20 MPa" → value="10~20", unit="MPa"
            value, unit = _split_value_unit(raw_value)
            if not value:
                continue # 无有效数值，跳过该属性

            # 工具函数：自动推断属性基础数据类型（int/float/string）
            ptype = _infer_property_type(raw_value)
```

```python
            # setdefault机制：属性不存在则新建定义；已存在直接取出旧对象
            dp = dp_map.setdefault(name, {"name": name, "type": ptype, "unit": unit, "appliesTo": set()})
            # 实例类型合法，将类加入该属性适用范围集合
            if inst_type:
                dp["appliesTo"].add(inst_type)
```
> ⚠️ 关键隐患：`setdefault`仅首次创建对象，**后续同名属性出现不同unit/ptype不会更新、不会冲突告警**。
> 例如先遇到`pressure=10 MPa`，后遇到`pressure=200 bar`，dp内unit永远保留MPa，bar直接被忽略。

```python
            # 正则匹配区间符号 ~ - ～ —，区分精确值 / 区间约束
            operator = "range" if re.search(r"[~\-～—]", value) else "="
            # 生成一条实例约束公理
            constraints.append({
                "subject": inst["id"],    # 主体：实例唯一ID
                "property": name,         # 属性名称
                "operator": operator,     # = 精确值 | range 区间
                "value": value,           # 剥离单位后的数值文本
                "unit": unit,             # 单位
            })
```

```python
    # 将dp_map字典转为标准列表结构，appliesTo集合排序，方便序列化JSON
    datatype_properties = [
        {"name": dp["name"], "type": dp["type"], "unit": dp["unit"], "appliesTo": sorted(dp["appliesTo"])}
        for dp in dp_map.values()
    ]
    return datatype_properties, constraints
```

## 三、核心字段语义说明
### datatypeProperties（数据属性定义）
- `name`：属性标识名
- `type`：自动推断的数据类型
- `unit`：首次出现属性时捕获的单位
- `appliesTo`：**该属性能够作用的本体类集合**

### constraints（实例约束）
每一条代表：某个实例拥有某属性，以及对应的取值条件。

## 四、现存工程缺陷
1. **单位/类型冲突静默处理**
同名属性出现多种单位、多种数据类型时，无日志、无报错，仅保留第一条定义，容易造成本体建模不一致。
2. **区间识别能力有限**
仅识别 `~、-` 符号，无法识别 `>、<、≥` 这类不等式约束。
3. **无单位换算逻辑**
同一物理量混杂MPa / bar等不同单位时，不会自动标准化，后续数据查询、对比存在障碍。

## 五、可选改造方向
### 方案1：增加冲突检测（最小改动，推荐过渡使用）
移除`setdefault`，手动判断属性是否存在，对比新旧unit、type，发现冲突输出警告日志。
### 方案2：严格校验模式
检测冲突直接抛出异常，阻断导入，强制上游清洗数据。
### 方案3：单位标准化（长期方案）
基于ISO80000体系构建单位库，自动识别、换算至基准单位，约束同时保存原始值与标准化数值。

## 六、简易业务示例
### 输入实例
```python
instances = [
    {"id": "eng01", "type": "Engine", "props": {"pressure": "10~20 MPa"}},
    {"id": "eng02", "type": "Engine", "props": {"pressure": "15 MPa"}},
    {"id": "pump01", "type": "Pump", "props": {"pressure": "5~8 MPa"}}
]
valid_types = {"Engine", "Pump"}
```
### 输出结果
1. datatypeProperties 生成`pressure`属性：
`appliesTo: ["Engine", "Pump"], unit:"MPa"`
2. constraints 生成3条约束，operator分别为range、=、range。

如果你需要，我可以输出**加入单位冲突告警的改造后完整代码**。

# infer_type_relations 代码详解
```python
def infer_type_relations(types: list[dict], instances: list[dict], relations: list[dict]) -> list[dict]:
    """从实例级关系中自动推断类型层级（kind-of / subClassOf）。PR-1: 纯函数。"""
    valid_types = {t["key"] for t in types}
    inst_type = {i["id"]: i["type"] for i in instances if i.get("type") in valid_types}
    seen = set()
    type_rels: list[dict] = []
    for rel in relations:
        label = (rel.get("label") or "").lower()
        if not any(kw in label for kw in _KIND_OF_LABELS):
            continue
        from_type = inst_type.get(rel.get("from"))
        to_type = inst_type.get(rel.get("to"))
        if not from_type or not to_type or from_type == to_type:
            continue
        key = (from_type, to_type)
        if key in seen:
            continue
        seen.add(key)
        type_rels.append({"from": from_type, "to": to_type, "label": "kind-of", "key": 0})
    return type_rels
```
## 一、函数整体功能
这是本体建模自动化推导工具，**通过扫描实例之间的关系，反向推理出类与类之间的 `kind-of(subClassOf 子类)` 层级关系**。

业务场景：
用户只录入了实例（ABox）之间的从属关系，没有手动定义类层级（TBox）。该函数自动提炼：
> 实例A kind-of 实例B → 实例A所属类 kind-of 实例B所属类

属于自动化本体构建链路的一环，注释标注为纯函数，无外部副作用。

### 入参说明
1. `types: list[dict]`：本体类列表，每个类包含 `key`（类唯一标识）
2. `instances: list[dict]`：实例列表，每个实例包含 `id`、`type`（归属的类）
3. `relations: list[dict]`：**实例与实例之间的关系列表**

### 返回值
`list[dict]`：推导出来的【类和类之间】的kind-of子类关系。

## 二、常量说明
```python
_KIND_OF_LABELS = {"子类", "is-a", "isa", "kind-of", "kindof", "subclass", "sub class", "类型", "category", "class"}
```
关系标签关键词集合。
只要实例关系的标签包含集合内任意词汇，就认定这条关系表达「从属、子类、is-a」语义。
支持中英文、多种写法，做兼容匹配。

## 三、逐段源码解析
```python
valid_types = {t["key"] for t in types}
```
提取所有合法本体类key，存入集合，用于过滤无效类型。

```python
inst_type = {i["id"]: i["type"] for i in instances if i.get("type") in valid_types}
```
构建字典：`实例ID → 实例归属的类key`
只保留类型在合法类清单内的实例；非法实例直接丢弃。

```python
seen = set()
type_rels: list[dict] = []
```
- `seen`：去重集合，防止重复生成相同的类层级关系
- `type_rels`：最终输出的类与类关系结果

```python
for rel in relations:
    label = (rel.get("label") or "").lower()
    # 判断当前实例关系是否属于【is-a/子类】类关系
    if not any(kw in label for kw in _KIND_OF_LABELS):
        continue
```
遍历每一条**实例之间的关系**：
1. 获取关系标签，并转小写（忽略大小写）
2. 如果标签不包含任意一个kind-of关键词 → 直接跳过这条关系

> 示例：标签 `Is-A`、`子类`、`subClass` 都会命中；`connected-to`、`contains` 直接跳过。

```python
from_type = inst_type.get(rel.get("from"))
to_type = inst_type.get(rel.get("to"))
if not from_type or not to_type or from_type == to_type:
    continue
```
- `rel["from"]`：源实例ID
- `rel["to"]`：目标实例ID
通过 `inst_type` 查询得到两个实例各自所属的**类**

过滤规则：
1. 源实例没有合法类型 → 跳过
2. 目标实例没有合法类型 → 跳过
3. 源类型 = 目标类型（类自己不能是自己的子类）→ 跳过

```python
key = (from_type, to_type)
if key in seen:
    continue
seen.add(key)
type_rels.append({"from": from_type, "to": to_type, "label": "kind-of", "key": 0})
```
1. 使用元组 `(源类,目标类)` 作为唯一标识做**去重**
   多条实例关系推导出同一组类关系时，只生成一条。
2. 新增一条类层级关系：
   `from_type kind-of to_type`
   语义：from_type 是 to_type 的子类（subClassOf）

## 四、完整推演示例
### 原始数据
```python
# 类定义
types = [{"key":"Engine"}, {"key":"RocketEngine"}]
# 实例
instances = [
    {"id":"eng1", "type":"RocketEngine"},
    {"id":"eng2", "type":"Engine"}
]
# 实例之间的关系
relations = [
    {"from":"eng1", "to":"eng2", "label":"is-a"}
]
```
### 推导流程
1. 关系标签 `is-a` 命中 `_KIND_OF_LABELS`
2. eng1所属类 = RocketEngine；eng2所属类 = Engine
3. 生成类关系：`from: RocketEngine, to: Engine, label: kind-of`
语义：**火箭发动机 是一种 发动机（子类关系）**

## 五、关键规则 & 潜在缺陷
### ✅ 现有优点
1. 兼容中英文多种关系标签；
2. 自动过滤非法类型、自环关系；
3. 自动去重，避免产生大量重复类层级；
4. 纯函数，无外部状态，易于单元测试。

### ⚠️ 现存问题（工程注意）
1. **模糊匹配风险**
使用 `any(kw in label)` 包含匹配。
如果标签是 `has-subclass`，里面包含 `subclass` 关键词，会被误识别为kind-of关系。
> 优化方案：改为精确匹配，或者使用单词边界正则。

2. **单向推导假设**
固定语义：`实例A is-a 实例B` ⇒ `A的类 kind-of B的类`。
不能配置方向，如果业务中存在反向语义会出错。

3. `key:0` 写死常量
输出关系的key固定为0，没有生成唯一标识，后续持久化存储时需要重新处理主键。

4. 不传递推导
只能直接实例关系推导；无法传递推导（A kind-of B，B kind-of C，不会自动推出A kind-of C）。

## 六、本体视角总结
这是 **ABox → TBox 自动派生链路** 的一环：
- ABox：实例 + 实例之间的关系
- 函数提取is-a类实例关系
- 向上归纳，生成TBox层面的类继承层级（subClassOf / kind-of）
和你之前 `derive_datatype_properties_and_constraints` 相互配合：
一个推导**数据属性**，一个推导**类继承关系**，共同实现「只导入实例，自动生成本体框架」。

如果你需要，我可以提供优化版本代码：修复关键词模糊匹配问题、增加日志输出。

# extract_entities_from_excel_file 函数完整讲解
## 1. 总览
```python
async def extract_entities_from_excel_file(tmp_path: str, suffix: str) -> list[dict]:
    """从 Excel 文件中抽取实体列表（不构建完整本体）。"""
```
这是**Excel实体抽取的上层异步接口**，就是上一节 `classify_and_parse` 里面优先调用的那个函数。

**整体逻辑：优先走「schema推断结构化解析」；一旦报错/拿不到实体，就降级到文本解析兜底。**

调用链路：
```
extract_entities_from_excel_file
├─优先路径：excel_schema 整套流水线（推断schema →抽取实体→校验）
│  └─失败 → 进入兜底分支
└─兜底路径：read_document读excel为文本 → _parse_excel_entities从文本里解析实体
```

> 返回：`list[dict]`，实体字典列表，不是对象，是字典，会把内部字段`_source`删掉。

## 逐行拆解
```python
if suffix.lower() == ".xlsx":
    try:
        schema = await excel_schema.infer_excel_schema(tmp_path)
        logger.info("[excel] inferred schema=%s", schema)
```
只对`.xlsx`尝试高级schema流水线；
`infer_excel_schema(tmp_path)`：**推断Excel表格的schema**，自动识别哪一列是名称、英文、编号、定义、属性名、属性值、单位，相当于自动识别表头映射关系。
> 对比你之前写的：`_detect_excel_headers`，`infer_excel_schema`是更完整的版本，输出完整的表格结构描述对象。

```python
entities = excel_schema.extract_entities_from_excel(tmp_path, schema)
```
拿着推断出来的schema，读取excel，提取出实体列表。
这一步就是结构化读取，直接拿到实体，不是文本。

```python
if entities:
    validation = await excel_schema.validate_extraction(schema, entities)
    logger.info("[excel] validation=%s", validation)
    if not validation.get("ok"):
        logger.warning("[excel] validation issues=%s", validation.get("issues"))
```
拿到实体之后，执行校验：
- 校验实体是否合法；字段是否缺失；属性格式是否正常；
- `validation`是字典：`{"ok":bool, "issues":[警告字符串]}`
- 校验不ok**不会抛异常**，只打warning日志，实体依旧继续往下返回。

```python
    for e in entities:
        e.pop("_source", None)
    return entities
```
`pop("_source", None)`：删除实体内部的`_source`字段（内部调试用元数据，对外输出不需要）；
`None`含义：如果key不存在，不会报错。

```python
except Exception as exc:
    logger.warning("[excel] schema pipeline failed, fallback to read_document: %s", exc)
```
> 重点：**整个schema流水线任意一步抛异常，不会向上抛出，仅仅打警告日志，直接跳出try块，进入下面兜底逻辑。**

触发场景举例：
1. excel格式损坏
2. 无法自动推断schema（表头识别失败）
3. 表格行格式错乱

---

## 兜底分支（schema流水线失败就走到这里）
```python
if read_document is None:
    raise RuntimeError(f"Excel 解析依赖 ontology-builder 主包，请安装：pip install -e ../../ontology-builder。详情：{_IMPORT_ERROR}")
```
检查依赖，如果文档读取工具没导入，直接抛出环境错误。

```python
text = read_document(tmp_path)
if not text.strip():
    raise ValueError("未能从 Excel 中识别出有效术语数据")
```
`read_document`：把Excel当成普通文档，提取出表格文本（不是结构化对象，是大段字符串）。
如果读出来是空文本，直接抛异常，这个异常会向上抛给`classify_and_parse`，被外层捕获，转为warnings。

```python
entities = _parse_excel_entities(text)
for e in entities:
    e.pop("_source", None)
return entities
```
`_parse_excel_entities(text)`：**从excel导出的大段文本中反向解析实体**。
> 和前面的结构化解析区别：
> ✅优先路径：直接读excel二进制文件，按行列解析，精度最高。
> ⚠兜底路径：先转文本，再解析文本，精度会下降，属于降级容错。

## 完整流程示例
### 场景1：excel正常，schema推断成功
1. suffix是`.xlsx`
2. `infer_excel_schema`成功推断表头映射
3. `extract_entities_from_excel`拿到实体列表
4. 执行validate_extraction校验，有问题只打日志
5. pop掉`_source`字段，返回实体列表。

### 场景2：excel表头混乱，schema推断抛异常
1. try内部发生异常，进入except，打印警告日志
2. 进入兜底逻辑
3. read_document读取excel得到文本字符串
4. `_parse_excel_entities(text)`从文本解析实体
5. 返回实体列表。

### 场景3：excel读出完全空白
兜底分支中`text.strip()`为空，抛出`ValueError`，向上抛到`classify_and_parse`，捕获后加入warnings。

## 初学者重点理解几个关键点
1. **try里面异常不会抛出去**
`except`捕获全部异常，仅仅打日志，自动降级，保证接口不崩。

2. 校验失败≠流程失败
`validation["ok"]=False`只是有警告，实体照样返回，不会抛出异常。

3. 两个解析路径对比

|路径|方式|优点|缺点|
|----|----|----|----|
|schema流水线|直接解析excel行列|精度高，区分实体行、属性附属行|表头错乱会直接失败|
|兜底_parse_excel_entities|先转文本，再解析文本|容错强|丢失表格行列结构，解析能力下降|

4. `e.pop("_source", None)`
`pop(key,默认值)`：删除字典key；key不存在，返回默认值，不会报错。

5. 只有`.xlsx`才走高级schema流水线；其他后缀直接走兜底。

## 和上层代码的关联（回忆classify_and_parse）
```python
try:
    entities = await ontology_service.extract_entities_from_excel_file(tmp_path, suffix)
except Exception as exc:
    logger.warning("[multi-source] Excel schema 抽取失败，回退到 read_document: %s", exc)
    doc_text = read_document(tmp_path)
    doc_text = _truncate(doc_text, MAX_FILE_CHARS)
    entities = ontology_service.parse_excel_entities(doc_text)
```
> 注意：
`extract_entities_from_excel_file`内部**已经自带一套降级逻辑**；
而`classify_and_parse`外层又包了一层try‑except，等于**双重容错保护**。

第一层：本函数内部：schema流水线失败 → 降级文本解析
第二层：上层调用处：本函数全部逻辑抛出异常 → 再一次兜底。

## 潜在小问题（拓展思考）
1. 如果schema流水线返回`entities=[]`（不是抛异常，但是实体为空），**不会进入兜底分支**，直接返回空列表。
> 也就是：推断schema成功，但是表格没有识别出任何实体，不会走到下面read_document兜底。
> 如果希望这种情况也触发兜底，需要增加判断：
> ```python
> if entities:
>     ...
> else:
>     raise RuntimeError("schema extract got zero entities")
> ```

# build_abox 函数完整逐行解析
## 一、函数整体作用
这个函数是**本体ABox实例层构建核心逻辑**：
输入：已有概念TBox（类型定义）+ 待解析文本 + 发动机型号提示
输出：结构化实例、实例关系、数据属性、约束公理，组成完整实例知识库。
业务定位：接收文档文本，调用大模型抽取实体实例，再做校验、自动派生属性约束，供上层接口返回给前端图谱渲染。

## 二、入参逐句说明
```python
async def build_abox(
    tbox_or_ontology: dict[str, Any] | None,
    source_text: str,
    *,
    include_props: bool = True,
    model_hints: list[str] | None = None,
) -> dict[str, Any]:
```
1. `tbox_or_ontology`
    已有的模式层本体（TBox），里面存所有**概念类型（发动机、燃烧室、涡轮等）**；兼容两种旧字段：`types` / `ontoTypes`，传None代表无预先定义类型。
2. `source_text`
    待抽取实例的原始文本（PDF/Excel/SysML解析出来的纯文本），大模型从这里提取实体、参数、关系。
3. `*,`
    Python语法：后面所有参数必须**关键字传参**，不能按位置传，防止调用顺序错乱。
4. `include_props: bool = True`
    开关：True=抽取实例自定义属性（推力、循环方式、推进剂等）；False=只抽实例和关系，忽略属性。
5. `model_hints`
    型号提示列表，就是前端接口传过来的 `model_hints: ["F-1"]`；告诉LLM优先生成指定型号发动机实例，匹配业务需求。

## 三、返回值结构（注释说明）
```python
Returns:
    dict 形如 {
        "instances": [...],          # 所有抽取到的实体实例
        "relations": [...],           # 实例之间的关系（part-of、kind-of等）
        "instanceAxioms": [...],      # 实例数值约束（推力=6800kN、氧化剂=液氧）
        "datatypeProperties": [...],  # 自动派生的数据属性定义
        "typeBindings": {id: type_key} # 实例id → 所属类型key映射，给关系推理用
        "constraints": [...],         # 兼容旧代码的别名，和instanceAxioms完全一样
    }
```

## 四、分步拆解代码逻辑
### 步骤1：提取所有合法类型key，用于后续校验实例type
```python
types = (
    (tbox_or_ontology or {}).get("types")
    or (tbox_or_ontology or {}).get("ontoTypes")
    or []
)
valid_type_keys = {t.get("key") for t in types if t.get("key")}
type_lines = ", ".join(f"{t.get('key')}: {t.get('name')}" for t in types if t.get("key"))
```
- 兼容新旧本体字段 `types` / `ontoTypes`，兜底为空列表；
- `valid_type_keys` 集合存放所有合法概念key，**限制实例type只能从中选取**，防止LLM随便造不存在的类型；
- `type_lines` 拼接成字符串，塞进大模型提示词，告诉模型现有哪些类型。

### 步骤2：组装LLM系统提示词（约束大模型输出规则）
```python
extra_system_lines = [
    "",
    "## 模式层（TBox）约束",
    "已有类别：" + (type_lines or "（无）") + "。",
    "请把抽取出的实例的 type 字段严格限定在已有类别 key 中；",
    "若需要新类别，请额外标注 ``new_type_suggestion`` 字段而非自由命名。",
]
extra_system = "\n".join(extra_system_lines)
if model_hints:
    extra_system += "\n需要支持的具体型号实例（hint）：" + "、".join(model_hints)

system = (ONTOLOGY_BUILD_SYSTEM if include_props else ONTOLOGY_BUILD_SYSTEM_NO_PROPS) + extra_system
```
1. 基础系统提示词二选一：
    - `include_props=True`：完整提示，要求抽取实例属性；
    - `include_props=False`：精简提示，忽略属性只抽实例关系。
2. 追加TBox约束：强制LLM实例type只能使用已存在的类型，不能乱造；
3. 追加型号hint：把前端传来的`["F-1"]`写入提示词，引导模型优先生成对应发动机实例。

### 步骤3：构造对话消息，调用大模型
```python
messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": ONTOLOGY_BUILD_USER.format(source_text=source_text)},
]
raw = await llm_service.chat(messages, temperature=0.1, max_tokens=8192)
data = llm_service.extract_json(raw)
if not data or "instances" not in data:
    raise ValueError(...)
```
1. 消息结构：系统约束词 + 用户待解析文本；
2. `temperature=0.1`：低随机性，保证抽取结果稳定、结构化；
3. `extract_json`：之前讲过的工具函数，清洗``标签、剥离markdown代码块，提取纯JSON；
4. 校验：没有instances直接抛异常，上层接口捕获后返回前端报错。

### 步骤4：数据修复与合法性校验
```python
data = _ensure_colors(data)
# 用 valid_type_keys 做引用校验
if valid_type_keys:
    for inst in data.get("instances", []):
        if inst.get("type") not in valid_type_keys and valid_type_keys:
            inst["type"] = list(valid_type_keys)[0]  # 兜底
data = _validate_references(data)
```
1. `_ensure_colors`：给实例补全默认颜色，前端图谱渲染用；
2. 实例类型兜底：如果LLM生成的实例type不在合法类型里，自动改成**第一个合法类型**，避免后续推理报错；
3. `_validate_references`：你之前解析过的函数，过滤两端实例id不存在的无效关系，修复非法type。

### 步骤5：自动派生数据属性与约束公理（核心自动建模逻辑）
```python
instances = data.get("instances", [])
relations = data.get("relations", [])
dpp, axioms = derive_datatype_properties_and_constraints(instances, valid_type_keys)
```
调用之前讲过的`derive_datatype_properties_and_constraints`：
- 遍历所有实例的属性键值对，自动生成本体**数据属性datatypeProperties**；
- 提取每个实例的数值约束，存入`instanceAxioms`（推力、尺寸、介质等参数约束）。

### 步骤6：构建实例-类型映射，打印耗时日志，组装返回字典
```python
typeBindings = {i["id"]: i.get("type") for i in instances if i.get("id")}
logger.info(...)
return {
    "instances": instances,
    "relations": relations,
    "instanceAxioms": axioms,
    "datatypeProperties": dpp,
    "typeBindings": typeBindings,
    "constraints": axioms, # 兼容旧前端/旧调用方
}
```
1. `typeBindings`：实例id → 所属类型key的映射表，给`infer_type_relations`类型关系推导函数使用；
2. 日志打印耗时、实例/关系/属性数量，方便调试性能；
3. 兼容字段`constraints`：旧代码只识别这个字段，新代码统一用`instanceAxioms`，两边同时返回保证兼容。

## 五、整条业务调用链路串联（结合你前后端代码）
1. 前端fetch `/api/ontology/build-abox`，上传 `documents` 文件列表、`model_hints: ["F-1"]`；
2. 后端接口读取多个文档，调用`_load_excel_document/_load_html_document`等解析出合并`source_text`；
3. 传入 `build_abox(tbox本体, source_text, model_hints=["F-1"])`；
4. build_abox 携带型号提示调用LLM，抽取发动机实例、零件、参数、关系；
5. 自动校验实例类型、派生数据属性约束，生成结构化ABox数据；
6. 接口把返回字典序列化JSON，传回前端绘制知识图谱。

## 六、关键设计亮点总结
1. **强约束LLM输出**：把现有TBox类型全部注入提示词，防止模型随意创建新概念；
2. **型号hint定向抽取**：对接前端下拉选择，精准提取指定发动机实例；
3. **容错兜底机制**：非法实例type自动修复、无效关系过滤，保证本体数据合法；
4. **自动化本体派生**：不用人工定义属性，从实例参数自动生成datatypeProperties；
5. **向下兼容**：同时提供新旧字段名，老页面不用同步改造即可对接新接口。