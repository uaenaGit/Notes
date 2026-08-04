---
created: 2026-08-04T10:42
updated: 2026-08-04T14:51
---
# normalize_text 文本规范化函数完整讲解
```python
def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    compact: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line
        if blank and previous_blank:
            continue
        compact.append(line)
        previous_blank = blank
    return "\n".join(compact).strip()
```
## 一、整体作用
清洗原始文本，实现3个目标：
1. 统一换行符（Windows / Mac / Linux换行统一）
2. 删除每行首尾多余空格
3. **连续多行空行合并成最多一行空行**
4. 最终去掉文本开头、结尾所有空白

适合处理LLM输出、文档读取文本，消除杂乱换行。

## 二、逐行拆解
```python
def normalize_text(text: str) -> str:
```
接收字符串文本，返回处理后的字符串。

```python
lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
```
分步执行：
1. `text.replace("\r\n", "\n")`：Windows换行 `\r\n` → `\n`
2. `.replace("\r", "\n")`：老式Mac换行 `\r` → `\n`
> 执行完之后，**所有换行统一变成 \n**
3. `.split("\n")` 根据换行切割，得到一行一行文本列表
4. `[line.strip() for line in ...]` 列表推导式：每一行前后空格全部删掉

举例：
原始行 `  hello world  ` → 处理后 `hello world`
原始行 `   `（只有空格）→ strip之后变成空字符串 `""`

```python
compact: list[str] = []
previous_blank = False
```
- compact：存放最终整理完成的行
- previous_blank：标记**上一行是不是空行**

```python
for line in lines:
    blank = not line  # line是空字符串 "" → blank=True
    if blank and previous_blank:
        continue  # 当前是空行 + 上一行也是空行 → 跳过，不加入列表
    compact.append(line)
    previous_blank = blank
```
核心逻辑：**禁止连续空行**
- 如果当前是空行，上一行也为空 → 丢弃，防止多个换行堆积
- 其他情况正常加入结果列表

模拟示例：
行序列：`["a", "", "", "b"]`
1. line="a"，非空 → 加入，previous_blank=False
2. line=""，空，上一行非空 → 加入，previous_blank=True
3. line=""，空，上一行是空 → continue，跳过！
4. line="b"，非空 → 加入，previous_blank=False
最终compact = `["a", "", "b"]`
连续两个空行被压缩成1个。

```python
return "\n".join(compact).strip()
```
1. `"\n".join(compact)` 使用换行符把所有行拼接回去
2. 最后的 `.strip()`：删掉**整个文本最开头、最末尾**的换行/空白

## 三、输入输出演示
### 输入文本（杂乱格式）
```

你好

这是第一段



这是第二段

```
处理过程：
1. 每行去空格，分割后得到 `["", "你好", "", "", "这是第一段", "", "", "这是第二段", ""]`
2. 合并连续空行
3. 首尾空白清除

### 输出结果
```
你好

这是第一段

这是第二段
```
✅ 多个空行全部压缩为单行空行，首尾没有多余换行。

## 四、适用场景 & 优缺点
✅ 优点：
- 跨平台兼容各种换行符
- 简洁纯Python，无第三方依赖
- 保留段落分隔（允许段落之间存在一行空行）

⚠️ 局限：
只会压缩**垂直空行**，不会处理一行内部多余空格；
如果想要把 `hello   world` 多个空格变成单个空格，需要额外处理。

## 五、初学者容易疑问点
1. `blank = not line`
空字符串 `""` 在Python中判定为假，`not "" = True`
非空字符串 `not "abc" = False`
用来快速判断该行是不是空白行。

2. `continue` 作用
直接结束本次循环，不执行后面 `append`，相当于丢弃当前这一行。

# `_load_html_document` 函数完整讲解（含BeautifulSoup基础说明）
## 1. 整体功能
读取本地HTML文件，借助BeautifulSoup解析网页，剔除JavaScript、CSS样式代码，抽取页面纯净正文文本；再调用`normalize_text()`规范化空白与换行，最终统一封装为`LoadedDocument`对象返回。
该函数是项目HTML文档专用加载器，和纯文本加载函数`_load_text_document`对外输出相同结构，上层业务无需区分文件类型。

依赖前置：
```bash
pip install beautifulsoup4
from bs4 import BeautifulSoup
from pathlib import Path
```

