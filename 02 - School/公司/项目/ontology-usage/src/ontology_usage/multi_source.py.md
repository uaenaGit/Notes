---
created: 2026-08-04T15:52
updated: 2026-08-04T15:53
---
# classify_and_parse 函数完整讲解
## 1. 函数总览
### 整体定位
这是**文件上传入口核心异步函数（FastAPI接口后端逻辑）**
接收前端上传的多个文件 + 可选文本输入；
自动区分文件角色：主Excel模板、补充Excel、普通内容文档；
统一解析、捕获异常、拼接全部上下文文本，最后输出三元组：
`(分类后的文件对象列表, 合并完整文本, 警告信息列表)`

### 返回值定义
```python
tuple[list[ClassifiedFile], str, list[str]]
(
    classified: list[ClassifiedFile], # 每个文件：角色、名称、解析结果
    combined: str,                    # 全部内容拼接后的总上下文（送给LLM）
    warnings: list[str]              # 警告数组，前端展示提示
)
```

### 前置常量说明（代码隐含）
- `MAX_FILES`：最大上传文件数量
- `MAX_FILE_CHARS`：单个文件文本最大长度
- `MAX_TOTAL_CHARS`：所有文件合并后的总文本上限
- `ALLOWED_EXCEL`：允许的excel后缀 `.xlsx`
- `ALLOWED_CONTENT`：txt/md/html/pdf等文本类后缀
### 文件角色枚举 FileRole
1. `TEMPLATE`：**主模板Excel**（第一个excel）
2. `SUPPLEMENT`：**补充Excel**（其余excel）
3. `CONTENT`：普通内容文件（txt、html、pdf等）

### 完整数据流
```
前端上传 files + 可选text
    ↓ 数量校验
    ↓ _classify_files：自动给每个文件分配角色
    ↓ 循环每个上传文件
        → 临时保存文件到本地
        → 根据角色区分解析方式
            Excel：优先抽取实体；失败则降级解析
            普通文档：直接读取文本
        → 封装 ClassifiedFile
        → 异常捕获，生成warning
        → 删除临时文件
    ↓ 汇总所有文件内容 + 前端传入text
    ↓ 拼接全局上下文文本，并截断总长度
    ↓ return (classified列表,合并文本,warnings)
```

## 2. 逐行源码拆解
```python
async def classify_and_parse(
    files: list[UploadFile],
    text: str | None = None,
) -> tuple[list[ClassifiedFile], str, list[str]]:
```
- `UploadFile`：FastAPI 内置类型，接口接收上传文件专用
- `text`：前端额外附带的文本输入（和文件内容合并在一起）
- `async`：异步函数，接口IO场景不阻塞服务

```python
warnings: list[str] = []
```
收集所有提示、错误告警，不直接抛出异常中断整体流程，**能解析多少算多少**。

```python
if len(files) > MAX_FILES:
    raise ValueError(f"单次上传文件数超过上限 {MAX_FILES}")
```
硬限制：文件数量超标直接报错，拒绝处理。

```python
if read_document is None or combine_documents is None:
    raise RuntimeError(
        "多源文档解析依赖 ontology-builder 主包，请安装：pip install -e ../../ontology-builder。"
        f"详情：{_DOCUMENTS_IMPORT_ERROR}"
    )
```
环境检测：文档解析工具未导入成功，提前抛出环境错误。

```python
classified: list[ClassifiedFile] = []
roles = _classify_files([f.filename or "" for f in files])
```
调用 `_classify_files` 核心规则：
**第一个Excel文件 → TEMPLATE(主模板)；剩下Excel → SUPPLEMENT；其他所有文件 → CONTENT**
输出：`[(文件名, FileRole), (文件名, FileRole), ...]`

```python
for file, (filename, role) in zip(files, roles):
```
同时遍历【上传文件】和【对应分配的角色】

```python
suffix = Path(filename).suffix.lower()
# 校验：模板/补充文件要求必须是excel
if role in (FileRole.TEMPLATE, FileRole.SUPPLEMENT) and suffix not in ALLOWED_EXCEL:
    warnings.append(f"{filename}: 期望 Excel 文件但后缀为 {suffix}")
    continue
# 普通内容文件校验后缀
if role == FileRole.CONTENT and suffix not in ALLOWED_CONTENT:
    warnings.append(f"{filename}: 不支持的文件格式 {suffix}")
    continue
```
格式校验不通过 → 添加警告，跳过当前文件，不崩溃。

```python
tmp_path = await _save_upload(file)
```
将前端内存中的上传文件，异步保存到服务器**临时文件路径**；
openpyxl等库需要本地文件路径读取，无法直接读取内存流。

