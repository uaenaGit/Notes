---
created: 2026-07-31T11:20
updated: 2026-08-06T14:35
---
# `async def chat` 函数详解

## 1. 函数签名

```python
async def chat(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.3,
    max_tokens: int = 8192,
) -> str:
```

逐项拆解：

- **`async def`**：异步函数。调用它时不会立即执行，而是返回一个"协程对象"（coroutine）。必须用 `await` 才能拿到结果。之所以用异步，是因为这个函数内部要发网络请求，等待期间可以让出 CPU 给其他任务。

- **`messages: list[dict[str, str]]`**：参数是一个列表，列表里每个元素是一个字典，字典的键和值都是字符串。这是 LLM API 的标准对话格式，比如：
  ```python
  [
      {"role": "system", "content": "你是一名本体工程师"},
      {"role": "user", "content": "请从以下文本中抽取本体..."}
  ]
  ```
  > **`list[dict[str, str]]` 是 Python 3.9+ 的泛型写法**，读作"一个列表，里面的元素是字典，字典的键是 `str`，值也是 `str`"。旧式写法 `List[Dict[str, str]]` 需要从 `typing` 导入，现在已不推荐。

- **`*`**：孤立的星号。强制星号后面的参数**只能用关键字方式传递**。比如调用时只能写 `chat(messages, temperature=0.3)`，不能写 `chat(messages, 0.3)`——后者会报错。这是 Python 提高代码可读性的手段：参数名必须显式写出，不会搞混顺序。

- **`temperature: float = 0.3`**：浮点数参数，默认值 0.3。控制 LLM 输出的随机性，0 到 1 之间，越低越确定。

- **`max_tokens: int = 8192`**：整数参数，默认值 8192。限制 LLM 输出的最大 token 数。

- **`-> str`**：返回值类型注解，说明这个函数返回一个字符串。

---

## 2. 模块级常量（函数外部，文件顶部）

理解函数行为前，先要知道这些"全局配置"：

```python
_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
```

`os.environ` 是 Python 读取**环境变量**的方式。环境变量是操作系统层面的一种键值对配置，不写在代码里，避免敏感信息泄露。`.get("MINIMAX_API_KEY", "")` 的意思是：尝试读取名为 `MINIMAX_API_KEY` 的环境变量，如果没设置，就用空字符串 `""` 作为默认值。

```python
_BASE_URL = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
```

API 的基础地址。同理，没设置环境变量就用默认值 `https://api.minimax.chat/v1`。最终请求的完整 URL 是 `{_BASE_URL}/chat/completions`，即 `https://api.minimax.chat/v1/chat/completions`。

```python
_MODEL = _MODEL_ENV if _MODEL_ENV in _MINIMAX_VALID_MODELS else "MiniMax-M2.7"
```

三元表达式：如果环境变量 `MINIMAX_MODEL` 的值在允许的模型列表中，就用它；否则回退到默认的 `MiniMax-M2.7`。这是一个安全阀，防止配置错误。

```python
_TIMEOUT = httpx.Timeout(600.0, connect=30.0)
```

`httpx` 是 Python 的 HTTP 客户端库（类似 `requests`，但支持异步）。`Timeout(600.0, connect=30.0)` 的意思是：连接超时 30 秒，整体请求超时 600 秒（10 分钟）。LLM 生成大段文本可能需要很长时间，所以整体超时设得很宽松。

---

## 3. 函数体逐行解析

### 3.1 统计输入长度

```python
prompt_tokens = sum(len(m.get("content", "")) for m in messages)
```

这是一个**生成器表达式**，拆开看：

- `for m in messages`：遍历消息列表中的每条消息
- `m.get("content", "")`：字典的 `.get()` 方法。尝试取键 `"content"` 的值，如果这个键不存在，返回默认值 `""`（空字符串）。比直接写 `m["content"]` 安全，不会因为缺键而崩溃。
- `len(...)`：取字符串长度（字符数）
- `sum(...)`：把所有的长度加起来

结果就是所有消息内容的总字符数。注意这里只是近似——实际 token 数和字符数不完全对应，但粗略估算够用了。