## 2. 完整源码
```python
def _load_html_document(path: Path) -> LoadedDocument:
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style"]):
        element.decompose()
    text = normalize_text(soup.get_text("\n"))
    return LoadedDocument(
        path=path,
        suffix=path.suffix.lower(),
        text=text,
        metadata={"parser": "beautifulsoup"}
    )
```

## 3. 逐行代码拆解 + BeautifulSoup知识点讲解
```python
def _load_html_document(path: Path) -> LoadedDocument:
```
- 入参：`path` 为`pathlib.Path`文件路径对象，指向本地html文件
- 返回值：标准化文档结构体`LoadedDocument`

```python
html = path.read_text(encoding="utf-8")
```
以UTF-8编码读取HTML文件，获取原始网页字符串。

```python
soup = BeautifulSoup(html, "html.parser")
```
### BeautifulSoup知识点1：构建文档解析树
1. `BeautifulSoup()`：解析HTML字符串的核心构造函数
2. 第一个参数：待解析的原始html文本
3. 第二个参数`"html.parser"`：解析器
   - Python内置解析器，**无需额外安装第三方库**；
   - 备选`lxml`解析器速度更快，但是需要额外安装包，本项目选择内置实现，减少环境依赖。
4. 变量`soup`：把一串杂乱的HTML文本，转换成**结构化标签树**，程序可以轻松查找、删除、读取标签内容。

```python
for element in soup(["script", "style"]):
    element.decompose()
```
### BeautifulSoup知识点2：查找标签并删除
1. `soup(["script", "style"])`
    等价 `soup.find_all(["script", "style"])`，自动查找文档中**全部**`<script>`、`<style>`标签
    - `<script>`：存放JS代码
    - `<style>`：存放CSS样式
2. `.decompose()`
    把当前标签**从文档树上彻底移除**，标签以及标签内部所有内容全部销毁。
> 对比区分（初学者重点）
> - `decompose()`：直接删除丢弃内容（本代码使用）
> - `extract()`：删除标签，同时返回被删除的内容，适合需要临时保存被移除文本的场景

作用：防止后续提取文本时，把代码、样式混入正文，造成文本噪音。

```python
text = normalize_text(soup.get_text("\n"))
```
### BeautifulSoup知识点3：提取页面纯文本
`soup.get_text("\n")`
遍历整个标签树，提取所有标签内可见文字；
传入参数`"\n"`：**不同标签的文本之间使用换行隔开**，保留原文段落结构。

示例对比：
假设html：`<h1>标题</h1><p>正文</p>`
- `soup.get_text()` → `标题正文`（文字挤在一起，丢失段落）
- `soup.get_text("\n")`
```
标题
正文
```

随后调用你项目内的`normalize_text()`：
1. 统一各类操作系统换行符；
2. 每行首尾空格清除；
3. 连续多行空行压缩为单行空行；
4. 清除文本首尾多余空白。

```python
return LoadedDocument(
    path=path,
    suffix=path.suffix.lower(),
    text=text,
    metadata={"parser": "beautifulsoup"}
)
```
组装统一文档对象：
- path：原始文件路径
- suffix：小写后的文件后缀（`.html`）
- text：清洗完成后的纯净文本
- metadata：标记解析器类型，方便日志、后续处理区分文档解析方式

## 4. 完整执行流程
1. 读取本地HTML原始字符串
2. BeautifulSoup加载HTML，生成结构化文档树
3. 删除所有script、style标签，清理代码噪音
4. 提取网页文字，标签之间使用换行分隔
5. normalize_text规范化换行、空白、空行
6. 封装为统一文档对象返回

## 5. 运行示例演示
原始HTML片段
```html
<html>
<style>body{color: black;}</style>
<script>console.log("测试")</script>
<h1>发动机文档</h1>
<p>本体建模相关说明</p>
</html>
```
处理后提取文本：
```
发动机文档
本体建模相关说明
```
CSS、JS内容全部被清除。

## 6. 函数局限性
1. 仅移除script、style，**不会自动清理导航栏、页脚、广告等多余网页模块**；如需进一步降噪，需要追加标签过滤；
2. 无法处理JavaScript动态渲染网页（只能解析静态HTML）；
3. 图片alt文字会一并提取，如果不需要图片文本需要额外过滤`<img>`标签。

## 7. 拓展小技巧
如果想要额外移除图片、导航栏，可以修改过滤代码：
```python
# 同时删除脚本、样式、导航标签
for element in soup(["script", "style", "nav"]):
    element.decompose()
```

