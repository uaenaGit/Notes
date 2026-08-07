---
created: 2026-08-07T10:32
updated: 2026-08-07T14:58
---
# `_apply_kg_alignment` 函数完整解析
## 整体概述
```python
def _apply_kg_alignment(
    raw_kg: dict[str, Any],
    mapping: dict[str, Any],
    ontology: dict[str, Any],
) -> dict[str, Any]:
```
**业务目的**
LLM从文本抽出来的原始知识图谱`raw_kg`：节点id是临时id、类型不标准、属性字段混乱。
`mapping`是大模型输出的映射规则：规定原始节点应该对应本体哪个类型/实例，原始边对应本体哪些关系。
这个函数**依据mapping规则，把原始图谱对齐到已有的本体ontology**。

> 重要设计：**无论映射成功还是失败，所有节点、边都保留在输出图谱中；映射失败的不会丢弃，只是单独记录一份失败清单，附带失败原因，供前端展示告警。**

**入参**
1. `raw_kg`：LLM抽取原始图谱，结构`{"nodes":[...], "edges":[...]}`
2. `mapping`：LLM生成映射规则，包含`node_mapping`节点映射、`edge_mapping`边映射
3. `ontology`：系统本体，包含`ontoTypes`类型定义、`instances`已有本体实例

**返回值**
```python
{
    "nodes": nodes,                # 处理完成全部节点（成功+失败）
    "edges": edges,                # 处理完成全部边（成功+失败）
    "unmapped_nodes": unmapped_nodes, # 映射失败节点，带reason
    "unmapped_edges": unmapped_edges, # 映射失败边，带reason
    "mapping_stats": {...}        # 映射统计：总数量、成功数量
}
```

---

## 第一阶段：构建查找字典（预处理）
```python
raw_nodes = raw_kg.get("nodes", [])
raw_edges = raw_kg.get("edges", [])

# node_mapping key:原始节点raw_id，value映射规则
node_mapping = {m["raw_id"]: m for m in mapping.get("node_mapping", [])}
raw_edge_rules = mapping.get("edge_mapping", [])

# 边精确匹配：(from,to,label)三元组
edge_mapping = {
    (e.get("from"), e.get("to"), e.get("label")): e
    for e in raw_edge_rules
}
# 兜底匹配：LLM输出省略label，只用(from,to)二元组匹配
edge_mapping_fallback = {
    (e.get("from"), e.get("to")): e
    for e in raw_edge_rules
}

# 本体实例字典 key=实例id，快速查找本体实例
onto_instances = {i["id"]: i for i in ontology.get("instances", [])}
# 本体全部合法type集合，用来校验type是否合法
onto_type_keys = {t.get("key", "") for t in ontology.get("ontoTypes", [])}
```
把列表转成字典/集合，后续查找O(1)速度，不用反复循环遍历。
> `edge_mapping_fallback`专门应对LLM输出边缺失`label`的脏输出；缺点：相同`(from,to)`多条不同label规则会被覆盖。

---

## 第二阶段：循环处理每一个节点 raw_nodes
```python
nodes: list[dict[str, Any]] = []
unmapped_nodes: list[dict[str, Any]] = []
mapped_node_ids: set[str] = set()

for n in raw_nodes:
    nid = n.get("id")
    rule = node_mapping.get(nid)

    # 分支A：存在映射规则，并且mappable=True允许映射
    if rule and rule.get("mappable"):
        mapped_node_ids.add(nid)
        # 优先使用映射规则给出onto_type；没有则使用原始节点type
        onto_type = rule.get("onto_type") or n.get("type")
        # 防御校验：如果onto_type不在本体合法类型集合，退回原始节点type
        if onto_type not in onto_type_keys:
            onto_type = n.get("type")

        # {**n, "type": onto_type}：复制原节点，覆盖type，生成新字典，不改动原始n
        merged = {**n, "type": onto_type}

        # 如果映射到本体已经存在的实例onto_instance_id
        inst_id = rule.get("onto_instance_id")
        if inst_id and inst_id in onto_instances:
            inst = onto_instances[inst_id]
            # 本体实例name优先；本体没有name，则保留merged原有name
            merged["name"] = inst.get("name") or merged.get("name")
            merged["desc"] = inst.get("desc") or merged.get("desc")

            # =========属性合并逻辑=========
            # 本体实例的props作为基础
            props = dict(inst.get("props") or {})
            # 兼容LLM输出properties字段
            props.update(merged.get("properties") or {})
            # 兼容LLM输出简写props字段
            props.update(merged.get("props") or {})
            # 统一标准化输出字段 properties
            merged["properties"] = props

        nodes.append(merged)

    # 分支B：无法映射（没有规则 / mappable=False）
    else:
        # 记录失败信息，给前端告警
        unmapped_nodes.append({
            "id": nid,
            "name": n.get("name"),
            "reason": rule.get("reason") if rule else "无法映射到本体类型",
        })
        # 重点：节点仍然保留进图谱，不丢弃
        nodes.append({**n})
```

