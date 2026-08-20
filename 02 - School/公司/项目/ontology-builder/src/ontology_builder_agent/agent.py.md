---
created: 2026-07-13T14:28
updated: 2026-08-20T11:50
---
# `ontology-generate_bridge_imbuilder/src/ontology_builder_agent/agent.py`
## 01 
```python
_OUTPUT_PATH_RE = re.compile(r"(?:输出到|保存到|写入|out(?:put)?(?:\s+path)?)\s*[:：=]?\s*(?P<path>[^\s，。；;]+)", re.IGNORECASE)
_BASE_IRI_RE = re.compile(r"https?://[^\s，。；;]+")
```
这两个正则表达式主要用于从非结构化文本（例如用户的自然语言指令、日志文件或文档）中**提取关键信息**。

根据上下文（`ontology-builder` 项目），它们的作用分别是：**提取文件保存路径**和**提取网络链接（IRI）**。

以下是详细拆解：

---

### 1. `_OUTPUT_PATH_RE`：提取输出路径
这个正则用于识别类似“输出到 /tmp/data”或“output path: C:\files”这样的指令，并提取出后面的路径部分。

```python
_OUTPUT_PATH_RE = re.compile(
    r"(?:输出到|保存到|写入|out(?:put)?(?:\s+path)?)\s*[:：=]?\s*(?P<path>[^\s，。；;]+)", 
    re.IGNORECASE
)
```
>[!note] 
>这个正则表达式有优化空间
#### 逐段解析：
- **`(?: ... )` (非捕获组 - 关键词匹配)**：
  这里定义了触发路径提取的“前缀词”。它支持中英文混合：
  - `输出到` | `保存到` | `写入`：中文指令。
  - `out(?:put)?`：匹配 "out" 或 "output"。
  - `(?:\s+path)?`：可选匹配，允许 "output" 后面跟着空格和 "path"（即匹配 "output path"）。
- **`\s*[:：=]?\s*` (分隔符)**：
  - `\s*`：允许关键词和路径之间有任意数量的空白字符（空格、换行等）。
  - `[:：=]?`：允许出现冒号（中英文均可）或等号作为连接符，也可以没有（直接接路径）。
- **`(?P<path> ... )` (命名捕获组)**：
  - 这是核心部分。`?P<path>` 给提取到的内容起了个名字叫 `path`，代码里可以通过 `.group('path')` 直接获取。
- **`[^\s，。；;]+` (路径内容)**：
  - `[...]`：字符集。
  - `^`：取反，表示“除了这些字符以外的所有字符”。
  - 这里排除了：空白符 (`\s`)、中文标点（逗号`，`、句号`。`、分号`；`）以及英文分号 `;`。
  - **目的**：确保提取的路径在遇到句子结束或列表分隔符时停止，防止把后面的废话也当成路径。
- **`re.IGNORECASE`**：
  - 忽略大小写，所以 "Output" 和 "output" 都能匹配。

#### 匹配示例：
- ✅ `"请把结果输出到 /home/user/data"` -> 提取 `/home/user/data`
- ✅ `"写入./config.json"` -> 提取 `./config.json`

---

### 2. `_BASE_IRI_RE`：提取基础 IRI (网址)
这个正则用于从文本中提取本体（Ontology）的基础 IRI（通常是 URL 格式）。

```python
_BASE_IRI_RE = re.compile(r"https?://[^\s，。；;]+")
```

#### 逐段解析：
- **`https?://` (协议头)**：
  - `http`：匹配 "http"。
  - `s?`：`s` 是可选的，所以同时支持 `"http://"` 和 `"https://"`。
  - `://`：标准的 URL 分隔符。
- **`[^\s，。；;]+` (URL 主体)**：
  - 逻辑与上面相同。匹配除了空白符和中英文标点（逗号、句号、分号）之外的所有字符。
  - **目的**：URL 通常很长且包含特殊符号（如 `/`, `-`, `_`, `?`, $=$），但不能包含空格或句子结束的标点。这个规则能精准地把整个 URL “切”出来。