# _normalize_excel_header + _detect_excel_headers 完整讲解
## 1. 整体作用
这两个函数配套使用，**自动识别Excel表头别名**，解决用户表格表头名称不统一的问题。
举例：
标准字段要求 `name`，但是用户Excel表头可能写：`名称`、`名字`、`Name`、`Name `、`name_`。
经过归一化处理后，程序可以自动识别，映射到统一字段。

依赖常量（代码里存在）：`_EXCEL_HEADER_ALIASES`
示例结构参考：
```python
_EXCEL_HEADER_ALIASES = {
    "name": ["名称", "名字", "Name", "实体名称"],
    "definition": ["定义", "描述", "说明"],
    "propertyName": ["属性名", "property名称"]
}
```

## 2. 源码
```python
def _normalize_excel_header(text: str | None) -> str:
    if text is None:
        return ""
    return str(text).strip().replace(" ", "").replace("_", "").lower()


def _detect_excel_headers(first_row: tuple) -> dict[str, int]:
    """根据第一行标题文本，把列索引映射到标准字段。"""
    mapping: dict[str, int] = {}
    normalized = [_normalize_excel_header(cell) for cell in first_row]
    for field_name, aliases in _EXCEL_HEADER_ALIASES.items():
        for alias in aliases:
            key = _normalize_excel_header(alias)
            if key in normalized:
                idx = normalized.index(key)
                if field_name not in mapping:
                    mapping[field_name] = idx
                break
    return mapping
```

## 3. 逐行解析第一个函数：_normalize_excel_header
```python
def _normalize_excel_header(text: str | None) -> str:
```
接收单元格内容，可以为空；返回清洗后的小写标准字符串。
```python
if text is None:
    return ""
```
单元格为空（None），直接返回空字符串，防止报错。
```python
return str(text).strip().replace(" ", "").replace("_", "").lower()
```
归一化流水线，依次执行：
1. `str(text)`：统一转为字符串
2. `.strip()`：去除单元格首尾空格
3. `.replace(" ", "")`：删除**所有中间空格**
4. `.replace("_", "")`：删除下划线
5. `.lower()`：全部转为小写

### 直观例子
原始表头：`Name _ `
处理流程：
`Name _ ` → `Name_` → `Name` → `name`

原始表头：`实体 名称`
处理后：`实体名称`

> 目的：消除格式差异，只保留文字核心用于匹配。

## 4. 逐行解析第二个函数：_detect_excel_headers
```python
def _detect_excel_headers(first_row: tuple) -> dict[str, int]:
```
入参：Excel第一行所有单元格（表头行）
返回：`{标准字段名: 列下标}`
示例返回结果：`{"name":0, "definition":2}`
含义：name字段在第0列，definition字段在第2列。

```python
mapping: dict[str, int] = {}
```
最终存储【标准字段 → 列索引】的字典。

```python
normalized = [_normalize_excel_header(cell) for cell in first_row]
```
把表头每一格全部执行归一化，生成清洗后的表头列表。
假设原始表头行：`["Name", "备注", "定义"]`
normalized = `["name", "备注", "定义"]`

```python
for field_name, aliases in _EXCEL_HEADER_ALIASES.items():
```
循环遍历系统内置标准字段和它所有允许的别名。
- field_name：内部标准字段，如 `name`
- aliases：所有能等价代表该字段的表头文本列表

```python
for alias in aliases:
    key = _normalize_excel_header(alias)
```
把别名也做同样归一化，保证匹配规则一致。

```python
if key in normalized:
    idx = normalized.index(key)
```
如果归一化后的别名，出现在表头列表中
找到这一列所在的下标。

```python
if field_name not in mapping:
    mapping[field_name] = idx
break
```
- 同一个标准字段只记录第一次匹配到的列
- break：匹配成功后，不再尝试该字段剩下的别名，提升效率

```python
return mapping
```
返回表头映射字典，给上层Excel解析代码使用。

## 5. 完整运行示例
假设常量：
```python
_EXCEL_HEADER_ALIASES = {
    "name": ["名称", "Name"],
    "definition": ["定义", "描述"]
}
```
Excel表头第一行：`["Name", "属性名", "定义"]`

1. normalized表头：`["name","属性名","定义"]`
2. 遍历标准字段
- 字段`name`，别名依次尝试`名称`(不匹配) → `Name`(归一化为name，匹配成功)，记录`"name":0`
- 字段`definition`，别名尝试`定义`，匹配成功，记录`"definition":2`

