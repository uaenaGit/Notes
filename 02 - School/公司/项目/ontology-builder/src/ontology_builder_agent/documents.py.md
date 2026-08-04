---
created: 2026-08-04T10:42
updated: 2026-08-04T11:07
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
