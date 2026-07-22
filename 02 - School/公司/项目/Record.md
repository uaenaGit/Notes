---
created: 2026-07-21T14:17
updated: 2026-07-22T10:00
---
# 一、给定pdf生成本体demo（mode=im-bridge）
## 1、不能直接使用原始PDF文件作为 ontology-builder 的输入，因为原始Pdf字体编码导致乱码、公式和表格结构丢失
注意：就算是原生 PDF，也会存在页眉页脚、图表、公式无法正常提取的问题，先转成 md 人工清洗再生成本体，是更稳妥的工程方案；

## 2、Invalid JSON: EOF while parsing a value at line 1 column 0 \[type=json_invalid, input_value='', input_type=str]
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721142003764.png)

也就是说解析器收到的只有空白字符，并不是“返回了一段格式错误的JSON”。
原因基本可以确定为：
1. V4-Pro仍然进行了深度思考；
2. `BridgeIMExtractor` 默认只允许4096个输出Token；
3. 对整个 `reviewed.md` 生成Bridge IM JSON时，推理消耗了输出预算；
4. 模型尚未输出最终JSON，请求就结束了；
5. 项目没有检查 `finish_reason` 和 `reasoning_content`，最终只显示JSON解析错误。
修改：
```python
class BridgeIMExtractor:
	extract()->BridgeIMDraft:
	response = await service.chat(
		messages=[
			{"role": "system", "content": BRIDGE_IM_EXTRACTION_SYSTEM_PROMPT},
			{"role": "user", "content": prompt},
		],
		temperature=0.1,
		max_tokens=16384,
		enable_thinking=False,
	)
	if response.error:
		raise RuntimeError(
			f"DeepSeek request failed: {response.error}"
		)
	if not (response.content or "").strip():
		raise RuntimeError(
			"DeepSeek returned empty final content. "
			f"finish_reason={response.finish_reason}, "
			f"reason_length={len(response.reasoning_content or '')}, "
			f"usage={response.usage}"
		)
```
将`max_tokens`改成`16384`，`enable_thingking`改为`False`(测试使用，真实场景还是`True`)，并加入错误日志。
修改后结果：
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721143929223.png)


## 3、RuntimeError: DeepSeek request failed: LLM Error:
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721142636812.png)
修改`timeout=600.0`，延长超时时间
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721142929029.png)
结果：
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721143838514.png)
生成的sysml在语法和结构转换上没有明显错误，重视反映了JSON，但是LLM生成的JSON不够完整。
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260721154035082.png)
## 4、修改`prompts`：BRIDGE_IM_EXTRACTION_SYSTEM_PROMPT
```
8. 本任务处理液体火箭发动机领域，RocketEngine 下应建立 LiquidRocketEngine，
   来源中的具体发动机型号应作为 LiquidRocketEngine 个体。
9. 对来源中每一个具体发动机型号、推进剂、循环方式、供应方式、用途和公式创建 individual。
   不要只创建个体名称，来源明确提供的事实必须写入 assertions。
10. individuals 中每项的结构为：
{
  "name": "rD170",
  "type": "LiquidRocketEngine",
  "anonymous": false,
  "assertions": [
    {
      "kind": "object",
      "property": "usesOxidizer",
      "value": "liquidOxygen"
    },
    {
      "kind": "data",
      "property": "vacuumThrustN",
      "value": "8060000",
      "datatype": "xsd:decimal"
    }
  ]
}
11. 对象之间的关系使用 kind="object"：
    - 发动机使用氧化剂：usesOxidizer
    - 发动机使用燃料：usesFuel
    - 发动机采用动力循环：hasCycle
    - 发动机采用供应方式：hasSupplySystemType
    - 发动机具有任务用途：hasMissionRole
12. 数值使用 kind="data"：
    - 真空推力统一换算为 N，属性名 vacuumThrustN
    - 真空比冲按来源单位 m/s，属性名 vacuumSpecificImpulseMPerS
    - 燃烧室压力使用 MPa，属性名 chamberPressureMPa
    - 密度使用 kg/m³，属性名 densityKgPerM3
    - 温度使用 K
13. 表格中的“—”、空白或来源未给出的数值必须省略，不得推测为0。
14. CycleType 只包含燃气发生器循环、补燃循环、膨胀循环等动力循环。
    挤压式和泵压式属于 SupplySystemType，不属于 CycleType。
15. MissionRole 表示一级发动机、二级发动机、上面级发动机、姿控发动机等用途。
    SSME 是具体发动机，不得建成 MissionRole。
16. 除非来源明确要求，关系基数不要设置为恰好1。
    hasCycle 使用 0..1，hasMissionRole、usesOxidizer、usesFuel 使用 0..*。
17. object assertion 的 value 必须对应已存在的 individual。
    data assertion 的 property 必须对应已存在的 data feature。
18. 公式个体必须包含 latexExpression、formulaNumber 和 sourcePage 断言。
19. 只提取来源明确陈述的事实，不得根据常识补充来源没有给出的性能参数。
```

结果：
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260722095636949.png)
修改提示词后，模型开始为大量发动机生成 `assertions`，输出从原来的“70个空个体”变成“70个带多个事实的个体”，所以16384 Token仍然可能不足。
## 5、Invalid JSON: EOF while parsing a string at line 231 column 45

提高输出上限`max_tokens=32768`，`timeout=900.0`，添加报错打印和完善提示词
