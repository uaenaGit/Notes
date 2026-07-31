---
created: 2026-07-13T14:31
updated: 2026-07-13T14:35
---
# `ontology-builder/src/ontology_builder_agent/extractor.py
## 01
```python
@dataclass(slots=True)
class SysmlExtractor:
    provider: str | None = None
    model: str | None = None

    async def extract(self, source_text: str, base_iri: str | None = None) -> str:
        settings = get_settings()

        from mbse_harness.core.llm import LLMProvider, LLMService

        provider_name = (self.provider or settings.default_llm_provider).lower()
        provider = LLMProvider(provider_name)
        service = LLMService(provider=provider, model=self.model or settings.default_llm_model)
        prompt = build_extraction_prompt(source_text=source_text, base_iri=base_iri or settings.default_base_iri)
        response = await service.chat(
            messages=[
                {"role": "system", "content": SYSML_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        return clean_sysml_text(response.content)

```
这段代码定义了一个 **SysML 抽取器**：给它一段自然语言文本，它会调用 LLM，把文本转换成 SysML 文本。

可以先把它理解成：

```text
输入：一段中文/英文需求描述
  ↓
构造提示词 prompt
  ↓
调用大模型 LLM
  ↓
清理模型输出
  ↓
返回 SysML 文本
```

### 1. `@dataclass(slots=True)`

```python
@dataclass(slots=True)
class SysmlExtractor:
```

`dataclass` 是 Python 标准库提供的工具，用来快速定义“只保存数据的类”。

普通写法可能要这样：

```python
class SysmlExtractor:
    def __init__(self, provider=None, model=None):
        self.provider = provider
        self.model = model
```

用了 `@dataclass` 后，可以简写成：

```python
@dataclass
class SysmlExtractor:
    provider: str | None = None
    model: str | None = None
```

`slots=True` 是一个性能和约束优化。简单理解：

```text
这个类只能有 provider 和 model 这两个属性
不能随便动态加新属性
内存占用更小
```

### 2. 类里的两个属性

```python
provider: str | None = None
model: str | None = None
```

这是 Python 类型注解。

意思是：

```text
provider 可以是 str，也可以是 None，默认是 None
model 可以是 str，也可以是 None，默认是 None
```

例如：

```python
extractor = SysmlExtractor()
```

这时：

```python
extractor.provider == None
extractor.model == None
```

也可以手动指定：

```python
extractor = SysmlExtractor(provider="openai", model="gpt-4.1")
```

在这个项目里：

| 属性 | 作用 |
|---|---|
| `provider` | 使用哪个 LLM 服务商 |
| `model` | 使用哪个具体模型 |

### 3. `async def extract(...)`

```python
async def extract(self, source_text: str, base_iri: str | None = None) -> str:
```

这是一个异步函数。

参数含义：

| 参数            | 含义                   |
| ------------- | -------------------- |
| `self`        | 当前对象自己，类方法里固定会有      |
| `source_text` | 用户输入的自然语言文本          |
| `base_iri`    | 本体的基础 IRI，可选         |
| `-> str`      | 返回值是字符串，也就是 SysML 文本 |

因为它是 `async def`，调用时要用：

```python
sysml_text = await extractor.extract("无人机系统包含飞控")
```

为什么要异步？  
因为它要调用 LLM 服务，网络请求可能比较慢。异步可以避免程序卡死在这里。

### 4. 读取配置

```python
settings = get_settings()
```

从项目配置中读取默认设置。

例如可能包括：

```text
default_llm_provider
default_llm_model
default_base_iri
sysml_owl_bridge_dir
```

这意味着，如果你创建 `SysmlExtractor()` 时没有手动传 provider/model，它会从配置里拿默认值。

### 5. 延迟导入 LLM 相关类

```python
from mbse_harness.core.llm import LLMProvider, LLMService
```

这里导入两个东西：

| 名称 | 作用 |
|---|---|
| `LLMProvider` | 表示模型服务商，比如 openai、qwen、deepseek |
| `LLMService` | 真正负责和大模型聊天的服务类 |

为什么放在函数里面导入，而不是文件开头？  
通常是为了“懒加载”：只有真的调用 LLM 时才导入 `mbse_harness`，避免普通离线路径也强依赖它。

### 6. 确定使用哪个 provider

```python
provider_name = (self.provider or settings.default_llm_provider).lower()
```

这一句对新手可能有点绕。

`or` 在这里表示：优先用左边，如果左边没有值，就用右边。

等价于：

```python
if self.provider:
    provider_name = self.provider.lower()
else:
    provider_name = settings.default_llm_provider.lower()
```

所以：

```text
如果创建 SysmlExtractor 时传了 provider，就用传入的
否则用配置里的 default_llm_provider
最后统一转小写
```

例如：

