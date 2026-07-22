---
created: 2026-03-10T20:40
updated: 2026-03-10T20:41
---
这是一份为您精心整理的 **C++ `std::queue` 全方位方法详解**。

`std::queue` 是一个**容器适配器**（Container Adapter），它基于**先进先出**（FIFO, First-In-First-Out）的原则实现。它的核心特性是：**只能在尾部插入，在头部删除**。

如果你需要处理“排队”、BFS（广度优先搜索）、消息缓冲、任务队列等场景，`queue` 是首选。

---

# 📚 C++ `std::queue` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <queue>      // queue 定义在此
#include <deque>      // 默认底层容器
#include <list>       // 可选底层容器

using namespace std;
```

> **核心特性速览**：
> 1. **FIFO 原则**：**先进先出**。最早进入的元素最早被取出（像超市排队结账）。
> 2. **两端操作**：只能从**队尾**（Back）进，从**队头**（Front）出。
> 3. **受限访问**：**只能**访问队头（`front()`）和队尾（`back()`），**不能**随机访问中间元素，**不能**遍历。
> 4. **复杂度**：插入 `push` 和删除 `pop` 均为 $O(1)$，访问两端为 $O(1)$。
> 5. **底层容器**：默认使用 `std::deque`（双端队列），也可指定 `std::list`。**不支持 `std::vector`**（因为 vector 头部删除效率低）。

---

## 1️⃣ 构造与模板定义 (Construction & Template)
`queue` 的模板定义包含两个参数。

| 方法/定义 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`template<...>`** | `T`: 元素类型`Container`: 底层容器 (默认 `deque<T>`) | - | 定义类型。⚠️ **注意**：底层容器必须支持 `push_back`, `pop_front`, `front`, `back` 操作。 |
| **`queue()`** | 无 | - | 默认构造，生成空队列。 |
| **`queue(const Container& c)`** | `c`: 初始容器 | - | 使用现有容器初始化队列。 |
| **`queue(InputIt first, InputIt last)`** | `first`, `last`: 迭代器范围 | - | 范围构造，从 `[first, last)` 初始化。 |

### 💡 核心口诀：进出方向
- **入队**：`push` / `emplace` $\rightarrow$ **队尾** (Back)
- **出队**：`pop` $\rightarrow$ **队头** (Front)
- **查看**：`front` (队头), `back` (队尾)

### 💻 代码示例
```cpp
int main() {
    // 1. 默认构造 (底层 deque)
    queue<int> q1; 
    
    // 2. 使用 list 作为底层容器 (适合频繁内存分配场景，但通常 deque 更快)
    queue<int, list<int>> q2;

    // 3. 范围构造
    vector<int> v = {1, 2, 3};
    queue<int> q3(v.begin(), v.end()); 
    // q3 中顺序: 1(头) -> 2 -> 3(尾)

    return 0;
}
```

---

## 2️⃣ 容量与状态 (Capacity & State)
与 `priority_queue` 类似，状态查询非常有限。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`size()`** | 无 | `size_t` | 返回元素个数。 |
| **`empty()`** | 无 | `bool` | 若为空返回 `true`。 |

> ⚠️ **注意**：没有 `capacity()` 方法。

### 💻 代码示例
```cpp
int main() {
    queue<string> q;
    cout << "Empty? " << q.empty() << endl; // 1
    
    q.push("Hello");
    cout << "Size: " << q.size() << endl;   // 1
    cout << "Empty? " << q.empty() << endl; // 0
    
    return 0;
}
```

---

## 3️⃣ 元素操作 (Element Operations)
核心操作围绕“队头”和“队尾”进行。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`front()`** | 无 | `T&` / `const T&` | **返回队头元素引用**（最老的元素）。⚠️ **不删除**。若队列为空调用，行为未定义。 |
| **`back()`** | 无 | `T&` / `const T&` | **返回队尾元素引用**（最新的元素）。⚠️ **不删除**。 |
| **`push(const T& val)`** | `val`: 要插入的值 | `void` | 在**队尾**插入元素 ($O(1)$)。 |
| **`emplace(args...)`** | `args`: 构造参数 (C++11) | `void` | 在**队尾**原地构造元素并插入。避免拷贝开销。 |
| **`pop()`** | 无 | `void` | **删除队头元素**。⚠️ **无返回值**。若需获取值，必须先 `front()` 再 `pop()`。 |
| **`swap(queue& other)`** | `other`: 另一个队列 | `void` | 交换两个队列内容 ($O(1)$)。 |

### 💡 常用模式：标准出队流程
```cpp
if (!q.empty()) {
    int val = q.front(); // 1. 获取队头值
    q.pop();             // 2. 移除队头
    // 使用 val...
}
```

### 💻 代码示例：模拟排队
```cpp
int main() {
    queue<string> customers;
    
    // 1. 入队 (Push to Back)
    customers.push("Alice");
    customers.push("Bob");
    customers.emplace("Charlie"); // 原地构造
    
    cout << "Queue Front (Next): " << customers.front() << endl; // Alice
    cout << "Queue Back (Last): " << customers.back() << endl;   // Charlie
    cout << "Current Size: " << customers.size() << endl;        // 3
    
    // 2. 出队 (Pop from Front)
    cout << "\nServing customers:" << endl;
    while (!customers.empty()) {
        cout << "Now serving: " << customers.front() << endl;
        customers.pop(); // 移除刚才服务的人
    }
    
    cout << "Final Size: " << customers.size() << endl; // 0
    
    return 0;
}
```
**输出结果**：
```text
Queue Front (Next): Alice
Queue Back (Last): Charlie
Current Size: 3