### 3.2 开始计时

```python
t0 = time.perf_counter()
```

`time.perf_counter()` 返回一个高精度的时间戳（单位秒），用于测量代码执行耗时。`t0` 是"起点时间"，后面用 `time.perf_counter() - t0` 就能算出经过了多少秒。

```python
ttfb = None
```

TTFB = **Time To First Byte**（首字节时间）。初始化为 `None`，后面会被赋值为实际的首字节到达时间。`None` 是 Python 的"空值"，表示"还没有值"。

### 3.3 发起 HTTP 流式请求

```python
async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
```

这是最核心的一行，需要逐层理解：

- **`httpx.AsyncClient`**：`httpx` 库提供的异步 HTTP 客户端。不同于同步的 `requests.get()`，`AsyncClient` 不会阻塞当前线程。它需要配合 `async with` 使用。
- **`async with`**：异步上下文管理器。`with` 语句（同步版本）的作用是"进入时做准备工作，退出时自动清理资源"。比如 `with open("file.txt") as f:` 会在退出时自动关闭文件。`async with` 是异步版本，用于需要 `await` 的清理操作。这里 `AsyncClient` 在退出时会自动关闭 HTTP 连接。
- **`timeout=_TIMEOUT`**：把前面定义的超时配置传给客户端。
- **`as client`**：把创建的 `AsyncClient` 对象赋值给变量 `client`，后续用 `client` 来发请求。

```python
    async with client.stream(
        "POST",
        f"{_BASE_URL}/chat/completions",
        headers={...},
        json={...},
    ) as resp:
```

- **`client.stream()`**：发起一个**流式** HTTP 请求。普通的 `client.post()` 会等整个响应体下载完才返回，`stream()` 则是一边下载一边可以处理数据。对于 LLM 调用，虽然这个 `chat` 函数是"非流式"（返回完整文本），但内部用流式请求可以更早拿到首字节，并记录 TTFB。
- **`"POST"`**：HTTP 方法。LLM API 一般用 POST，因为请求体（body）里要放对话内容。
- **`f"{_BASE_URL}/chat/completions"`**：f-string（格式化字符串）。`{_BASE_URL}` 会被替换成实际值，最终变成 `"https://api.minimax.chat/v1/chat/completions"`。
- **`headers={...}`**：HTTP 请求头。告诉服务器"我是谁"（Authorization）和"我发的是什么格式"（Content-Type）。
  - `"Authorization": f"Bearer {_API_KEY}"`：Bearer 认证方式，把 API 密钥放在请求头里，服务器用它验证身份。
  - `"Content-Type": "application/json"`：告诉服务器，请求体是 JSON 格式。
- **`json={...}`**：请求体，直接传 Python 字典，`httpx` 会自动把它序列化成 JSON 字符串。
  - `"model"`：用哪个模型
  - `"messages"`：对话内容
  - `"temperature"`：随机性
  - `"max_tokens"`：最大输出 token 数
- **`as resp`**：响应对象，包含服务器返回的状态码、响应头、响应体等。

### 3.4 检查响应状态

```python
        resp.raise_for_status()
```

`httpx` 响应对象的方法。如果 HTTP 状态码是 4xx（客户端错误）或 5xx（服务器错误），就抛出异常。比如 API 密钥无效会返回 401，这个调用会立即抛出一个 `HTTPStatusError`，停止后续执行。

### 3.5 记录首字节时间

```python
        ttfb = time.perf_counter() - t0
```

`raise_for_status()` 通过后，说明服务器已经开始响应了。此时计算从请求发出到收到响应头的时间差，这就是 TTFB。这是衡量 LLM 服务响应速度的关键指标。

### 3.6 读取全部响应字节

```python
        content_bytes = b"".join([c async for c in resp.aiter_bytes()])
```

这一行比较密集，拆开看：