```python
SysmlExtractor(provider="OpenAI")
```

会变成：

```python
provider_name = "openai"
```

### 7. 创建 provider 对象

```python
provider = LLMProvider(provider_name)
```

把字符串转换成 `LLMProvider` 对象。

如果 `LLMProvider` 是枚举，那么它可能类似：

```python
LLMProvider("openai")
LLMProvider("qwen")
LLMProvider("deepseek")
```

这样做的好处是：后面 `LLMService` 不直接拿字符串，而是拿一个受限制的 provider 类型，减少拼写错误。

### 8. 创建 LLM 服务

```python
service = LLMService(
    provider=provider,
    model=self.model or settings.default_llm_model
)
```

创建真正调用大模型的服务。

`model=self.model or settings.default_llm_model` 的意思类似：

```python
if self.model:
    model = self.model
else:
    model = settings.default_llm_model
```

也就是：

```text
优先使用对象里指定的模型
否则使用配置里的默认模型
```

### 9. 构造提示词

```python
prompt = build_extraction_prompt(
    source_text=source_text,
    base_iri=base_iri or settings.default_base_iri
)
```

把用户输入的文本和 `base_iri` 组装成一个完整提示词。

例如用户输入：

```text
无人机系统包含飞控、导航和任务载荷
```

`build_extraction_prompt(...)` 可能会把它包装成类似：

```text
请把下面领域描述转换成 sysmlv2-owl-bridge 可解析的 SysML v2 子集。
base IRI 是 http://example.org/uav#
领域描述：
无人机系统包含飞控、导航和任务载荷
```

注意：

```python
base_iri or settings.default_base_iri
```

意思是：

```text
如果调用 extract 时传了 base_iri，就用传入的
否则用默认 base_iri
```

### 10. 调用大模型

```python
response = await service.chat(
    messages=[
        {"role": "system", "content": SYSML_EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ],
    temperature=0.1,
)
```

这里是真正请求 LLM。

`messages` 是聊天消息列表。

第一条：

```python
{"role": "system", "content": SYSML_EXTRACTION_SYSTEM_PROMPT}
```

是系统提示词，用来告诉模型它的身份和规则。例如：

```text
你是 SysML 抽取器，只输出可解析的 SysML，不要输出解释文字
```

第二条：

```python
{"role": "user", "content": prompt}
```

是用户提示词，包含具体的领域文本和输出要求。

`temperature=0.1` 表示让模型输出更稳定、更少随机性。

temperature 越高，模型越发散；越低，越保守。这里生成结构化 SysML，所以温度设得很低。

因为 `service.chat(...)` 是异步的，所以前面要写：

```python
await
```

### 11. 清理并返回 SysML

```python
return clean_sysml_text(response.content)
```

LLM 返回的内容在：
```python
response.content
```

但大模型可能会返回：

```sysml
package UAV {
  ...
}
```

或者带一些解释文字。

所以要调用：

```python
clean_sysml_text(...)
```

把多余的 Markdown 代码块、解释文字、空白等清理掉，只保留 SysML 文本。

最后返回一个字符串。

### 整体等价的伪代码

你可以把它理解成下面这样：

```python
class SysmlExtractor:
    def __init__(self, provider=None, model=None):
        self.provider = provider
        self.model = model

    async def extract(self, source_text, base_iri=None):
        settings = get_settings()

        if self.provider is not None:
            provider_name = self.provider.lower()
        else:
            provider_name = settings.default_llm_provider.lower()

        provider = LLMProvider(provider_name)

        if self.model is not None:
            model_name = self.model
        else:
            model_name = settings.default_llm_model

        service = LLMService(provider=provider, model=model_name)

        if base_iri is None:
            base_iri = settings.default_base_iri

        prompt = build_extraction_prompt(source_text, base_iri)

        response = await service.chat(
            messages=[
                {"role": "system", "content": SYSML_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        return clean_sysml_text(response.content)
```

### 一句话总结

这段代码的作用是：

```text
SysmlExtractor 是一个调用大模型的 SysML 生成器。
它读取配置，确定 provider 和 model，
把自然语言文本包装成 prompt，
调用 LLM，
最后清理模型输出并返回 SysML 文本。
```

你作为 Python 新手，重点先掌握这几个语法点：

```text
@dataclass
类型注解 str | None
async / await
self
or 的默认值用法
函数内 import
字典和列表
对象方法调用
```