```python
try:
    if role in (FileRole.TEMPLATE, FileRole.SUPPLEMENT):
        # ========= Excel文件解析分支 =========
        try:
            # 优先方案：ontology服务直接提取实体（结构化解析，最优路径）
            entities = await ontology_service.extract_entities_from_excel_file(tmp_path, suffix)
        except Exception as exc:
            # 【降级容错逻辑】结构化解析失败时执行兜底
            logger.warning("[multi-source] Excel schema 抽取失败，回退到 read_document: %s", exc)
            doc_text = read_document(tmp_path)
            doc_text = _truncate(doc_text, MAX_FILE_CHARS)
            entities = ontology_service.parse_excel_entities(doc_text)
        
        # 封装文件对象，携带解析出来的实体列表
        cf = ClassifiedFile(role, filename, suffix, entities=entities)
    else:
        # ========= 普通文本文件分支 txt/html/pdf/md =========
        doc_text = read_document(tmp_path)
        doc_text = _truncate(doc_text, MAX_FILE_CHARS)
        cf = ClassifiedFile(role, filename, suffix, text=doc_text)
    classified.append(cf)

except Exception as exc:
    # 任意文件解析报错，记录警告，不中断整个任务
    warnings.append(f"{filename}: 解析失败 {exc}")
finally:
    # 【极其重要】无论成功失败，删除临时文件，防止磁盘占满
    Path(tmp_path).unlink(missing_ok=True)
```

> ✨重点Excel降级逻辑解读（初学者重点）
> 1.首选：直接读取Excel文件 → 输出结构化`_ExcelEntity`实体（就是前面整套Excel解析链路）
> 2.如果解析崩溃（表格格式异常、表头识别失败）
> 降级策略：先把Excel当成普通文档读出原始文本，再尝试从文本中提取实体。
> 目的：提高接口容错，不要因为一个表格格式错误导致整个上传流程废掉。

```python
# 开始组装送入LLM的完整上下文
parts: list[str] = []
if text:
    parts.append(text.strip()) # 先放入前端手动输入文本

for cf in classified:
    if cf.role == FileRole.CONTENT:
        # 普通文档：直接拼接文件名+文本
        parts.append(f"【{cf.filename}】\n{cf.text}")
    elif cf.entities:
        # Excel文件：调用 _render_entities_text，等价于之前的 _entities_to_text
        # 把实体列表转为Markdown文本再拼接
        parts.append(f"【{cf.filename}】\n{_render_entities_text(cf.entities)}")

combined = "\n\n".join(parts)
combined = _truncate(combined, MAX_TOTAL_CHARS)
```
把所有来源内容统一拼接成一段大文本，最后执行**全局总长度截断**，防止超出LLM上下文窗口。

```python
return classified, combined, warnings
```

## 3. 业务示例演示
### 前端上传内容
1. `本体模板.xlsx`（第一个Excel → TEMPLATE）
2. `补充术语.xlsx`（第二个Excel → SUPPLEMENT）
3. `发动机说明.html`（CONTENT）
4. 附带前端输入文本：`请基于以上本体构建TBox`

运行过程：
1. 三个文件分别保存临时文件、解析
2. 两个Excel解析成实体列表，自动转为markdown文本
3. html读取原始文本
4. 所有内容 + 前端文本合并
5. 生成combined大文本，准备传给大模型
6. 返回：
    - classified：3个ClassifiedFile对象，标记各自角色
    - combined：全部拼接文本
    - warnings：空列表（没有错误）

## 4. 关键设计亮点
1. **角色区分机制**
区分主模板Excel、补充Excel、普通文档，上层业务可以优先使用主模板本体；
2. **Excel双层容错策略**
结构化解析失败自动降级，提升接口稳定性；
3. **临时文件自动清理**
finally保证磁盘不会堆积临时上传文件；
4. **容错设计：局部失败 ≠ 整体失败**
单个文件解析失败仅记录warning，其余文件照常处理；
5. **双层文本截断**
单个文件限制长度 + 全部文本汇总后再次限制，双重保护LLM上下文溢出；
6. **统一输出文本**
不管是Excel结构化数据、html、txt，最终全部转换成统一文本格式，喂给LLM，上层不需要区分文件类型。

## 5. 和你之前学习代码的关联
```
ontology_service.extract_entities_from_excel_file(tmp_path)
    → 内部最终调用 【_load_excel_document】
        → _parse_excel_workbook
        → _entities_to_text
```
你前面学习的整套Excel解析函数，**都是本函数底层依赖**。

## 6. 初学者容易疑惑点
1. 为什么要先存临时文件？
FastAPI的UploadFile是内存数据流；openpyxl、各类文档解析库只支持磁盘路径读取，无法直接读取流。
2. async 为什么配合`await _save_upload`？
文件IO使用异步操作，不会阻塞FastAPI服务，支持并发上传。
3. `unlink(missing_ok=True)`
删除文件；即使文件已经不存在，也不会抛出异常。
4. 为什么Excel实体要转成文本？
大模型只能接收文本，无法直接传入Python对象，因此统一渲染为Markdown。

## 7. 现存可优化点（拓展思考）
1. 可以区分警告等级；
2. 增加日志，记录每个文件解析耗时；
3. 可以支持开关：控制是否启用Excel降级解析；
4. 可以给截断文本增加提示：`【内容过长，已截断】`。