#### 匹配示例：
- ✅ `"The base IRI is https://example.org/ontology#"` -> 提取 `https://example.org/ontology#`
- ✅ `"访问 http://192.168.1.1:8080/api"` -> 提取 `http://192.168.1.1:8080/api`

---

### 总结
这段代码的设计非常**实用主义**：
1.  **兼容性强**：同时考虑了中文语境（“输出到”）和英文语境（"output path"），以及中英文标点符号的区别。
2.  **鲁棒性**：通过排除法（`[^...]`）来界定字符串的结束，而不是尝试去匹配所有合法的路径字符（因为路径字符太复杂了，排除法更不容易出错）。
3.  **用途**：这通常用于 AI Agent（智能体）解析用户的自然语言命令。比如用户说：“帮我建个本体，**输出到** `/tmp/test.owl`，**Base IRI 是** `http://my.site.com`”，程序就能用这两个正则把参数自动填好。


---

## 02
```python
class OntologyBuilderAgent:
	...
```
下面按源码结构详细拆 `OntologyBuilderAgent`。它位于：

[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:30)

这个类可以理解为 `ontology-builder` 的**核心门面类**：CLI、Harness Agent、文档构建、文本构建，最后都会汇总到它这里。

### 一、它整体负责什么

`OntologyBuilderAgent` 负责把输入内容变成本体文件。

输入可以是：

```text
自然语言文本
单个文档
多个文档
Harness Agent 消息
```

输出可以是：

```text
SysML 文本
IM JSON
Bridge IM JSON
OWL/Turtle 文件
BuildResult 结果对象
```

它内部串起了几类组件：

```text
Extractor      负责从文本中抽取结构
Renderer       负责把结构渲染成 SysML / OWL
Bridge         负责调用 Java sysml-owl-bridge
Validator      负责检查渲染完整性
Harness Agent  负责以 Agent 方式运行
```

---

### 二、初始化方法 `__init__`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:30)

```python
def __init__(
    self,
    provider: str | None = None,
    model: str | None = None,
    bridge: SysmlOwlBridge | None = None,
) -> None:
```

初始化时创建几个关键成员：

```python
self.settings = get_settings()
```

读取配置，例如默认 `base_iri`、默认输出格式、Java bridge 目录、默认 L LM 模型等。

```python
self.extractor = SysmlExtractor(provider=provider, model=model)
```

用于直接从自然语言生成 SysML 文本。

```python
self.im_extractor = OntologyModelExtractor(provider=provider, model=model)
```

用于生成项目自定义的 `OntologyModel`。这个模型比较像简化版本体结构，里面有 classes、object_properties、datatype_properties、individuals。

```python
self.bridge_im_extractor = BridgeIMExtractor(provider=provider, model=model)
```

用于生成 Bridge IM Draft，也就是更贴近 Java `sysml-owl-bridge` 的中间模型草稿。

```python
self.bridge = bridge or SysmlOwlBridge(self.settings.sysml_owl_bridge_dir)
```

如果外部没传 bridge，就创建一个 `SysmlOwlBridge`，用于后面调用 Java Maven 项目做 SysML -> OWL 转换。

```python
self._agent = None
```

缓存 Harness Agent。第一次调用 `harness_agent()` 时才真正创建。

---

### 三、生成 SysML：`generate_sysml`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:44)

```python
async def generate_sysml(self, text, base_iri=None, use_llm=True) -> str:
```

作用：从自然语言生成 SysML 文本。

逻辑：

```python
if not use_llm:
    return fallback_sysml_from_text(text)
```

如果不用 LLM，就走本地 fallback 规则，生成一个简单 SysML。

```python
sysml_text = clean_sysml_text(
    await self.extractor.extract(text, base_iri or self.settings.default_base_iri)
)
```

如果用 LLM，则调用 `SysmlExtractor.extract()` 抽取 SysML，然后清理文本。