最终mapping：
```python
{"name":0, "definition":2}
```

## 6. 核心业务价值
1. **降低Excel导入门槛**
用户不需要严格强制固定表头文字，多种写法都能识别；
2. 统一匹配规则
表头清洗逻辑集中在`_normalize_excel_header`，后续修改规则只改一处；
3. 大小写、空格、下划线全部兼容，容错强。

## 7. 现有代码存在的小局限（初学者可以留意）
1. `normalized.index(key)` 只会返回**第一个匹配列**；如果表格出现重复表头，后面的列会被忽略；
2. 使用完全匹配，不支持模糊包含；比如别名`名称`无法匹配`实体名称`；
3. 一旦归一化规则修改，所有表头识别逻辑同步变化。

## 8. 和上层代码关联回顾
在上一份 `_parse_excel_workbook` 中：
```python
headers = _detect_excel_headers(rows[0])
if "name" not in headers and "definition" not in headers:
    continue
```
这里拿到的headers就是本函数输出的映射字典，用来判断表格是否有效、读取对应列的数据。

# `_parse_excel_workbook` 函数完整讲解
## 1. 整体功能
使用 `openpyxl` 读取本地 `.xlsx` Excel 文件，遍历文件内所有工作表；
识别表头、区分**主数据行**与**附属属性行**，把表格数据解析成 `_ExcelEntity` 对象列表。
业务设计：**一行主体 + 多行附属属性**，属性归属上方最近的主体条目。

适用场景：本体概念、实例、属性在Excel批量录入，程序导入解析。
> 限制：仅支持 xlsx，不支持老式 xls；需要安装依赖
```bash
pip install openpyxl
```

## 2. 源码
```python
def _parse_excel_workbook(path: Path) -> list[_ExcelEntity]:
    import openpyxl

    wb = openpyxl.load_workbook(path, data_only=True)
    entities: list[_ExcelEntity] = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue

        headers = _detect_excel_headers(rows[0])
        if "name" not in headers and "definition" not in headers:
            continue

        current: _ExcelEntity | None = None
        for row in rows[1:]:
            texts = _excel_row_texts(row)
            if not any(texts):
                continue

            if _is_excel_main_row(texts, headers):
                current = _read_excel_entity(texts, headers, sheet_name)
                prop = _read_excel_property(texts, headers)
                if prop:
                    current.properties.append(prop)
                entities.append(current)
            elif current is not None:
                prop = _read_excel_property(texts, headers)
                if prop:
                    current.properties.append(prop)

    return entities
```

## 3. 逐行拆解
```python
import openpyxl
```
函数内部懒导入，只有解析Excel时才加载包，减少程序启动开销。

```python
wb = openpyxl.load_workbook(path, data_only=True)
```
- `wb`：整个Excel工作簿（一个文件）
- `data_only=True`：**读取单元格计算结果，而不是公式**
> 举例：单元格写 `=A1+B1`，开启后拿到数值；关闭拿到公式字符串。

```python
entities: list[_ExcelEntity] = []
```
存放最终解析完成的所有实体对象。

```python
for sheet_name in wb.sheetnames:
```
循环遍历Excel里每一个工作表（Sheet1、Sheet2……）

```python
ws = wb[sheet_name]
rows = list(ws.iter_rows(values_only=True))
```
- `ws` 代表单个工作表
- `iter_rows(values_only=True)`：只获取单元格值，不获取格式、样式；
- 所有行转为列表，方便随机访问。

```python
if not rows:
    continue
```
工作表完全空白，直接跳过。

```python
headers = _detect_excel_headers(rows[0])
```
`rows[0]` 第一行，调用函数识别表头，输出字典：`列名 -> 列下标`。

```python
if "name" not in headers and "definition" not in headers:
    continue
```
校验：表头缺少关键字段，判定不是目标数据表，跳过当前sheet。

```python
current: _ExcelEntity | None = None
```
缓存**当前正在处理的实体**，附属属性行挂载到这个对象上。

```python
for row in rows[1:]:
```
从第2行开始循环（跳过表头）。

```python
texts = _excel_row_texts(row)
if not any(texts):
    continue
```
把一行单元格统一清洗成文本；整行全部为空则跳过空行。

```python
if _is_excel_main_row(texts, headers):
```
关键判断：识别**主体行（新实体开始）**
规则约定：该行存在实体名称name，代表一条全新本体/实例。