## 02 
```python
def clean_sysml_text(text: str) -> str:
    think_end = list(_THINK_END_RE.finditer(text))
    if think_end:
        text = text[think_end[-1].end() :]

    cleaned = _THINK_BLOCK_RE.sub("", text)
    cleaned = _CODE_FENCE_RE.sub("", cleaned).strip()
    package_block = _extract_last_package_block(cleaned)
    if package_block:
        return package_block.strip()

    package_index = cleaned.find("package ")
    if package_index > 0:
        cleaned = cleaned[package_index:]
    return cleaned.strip()


def _extract_last_package_block(text: str) -> str | None:
    for match in reversed(list(re.finditer(r"\bpackage\s+", text))):
        open_brace = text.find("{", match.end())
        if open_brace == -1:
            continue
        close_brace = _find_matching_brace(text, open_brace)
        if close_brace != -1:
            return text[match.start() : close_brace + 1]
    return None
```
这两段代码的作用是：

```text
把大模型返回的一大段文本，清理成真正可用的 SysML 代码。
```

因为大模型可能返回这种内容：

````text
<think>
我先分析一下需求……
</think>

下面是 SysML：

```sysml
package UAV {
    part def FlightController;
}
```
````

但程序真正想要的是：

```sysml
package UAV {
    part def FlightController;
}
```

---

### 1. `clean_sysml_text`

```python
def clean_sysml_text(text: str) -> str:
```

定义一个函数。

意思是：

```text
输入：text，一个字符串
输出：也是字符串
```

`text: str` 表示参数 `text` 应该是字符串。

`-> str` 表示函数返回字符串。

---

### 2. 删除 `</think>` 前面的内容

```python
think_end = list(_THINK_END_RE.finditer(text))
```

这行是在找文本里所有的：

```text
</think>
```

`finditer(text)` 会返回所有匹配位置。

`list(...)` 是把结果转成列表。

例如：

```python
text = "<think>分析过程</think> package UAV {}"
```

那么 `think_end` 里面会记录 `</think>` 出现的位置。

接着：

```python
if think_end:
    text = text[think_end[-1].end() :]
```

意思是：

```text
如果找到了 </think>，
就从最后一个 </think> 的后面开始截取文本。
```

比如：

```python
text = "<think>分析过程</think> package UAV {}"
```

处理后变成：

```python
" package UAV {}"
```

为什么用最后一个？

因为有时模型可能输出多个 `</think>`，代码选择最后一个，尽量保证把思考内容全部丢掉。

---

### 3. 删除完整 `<think>...</think>` 块

```python
cleaned = _THINK_BLOCK_RE.sub("", text)
```

`sub("", text)` 的意思是：

```text
找到匹配内容，并替换成空字符串
```

也就是删除。

比如：

```python
text = "<think>分析过程</think> package UAV {}"
```

处理后：

```python
" package UAV {}"
```

这一步和上一步有点像，都是为了删除模型的思考内容。

---

### 4. 删除 Markdown 代码块标记

```python
cleaned = _CODE_FENCE_RE.sub("", cleaned).strip()
```

这一行做两件事：

```python
_CODE_FENCE_RE.sub("", cleaned)
```

删除 Markdown 代码块标记，例如：

````text
```sysml
package UAV {}
```
````

会变成：

```text
package UAV {}
```

后面的：

```python
.strip()
```

是去掉字符串首尾空白。

比如：

```python
"   package UAV {}   ".strip()
```

结果是：

```python
"package UAV {}"
```

---

### 5. 尝试提取最后一个完整的 package 块

```python
package_block = _extract_last_package_block(cleaned)
```

SysML 通常长这样：

```sysml
package UAV {
    part def FlightController;
}
```

所以这里尝试从文本中提取完整的：

```text
package ... { ... }
```

如果找到了：

```python
if package_block:
    return package_block.strip()
```

就直接返回这个 package 块。

---

### 6. 如果没找到完整 package，就找 `package ` 开始的位置

```python
package_index = cleaned.find("package ")
```

`find("package ")` 会查找字符串中第一次出现 `package ` 的位置。

例如：

```python
cleaned = "下面是结果： package UAV {}"
package_index = cleaned.find("package ")
```

`package_index` 就是 `package` 出现的位置。

接着：

```python
if package_index > 0:
    cleaned = cleaned[package_index:]
```

意思是：

```text
如果 package 不是在开头，而是在中间，
就把 package 前面的解释文字删掉。
```

比如：

```python
"下面是结果： package UAV {}"
```

会变成：

```python
"package UAV {}"
```

最后：

```python
return cleaned.strip()
```

返回清理后的文本。

---

### 第二个函数：`_extract_last_package_block`

```python
def _extract_last_package_block(text: str) -> str | None:
```

这个函数作用是：

```text
从文本中找最后一个完整的 package {...} 块
```

返回值：

```text
如果找到了，返回字符串
如果没找到，返回 None
```

`str | None` 的意思是：

```text
返回值可能是字符串，也可能是 None
```

---

### 1. 找所有 `package`

```python
re.finditer(r"\bpackage\s+", text)
```

这是用正则查找所有 `package`。