Serving customers:
Now serving: Alice
Now serving: Bob
Now serving: Charlie
Final Size: 0
```

---

## 4️⃣ 底层容器与迭代器 (Underlying Container & Iterators)

| 特性 | 说明 |
| :--- | :--- |
| **底层容器** | 默认为 `std::deque`。也可指定 `std::list`。❌ **不能使用 `std::vector`**，因为 `vector` 的 `pop_front` 操作是 $O(N)$ 的，不符合队列 $O(1)$ 的要求。 |
| **迭代器** | **❌ 不支持迭代器！** `queue` 没有 `begin()`, `end()` 方法。 |
| **遍历** | **无法直接遍历**。若需遍历，必须不断 `pop()` 直到空（会破坏队列），或者拷贝一份出来再 pop。 |

### 💻 代码示例：如何“遍历”
```cpp
int main() {
    queue<int> q{10, 20, 30};
    
    // 错误写法：for (auto x : q) ... ❌ 编译错误
    
    // 正确写法：逐个弹出 (销毁性读取)
    cout << "Elements: ";
    while (!q.empty()) {
        cout << q.front() << " ";
        q.pop();
    }
    // 此时 q 已空
    cout << "\nIs empty now? " << q.empty() << endl; // 1
    
    return 0;
}
```

---

## 5️⃣ 常见应用场景

### 场景 A：广度优先搜索 (BFS)
这是 `queue` 最经典的应用。在图或树的遍历中，需要按“层”处理节点，先访问的节点的邻居也要先访问。
```cpp
// 伪代码示例
queue<int> q;
q.push(start_node);
visited[start_node] = true;

while (!q.empty()) {
    int u = q.front();
    q.pop();
    
    for (int v : neighbors(u)) {
        if (!visited[v]) {
            visited[v] = true;
            q.push(v); // 新发现的节点排到队尾
        }
    }
}
```

### 场景 B：消息缓冲区 / 任务调度
生产者 - 消费者模型中，生产者将任务 `push` 到队列尾部，消费者从队列头部 `pop` 任务执行，保证任务按顺序处理。

### 场景 C：滑动窗口 (基础版)
虽然 `deque` 更适合复杂的滑动窗口（如求最大值），但简单的固定长度 FIFO 缓冲可以用 `queue` 实现。

---

## 6️⃣ `queue` vs `deque` vs `vector` 终极对比

| 特性 | `std::queue` (适配器) | `std::deque` (容器) | `std::vector` (容器) |
| :--- | :--- | :--- | :--- |
| **访问原则** | **FIFO** (先进先出) | 双端访问 | 随机访问 |
| **访问头部** | ✅ `front()` $O(1)$ | ✅ `front()` $O(1)$ | ❌ $O(N)$ (需移动元素) |
| **访问尾部** | ✅ `back()` $O(1)$ | ✅ `back()` $O(1)$ | ✅ `back()` $O(1)$ |
| **头部删除** | ✅ `pop()` $O(1)$ | ✅ `pop_front()` $O(1)$ | ❌ $O(N)$ |
| **尾部插入** | ✅ `push()` $O(1)$ | ✅ `push_back()` $O(1)$ | ✅ `push_back()` $O(1)$* |
| **随机访问** | ❌ **不支持** (`[]`, `at`) | ✅ 支持 (`[]`, `at`) $O(1)$ | ✅ 支持 (`[]`, `at`) $O(1)$ |
| **迭代器** | ❌ **不支持** | ✅ 支持 | ✅ 支持 |
| **内存连续性** | 取决于底层 (deque 不连续) | 分段连续 | **完全连续** (缓存友好) |
| **适用场景** | 严格 FIFO，无需遍历 | 需要两头操作 + 随机访问 | 需要随机访问，主要尾部操作 |

*\*注：vector 尾部插入均摊 $O(1)$，但在扩容时会有 $O(N)$ 开销。*

---

## 7️⃣ 进阶：`queue` 能自定义排序吗？
**不能。**
`std::queue` 严格遵循 **FIFO** 顺序，你无法改变元素的出队顺序（除非你自己维护逻辑）。
- 如果你需要根据优先级出队（比如紧急任务插队），请使用 **`std::priority_queue`**。
- 如果你需要双端操作且能随机访问，请直接使用 **`std::deque`**。

---

### 💡 核心总结
1. **严格 FIFO**：记住 `queue` 就是排队，后来者居后，先来者先走。
2. **只通两头**：只能摸到头（`front`）和尾（`back`），中间是黑盒。
3. **无迭代器**：不要试图遍历它！如果需要遍历，说明你可能选错了容器（考虑 `vector` 或 `deque`）。
4. **底层选择**：默认 `deque` 是最优解，千万别强行用 `vector` 做底层。
5. **性能优势**：在严格的 FIFO 场景下，它的语义最清晰，且头部删除操作比 `vector` 快得多。

**一句话口诀**：
> “先进先出排队行，头删尾插 O(1) 灵；
> 默认 deque 莫用 vec，无迭代器莫强巡；
> BFS 算法它是宝，优先级高请换堆。”