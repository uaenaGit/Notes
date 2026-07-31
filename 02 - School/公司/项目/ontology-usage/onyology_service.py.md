---
created: 2026-07-31T11:01
updated: 2026-07-31T16:31
---
# 一、`build_ontology` 函数详解

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

([[#二、`_validate_references(data dict)` 解析]])LLM 可能生成指向不存在实例的 relations（比如 `from: "FOO"` 但 `FOO` 这个实例根本不存在），或者实例的 `type` 指向一个不存在的 `ontoType`。这个函数：

- 过滤掉无效的 relations（`from` 或 `to` 在实例 ID 集合中找不到的）
- 把 `type` 无效的实例修正为第一个有效类型

#### 4c. 推导数据属性与约束

```
dpp, axioms = derive_datatype_properties_and_constraints(instances, valid_types)
data["datatypeProperties"] = dpp
data["constraints"] = axioms
```

这个函数()遍历所有实例的 `props`（属性字典），做两件事：

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

# 二、`_validate_references(data: dict)` 解析
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

# 边界情况梳理
1. `ontoTypes` 为空列表 → `valid_types`为空，不会执行type自动修复（防止强行赋值）
2. `instances` 为空 → `inst_ids`为空，**所有relations全部清空**
3. relation缺少`from` 或者 `to` 字段 → `r.get()`得到`None`，必然不在inst_ids，这条关系被过滤
4. 实例type大小写不一致（`engine` vs `Engine`）：代码不会自动兼容，需要额外统一大小写

# 潜在优化点（你后续开发可以参考）
1. 不要使用set存放valid_types，解决`list(valid_types)[0]`顺序随机问题；
2. 非法type不要静默覆盖，可以增加日志告警，方便排查脏数据；
3. 区分「原地修改」，如果不想改动原始入参，可以先深拷贝一份data再处理。

如果你需要，我可以写一段测试代码，复制就能运行，直观看到修复前后的数据变化。