* **`re.finditer(pattern, string)`**：这个方法会在 `string`（这里是 `text`）中查找所有匹配 `pattern` 的位置，并返回一个**迭代器**。与 `re.findall()` 返回字符串列表不同，`finditer` 返回的是**匹配对象（Match Object）**，你可以通过它获取匹配到的文本、在原文中的起始和结束索引等丰富信息。
* **`r"\bpackage\s+"`**：这是正则表达式（前面的 `r` 表示原始字符串，防止反斜杠被转义）：
  * `\b`：**单词边界**。确保 `package` 是一个完整的单词，而不是其他单词的一部分（比如不会匹配到 `mypackage` 或 `packages` 中的 `package`）。
  * `package`：精确匹配字面量 `package`。
  * `\s+`：**一个或多个空白字符**（包括空格、制表符、换行符等）。这意味着 `package` 后面必须紧跟至少一个空白符。

简单理解：

```text
找出文本里所有 package 开头的位置
```

然后：

```python
list(...)
```

转成列表。

再：

```python
reversed(...)
```

倒着遍历。

为什么倒着？

因为函数名叫：

```python
_extract_last_package_block
```

也就是优先取最后一个 package 块。

这对 LLM 输出很有用。因为模型可能先给解释，然后又给一个修正版：

```text
第一次：
package Old {
}

修正后：
package New {
}
```

代码会优先取最后的 `package New {}`。

---

### 2. 找左大括号 `{`

```python
open_brace = text.find("{", match.end())
```

意思是：

```text
从 package 后面开始，找第一个 {
```

例如：

```sysml
package UAV {
```

这里的 `{` 就是 package 块开始的地方。

如果没找到：

```python
if open_brace == -1:
    continue
```

就跳过这个 package，继续找前一个。

`-1` 是 Python 里 `find()` 找不到时的返回值。

---

### 3. 找匹配的右大括号 `}`

```python
close_brace = _find_matching_brace(text, open_brace)
```

这个函数没有贴出来，但从名字看，它应该是：

```text
从左大括号 { 开始，找到与它配对的右大括号 }
```

为什么不能简单找第一个 `}`？

因为 SysML 里面可能有嵌套：

```sysml
package UAV {
    part def Drone {
        attribute mass : Real;
    }
}
```

这里有两层 `{}`。

真正的 package 结束位置是最后一个 `}`，不是第一个。

所以需要 `_find_matching_brace(...)`。

---

### 4. 如果找到了完整块，就返回

```python
if close_brace != -1:
    return text[match.start() : close_brace + 1]
```

意思是：

```text
从 package 开始位置，截取到匹配的 } 结束位置
```

注意：

```python
close_brace + 1
```

Python 切片右边是不包含的。

比如：

```python
text[0:5]
```

取的是位置 0、1、2、3、4，不包含 5。

所以要 `+ 1`，才能把 `}` 也包含进去。

---

### 5. 如果都没找到，返回 None

```python
return None
```

表示没有找到完整的 package 块。

---

### 示例 1：清理代码块

输入：

````python
text = """
```sysml
package UAV {
    part def FlightController;
}
```
"""
````

执行：

```python
clean_sysml_text(text)
```

输出：

```sysml
package UAV {
    part def FlightController;
}
```

---

### 示例 2：删除思考内容

输入：

```python
text = """
<think>
我先分析：用户要无人机系统本体。
</think>

package UAV {
    part def Payload;
}
"""
```

输出：

```sysml
package UAV {
    part def Payload;
}
```

---

### 示例 3：删除解释文字

输入：

```python
text = """
下面是生成的 SysML：

package UAV {
    part def Navigation;
}
"""
```

输出：

```sysml
package UAV {
    part def Navigation;
}
```

---

### 示例 4：有多个 package，取最后一个

输入：

```python
text = """
package Draft {
    part def OldPart;
}

这里是修正版本：

package UAV {
    part def FlightController;
}
"""
```

输出：

```sysml
package UAV {
    part def FlightController;
}
```

因为 `_extract_last_package_block` 是倒着找的。

---

### 示例 5：有嵌套大括号

输入：

```python
text = """
package UAV {
    part def Drone {
        attribute mass : Real;
    }
}
"""
```

输出：

```sysml
package UAV {
    part def Drone {
        attribute mass : Real;
    }
}
```

这里必须靠 `_find_matching_brace` 找到真正配对的最后一个 `}`。

---

### 最简单总结

`clean_sysml_text()` 就像一个“清洁工”：

```text
1. 去掉模型思考内容
2. 去掉 Markdown 代码块符号
3. 去掉解释文字
4. 找出真正的 package {...}
5. 返回干净的 SysML
```

`_extract_last_package_block()` 就像一个“裁剪器”：

```text
从一大段文本里，裁剪出最后一个完整的 package {...} 代码块。
```

你作为 Python 初学者，重点理解这几个语法就够了：

