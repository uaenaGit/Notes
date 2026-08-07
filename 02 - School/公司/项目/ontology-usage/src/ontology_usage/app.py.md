---
created: 2026-07-31T11:00
updated: 2026-08-07T10:32
---
# api_build_kg_streamed 完整分层解析
## 一、函数整体定位
这是一个 FastAPI 后端**SSE 流式接口**，接口作用：分4个阶段实时构建知识图谱，一边计算一边把进度、中间结果推送到前端页面，不用等全部计算完成才一次性返回。
- 协议：`text/event-stream`（SSE 服务端推送长连接）
- 核心载体：内部嵌套异步生成器 `event_stream()`，靠 `yield` 分段输出消息
- 前置校验：必须先存在本体 `ontology`，否则直接返回400错误，不走流式逻辑

## 二、外层主函数 api_build_kg_streamed 逐段解析
```python
async def api_build_kg_streamed(req: BuildKGReq):
    """PR-2：流式 4 步 KG 构建。每次事件形如 ``data: {json}\n\n``。
    文档注释：定义前端会收到的所有消息类型、含义，方便前后端对接
    """
    from fastapi.responses import StreamingResponse
    # 1. 读取全局会话存储里的已构建本体TBox
    ontology = store.get_ontology()
    # 2. 前置校验：没有本体无法生成图谱，直接返回普通JSON错误响应
    if not ontology:
        return JSONResponse(
            {"ok": False, "error": "尚未构建本体，无法生成知识图谱"},
            status_code=400,
        )
```
### 外层逻辑说明
1. `req: BuildKGReq`：FastAPI 请求体，前端POST上传的参数（包含 `topic` 主题标识）
2. `store.get_ontology()`：读取全局会话内存里的模式层本体（TBox，所有概念类型定义）
3. 提前拦截错误：如果本体为空，直接返回普通JSON，不创建流式连接，减少资源浪费
4. `StreamingResponse` 延迟导入：规范写法，减少模块启动加载耗时

### 流式返回构造（最关键一行）
```python
    # 定义内部异步生成器event_stream（仅函数声明，内部代码此时不执行）
    async def event_stream():
        # ... 大量yield业务逻辑，后面单独拆解 ...

    # 重点：event_stream() 仅调用1次，生成异步生成器对象，传给StreamingResponse
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",  # 声明是SSE流式协议
        headers={
            "Cache-Control": "no-cache",        # 浏览器禁止缓存流消息
            "X-Accel-Buffering": "no"           # Nginx反向代理关闭缓冲区，消息实时下发
        },
    )
```
1. `event_stream()`：只执行**一次**，创建生成器实例，不会跑内部 `yield` 代码；
2. `StreamingResponse` 内部的 `async for chunk in self.body_iterator`（你截图里的源码）会**循环反复唤醒这个生成器**，每次取一条 `yield` 的消息发给前端；
3. 两个响应头作用：
   - `no-cache`：浏览器不缓存SSE数据流，实时接收；
   - `X-Accel-Buffering: no`：解决Nginx缓冲堆积问题，否则前端要等全部计算完才一次性收到所有消息，失去流式实时效果。

## 三、内部异步生成器 event_stream 完整流程拆解
作用：封装4阶段图谱构建逻辑，每完成一步通过 `yield` 输出一条SSE标准格式消息，**函数暂停保存上下文，等待框架下一次唤醒继续执行**。
SSE固定格式：`b"data: JSON字符串\n\n"`，`\n\n` 是浏览器识别单条消息结束的标记。

### 整体结构：try-except 全局捕获异常
- `try`：正常4阶段完整执行，依次推送 start → step1 → kg_raw → step2 → mapping ... → done
- `except`：任意阶段报错，打印完整异常堆栈日志，向前端推送 `type:error` 消息，流正常关闭，不会直接断连

### 步骤1：推送流启动信号 start
```python
yield b"data: " + json.dumps(
    {"type": "start", "topic": req.topic, "stages": kg_service.KG_STAGE_LABELS},
    ensure_ascii=False,
).encode() + b"\n\n"
```
- 消息类型 `start`：通知前端流式任务正式启动；
- 携带数据：当前任务主题 `topic`、4个阶段的中文名称列表 `stages`，前端初始化进度条UI；
- `ensure_ascii=False`：JSON内中文不转义为 `\uXXXX`，前端直接展示中文。

### Stage 1：原始知识抽取 raw
```python
# 第一条消息：通知前端进入第1阶段，更新进度条
yield b"data: " + json.dumps(
    {"type": "step", "idx": 1, "label": kg_service.KG_STAGE_LABELS[0], "total": 4},
    ensure_ascii=False,
).encode() + b"\n\n"
# 执行业务：原始文本抽取无约束的原始知识图谱
raw_kg = await kg_service.kg_step_raw(req.topic)
# 第二条消息：把抽取完成的原始图谱推送给前端渲染
yield b"data: " + json.dumps(
    {"type": "kg_raw", "data": raw_kg},
    ensure_ascii=False,
).encode() + b"\n\n"
```
执行顺序：
1. `yield step` → 前端进度条走到1/4，显示阶段名称；
2. `await kg_step_raw` 阻塞执行耗时抽取逻辑；
3. 计算完成，`yield kg_raw`，下发原始图谱数据，函数暂停等待下一次唤醒。