```python
if "package " not in sysml_text:
    return fallback_sysml_from_text(text)
```

如果 LLM 输出不像合法 SysML，兜底生成 fallback SysML。

这一点很重要：它对 LLM 输出不完全信任，会做最小结构检查。

---

### 四、生成项目自定义 IM：`generate_im`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:52)

```python
async def generate_im(self, text, base_iri=None, use_llm=True) -> OntologyModel:
```

作用：从自然语言生成 `OntologyModel`。

`OntologyModel` 定义在：

[im.py](./ontology-builder/src/ontology_builder_agent/im.py:116)

结构大概是：

```python
class OntologyModel(BaseModel):
    base_iri: str
    name: str
    classes: list[OntologyClass]
    object_properties: list[ObjectProperty]
    datatype_properties: list[DatatypeProperty]
    individuals: list[Individual]
```

如果 `use_llm=False`：

```python
return fallback_im_from_text(text, base_iri=resolved_base_iri)
```

如果 `use_llm=True`：

```python
return await self.im_extractor.extract(text, resolved_base_iri)
```

所以它输出的是结构化模型，而不是文本。

---

### 五、生成 Bridge IM：`generate_bridge_im`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:58)

```python
async def generate_bridge_im(self, text, base_iri=None, use_llm=True)
```

作用：生成更贴近 Java bridge 的中间模型。

它和 `generate_im()` 的区别是：

| 方法                     | 生成对象            | 适用路径                           |
| ---------------------- | --------------- | ------------------------------ |
| `generate_im()`        | `OntologyModel` | 本地直接渲染、debug、简单 OWL            |
| `generate_bridge_im()` | `BridgeIMDraft` | 走 Java bridge 的 canonical 转换路径 |

如果不用 LLM，走：

```python
fallback_bridge_im_from_text(...)
```

如果用 LLM，走：

```python
self.bridge_im_extractor.extract(...)
```

---

### 六、只生成 IM：`build_im_from_text`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:64)

```python
async def build_im_from_text(...):
```

这是 `mode="im-only"` 时会用的路径。

流程：

```text
文本 -> OntologyModel -> 写成 .json -> 返回 BuildResult
```

关键代码：

```python
model = await self.generate_im(...)
```

生成 IM。

```python
im_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
```

把 Pydantic 模型写成 JSON。

返回：

```python
BuildResult(
    im=model,
    im_path=im_path,
    output_format="json",
    generation_mode="im-only",
    dry_run=True,
)
```

注意：这里 `dry_run=True`，因为它没有生成真正 OWL，只是生成中间模型。

---

### 七、本地直接生成 OWL：`build_direct_from_text` 和 `build_from_im`

位置：

[build_direct_from_text](./ontology-builder/src/ontology_builder_agent/agent.py:87)
[build_from_im](./ontology-builder/src/ontology_builder_agent/agent.py:108)

`build_direct_from_text()` 是外壳：

```python
model = await self.generate_im(...)
return await self.build_from_im(model, ...)
```

真正干活的是 `build_from_im()`。

流程：

```text
文本
 -> OntologyModel
 -> 本地 renderer 直接写 OWL/Turtle
 -> 同时写 .sysml
 -> 同时写 .im.json
 -> 返回 BuildResult
```

核心：

```python
ontology_path = write_ontology_model(model, output_path, resolved_format)
```

把 `OntologyModel` 直接写成本体文件。

```python
sysml_text = render_ontology_model_to_sysml(model)
```

把 IM 渲染成 SysML。

```python
sysml_path.write_text(sysml_text, encoding="utf-8")
im_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
```

额外输出 SysML 和 IM JSON。

然后做完整性检查：

```python
validation = validate_im_rendering_completeness(...)
```

返回的 `generation_mode` 是：

```python
generation_mode="im-direct"
```

源码里还明确写了 warning：

```python
"im-direct uses a limited local Turtle renderer; use im-bridge/sysml-bridge for canonical Java bridge mapping."
```