```text
list(...)
if ...
字符串切片 text[a:b]
.strip()
.find()
for 循环
return
None
```

不用一开始把正则完全吃透，先知道它们是在“查找特定文本模式”就行。

## 03
```python
def fallback_sysml_from_text(source_text: str, package_name: str = "GeneratedOntology") -> str:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,}", source_text)
    candidates: list[str] = []
    non_ascii_count = 1
    for word in words:
        normalized = _to_pascal_case(word)
        if not normalized:
            normalized = f"DomainConcept{non_ascii_count}"
            non_ascii_count += 1
        if normalized not in candidates:
            candidates.append(normalized)
        if len(candidates) >= 8:
            break
    if not candidates:
        candidates = ["Concept"]

    definitions = "\n".join(f"  item def {name};" for name in candidates)
    return f"package {package_name} {{\n{definitions}\n}}"


def _to_pascal_case(value: str) -> str:
    ascii_value = re.sub(r"[^A-Za-z0-9_\-]+", " ", value)
    parts = re.split(r"[^A-Za-z0-9]+", ascii_value)
    text = "".join(part[:1].upper() + part[1:] for part in parts if part)
    if not text:
        return ""
    if re.match(r"^[0-9]", text):
        text = f"Concept{text}"
    return text
```

### 一、代码整体概述

这段 Python 代码由**1个主函数 \+ 1个辅助工具函数**组成，核心作用：接收一段任意中英文混合文本，自动提取有效关键词、统一转换成 SysML 建模语言规范的大驼峰命名，最终生成一段合法、无语法错误的 SysML 包结构字符串。

简单一句话总结：**随便输一段文字，自动帮你生成标准化的SysML建模概念代码**。

前置必备知识点：

- **大驼峰（PascalCase）**：每个单词首字母大写，无空格、无下划线，SysML 官方规范命名格式，例：Engine、CarBattery

- 代码依赖 Python 内置正则库 `re`，运行前必须导入：`import re`

标准输出效果示例：

```python
package GeneratedOntology {
  item def CarModel;
  item def Battery;
}
```

### 二、辅助函数：\_to\_pascal\_case（命名格式化工具）

**函数作用**：清洗任意杂乱文本（中文、符号、数字、特殊字符），转换成合法的大驼峰命名；无法转换则返回空字符串，给主函数做容错判断。

**入参出参**：接收任意字符串，返回格式化后的标准命名字符串。

#### 1\. 函数定义

```python
def _to_pascal_case(value: str) -> str:
```

初学者注解：`: str`、`-> str` 是**类型注解**，只做代码规范提示，不影响程序运行，用来标注「输入、输出都是字符串」。下划线开头函数为私有辅助函数，仅内部调用。

#### 2\. 清洗非法字符

```python
ascii_value = re.sub(r"[^A-Za-z0-9_\-]+", " ", value)
```

核心逻辑：

- `re.sub`：正则替换函数，匹配到的内容统一替换成空格

- 正则 `[^A-Za-z0-9_\-]`：`[]`内`^`代表取反，匹配**所有不是字母、数字、下划线、横杠**的字符（中文、标点、感叹号、括号等全部清空）

示例：`汽车-发动机！123` → 清洗后变为 ` -  123 `

#### 3\. 切割纯有效片段

```python
parts = re.split(r"[^A-Za-z0-9]+", ascii_value)
```

核心逻辑：用所有非字母数字的字符（空格、横杠、下划线）切割文本，得到纯字母、数字的片段列表，剔除杂乱符号。

承接上例：切割后得到 `["", "", "123", ""]`

#### 4\. 拼接大驼峰名称

```python
text = "".join(part[:1].upper() + part[1:] for part in parts if part)
```

逐段拆解（初学者友好）：

- `if part`：过滤列表中的空字符串，只保留有效片段

- `part[:1].upper()`：取每个片段第一个字符，转为大写

- `part[1:]`：保留片段剩余所有字符，不做修改

- `"".join()`：将所有处理后的片段无缝拼接

示例：`car-model` → 拆分 `car、model` → 首字母大写拼接 → `CarModel`

#### 5\. 空值容错判断

```python
if not text:
    return ""
```

逻辑：如果输入纯中文、全符号，清洗后无有效内容，返回空字符串，告知主函数「该关键词无法格式化」。

#### 6\. 数字开头容错修复

```python
if re.match(r"^[0-9]", text):
    text = f"Concept{text}"
```

核心规则：SysML 命名**禁止数字开头**，会语法报错。

修复逻辑：数字开头的名称，统一拼接前缀 `Concept`。示例：`123` → `Concept123`

#### 7\. 函数返回

```python
return text
```

返回最终标准化的大驼峰名称，转换失败则返回空。

### 三、主函数：fallback\_sysml\_from\_text（核心生成逻辑）