```python
current = _read_excel_entity(texts, headers, sheet_name)
prop = _read_excel_property(texts, headers)
if prop:
    current.properties.append(prop)
entities.append(current)
```
1. 创建新的 `_ExcelEntity` 实体
2. 主体行自身也可能附带属性，读取并加入实体属性列表
3. 存入总列表
4. 更新 `current`，后续附属行归属这个实体

```python
elif current is not None:
    prop = _read_excel_property(texts, headers)
    if prop:
        current.properties.append(prop)
```
不是主体行 → 判定为**附属属性行**
把属性追加到最近一个 `current` 实体上。
> 如果前面还没有主体，这一行数据直接丢弃。

## 4. 业务数据模型示意（表格结构）
| name   | definition | propertyName | propertyValue |
|--------|------------|--------------|---------------|
| 发动机 | 动力装置   | 重量         | 200kg         |
|        |            | 推力         | 5000N         |
| 阀门   | 控制组件   | 材质         | 钛合金        |

执行逻辑：
1. 发动机 → 主体行，创建实体，添加【重量】属性
2. 空name行 → 附属行，追加【推力】到发动机
3. 阀门 → 新主体行，新建实体，添加【材质】

## 5. 完整执行流程
1. 打开Excel文件，读取单元格数值（不读取公式）
2. 逐个工作表处理
3. 读取第一行，识别表头；无关键字段直接跳过sheet
4. 逐行遍历表格内容
    - 空行：跳过
    - 主体行：新建实体，缓存到current，加入总列表
    - 属性附属行：挂载到current实体的properties数组
5. 全部sheet处理完毕，返回所有实体列表

## 6. 重点设计特点（初学者重点理解）
1. **层级结构**
实体 + 多行属性，不需要每个属性重复填写name，简化Excel录入；
2. 跨Sheet支持
一个Excel多个sheet可以存放多组本体数据；
3. 容错
空白工作表、无关数据表自动跳过；
4. `data_only=True`
工程表格大量存在公式，这个参数避免拿到计算公式字符串。

## 7. 潜在局限
1. 只能从上往下解析：属性**不能向上归属**，附属行必须紧跟主体下方；
2. 如果中间主体行被删除，下方所有属性行会丢失；
3. 只支持 `.xlsx`，不兼容旧版 `.xls`；
4. 依赖配套辅助函数：
`_detect_excel_headers` / `_excel_row_texts` / `_is_excel_main_row` / `_read_excel_entity` / `_read_excel_property`

## 8. 拓展思考
如果后续需要支持：一个属性拥有多个值、属性附带单位、注释，只需扩充 `properties` 对象字段即可。

# `_entities_to_text` 函数完整讲解
## 1. 整体功能
接收Excel解析出来的实体列表 `list[_ExcelEntity]`，**把结构化实体数据转换成可读Markdown文本**。
作用：将表格里的本体实体、属性整理成文档文本，可直接用于：LLM输入、预览展示、导出文本报告。

核心逻辑：
1. 先按照 `工作表sheet + 分类category` 分组；
2. 按分组渲染Markdown二级标题；
3. 逐个渲染实体名称、英文、编号、定义、注释、属性列表；
4. 属性自动拼接单位；
5. 最终拼接为一整段字符串返回。

## 2. 源码
```python
def _entities_to_text(entities: list[_ExcelEntity]) -> str:
    lines: list[str] = []
    if not entities:
        return ""

    grouped: dict[tuple[str, str], list[_ExcelEntity]] = {}
    for e in entities:
        key = (e.sheet, e.category)
        grouped.setdefault(key, []).append(e)

    for (sheet, category), items in grouped.items():
        lines.append(f"## Sheet: {sheet} | 分类: {category or '未分类'}")
        if category:
            lines.append("（该分类下的对象可作为一个本体类型）")
        for e in items:
            title = e.name or e.english_name or f"术语{e.code}"
            lines.append(f"\n### {title}")
            if e.english_name:
                lines.append(f"英文：{e.english_name}")
            if e.code:
                lines.append(f"编号：{e.code}")
            if e.definition:
                lines.append(f"定义：{e.definition}")
            if e.note:
                lines.append(f"注释：{e.note}")
            if e.properties:
                lines.append("典型属性：")
                for p in e.properties:
                    val = f"{p['value']} {p['unit']}".strip() if p["unit"] else p["value"]
                    lines.append(f"- {p['name']}：{val}")
        lines.append("")

    return "\n".join(lines)
```

