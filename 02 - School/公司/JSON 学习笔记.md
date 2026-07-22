---
created: 2026-07-21T17:36
updated: 2026-07-21T17:36
---
# JSON 完整学习笔记（面向开发新手，兼顾你 MBSE / Python 项目场景）
## 一、JSON 基础概念
### 1. 全称
**JSON = JavaScript Object Notation**
中文：JavaScript 对象表示法。
> 注意：名字带 JavaScript，但**和JS语言解绑**，是独立通用数据格式，Python、Java、C++、Go全部原生支持。

### 2. 核心定位
一种**纯文本、结构化的数据存储/交换格式**，后缀名：`.json`。
用途：
1. 程序之间传递数据（接口API返回内容几乎全是JSON）
2. 保存程序内存里的对象快照（就像你代码里 `bridge-im.json` 存储BridgeIM模型）
3. 简易配置文件

### 3. 关键特性
1. **纯文本**：记事本、VSCode可以直接打开编辑；不是二进制文件。
2. **人类可读**，结构直观。
3. **语言无关**，跨语言互通。
4. 语法严格，**不能随便乱写注释**（标准JSON不支持`//`单行注释）。
5. 体积轻量，互联网行业默认交换标准。

> ❌ 误区：JSON不是编程语言，只是「描述数据的文本规范」。

---

## 二、JSON 仅有的6种基础数据类型
JSON 一共只有6种合法类型，没有更多：
1. **对象 Object** `{ ... }` 键值对集合（最常用）
2. **数组 Array** `[ ... ]` 有序列表
3. **字符串 String** 必须用**双引号** `"text"`（单引号非法！）
4. **数字 Number** 整数、小数，不加引号
5. **布尔 Boolean** `true` / `false`（全部小写，不能True/TRUE）
6. **空值 Null** `null`（全部小写）

⚠️ 重要语法红线：
- 字符串**只能双引号 `"`**，`'abc'` 标准JSON不合法；
- 键名（key）**必须带双引号**；
- 末尾不能多余逗号 `,`；
- 没有日期类型、没有二进制、没有注释。

## 三、语法范例
### 1）Object 对象 `{}`
键值对格式 ` "key": value `
```json
{
  "name": "动力总成模块",
  "id": "Block_001",
  "maxPower": 250
}
```

### 2）Array 数组 `[]`
一组有序数据，元素可以是任意类型
```json
["输入端口", "输出端口", "冷却端口"]
```

### 3）嵌套（最常见！对应你的IM模型）
对象套数组、数组套对象，表达层级结构
```json
{
  "type": "Block",
  "name": "发动机",
  "ports": [
    {
      "portName": "燃油入口",
      "direction": "in"
    },
    {
      "portName": "动力输出轴",
      "direction": "out"
    }
  ]
}
```

## 四、合法 VS 非法写法（高频踩坑清单）
✅ 合法
```json
{
  "enabled": true,
  "count": 100,
  "desc": null
}
```
❌ 非法（新手常犯）
```json
{
  name: "发动机",        // key没有双引号
  'enabled': true,       // 使用单引号
  count: 100,            // 数字没问题，但上面key违规
  list: [1,2,3,]         // 数组末尾多余逗号
}
```

## 五、JSON 和 Python 的对应关系（重点！适配你代码）
| JSON类型 | Python类型 |
|---------|-----------|
| `{}` 对象 | `dict` 字典 |
| `[]` 数组 | `list` 列表 |
| `"字符串"` | `str` |
| `123 / 12.5` | `int` / `float` |
| `true` | `True` |
| `false` | `False` |
| `null` | `None` |

### 你代码里核心操作回顾
```python
# Pydantic模型 → JSON字符串
json_text = model.model_dump_json(indent=2)
# 写入文件
im_path.write_text(json_text, encoding="utf-8")
```
等价流程：内存里的Python对象 → 转换成标准JSON文本 → 保存为 `.bridge-im.json` 文件。

反向读取：从文件加载JSON，还原成Python对象
```python
import json
text = Path("xxx.bridge-im.json").read_text(encoding="utf-8")
data = json.loads(text)   # json文本 → Python dict
# 再可以用 BridgeIM.model_validate(data) 还原模型
```

## 六、两个核心术语：序列化 & 反序列化
1. **序列化（Serialize）**
内存对象 → JSON文本
`model.model_dump_json()` / `json.dumps()`
> 用途：存文件、网络传输

2. **反序列化（Deserialize）**
JSON文本 → 内存对象
`json.loads()` / `BridgeIM.model_validate()`

形象理解：
序列化 = 把积木拍照保存成图纸（JSON文件）；
反序列化 = 根据图纸重新搭出积木。
你的 `bridge-im.json` 就是IM模型的“图纸”。

## 七、JSON 和相似格式对比
### 1. JSON vs YAML
- JSON：严格标准，所有语言原生支持；不支持注释；适合机器读写（API、模型快照）
- YAML：可读性更强，支持注释；多用于配置文件

### 2. JSON vs XML
XML老旧、标签繁琐；JSON轻量化，现在接口几乎淘汰XML。

### 3. JSON vs .sysml / .ttl
结合你的项目：
- `.bridge-im.json`：结构化模型快照，方便程序读写
- `.sysml`：面向人的领域建模代码
- `.ttl`：语义网RDF本体格式，用于知识图谱推理

## 八、日常开发实用技巧
1. **格式化美化JSON**
压缩成一行很难看，`indent=2` 输出带换行缩进（你代码里就是这么写的）。
2. **校验JSON语法**
在线工具：JSONLint，粘贴即可检查语法错误。
3. **不要手动大规模编辑JSON**
复杂模型JSON手动改错逗号、引号非常容易崩溃，优先用程序生成。
4. 标准JSON无注释！
如果你看到带`//`注释的json，属于**JSON5扩展格式**，标准库读取会报错。

## 九、结合你的业务场景总结
在你这套 SysML → Bridge IM → OWL 链路中：
`xxx.bridge-im.json` = **中间模型持久化载体**
1. LLM生成内存中的BridgeIM对象（Pydantic）
2. 序列化为JSON存入文件
3. 作用：
   - 调试：直接打开查看模型元素是否正确
   - 缓存：无需重复调用LLM
   - 跨工具交换：Python、Java桥程序都能读取这份模型数据

## 十、极简记忆口诀
JSON是带严格语法的文本；
只有6种数据类型；
键名、字符串必须双引号；
用来存对象、网络传数据；
Python字典和JSON对象可以互相转换；
序列化：对象→文本；反序列化：文本→对象。

如果你需要，我可以再加一节：Python 原生 `json` 库完整示例 + Pydantic 模型与JSON互转代码模板，直接复制就能用。