意思是：这个路径是本地简化渲染，不是权威 Java bridge 路径。适合调试，不适合作为最终严肃转换路径。

---

### 八、Bridge IM 路径：`build_bridge_im_from_text`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:153)

这是 `mode="im-bridge"` 时用的路径。

流程：

```text
文本
 -> BridgeIMDraft
 -> render_bridge_im_to_sysml()
 -> 写 .bridge-im.json
 -> 写 .sysml
 -> 如果 dry_run：到此结束
 -> 调 Java sysml-owl-bridge
 -> 生成 OWL/Turtle
 -> 返回 BuildResult
```

关键代码：

```python
model = await self.generate_bridge_im(...)
sysml_text = render_bridge_im_to_sysml(model)
```

先生成 Bridge IM，再渲染成 bridge 可读的 SysML。

```python
im_path = ontology_path.with_suffix(".bridge-im.json")
sysml_path = ontology_path.with_suffix(".sysml")
```

默认会在目标 TTL 旁边生成：

```text
xxx.bridge-im.json
xxx.sysml
```

如果是 dry-run：

```python
if dry_run:
    return result
```

就不会调用 Java bridge。

如果不是 dry-run：

```python
bridge_result = await asyncio.to_thread(
    self.bridge.convert_sysml_file,
    sysml_path,
    ontology_path,
    resolved_format,
    resolved_base_iri,
)
```

这里很关键。

`self.bridge.convert_sysml_file(...)` 是同步阻塞函数，会调用 Maven/Java bridge。为了不阻塞 async event loop，代码用：

```python
asyncio.to_thread(...)
```

把阻塞任务丢到线程里执行。

---

### 九、主入口：`build_from_text`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:212)

这是最重要的方法。CLI 的 `from-text` 最终就会调用它。

```python
async def build_from_text(
    text,
    output_path,
    base_iri=None,
    output_format=None,
    dry_run=False,
    use_llm=True,
    mode="sysml-bridge",
    emit_im_path=None,
    emit_sysml_path=None,
) -> BuildResult:
```

它根据 `mode` 分发到不同构建路径：

```python
if mode == "im-only":
    return await self.build_im_from_text(...)
```

只生成 IM JSON。

```python
if mode in {"im-direct", "direct"}:
    return await self.build_direct_from_text(...)
```

本地直接从 IM 渲染 OWL，不调用 Java bridge。

```python
if mode == "im-bridge":
    return await self.build_bridge_im_from_text(...)
```

生成 Bridge IM，再渲染 SysML，再调用 Java bridge。

如果不是以上模式，就走默认路径：

```text
sysml-bridge
```

默认路径流程是：

```text
文本
 -> generate_sysml()
 -> 写 .sysml
 -> bridge_im_from_sysml_text()
 -> 校验
 -> 如果 dry_run：返回
 -> 调 Java bridge convert_sysml_file()
 -> 输出 OWL/Turtle
 -> 返回 BuildResult
```

核心代码：

```python
sysml_text = await self.generate_sysml(text, resolved_base_iri, use_llm=use_llm and not dry_run)
```

注意这里：

```python
use_llm=use_llm and not dry_run
```

如果 `dry_run=True`，即使外面说 `use_llm=True`，这里也不会用 LLM，而是走 fallback SysML。这个设计是为了让 dry-run 更离线、更稳定。

然后：

```python
sysml_path.write_text(sysml_text, encoding="utf-8")
```

写 SysML 文件。

```python
bridge_model = bridge_im_from_sysml_text(sysml_text, resolved_base_iri)
```

从 SysML 反推出一个 Bridge IM，用于校验和结果展示。

如果不是 dry-run，就调用 Java bridge：

```python
bridge_result = await asyncio.to_thread(
    self.bridge.convert_sysml_file,
    sysml_path,
    ontology_path,
    resolved_format,
    resolved_base_iri,
)
```