## 3. 逐行拆解
```python
lines: list[str] = []
```
收集所有文本片段，最后统一换行拼接（字符串拼接最优写法，避免频繁`+=`）。

```python
if not entities:
    return ""
```
没有实体数据，直接返回空字符串，提前退出。

```python
grouped: dict[tuple[str, str], list[_ExcelEntity]] = {}
for e in entities:
    key = (e.sheet, e.category)
    grouped.setdefault(key, []).append(e)
```
### 分组逻辑重点
- `key = (e.sheet, e.category)`
  使用**元组**作为字典key：`(工作表名称, 分类名称)`
- `setdefault(key, [])`
  如果key不存在，新建空列表；然后把实体追加进去。
> 效果：同一个Sheet、同一个分类下的实体聚合在一起。

示例分组key：
`("本体概念", "发动机组件")`

```python
for (sheet, category), items in grouped.items():
```
循环每一组数据
```python
lines.append(f"## Sheet: {sheet} | 分类: {category or '未分类'}")
```
Markdown二级标题；`category or "未分类"`：分类为空时展示默认文字。

```python
if category:
    lines.append("（该分类下的对象可作为一个本体类型）")
```
业务注释，适配你的本体建模场景。

```python
for e in items:
    title = e.name or e.english_name or f"术语{e.code}"
```
**标题优先级规则**
优先使用 `name`；
name为空 → 使用 `english_name`；
都没有 → 使用编号兜底 `术语xxx`。
Python `or` 短路特性。

```python
lines.append(f"\n### {title}")
```
Markdown三级标题，单个实体。

下面一批 `if` 判断：**有数据才输出，避免出现空行、空标签**
```python
if e.english_name:
    lines.append(f"英文：{e.english_name}")
if e.code:
    lines.append(f"编号：{e.code}")
if e.definition:
    lines.append(f"定义：{e.definition}")
if e.note:
    lines.append(f"注释：{e.note}")
```

```python
if e.properties:
    lines.append("典型属性：")
    for p in e.properties:
        val = f"{p['value']} {p['unit']}".strip() if p["unit"] else p["value"]
        lines.append(f"- {p['name']}：{val}")
```
遍历实体属性：
- 如果属性带有单位 `unit`，自动拼接：`200 kg`
- `.strip()` 防止单位为空时多出空格
最终渲染成无序列表 `-`

```python
lines.append("")
```
每组末尾增加空行，分隔内容，排版更好看。

```python
return "\n".join(lines)
```
把列表中所有文本用换行符连接，返回完整文本。

## 4. 输出文本样例（直观感受）
```markdown
## Sheet: 本体 | 分类: 发动机组件
（该分类下的对象可作为一个本体类型）

### 液体火箭发动机
英文：LiquidEngine
编号：ENG-001
定义：以液体推进剂为燃料的动力装置
注释：用于一级助推器
典型属性：
- 推力：5000 kN
- 自重：2300 kg

### 涡轮泵
英文：Turbopump
编号：PUMP-02
定义：输送推进剂的核心组件
典型属性：
- 转速：22000 rpm

```

## 5. 上下游关联
上游：`_parse_excel_workbook` 读取Excel，输出 `list[_ExcelEntity]`
下游：得到markdown文本后，可以：
1. 送入大模型进行本体抽取；
2. 界面预览展示；
3. 保存为`.md`文件。

## 6. 优点
1. 分组展示，结构清晰；
2. 空字段自动隐藏，不会出现「定义：（空白）」；
3. 属性单位自动拼接，适配你之前关心的单位业务；
4. 输出标准Markdown，通用易阅读。

## 7. 可以优化的点（可选）
1. 增加换行控制，避免大量连续空行；
2. 可以增加过滤：过滤定义为空的实体；
3. 支持限制文本长度，防止输入LLM时文本超长；
4. 分组key如果不需要同时区分sheet+category，可以灵活调整。

## 8. 初学者重点理解
`key = (e.sheet, e.category)`
字典不能用列表`[]`作为key（列表不可哈希），**元组tuple可以**，非常常用的多条件分组写法。

`a or b or c`
依次判断，如果第一个不为空直接取用，向后兜底，是Python非常简洁的取值写法。

如果你需要，我可以把Excel整套解析函数（读取、表头识别、实体解析、文本导出）汇总成一份完整笔记。