### Stage 2：本体映射对齐 mapping
逻辑完全复用Stage1模板：
1. `yield step`：通知前端切换到第2阶段；
2. `await kg_step_mapping(raw_kg, ontology)`：用预先定义的本体类型，把原始实体做类型对齐、建立映射关系；
3. `yield mapping`：下发对齐规则、映射对照表给前端。

### Stage 3：生成规范化本体图谱 onto（核心存储步骤）
```python
yield b"data: " + json.dumps(
    {"type": "step", "idx": 3, "label": kg_service.KG_STAGE_LABELS[2], "total": 4},
    ensure_ascii=False,
).encode() + b"\n\n"
# 基于原始图谱+映射规则，生成符合TBox约束的标准本体知识图谱
onto_kg = await kg_service.kg_step_onto(raw_kg, mapping, ontology)
# 存入全局会话store，其他接口（build-abox等）可以读取这份图谱数据
store.set_raw_kg(raw_kg)
store.set_kg(onto_kg)
# 推送标准化图谱 + 映射过程警告信息
yield b"data: " + json.dumps(
    {"type": "kg_onto", "data": onto_kg, "warnings": _kg_mapping_warnings(onto_kg)},
    ensure_ascii=False,
).encode() + b"\n\n"
```
独有逻辑：
1. 执行完标准化图谱后，调用 `store.set_raw_kg / set_kg` 存入会话内存；
2. 消息额外携带 `warnings`：模型映射时产生的提示、冲突警告，前端可以弹窗展示。

### Stage 4：新旧图谱对比校验 compare
```python
yield b"data: " + json.dumps(
    {"type": "step", "idx": 4, "label": kg_service.KG_STAGE_LABELS[3], "total": 4},
    ensure_ascii=False,
).encode() + b"\n\n"
# 同步对比函数，无await
compare = kg_service.kg_step_compare(raw_kg, onto_kg, ontology)
yield b"data: " + json.dumps(
    {"type": "compare", "data": compare},
    ensure_ascii=False,
).encode() + b"\n\n"
# 全部4阶段执行完毕，推送完成信号
yield b"data: " + json.dumps({"type": "done"}, ensure_ascii=False).encode() + b"\n\n"
```
1. `kg_step_compare` 是同步函数，不需要 `await`；
2. `type:done`：前端收到后，判定整个流式任务正常结束，关闭EventSource长连接。

### except 异常捕获分支
```python
except Exception as e:
    logging.exception("[kg-streamed] failed at topic=%r", req.topic)
    yield b"data: " + json.dumps(
        {"type": "error", "error": str(e)},
        ensure_ascii=False,
    ).encode() + b"\n\n"
```
1. `logging.exception`：自动打印完整异常堆栈（报错行、错误信息），后端日志排查；
2. `yield type:error`：向前端推送报错文本，前端弹窗提示用户，不会直接断开页面。

## 四、完整消息推送时序（前端接收顺序）
1. `{"type":"start"}` → 任务初始化
2. `{"type":"step",idx:1}` → 进度1/4
3. `{"type":"kg_raw"}` → 原始图谱结果
4. `{"type":"step",idx:2}` → 进度2/4
5. `{"type":"mapping"}` → 映射规则
6. `{"type":"step",idx:3}` → 进度3/4
7. `{"type":"kg_onto"}` → 标准本体图谱+警告，后端存入store
8. `{"type":"step",idx:4}` → 进度4/4
9. `{"type":"compare"}` → 新旧图谱对比报告
10. `{"type":"done"}` → 任务正常结束，关闭流
> 任意步骤抛出异常：直接跳到第11步，推送 `{"type":"error"}`，流终止。

## 五、核心关键知识点总结（结合你之前的疑问）
1. `event_stream()` 仅调用1次，只生成生成器对象；StreamingResponse内部 `async for` 循环反复唤醒同一个生成器，多次产出 `yield` 消息，**不会重复创建函数上下文**；
2. `yield` 作用：吐出一条SSE消息，函数暂停，保留所有局部变量（raw_kg/mapping/onto_kg），下次唤醒从暂停位置继续执行；
3. 区分两种返回逻辑：
   - 无本体：直接 `return JSONResponse`，普通一次性接口，无长连接；
   - 有本体：`return StreamingResponse`，SSE长连接流式分段推送；
4. 会话存储 `store`：第三阶段生成标准图谱后存入内存，其他接口可以复用本次构建的图谱数据，不用重复计算。

## 六、前端对接极简伪代码（辅助理解代码用途）
```javascript
// 前端SSE接收逻辑
const sse = new EventSource("/api/kg/build-streamed");
sse.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch(msg.type) {
    case "start": 初始化4步进度条; break;
    case "step": 更新页面进度文字与进度条; break;
    case "kg_raw": 渲染原始知识图谱画布; break;
    case "mapping": 展示实体类型映射对照表; break;
    case "kg_onto": 渲染标准化本体图谱，展示警告弹窗; break;
    case "compare": 渲染新旧图谱差异对比报告; break;
    case "done": sse.close(); alert("图谱构建完成"); break;
    case "error": sse.close(); alert("构建失败：" + msg.error); break;
  }
}
```