最后返回 `BuildResult`。

---

### 十、从文档构建：`build_from_document`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:303)

```python
document_text = read_document(path)
```

先读取文档内容。支持 README 中提到的 txt/md/html/pdf 等。

然后直接复用：

```python
result = await self.build_from_text(document_text, ...)
```

也就是说，文档路径只是多了一步：

```text
文件 -> 文本
```

后续全部和自然语言文本路径一致。

最后补充元数据：

```python
result.metadata["document_path"] = str(Path(path).resolve())
```

---

### 十一、从多个文档构建：`build_from_documents`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:330)

和单文档类似，只是读取多个文件：

```python
document_text = read_documents(paths)
```

然后复用：

```python
self.build_from_text(...)
```

最后记录：

```python
result.metadata["document_paths"] = [...]
```

所以多个文档构建的核心逻辑仍然是 `build_from_text()`。

---

### 十二、创建 Harness Agent：`harness_agent`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:357)

这个方法把当前类的能力包装成 Harness Agent 工具。

开头：

```python
if self._agent is not None:
    return self._agent
```

如果已经创建过 Agent，就直接复用，避免重复创建。

然后：

```python
from mbse_harness.sdk.forge import Agent, tool
```

懒加载 Harness。这样普通 CLI 路径如果不用 agent，就不会一开始强依赖 Harness。

里面定义了多个工具函数，并用 `@tool` 装饰：

```python
@tool(...)
async def build_ontology_from_text(...)
```

这些工具包括：

```text
build_ontology_from_text
build_ontology_from_document
generate_sysml_from_text
generate_im_from_text
build_ontology_direct_from_text
```

它们本质上都是对当前类方法的包装。

最后创建 Agent：

```python
self._agent = Agent(
    name="ontology-builder-agent",
    system_prompt=...,
    tools=[...],
    model=self.settings.default_llm_model,
    temperature=0.1,
)
```

也就是说，`OntologyBuilderAgent` 既可以作为普通 Python 服务类用，也可以包装成 Harness Agent，让 Agent 自己调用工具完成任务。

---

### 十三、Agent 方式运行：`run`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:427)

```python
async def run(self, message: str) -> str:
```

对应 CLI：

```powershell
python -m ontology_builder_agent agent "..."
```

流程：

```python
_ensure_harness_db_engine_initialized()
```

先确保 Harness 数据库引擎已初始化。

```python
agent = self.harness_agent()
result = await agent.run(message)
```

创建/获取 Harness Agent，然后运行用户消息。

接着有一个兜底判断：

```python
output_path = _extract_output_path(message)
if "missing 1 required positional argument: 'text'" in result.content or not Path(output_path).exists():
    return await self._run_direct_build_from_message(message)
```

意思是：如果 Harness Agent 调工具失败，或者预期输出文件没生成，就不要直接失败，而是走本类的直接构建兜底路径。

这是一种很实用的防御设计：Agent 工具调用不稳定时，仍然尽量完成用户任务。

---

### 十四、Agent 失败后的兜底：`_run_direct_build_from_message`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:436)

这个方法直接把整条用户消息当作输入文本：

```python
result = await self.build_from_text(
    message,
    output_path=output_path,
    base_iri=base_iri,
)
```

`output_path` 和 `base_iri` 从用户消息里用正则提取：

```python
output_path = _extract_output_path(message)
base_iri = _extract_base_iri(message)
```

然后返回一段摘要文本，包括：

```text
sysml_path
ontology_path
base_iri
bridge_returncode
```

你看到源码里中文是乱码，是终端编码问题，不影响逻辑。

---

### 十五、资源清理：`close`

位置：[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:452)

```python
async def close(self) -> None:
    if self._agent is not None:
        await self._agent.close()
```

如果创建过 Harness Agent，就关闭它。

这也是为什么 `__main__.py` 里有：

```python
finally:
    await builder.close()
```

确保 CLI 执行完后资源释放。

---

### 十六、辅助函数