### 节点业务逻辑梳理
1. 根据节点原始id拿到LLM给出的映射规则`rule`；
2. 如果允许映射：
    - 确定目标`onto_type`，校验类型是否存在本体；不存在就回退原始type；
    - `merged = {**n, "type": onto_type}`复制节点，覆写type；
    - 如果映射到本体已有实例`inst`：
        - **本体实例的name、desc优先级高于大模型抽取出来的内容**；
        - 兼容LLM输出不稳定的两个属性字段`props` / `properties`，全部合并，统一存入`merged["properties"]`；
    - 加入nodes列表。
3. 如果不能映射：
    - 把id、name、失败原因存入`unmapped_nodes`；
    - **原始节点依旧保留在nodes中，图谱不会丢数据**。

> 你之前疑惑的两行：
> `merged["name"] = inst.get("name") or merged.get("name")`
> 利用or短路：inst有name就用inst；inst没有，表达式等价`merged["name"] = merged.get("name")`，等于不修改。
> 只是简写写法，可读性一般。

> `props`与`properties`两个key：大模型输出不稳定，一会写properties，一会简写props，代码把两份都读取合并，最终统一输出`properties`。

---

## 第三阶段：循环处理每一条边 raw_edges
```python
edges: list[dict[str, Any]] = []
unmapped_edges: list[dict[str, Any]] = []
mapped_edge_count = 0

for e in raw_edges:
    key = (e.get("from"), e.get("to"), e.get("label"))
    fallback_key = (e.get("from"), e.get("to"))
    # 优先三元组精确匹配；匹配不到走二元组兜底，应对LLM丢label
    rule = edge_mapping.get(key) or edge_mapping_fallback.get(fallback_key)

    if rule and rule.get("mappable"):
        mapped_edge_count += 1
        edges.append({**e})
    else:
        unmapped_edges.append({
            "from": e.get("from"),
            "to": e.get("to"),
            "label": e.get("label"),
            "reason": rule.get("reason") if rule else "无法映射到本体关系",
        })
        edges.append({**e}) # 未映射边同样保留
```

边逻辑和节点逻辑大体相似，但**有一个重要区别**：
> 节点会修改type、合并实例name/desc/props；
> **边这里只做匹配标记统计，不会修改边本身的任何字段**。

逻辑：
1. 优先`(from,to,label)`三元组精确匹配映射规则；匹配失败，使用`(from,to)`二元组兜底；
2. 如果命中规则且`mappable=True`，计数+1，直接把原始边加入edges；
3. 映射失败：记录到`unmapped_edges`，带上reason；**原始边依旧保留在edges中**。

> 风险：`edge_mapping_fallback`字典，当`(from,to)`相同、label不同多条规则，后面条目覆盖前面，会丢失规则。

---

## 第四阶段：组装返回结果
```python
return {
    "nodes": nodes,
    "edges": edges,
    "unmapped_nodes": unmapped_nodes,
    "unmapped_edges": unmapped_edges,
    "mapping_stats": {
        "total_nodes": len(raw_nodes),
        "mapped_nodes": len(mapped_node_ids),
        "total_edges": len(raw_edges),
        "mapped_edges": mapped_edge_count,
    },
}
```
- `nodes`、`edges`：完整图谱，映射成功、失败全部数据都在这里；
- `unmapped_nodes/unmapped_edges`：失败清单，前端可以展示警告弹窗，告诉用户哪些实体、关系没有映射到本体；
- `mapping_stats`：统计指标，页面展示映射成功率。

## 整体业务链路
1. LLM从文档抽取`raw_kg`（临时id，类型混乱，字段不稳定）
2. LLM输出`mapping`映射规则：告诉程序哪些原始节点/边对应本体
3. `_apply_kg_alignment`执行对齐：
   - 节点：覆写本体标准type；如果映射到本体实例，合并实例name、desc、属性；兼容LLM输出`props/properties`两套字段。
   - 边：精确匹配+兜底匹配，只做标记统计，不修改边内容。
4. **不丢弃任何节点、边**；映射失败数据保留，单独记录失败原因。
5. 返回对齐后的图谱、失败清单、统计数据，交给上层`build_abox`，同时给到前端做提示。

## 代码现存小问题总结
1. `merged["name"] = inst.get("name") or merged.get("name")`简写可读性差；
2. 边的fallback字典存在key覆盖风险；
3. 原始节点的`props`不会删除，返回字典同时存在`props`、`properties`两个key，上层读取优先使用`properties`；
4. 属性合并发生key冲突时直接覆盖，没有日志告警。