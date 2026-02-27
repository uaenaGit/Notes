---
created: 2026-02-25T23:42
updated: 2026-02-27T12:37
---
这是一份为您精心整理的 **C++ `std::priority_queue` 全方位方法详解**。

`std::priority_queue` 是一个**容器适配器**（Container Adapter），它基于**堆**（Heap）数据结构实现。它的核心特性是：**只能访问最大**（或最小）。

如果你需要处理“Top K”问题、任务调度、Dijkstra 算法等场景，`priority_queue` 是首选。

---

# 📚 C++ `std::priority_queue` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <queue>      // priority_queue 定义在此
#include <vector>     // 默认底层容器
#include <functional> // greater, less 定义在此

using namespace std;
```

> **核心特性速览**：
> 1. **大顶堆/小顶堆**：默认是**大顶堆**（最大值在顶），可配置为小顶堆。
> 2. **受限访问**：**只能**访问堆顶元素（`top()`），**不能**遍历，**不能**随机访问中间元素。
> 3. **自动排序**：插入元素后自动调整堆结构，保持堆性质。
> 4. **复杂度**：插入 `push` 和删除 `pop` 均为 $O(\log N)$，访问堆顶 `top` 为 $O(1)$。
> 5. **底层容器**：默认使用 `std::vector`，也可指定 `std::deque`。

---

## 1️⃣ 构造与模板定义 (Construction & Template)
`priority_queue` 的模板定义包含三个参数，理解它们对自定义排序至关重要。

| 方法/定义 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`template<...>`** | `T`: 元素类型`Container`: 底层容器 (默认 `vector<T>`)`Compare`: 比较函数对象 (默认 `less<T>`) | - | 定义类型。⚠️ **注意**：`less<T>` 对应**大顶堆**（因为 `a < b` 为真时，b 上浮），`greater<T>` 对应**小顶堆**。 |
| **`priority_queue()`** | 无 | - | 默认构造，生成空优先队列（大顶堆）。 |
| **`priority_queue(Compare comp)`** | `comp`: 比较函数对象 | - | 使用自定义比较器构造。 |
| **`priority_queue(Compare comp, const Container& c)`** | `comp`: 比较器`c`: 初始容器 | - | 使用现有容器初始化并构建堆。 |
| **`priority_queue(InputIt first, InputIt last)`** | `first`, `last`: 迭代器范围 | - | 范围构造，从 `[first, last)` 初始化并建堆 ($O(N)$)。 |

### 💡 核心口诀：比较器与堆类型的关系
- **`less<T>`** (默认) $\rightarrow$ **大顶堆** (最大值在 top)。逻辑：小的沉下去，大的浮上来。
- **`greater<T>`** $\rightarrow$ **小顶堆** (最小值在 top)。逻辑：大的沉下去，小的浮上来。

### 💻 代码示例
```cpp
int main() {
    // 1. 默认构造 (大顶堆)
    priority_queue<int> max_pq; 
    max_pq.push(10); max_pq.push(30); max_pq.push(20);
    cout << "Max Top: " << max_pq.top() << endl; // 30

    // 2. 小顶堆 (使用 greater)
    priority_queue<int, vector<int>, greater<int>> min_pq;
    min_pq.push(10); min_pq.push(30); min_pq.push(20);
    cout << "Min Top: " << min_pq.top() << endl; // 10

    // 3. 范围构造
    vector<int> v = {5, 1, 9};
    priority_queue<int> pq(v.begin(), v.end());

    return 0;
}
```

---

## 2️⃣ 容量与状态 (Capacity & State)
优先队列提供的状态查询非常有限，因为它不支持遍历。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`size()`** | 无 | `size_t` | 返回元素个数。 |
| **`empty()`** | 无 | `bool` | 若为空返回 `true`。 |

> ⚠️ **注意**：没有 `capacity()` 方法，因为底层容器的容量管理被封装了。

### 💻 代码示例
```cpp
int main() {
    priority_queue<int> pq;
    cout << "Empty? " << pq.empty() << endl; // 1
    
    pq.push(100);
    cout << "Size: " << pq.size() << endl;   // 1
    cout << "Empty? " << pq.empty() << endl; // 0
    
    return 0;
}
```

---

## 3️⃣ 元素操作 (Element Operations)
核心操作只有三个：看堆顶、推入、弹出。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`top()`** | 无 | `const T&` | **返回堆顶元素引用**（最大或最小，取决于比较器）。⚠️ **不删除**元素。若队列为空调用此函数，行为未定义。 |
| **`push(const T& val)`** | `val`: 要插入的值 | `void` | 插入元素，并自动调整堆结构 ($O(\log N)$)。 |
| **`emplace(args...)`** | `args`: 构造参数 (C++11) | `void` | **原地构造**元素并插入。避免拷贝开销，效率更高。 |
| **`pop()`** | 无 | `void` | **删除堆顶元素**，并自动调整堆结构 ($O(\log N)$)。⚠️ **无返回值**。若需获取值，必须先 `top()` 再 `pop()`。 |
| **`swap(priority_queue& other)`** | `other`: 另一个优先队列 | `void` | 交换两个优先队列内容 ($O(1)$)。 |

### 💡 常用模式：获取并删除堆顶
```cpp
if (!pq.empty()) {
    int val = pq.top(); // 1. 获取值
    pq.pop();           // 2. 删除
    // 使用 val...
}
```

### 💻 代码示例
```cpp
int main() {
    priority_queue<int> pq;
    
    // 1. 插入
    pq.push(10);
    pq.push(50);
    pq.emplace(30); // 原地构造
    
    // 2. 访问堆顶
    cout << "Top: " << pq.top() << endl; // 50
    
    // 3. 弹出堆顶
    pq.pop(); // 50 被移除
    cout << "New Top: " << pq.top() << endl; // 30
    
    // 4. 循环弹出所有元素 (排序输出)
    while (!pq.empty()) {
        cout << pq.top() << " "; // 30 10 (降序)
        pq.pop();
    }
    cout << endl;
    
    return 0;
}
```

---

## 4️⃣ 自定义比较器 (Custom Comparator)
这是 `priority_queue` 最强大的功能，用于处理自定义结构体或复杂的排序逻辑（如“分数高的优先，分数相同则时间早的优先”）。

### 方法 A：重载运算符 (适用于简单结构体)
```cpp
struct Task {
    int id;
    int priority;
    