类外还有几个辅助函数。

`_extract_output_path(message)`：

[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:457)

从自然语言里提取输出路径。如果没找到，默认：

```text
target/ontology.ttl
```

`_extract_base_iri(message)`：

[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:464)

从消息里找 URL，作为 `base_iri`。

`_ensure_harness_db_engine_initialized()`：

[agent.py](./ontology-builder/src/ontology_builder_agent/agent.py:471)

确保 `mbse_harness` 的数据库引擎已初始化。只在 Agent 模式下需要。

---

### 十七、最核心的数据流

默认 `sysml-bridge` 模式：

```text
自然语言 text
  -> generate_sysml()
  -> 写 output.sysml
  -> bridge_im_from_sysml_text()
  -> validate_bridge_im_rendering_completeness()
  -> self.bridge.convert_sysml_file()
  -> Java sysml-owl-bridge
  -> output.ttl
  -> BuildResult
```

`im-bridge` 模式：

```text
自然语言 text
  -> generate_bridge_im()
  -> render_bridge_im_to_sysml()
  -> 写 .bridge-im.json
  -> 写 .sysml
  -> Java bridge
  -> output.ttl
  -> BuildResult
```

`im-direct` 模式：

```text
自然语言 text
  -> generate_im()
  -> write_ontology_model()
  -> 本地写 TTL
  -> 写 .im.json
  -> 写 .sysml
  -> BuildResult
```

`im-only` 模式：

```text
自然语言 text
  -> generate_im()
  -> 写 .im.json
  -> BuildResult
```

---

### 一句话总结

`OntologyBuilderAgent` 是 `ontology-builder` 的核心调度类：

```text
它负责接收文本/文档/Agent 消息，
选择构建模式，
调用 LLM 或 fallback 抽取结构，
生成 SysML 或 IM，
必要时调用 Java sysml-owl-bridge，
最后返回统一的 BuildResult。
```

新手读这个类时，最重要的是抓住一个主入口：

```python
build_from_text()
```

再围绕它看四种模式：

```text
sysml-bridge  默认主路径，文本 -> SysML -> Java bridge -> OWL
im-bridge     文本 -> Bridge IM -> SysML -> Java bridge -> OWL
im-direct     文本 -> OntologyModel -> 本地 renderer -> OWL
im-only       文本 -> OntologyModel JSON
```
## 03
```python
async def build_bridge_im_from_text(
        self,
        text: str,
        output_path: str | Path,
        base_iri: str | None = None,
        output_format: str | None = None,
        dry_run: bool = False,
        use_llm: bool = True,
        emit_im_path: str | Path | None = None,
        emit_sysml_path: str | Path | None = None,
    ) -> BuildResult:
        resolved_base_iri = base_iri or self.settings.default_base_iri
        resolved_format = output_format or self.settings.default_owl_format
        ontology_path = Path(output_path).resolve()
        model = await self.generate_bridge_im(text, resolved_base_iri, use_llm=use_llm)
        sysml_text = render_bridge_im_to_sysml(model)

        im_path = Path(emit_im_path).resolve() if emit_im_path else ontology_path.with_suffix(".bridge-im.json")
        im_path.parent.mkdir(parents=True, exist_ok=True)
        im_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")

        sysml_path = Path(emit_sysml_path).resolve() if emit_sysml_path else ontology_path.with_suffix(".sysml")
        sysml_path.parent.mkdir(parents=True, exist_ok=True)
        sysml_path.write_text(sysml_text, encoding="utf-8")

        validation = validate_bridge_im_rendering_completeness(model, sysml_text=sysml_text)
        result = BuildResult(
            sysml_text=sysml_text,
            sysml_path=sysml_path,
            ontology_path=None if dry_run else ontology_path,
            im_path=im_path,
            im=model,
            output_format=resolved_format,
            base_iri=resolved_base_iri,
            generation_mode="im-bridge",
            dry_run=dry_run,
            metadata={
                "canonical_im": "Java sysmlv2-owl-bridge IMOntology",
                "bridge_input_format": "sysml-text",
                "validation": validation.as_dict(),
            },
        )
        if dry_run:
            return result

        bridge_result = await asyncio.to_thread(
            self.bridge.convert_sysml_file,
            sysml_path,
            ontology_path,
            resolved_format,
            resolved_base_iri,
        )
        result.bridge = bridge_result
        if ontology_path.exists():
            ttl_text = ontology_path.read_text(encoding="utf-8", errors="replace")
            validation = validate_bridge_im_rendering_completeness(model, sysml_text=sysml_text, ttl_text=ttl_text)
            result.metadata["validation"] = validation.as_dict()
        return result
```