**函数作用**：从原始文本提取有效关键词、批量格式化、去重、限制数量，最终组装成完整 SysML 代码。

**入参说明**：

- `source_text`：必填，原始任意文本（中英文、标点混合均可）

- `package_name`：选填，SysML 包名，默认 `GeneratedOntology`

#### 1\. 关键词精准提取（核心正则）

```python
words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,}", source_text)
```

`re.findall`：全局匹配所有符合规则的内容，返回关键词列表，正则分两大规则（或关系）：

- 英文规则 `[A-Za-z][A-Za-z0-9_\-]*`：只匹配**字母开头**，后续可跟字母、数字、下划线、横杠的有效英文词汇，杜绝数字开头英文

- 中文规则 `[\u4e00-\u9fff]{2,}`：匹配连续**2个及以上汉字**，忽略单字中文（避免无效关键词）

提取示例：文本「汽车电池，电机99，car\-model，车」→ 提取结果 `["汽车电池", "电机", "car-model"]`

#### 2\. 初始化变量

```python
candidates: list[str] = []
non_ascii_count = 1
```

- `candidates`：存储最终去重、合法的 SysML 概念名称

- `non_ascii_count`：中文关键词计数器，纯中文无法转驼峰，用来生成 `DomainConcept1/2/3...` 备用名称

#### 3\. 关键词遍历、格式化、去重、限量

```python
for word in words:
    normalized = _to_pascal_case(word)
    if not normalized:
        normalized = f"DomainConcept{non_ascii_count}"
        non_ascii_count += 1
    if normalized not in candidates:
        candidates.append(normalized)
    if len(candidates) >= 8:
        break
```

分步逻辑：

1. 遍历每一个提取的关键词，调用辅助函数格式化

2. 中文关键词格式化后为空，自动生成递增备用名称

3. 自动去重：重复名称不重复添加

4. 数量限制：最多保留**8个概念**，超出直接终止循环，精简代码

#### 4\. 极端场景兜底

```python
if not candidates:
    candidates = ["Concept"]
```

逻辑：如果文本无任何有效关键词（全标点、单字、符号），强制填充默认概念，避免生成空代码、程序报错。

#### 5\. 拼接SysML行代码

```python
definitions = "\n".join(f"  item def {name};" for name in candidates)
```

遍历候选概念，生成标准缩进的 SysML 定义语句，用换行符拼接为完整多行文本。

#### 6\. 组装完整代码并返回

```python
return f"package {package_name} {{\n{definitions}\n}}"
```

拼接 SysML 标准包结构，首尾闭合，返回可直接使用的完整代码字符串。

### 四、完整运行测试示例

#### 示例1：中英文混合文本

```python
import re
# 粘贴全部函数代码
text = "新能源汽车，动力电池，car-controller，battery-12v"
print(fallback_sysml_from_text(text, "AutoDomain"))
```

输出结果：

```python
package AutoDomain {
  item def DomainConcept1;
  item def DomainConcept2;
  item def CarController;
  item def Battery12v;
}
```

#### 示例2：无有效关键词兜底测试

```python
text = "！，。？单字车、人"
```

输出结果：

```python
package GeneratedOntology {
  item def Concept;
}
```

### 五、初学者核心知识点总结

- **正则核心**：findall提取关键词、sub替换脏字符、split切割文本、match匹配开头

- **容错设计**：数字开头修复、中文占位兜底、空文本兜底，保证代码永不报错

- **规范设计**：自动去重、最多8个概念、严格遵循SysML命名规范

- **代码思想**：功能拆分（主函数\+辅助函数），逻辑清晰、便于维护

> （注：部分内容可能由 AI 生成）

---
## 04
```python
_CONTAINS_RE = re.compile(r"(?P<subject>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})\s*(?:包含|包括|contains?|has|具有)\s*(?P<object>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})", re.IGNORECASE)
_ATTRIBUTE_RE = re.compile(r"(?P<subject>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})\s*(?:有|具有|has)\s*(?P<attribute>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})(?:属性|attribute|property)?", re.IGNORECASE)

def fallback_im_from_text(source_text: str, base_iri: str, model_name: str = "GeneratedOntology") -> OntologyModel:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,}", source_text)
    class_names: list[str] = []
    for word in words:
        name = safe_name(word, "pascal")
        if name not in class_names:
            class_names.append(name)
        if len(class_names) >= 16:
            break
    if not class_names:
        class_names = ["Concept"]

    object_properties: list[ObjectProperty] = []
    datatype_properties: list[DatatypeProperty] = []
    for match in _CONTAINS_RE.finditer(source_text):
        subject = safe_name(match.group("subject"), "pascal")
        obj = safe_name(match.group("object"), "pascal")
        if subject not in class_names:
            class_names.append(subject)
        if obj not in class_names:
            class_names.append(obj)
        object_properties.append(ObjectProperty(name=f"has{obj}", domain=subject, range=obj))
    for match in _ATTRIBUTE_RE.finditer(source_text):
        subject = safe_name(match.group("subject"), "pascal")
        attribute = safe_name(match.group("attribute"), "camel")
        if subject not in class_names:
            class_names.append(subject)
        if safe_name(attribute, "pascal") in class_names:
            continue
        datatype_properties.append(DatatypeProperty(name=attribute, domain=subject, range="string"))

    return OntologyModel(
        base_iri=base_iri,
        name=model_name,
        classes=[OntologyClass(name=name) for name in class_names],
        object_properties=object_properties,
        datatype_properties=datatype_properties,
    )
```