- **`resp.aiter_bytes()`**：异步迭代器，每次 `await` 时返回一小块字节数据（chunk）。LLM 的输出是逐步生成的，服务端一边生成一边发送，`aiter_bytes()` 就是逐块读取这些数据。
- **`c async for c in resp.aiter_bytes()`**：异步推导式（async comprehension）。`async for` 是 `for` 的异步版本，用于遍历异步迭代器。这里把每个 chunk 收集到一个列表里。
- **`b"".join([...])`**：`b""` 是**字节串（bytes）**的前缀，表示空字节串。`.join()` 用空字节串把列表中的所有 chunk 拼接成一个完整的字节串。`content_bytes` 就是完整的响应体原始字节。
- 为什么用字节串（bytes）而不是字符串（str）？因为 MiniMax 的响应编码可能不标准（不一定是 UTF-8），先拿到原始字节，后面再手动解码，更可控。

### 3.7 解码字节串

```python
    text = robust_decode_bytes(content_bytes)
```

`robust_decode_bytes` 是同一个文件里定义的函数（未在截取范围内），它尝试用多种编码（UTF-8、GB18030 等）解码字节串，确保中文不乱码。相对于直接调用 `.decode("utf-8")`，这个方法更健壮。

### 3.8 解析 JSON 响应

```python
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            f"MiniMax 返回非 JSON（编码已尝试 utf-8/gb18030）: {text[:200]!r}",
            exc.doc,
            exc.pos,
        ) from exc
```

- **`try: ... except ... `**：Python 的异常处理结构。`try` 块里的代码如果出错，会跳到 `except` 块执行，而不是让程序崩溃。
- **`json.loads(text)`**：把 JSON 字符串解析成 Python 字典。`loads` 是 "load string" 的缩写。
- **`except json.JSONDecodeError as exc`**：捕获 `JSONDecodeError` 这个特定异常，赋值给变量 `exc`。如果解析失败（比如 LLM 返回的不是合法 JSON），就执行 `except` 块。
- **`raise json.JSONDecodeError(...) from exc`**：重新抛出一个异常。`from exc` 保留了原始异常链，调试时能看到完整的错误来源。新的错误消息里包含了原始文本的前 200 个字符（`text[:200]`），方便排查问题。
  - `!r` 是字符串格式化中的"repr"模式，会输出带引号的字符串，比如 `"hello"` 而不是 `hello`，方便看出字符串里有没有特殊字符。

### 3.9 提取响应内容

```python
    content = data["choices"][0]["message"]["content"]
```

LLM API 的标准响应格式是一个嵌套的字典，结构大致是：

```json
{
    "choices": [
        {
            "message": {
                "content": "这是 LLM 生成的文本..."
            }
        }
    ]
}
```

`data["choices"][0]` 取第一个（通常也是唯一一个）选择，`["message"]["content"]` 取其中的文本内容。

```python
    if not isinstance(content, str):
        content = str(content)
```

`isinstance(content, str)` 检查 `content` 是不是字符串类型。如果 API 返回的不是字符串（极端情况），用 `str()` 强制转换成字符串。

### 3.10 日志与清理

```python
    logger.info(
        "[llm.chat] model=%s prompt_chars=%d response_chars=%d ttfb=%.2fs total=%.2fs",
        _MODEL, prompt_tokens, len(content), ttfb or 0.0, total,
    )
```

`logger.info()` 记录一条日志，包含模型名、输入字符数、输出字符数、首字节时间、总耗时。`ttfb or 0.0` 是 Python 的短路运算：如果 `ttfb` 是 `None`（假值），就用 `0.0` 替代。

```python
    return clean_think_tags(content)
```

`clean_think_tags()` 在文件同位置定义，用正则表达式移除 MiniMax M2.7 模型可能输出的 `...` 标签。这些标签是模型的"思考过程"，不需要返回给调用者。

---

## 4. 完整调用链总结