### 一、先搞懂整体作用
这个函数是**一套全自动本体生成流水线**，输入一篇文档文本，自动走完3步：
1. 调用大模型，从文字里提取结构化的系统信息（叫`BridgeIM`）
2. 把结构化信息翻译成标准SysML系统建模文本，并保存文件
3. 调用转换工具，把SysML转成owl/ttl领域本体文件
全程自动，不用手动画SysML模型。

### 二、函数定义与入参解释
```python
async def build_bridge_im_from_text(
        self,
        text: str,
        output_path: str | Path,
        base_iri: str | None = None,
        output_format: str | None = None,
        dry_run: bool = False,
        use_llm: bool = True,
        emit_im_path: str | Path | None = None,
        emit_sysml_path: str | Path | None = None,
    ) -> BuildResult:
```
1. `async def`：异步函数，不会卡住程序，可以同时处理多个任务
2. `self`：类方法固定参数，代表当前这个工具实例，存了配置、大模型、转换工具
3. `text: str`：输入，你清洗好的md文档正文（字符串）
4. `output_path`：最终本体文件（ttl/owl）保存路径
5. `base_iri`：本体唯一标识链接，不填就用配置文件默认值
6. `output_format`：输出本体格式（ttl/owl），不填读默认配置
7. `dry_run`：试运行开关。`True`=只生成中间文件，不生成最终本体；`False`=完整跑完全流程
8. `use_llm`：是否启用大模型提取信息，默认打开
9. `emit_im_path`：自定义中间结构化json文件保存路径，不填自动和本体放同目录
10. `emit_sysml_path`：自定义SysML模型文件保存路径，不填自动生成
11. `-> BuildResult`：函数最后会返回一个`BuildResult`对象，存所有生成文件路径、校验结果

### 三、前4行：读取配置、处理路径
```python
resolved_base_iri = base_iri or self.settings.default_base_iri
resolved_format = output_format or self.settings.default_owl_format
ontology_path = Path(output_path).resolve()
```
1. `resolved_base_iri`：如果调用函数时传了`base_iri`就用传入值，否则读取程序配置里默认的IRI
2. `resolved_format`：同理，优先用传入的输出格式，没有就用配置默认格式
3. `Path(output_path).resolve()`：把你传入的文件路径转成**绝对路径**，避免相对路径找不到文件

### 四、核心第一步：调用大模型提取结构化数据
```python
model = await self.generate_bridge_im(text, resolved_base_iri, use_llm=use_llm)
```
1. `await`：异步函数必须加，等待大模型接口返回结果，程序不会卡死
2. `generate_bridge_im`：内部会把你的文档文本发给大模型，要求模型输出固定格式JSON
3. `model`：接收返回结果，是一个结构化对象（BridgeIM），存文档里的系统、部件、关系、参数

### 五、第二步：把结构化数据转成SysML文本
```python
sysml_text = render_bridge_im_to_sysml(model)
```
工具函数`render_bridge_im_to_sysml`：把上一步大模型产出的`model`，自动翻译成标准SysML建模语言的纯文本字符串。