    // 注意：priority_queue 默认是 less，即 a < b 时 b 上浮（大顶堆）。
    // 若要实现“优先级数字越大越优先”，直接比较 priority 即可。
    bool operator<(const Task& other) const {
        return priority < other.priority; // 大顶堆：priority 大的在顶
    }
};

int main() {
    priority_queue<Task> pq;
    pq.push({1, 10});
    pq.push({2, 50});
    pq.push({3, 30});
    
    cout << "Top Task ID: " << pq.top().id << ", Priority: " << pq.top().priority << endl; 
    // 输出: ID 2, Priority 50
    return 0;
}
```

### 方法 B：使用仿函数 (更灵活，推荐)
如果需要**小顶堆**或者**多字段复杂排序**，使用仿函数最清晰。

```cpp
struct Task {
    int id;
    int priority;
    int time; // 时间戳，越小越早
};

// 仿函数：定义“谁应该排在后面”（即谁更小）
// 对于大顶堆，返回 true 表示 lhs 应该比 rhs 低优先级（沉下去）
struct TaskCompare {
    bool operator()(const Task& lhs, const Task& rhs) const {
        if (lhs.priority != rhs.priority) {
            return lhs.priority < rhs.priority; // 优先级低的沉下去
        }
        return lhs.time > rhs.time; // 优先级相同时，时间晚的沉下去（时间早的浮上来）
    }
};