```
chat(messages, temperature=0.3, max_tokens=8192)
 │
 ├─ 统计输入字符数（仅用于日志）
 ├─ 记录开始时间 t0
 │
 ├─ async with httpx.AsyncClient 创建 HTTP 客户端
 │   └─ client.stream("POST", url, headers, json) 发起流式 POST 请求
 │       ├─ resp.raise_for_status() 检查 HTTP 状态码
 │       ├─ 记录 TTFB（首字节到达时间）
 │       └─ 逐块读取响应字节 → 拼接成 content_bytes
 │
 ├─ robust_decode_bytes(content_bytes) 解码（尝试多种编码）
 ├─ json.loads(text) 解析 JSON
 ├─ 提取 data["choices"][0]["message"]["content"]
 ├─ 记录日志（耗时、字符数）
 └─ clean_think_tags(content) → 返回清理后的文本
```

---

## 5. 一个关键概念：异步 ≠ 多线程

Python 初学者容易混淆异步和多线程，这里澄清一下：

- **多线程**：多个任务**同时**在不同线程上执行（真正的并行）。适合 CPU 密集型任务。
- **异步（async/await）**：单线程内任务**交替**执行。当任务 A 在等网络 I/O 时，CPU 切换到任务 B。适合 I/O 密集型任务（网络请求、文件读写）。

`chat()` 函数用异步，是因为它的大部分时间花在等待 MiniMax 服务器生成文本——这段时间 CPU 是空闲的。异步让 CPU 在等待期间去处理其他请求（比如另一个用户的 `build_ontology` 调用），而不是傻等。

`await` 就是"暂停点"：程序跑到 `await` 时，把控制权交还给**事件循环**（event loop），事件循环去找其他可以执行的任务。等 `await` 后面的操作完成，事件循环再回到这个函数继续往下跑。

# extract_json 代码完整解析
```python
def extract_json(text: str) -> dict | list | None:
    """从 LLM 输出中提取 JSON 对象或数组。"""
    cleaned = clean_think_tags(text)
    # 去除 markdown code fence
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    # 找第一个 { 或 [
    for i, ch in enumerate(cleaned):
        if ch in "{[":
            break
    else:
        return None
    start = i
    open_ch = cleaned[start]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    in_str = False
    escaped = False
    for j in range(start, len(cleaned)):
        c = cleaned[j]
        if in_str:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(cleaned[start : j + 1])
                except json.JSONDecodeError:
                    return None
    return None
```
## 整体功能
大模型输出经常混有说明文字、markdown代码块、`思考标签`，这个函数**不直接整个文本json.loads**，手动扫描字符串，把里面嵌套完整的`{...}`对象或者`[...]`数组抠出来，解析返回；解析失败返回`None`。

> 为什么不直接正则截取？
JSON支持嵌套`{ { } }`，正则很难处理嵌套括号；所以手写状态机，维护括号深度。

## 逐段拆解

### ① 前期清洗
```python
cleaned = clean_think_tags(text)
# 去除 markdown code fence
cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
```
1. `clean_think_tags(text)`：把大模型输出的`...`整块删掉（之前学过的函数）
2. 去掉markdown的json代码块标记：
```
```json
{"a":1}
```

把开头的`` ```json `` 和结尾 `` ``` `` 删除，只保留json本体。

### ② 找到JSON真正开始的位置
```python
for i, ch in enumerate(cleaned):
    if ch in "{[":
        break
else:
    return None