### 六、保存中间文件1：BridgeIM结构化JSON
```python
im_path = Path(emit_im_path).resolve() if emit_im_path else ontology_path.with_suffix(".bridge-im.json")
im_path.parent.mkdir(parents=True, exist_ok=True)
im_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
```
1. 第一行判断：如果你自定义了`emit_im_path`就用自定义路径；没传就自动生成和本体同名、后缀`.bridge-im.json`的文件
2. `mkdir(parents=True, exist_ok=True)`：如果文件夹不存在，自动创建文件夹，不会报错
3. `model.model_dump_json(indent=2)`：把结构化model对象转成格式化、易读的JSON字符串
4. `write_text`：把JSON写入本地文件，方便人工查看、修改大模型提取的内容

### 七、保存中间文件2：SysML模型文件
```python
sysml_path = Path(emit_sysml_path).resolve() if emit_sysml_path else ontology_path.with_suffix(".sysml")
sysml_path.parent.mkdir(parents=True, exist_ok=True)
sysml_path.write_text(sysml_text, encoding="utf-8")
```
逻辑和上面完全一致：
自动生成`.sysml`后缀文件，把刚才生成的SysML文本写入本地，这个文件就是SysML建模文件。

### 八、第一轮校验：检查转换是否完整
```python
validation = validate_bridge_im_rendering_completeness(model, sysml_text=sysml_text)
```
调用校验函数，检查：大模型提取的所有实体、关系，是不是完整转进了SysML文本，有没有丢失内容，校验结果存入`validation`。

### 九、组装返回结果对象
```python
result = BuildResult(
    sysml_text=sysml_text,
    sysml_path=sysml_path,
    ontology_path=None if dry_run else ontology_path,
    im_path=im_path,
    im=model,
    output_format=resolved_format,
    base_iri=resolved_base_iri,
    generation_mode="im-bridge",
    dry_run=dry_run,
    metadata={
        "canonical_im": "Java sysmlv2-owl-bridge IMOntology",
        "bridge_input_format": "sysml-text",
        "validation": validation.as_dict(),
    },
)
if dry_run:
    return result
```
1. 创建`BuildResult`对象，把当前所有信息打包：SysML文本、文件路径、中间IM数据、模式标记、校验报告
2. 如果开启了`dry_run`（试运行），直接返回结果，**不执行后面SysML转本体的步骤**

### 十、正式流程：SysML转换为最终本体文件
```python
bridge_result = await asyncio.to_thread(
    self.bridge.convert_sysml_file,
    sysml_path,
    ontology_path,
    resolved_format,
    resolved_base_iri,
)
result.bridge = bridge_result
```
1. `asyncio.to_thread`：转换工具是同步阻塞程序，放到子线程运行，不打断异步主流程
2. `self.bridge.convert_sysml_file`：调用`sysml-owl-bridge`工具，读取`.sysml`文件，转换成ttl/owl本体
3. 转换结果存入result对象的bridge字段

### 十一、第二轮校验：本体生成完成后二次检查
```python
if ontology_path.exists():
    ttl_text = ontology_path.read_text(encoding="utf-8", errors="replace")
    validation = validate_bridge_im_rendering_completeness(model, sysml_text=sysml_text, ttl_text=ttl_text)
    result.metadata["validation"] = validation.as_dict()
```
1. 判断本体文件是否成功生成
2. 读取本体文件内容，再次校验整条链路（文本→IM→SysML→本体）有没有信息丢失
3. 把最新校验结果更新到返回对象的元数据里

### 十二、函数结束，返回结果
```python
return result
```
把包含全部文件路径、校验信息、中间数据的`result`返回给调用者。

### 极简流程总结（方便初学者记忆）
1. 接收文档文本和输出路径
2. 调用大模型，提取结构化系统信息（BridgeIM）
3. 结构化信息转SysML文本，保存两份中间文件
4. 校验IM→SysML转换完整性
5. 试运行模式：直接返回结果，不生成本体
6. 完整模式：调用转换工具把SysML转为本体文件
7. 二次校验全链路完整性，返回所有文件与校验信息