### 一、整体功能概述
本段代码由**2条正则常量 + 1个主函数**组成，依赖之前写好的 `safe_name` 命名清洗工具、本体数据模型类（`OntologyModel`/`OntologyClass`/`ObjectProperty`/`DatatypeProperty`）。
整体作用：传入一段中英文混合自然文本、本体唯一标识 `base_iri`，自动解析文本生成标准OWL领域本体模型：
1. 自动提取文本内所有实体名词，生成本体Class（实体概念），最多16个；
2. 通过 `_CONTAINS_RE` 匹配「A包含B」句式，生成**对象属性**（实体和实体之间的关联关系）；
3. 通过 `_ATTRIBUTE_RE` 匹配「A有B属性」句式，生成**数据属性**（实体自身的字符串字段）；
4. 自动补全关系/属性中出现的新实体，自动规避类名与属性名冲突；
5. 所有名称统一标准化为合法标识符，避免建模语法报错。

### 二、两条正则常量逐行解析
#### 2.1 公共匹配规则（两条正则共用）
两条正则捕获实体的片段完全相同：
```regex
[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,}
```
- 英文实体：首字符必须是字母，后续允许字母/数字/下划线/横杠，禁止数字开头；
- 中文实体：匹配连续2个及以上汉字，单字直接忽略，减少无效匹配；
- `|` 代表「或」，英文、中文实体满足其一即可捕获。

配套符号说明：
1. `(?P<name>正则)`：命名捕获组，代码中用 `match.group("分组名")` 直接取出文本，不用数字下标；
2. `\s*`：匹配0个或多个空格，忽略实体与连接词之间的空白；
3. `(?:xxx)`：非捕获分组，仅做匹配、不单独存储分组内容，节省性能；
4. `re.IGNORECASE`：英文关键词大小写不敏感，`Has`/`CONTAINS` 都能匹配。

#### 2.2 _CONTAINS_RE 包含关系正则
```python
_CONTAINS_RE = re.compile(
    r"(?P<subject>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})\s*(?:包含|包括|contains?|has|具有)\s*(?P<object>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})",
    re.IGNORECASE
)
```
分段拆解：
1. `(?P<subject>)`：捕获关系主体（发起实体，如“汽车”）；
2. `(?:包含|包括|contains?|has|具有)`：匹配关系连接词，中英文兼容；
   - `contains?`：`s` 可选，匹配 contain / contains；
3. `(?P<object>)`：捕获被包含的客体实体（如“电池”）。

可匹配句式：
- 汽车包含动力电池
- Vehicle has Motor
- 设备包括传感器

#### 2.3 _ATTRIBUTE_RE 属性抽取正则
```python
_ATTRIBUTE_RE = re.compile(
    r"(?P<subject>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})\s*(?:有|具有|has)\s*(?P<attribute>[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,})(?:属性|attribute|property)?",
    re.IGNORECASE
)
```
分段拆解：
1. `(?P<subject>)`：拥有属性的实体；
2. `(?:有|具有|has)`：属性连接词；
3. `(?P<attribute>)`：捕获属性名称；
4. `(?:属性|attribute|property)?`：末尾后缀可选，`?` 表示有无都能匹配。

可匹配句式：
- 电机有功率
- 电池具有容量属性
- Car has weight attribute

### 三、主函数 fallback_im_from_text 逐段拆解
```python
def fallback_im_from_text(source_text: str, base_iri: str, model_name: str = "GeneratedOntology") -> OntologyModel:
```
参数说明：
- `source_text`：原始待解析自然文本；
- `base_iri`：本体全局唯一资源标识，建模规范必填；
- `model_name`：本体名称，默认 `GeneratedOntology`；
- 返回值：完整本体实例 `OntologyModel`。