int main() {
    // 声明时传入仿函数类型
    priority_queue<Task, vector<Task>, TaskCompare> pq;
    
    pq.push({1, 10, 100});
    pq.push({2, 10, 50});  // 优先级相同，时间更早
    pq.push({3, 20, 200}); // 优先级最高
    
    // 输出顺序: ID 3 (优先20) -> ID 2 (优先10, 时间50) -> ID 1 (优先10, 时间100)
    while (!pq.empty()) {
        cout << "ID: " << pq.top().id << " ";
        pq.pop();
    }
    cout << endl;
    
    return 0;
}
```

### 方法 C：Lambda 表达式 (C++11，需注意构造方式)
Lambda 不能直接作为模板参数（因为类型未知），需要配合 `decltype` 和构造函数传递。

```cpp
int main() {
    auto cmp = [](int left, int right) {
        return left > right; // 小顶堆：左边大于右边时，左边沉下去
    };
    
    // 必须将 lambda 对象传递给构造函数
    priority_queue<int, vector<int>, decltype(cmp)> pq(cmp);
    
    pq.push(10); pq.push(5); pq.push(20);
    cout << "Min Top: " << pq.top() << endl; // 5
    
    return 0;
}
```

---

## 5️⃣ 底层容器与迭代器 (Underlying Container & Iterators)

| 特性 | 说明 |
| :--- | :--- |
| **底层容器** | 默认为 `std::vector`，也可指定 `std::deque`。**不支持 `std::list`**（因为堆需要随机访问）。 |
| **迭代器** | **❌ 不支持迭代器！** `priority_queue` 没有 `begin()`, `end()` 方法。 |
| **遍历** | **无法直接遍历**。若需遍历，必须不断 `pop()` 直到空（会破坏队列），或者拷贝一份出来再 pop。 |

### 💻 代码示例：如何“遍历”（实际上是销毁性读取）
```cpp
int main() {
    priority_queue<int> pq{5, 1, 9};
    
    // 错误写法：for (auto x : pq) ... ❌ 编译错误，没有迭代器
    
    // 正确写法：逐个弹出
    cout << "Elements: ";
    while (!pq.empty()) {
        cout << pq.top() << " ";
        pq.pop();
    }
    // 此时 pq 已空
    cout << "\nSize after traversal: " << pq.size() << endl; // 0
    
    return 0;
}
```

---

## 6️⃣ 常见应用场景

### 场景 A：Top K 问题（求最大的 K 个数）
维护一个大小为 K 的**小顶堆**。
- 若新数 > 堆顶，则 `pop` 堆顶，`push` 新数。
- 最终堆中即为最大的 K 个数。

```cpp
vector<int> topK(vector<int>& nums, int k) {
    priority_queue<int, vector<int>, greater<int>> min_pq; // 小顶堆
    
    for (int num : nums) {
        if (min_pq.size() < k) {
            min_pq.push(num);
        } else if (num > min_pq.top()) {
            min_pq.pop();
            min_pq.push(num);
        }
    }
    
    // 转存到 vector 返回
    vector<int> res;
    while (!min_pq.empty()) {
        res.push_back(min_pq.top());
        min_pq.pop();
    }
    return res;
}
```

### 场景 B：合并 K 个有序链表
利用小顶堆每次取出 K 个链表头中最小的节点。

### 场景 C：带权图最短路径 (Dijkstra)
利用小顶堆快速取出当前距离起点最近的未访问节点。

---

## 7️⃣ `priority_queue` vs `set` vs `sort` 终极对比

| 特性 | `std::priority_queue` | `std::set` / `multiset` | `std::vector` + `sort` |
| :--- | :--- | :--- | :--- |
| **核心功能** | 快速获取最大/最小值 | 有序集合，支持去重/重复 | 通用动态数组 |
| **访问极值** | **$O(1)$** (`top`) | $O(1)$ (`begin`/`rbegin`) | $O(1)$ (排序后) |
| **插入复杂度** | **$O(\log N)$** | $O(\log N)$ | $O(1)$ (尾部), $O(N \log N)$ (整体排序) |
| **删除极值** | **$O(\log N)$** (`pop`) | $O(1)$ (擦除迭代器) | $O(1)$ (尾部) |
| **遍历能力** | ❌ **不支持** | ✅ 支持 (有序遍历) | ✅ 支持 |
| **中间访问** | ❌ 不支持 | ❌ 不支持 (需迭代) | ✅ 支持 ($O(1)$) |
| **内存占用** | 低 (仅存储数据) | 高 (红黑树指针开销) | 低 |
| **适用场景** | **只关心最大/最小值**，不需要遍历 | 需要**有序遍历**、查找特定值 | 需要**随机访问**、一次性排序 |

---

### 💡 核心总结
1. **只能看顶**：记住 `priority_queue` 是个“黑盒”，你只能看到最上面那个元素，看不到里面的顺序，也不能遍历。
2. **大小顶堆切换**：
   - 大顶堆（默认）：`priority_queue<T>`
   - 小顶堆：`priority_queue<T, vector<T>, greater<T>>`
3. **自定义排序**：处理结构体时，务必理清 `operator<` 或仿函数的逻辑（谁 `<` 谁，谁就沉底）。
4. **性能优势**：在只需要“不断取最大/最小值”的场景下（如流式数据处理），它的性能优于每次都对 `vector` 排序，也优于 `set`（因为常数因子更小，内存更紧凑）。
5. **陷阱**：不要试图用迭代器遍历它！如果需要遍历且保持有序，请用 `std::set` 或将数据倒入 `vector` 后 `sort`。

**一句话口诀**：
> “堆顶元素随时取，插入删除 log N 级；
> 默认大顶 greater 小，无法遍历莫强求；
> Top K 问题它最强，自定义类仿函记。”