---
created: 2026-08-04T10:42
updated: 2026-08-04T14:01
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