start = i
```
- `enumerate`：同时拿到下标`i`和字符`ch`
- 向后遍历，找到**第一个 `{` 或者 `[`**，这就是json的起点
- `for ... else`语法：for循环正常遍历完、没有触发break，就执行else。
> 如果整篇文本找不到`{`也找不到`[` → 没有json，直接return None。

示例输入：`好的，结果如下：{"name":"发动机"}`
循环跳过前面汉字，i定位到`{`的下标。

```python
open_ch = cleaned[start]
close_ch = "}" if open_ch == "{" else "]"
```
- 如果起点是`{`，匹配闭合字符`}`
- 如果起点是`[`，匹配闭合字符`]`

### ③ 状态机遍历，寻找匹配的结束括号（核心）
变量说明：

|变量|含义|
|---|---|
|`depth`|括号嵌套深度，遇到开括号+1，闭括号-1；depth=0代表完整json结束|
|`in_str`|是否现在处在JSON双引号字符串内部，**字符串里面的大括号不算真正括号！**|
|`escaped`|是否遇到转义符`\`，处理`\"`转义双引号|

```python
for j in range(start, len(cleaned)):
    c = cleaned[j]
    # ========== 如果当前在字符串内部 ==========
    if in_str:
        if escaped:
            escaped = False
        elif c == "\\":
            escaped = True
        elif c == '"':
            in_str = False
        continue
    # ========== 不在字符串里面 ==========
    if c == '"':
        in_str = True
    elif c == open_ch:
        depth += 1
    elif c == close_ch:
        depth -= 1
        if depth == 0:
            # 找到了完整闭合的json片段
            try:
                return json.loads(cleaned[start : j + 1])
            except json.JSONDecodeError:
                return None
# 循环跑完没找到匹配闭合括号
return None
```

#### 状态逻辑通俗讲
1. **一旦进入双引号 `"` 内部：`in_str=True`**
> JSON字符串内部`{"text":"这是{符号"}`，这里面的`{`只是普通文字，**不能算括号嵌套**，直接跳过处理。

2. 处理转义`\"`：字符串里面 `\"` 是引号的转义，**不是字符串结束标记**，靠`escaped`标记。
3. 不在字符串内的时候：
    - 碰到开符号`{`/`[` → `depth +=1`，嵌套加深一层
    - 碰到闭符号`}`/`]` → `depth -=1`
    - ✅**当depth==0：代表找到了和最开头配对的结束符号，整个JSON截取完成**

截取片段：`cleaned[start : j + 1]`，切片，从起始位置到当前闭合字符。
然后`json.loads()`解析；如果json格式依旧错误，捕获异常返回`None`。

> 如果文本遍历全部结束，始终没有depth回到0，代表json没有闭合，返回None。

## 举实例演示
输入文本：
```
模型输出：
下面是结果
{
  "id":1,
  "info":"里面有一个{符号"
}
额外废话
```
1. 清洗完成，去掉think标签、去掉```
2. 循环找到第一个`{`，start定位
3. 开始遍历：
- 遇到`"`，`in_str=True`；字符串内部遇到`{`，因为`in_str=True`直接忽略，不修改depth
- 遇到闭合`"`，退出字符串
- 继续往后，遇到最后的`}`，`depth`减到0
- 截取`{ ... }`片段，调用json.loads返回字典。

## 边界场景处理
1. ✅JSON字符串内部包含`{ } [ ]`符号，不会误判结束
2. ✅支持嵌套JSON `{"a":{"b":1}}`，depth深度计数正确
3. ✅支持转义引号 `{"text":"hello\"world"}`
4. ✅支持数组`[1,2,{"x":3}]`
5. ❌如果JSON没有闭合（LLM输出半截），函数返回None
6. ❌截取出来片段语法依然错误，捕获JSONDecodeError返回None

## 初学者容易迷惑的两个语法点
1. `for ... else`
```python
for i in xxx:
    if ...:
        break
else:
    # 只有循环没有break才走到这里
```
不是if‑else，是for循环自带else。

2. `cleaned[start : j + 1]`
Python切片`[a:b]`，**b位置不包含**，所以结束下标j要写`j+1`，把`}`/`]`包含进来。

## 潜在小局限
1. 只会提取**第一个出现**的JSON对象/数组；如果文本有多段json，后面全部忽略。
2. 只识别以`{`或者`[`开头的json；纯字符串、数字json不提取。

## 调用示例
```python
text = """
思考内容
输出结果：
```json
{"name":"发动机","pressure":"10MPa"}
完事。
```

```python
res = extract_json(text)
print(res) # {'name':'发动机','pressure':'10MPa'}
```

## 整体流程总结
1. 清洗：移除think标签、markdown代码块标记
2. 扫描，找到第一个`{`或`[`，确定json起点；找不到返回None
3. 状态机遍历后面全部字符：区分是否在字符串内，维护括号嵌套depth
4. depth归零，代表完整json结束；截取片段，尝试json解析返回结果
5. 解析失败 / 找不到闭合括号 → 返回None。

# `_ensure_colors` 函数完整讲解
## 一、整体功能
给本体类型（`ontoType`）自动填充颜色字段：
如果某个类型没有设置 `color`，就从预设的颜色池里按顺序分配一个颜色，保证每一类本体都有可视化颜色（前端图谱/图表渲染用）。

## 二、逐行拆解代码
```python
def _ensure_colors(data: dict) -> dict:
    """确保每个 ontoType 都有 color。"""
    # 1. 遍历所有本体类型，带上下标i
    for i, t in enumerate(data.get("ontoTypes", [])):
        # 2. 判断当前类型是否缺失color（空/None都算缺失）
        if not t.get("color"):
            # 3. 从颜色池循环取色，赋值给当前类型color字段
            t["color"] = _COLOR_POOL[i % len(_COLOR_POOL)]
    # 4. 返回修改后的data字典
    return data
```

### 1. `data.get("ontoTypes", [])`
- `data` 是本体顶层字典，`"ontoTypes"` 存放所有类型定义列表
- `.get(key, 默认值)`：如果字典里没有 `ontoTypes` 键，不会报错，直接返回空列表 `[]`，循环不会执行

### 2. `enumerate(data.get("ontoTypes", []))`
`enumerate` 同时拿到两件东西：
- `i`：当前类型在列表中的**下标序号**（0、1、2、3……）
- `t`：单个本体类型字典，结构类似 `{"name":"发动机", "color":"#ff0000"}`

### 3. `if not t.get("color")`
- `t.get("color")` 安全读取color字段，不存在返回`None`
- `not` 判断：只要color是 `None`、空字符串 `""`，都会进入自动分配颜色逻辑
- 如果已经手动填了颜色，直接跳过，不覆盖用户自定义颜色

### 4. 核心取色逻辑 `_COLOR_POOL[i % len(_COLOR_POOL)]`
1. `_COLOR_POOL`：全局预设的颜色列表，示例：
```python
_COLOR_POOL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
```
2. `len(_COLOR_POOL)`：颜色池总数量（上面例子是4个颜色）
3. `%` 取模运算，实现**循环复用颜色**：
    - i=0 → 0%4=0 → 第1个颜色
    - i=1 → 1%4=1 → 第2个颜色
    - i=4 → 4%4=0 → 重新取第1个颜色
    哪怕本体类型数量远超颜色池，也不会下标越界，无限循环轮询配色

### 5. `t["color"] = xxx`
`t` 是字典引用，这里**原地修改原始data里的类型字典**；最后`return data`把修改完的字典返回。

## 三、完整运行示例
### 原始输入 data
```python
_COLOR_POOL = ["red", "blue", "green"]
data = {
    "ontoTypes": [
        {"name": "发动机"},          # 无color，自动分配
        {"name": "阀门", "color": "yellow"}, # 已有color，不改动
        {"name": "管路"},            # 无color，自动分配
        {"name": "传感器"}           # 无color，自动分配
    ]
}
```
### 执行过程
- i=0，t={"name":"发动机"} → 无color → `0%3=0` → color="red"
- i=1，t={"name":"阀门","color":"yellow"} → 跳过
- i=2，t={"name":"管路"} → `2%3=2` → color="green"
- i=3，t={"name":"传感器"} → `3%3=0` → color="red"

### 处理后结果
```python
{
    "ontoTypes": [
        {"name": "发动机", "color": "red"},
        {"name": "阀门", "color": "yellow"},
        {"name": "管路", "color": "green"},
        {"name": "传感器", "color": "red"},
    ]
}
```

## 四、业务场景说明
本体可视化、知识图谱前端渲染时，每种类型需要固定区分色；
用户导入Excel/文本本体时，经常没填写颜色字段，这个函数做兜底填充，保证前端渲染不会缺失颜色报错。

## 五、关键点总结
1. 只补全缺失的color，**不会覆盖用户手动设置的颜色**；
2. 取模运算实现颜色循环，再多类型也不会下标报错；
3. 直接原地修改字典，最后返回原字典；
4. 兼容 `ontoTypes` 键不存在的空数据场景，不会抛异常。