#### 3.1 第一步：提取基础实体，初始化类名称列表
```python
words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]*|[\u4e00-\u9fff]{2,}", source_text)
class_names: list[str] = []
for word in words:
    name = safe_name(word, "pascal")
    if name not in class_names:
        class_names.append(name)
    if len(class_names) >= 16:
        break
if not class_names:
    class_names = ["Concept"]
```
1. `re.findall` 一次性提取文本中所有符合规则的中英文实体；
2. 循环遍历每个实体，调用 `safe_name` 转为**大驼峰**合法类名；
3. `if name not in class_names`：自动去重，同一个类名不重复存入；
4. 数量限制：基础实体最多16个，满16个直接跳出循环，防止本体过于庞大；
5. 兜底逻辑：文本无任何有效实体时，默认创建基础类 `Concept`，避免空本体报错。

#### 3.2 初始化两种属性存储容器
```python
object_properties: list[ObjectProperty] = []
datatype_properties: list[DatatypeProperty] = []
```
- `object_properties`：存储实体间关联关系（对象属性）；
- `datatype_properties`：存储实体的字符串字段（数据属性）。

#### 3.3 循环匹配所有包含关系，生成对象属性
```python
for match in _CONTAINS_RE.finditer(source_text):
    subject = safe_name(match.group("subject"), "pascal")
    obj = safe_name(match.group("object"), "pascal")
    if subject not in class_names:
        class_names.append(subject)
    if obj not in class_names:
        class_names.append(obj)
    object_properties.append(ObjectProperty(name=f"has{obj}", domain=subject, range=obj))
```
1. `finditer()`：遍历文本中**所有**匹配「A包含B」的片段；
2. `match.group("subject")` / `match.group("object")` 取出主体、客体，统一转大驼峰；
3. 自动补全实体：如果主体/客体不在初始类列表，直接追加进 `class_names`，保证本体不存在孤立关系；
4. 关系命名规则：固定 `has + 客体类名`；
5. 实例化 `ObjectProperty`：
   - `domain`：定义域（关系发起实体）
   - `range`：值域（关系指向实体）

示例：`汽车包含电池` → `ObjectProperty(name="hasBattery", domain="Car", range="Battery")`

#### 3.4 循环匹配所有属性句式，生成数据属性
```python
for match in _ATTRIBUTE_RE.finditer(source_text):
    subject = safe_name(match.group("subject"), "pascal")
    attribute = safe_name(match.group("attribute"), "camel")
    if subject not in class_names:
        class_names.append(subject)
    if safe_name(attribute, "pascal") in class_names:
        continue
    datatype_properties.append(DatatypeProperty(name=attribute, domain=subject, range="string"))
```
1. 遍历所有「实体-属性」匹配片段；
2. 实体名称用大驼峰，**属性名称强制小驼峰**（变量命名规范）；
3. 实体不在类列表则自动新增；
4. 冲突拦截逻辑：
   将属性名转为大驼峰，如果该名称已经存在于类列表，直接跳过这条属性；
   作用：避免属性名和实体类重名造成本体语义歧义；
5. 实例化 `DatatypeProperty`，值域固定为字符串 `string`。

示例：`汽车有重量` → `DatatypeProperty(name="weight", domain="Car", range="string")`

#### 3.5 组装并返回完整本体模型
```python
return OntologyModel(
    base_iri=base_iri,
    name=model_name,
    classes=[OntologyClass(name=name) for name in class_names],
    object_properties=object_properties,
    datatype_properties=datatype_properties,
)
```
1. 列表推导式：把所有类名字符串批量转为 `OntologyClass` 对象；
2. 将基础IRI、本体名称、全部实体类、对象关系、数据属性全部封装进 `OntologyModel`；
3. 返回完整本体对象，外部可序列化导出OWL、SysML等建模文件。

### 四、代码核心设计特点
1. **命名统一规范**
   全部复用 `safe_name` 工具，自动处理中文、数字开头、特殊符号，保证本体标识符语法合法。
2. **自动补全实体**
   关系、属性里出现的新名词会自动加入类列表，不会出现“有关系但无对应实体”的非法本体。
3. **中英文双兼容**
   正则同时识别中文、英文连接词，适配混合业务文本。
4. **冲突防护**
   检测属性名与实体类重名时自动跳过，规避建模歧义。
5. **多层容错兜底**
   限制基础实体最大数量，无输入实体时默认生成 `Concept`，程序不会崩溃。

### 五、初学者需要掌握的知识点
1. 正则高级语法：命名捕获组 `(?P<name>)`、非捕获组 `(?:)`、`finditer` 遍历全部匹配、忽略大小写标识；
2. 字符串工具复用：`safe_name` 大/小驼峰转换、中文哈希兜底；
3. 列表操作：去重判断、循环提前终止、列表推导式批量创建对象；
4. 本体建模基础概念
   - Class：领域实体概念；
   - ObjectProperty：实体之间的关联；
   - DatatypeProperty：实体绑定的基础文本字段；
   - domain（定义域）、range（值域）约束关系两端；
   - base_iri：本体唯一标识。
---