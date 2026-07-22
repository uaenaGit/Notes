---
created: 2026-03-19T18:12
updated: 2026-03-19T18:12
---
以下是一份为您精心整理的 **C++ `std::stable_sort` 全方位方法详解**，延续了 `std::sort` 指南的结构与风格，重点突出 **稳定性** 及其应用场景。

---

# 📚 C++ `std::stable_sort` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // 必须包含此头文件
#include <functional> // 用于 std::greater

using namespace std;
```

> **核心特性速览**：
> 1. **稳定排序**：相等元素的**相对顺序保持不变**——这是它与 `std::sort` 最核心的区别。
> 2. **时间复杂度**：$O(N \log^2 N)$ 在最坏情况下，但若有足够额外内存，可达到 $O(N \log N)$。
> 3. **内存开销**：可能需要额外内存（归并排序实现），若内存不足则退化为 $O(N \log^2 N)$ 的就地算法。
> 4. **迭代器要求**：同样需要 **随机访问迭代器**（Random Access Iterator），适用于 `vector`, `array`, 原生数组，不适用于 `list`（`list` 有自己的 `stable` 成员函数 `sort`）。
> 5. **函数签名**：与 `std::sort` 完全一致，只是内部实现保证稳定性。

---

## 1️⃣ 函数原型与参数 (Function Signature)

| 形式 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`void stable_sort(RandomIt first, RandomIt last)`** | `first`: 起始迭代器<br>`last`: 结束迭代器（开区间） | `void` | 使用默认比较器（`operator<`，即**升序**）进行**稳定排序**。 |
| **`void stable_sort(RandomIt first, RandomIt last, Compare comp)`** | `comp`: 自定义比较函数/对象<br>签名：`bool cmp(const T& a, const T& b)` | `void` | 使用自定义规则进行**稳定排序**。比较函数语义与 `sort` 相同：若 `comp(a, b)` 为 `true`，则 `a` 排在 `b` 前面。 |

> **关键逻辑**：比较函数 `comp(a, b)` 返回 `true` 意味着 **"a 应该排在 b 之前"**，且必须满足**严格弱序**（与 `sort` 要求一致）。

---

## 2️⃣ 标准用法模板 (The Golden Patterns)

### 💻 场景 A：基础排序（原生数组 & Vector）
默认行为是**从小到大**稳定排序。

```cpp
int main() {
    // 1. 原生数组
    int arr[] = {5, 2, 9, 1, 5, 6};
    int n = sizeof(arr) / sizeof(arr[0]);
    
    // 升序稳定排列
    stable_sort(arr, arr + n); 
    // 结果: 1 2 5 5 6 9 （注意两个 5 的相对顺序与输入一致）

    // 2. std::vector
    vector<int> v = {5, 2, 9, 1, 5, 6};
    
    // 升序稳定排列
    stable_sort(v.begin(), v.end());
    // 结果: 1 2 5 5 6 9 （两个 5 保持输入顺序）
    
    return 0;
}
```

### 💻 场景 B：降序排序（两种写法）
降序稳定排序同样支持。

**写法 1：使用 `std::greater<T>()` (推荐)**
```cpp
vector<int> v = {5, 2, 9, 1, 5};
stable_sort(v.begin(), v.end(), greater<int>()); 
// 结果: 9 5 5 2 1 （两个 5 保持原相对顺序）
```

**写法 2：使用 Lambda 表达式**
```cpp
vector<int> v = {5, 2, 9, 1, 5};
stable_sort(v.begin(), v.end(), [](int a, int b) {
    return a > b; 
});
// 结果: 9 5 5 2 1
```

### 💻 场景 C：自定义结构体/类排序（稳定性的价值）
当需要**多关键字排序**且希望**后续排序不影响先前排序结果**时，稳定性至关重要。

例如，对学生先按**分数降序**，再按**年龄升序**，但如果用不稳定排序直接排，可能会打乱相同分数下的年龄顺序。正确做法是**先排次要关键字，再排主要关键字**（利用稳定性）。

```cpp
struct Student {
    string name;
    int score;
    int age;
};

vector<Student> students = {
    {"Alice", 90, 20},
    {"Bob", 90, 19},
    {"Charlie", 85, 21},
    {"David", 90, 18}
};

// 目标：分数降序，分数相同则年龄升序
// 正确步骤（稳定排序）：
// 1. 先按年龄升序（次要关键字）
stable_sort(students.begin(), students.end(),
            [](const Student& a, const Student& b) {
                return a.age < b.age;
            });
// 2. 再按分数降序（主要关键字）- 稳定排序保持年龄顺序
stable_sort(students.begin(), students.end(),
            [](const Student& a, const Student& b) {
                return a.score > b.score;
            });

// 最终顺序：David(90,18), Bob(90,19), Alice(90,20), Charlie(85,21)
// 注意：分数相同的学生按年龄升序（第一步的结果被保留）
```

> **要点**：若用 `std::sort` 执行上述第二步，相同分数的学生**可能**会丢失第一步的年龄顺序，因为 `sort` 不稳定。

---

## 3️⃣ 深度对比：`std::stable_sort` vs `std::sort` vs 手动稳定排序

| 特性        | `std::stable_sort`                          | `std::sort`        | 手动稳定（如 `std::pair` 带索引）                   |
| :-------- | :------------------------------------------ | :----------------- | :---------------------------------------- |
| **稳定性**   | **保证稳定**                                    | 不稳定                | 可以模拟（但增加代码复杂度）                            |
| **时间复杂度** | $O(N \log^2 N)$（最坏）<br>$O(N \log N)$（有额外内存） | $O(N \log N)$（始终）  | $O(N \log N)$（若用 `sort` 加索引）              |
| **内存开销**  | 可能需要额外 $O(N)$ 内存                            | 原地排序（除递归栈外无额外内存）   | 需要额外 $O(N)$ 存储索引或原始位置                     |
| **速度**    | 通常比 `sort` 慢（常数大）                           | 最快                 | 较慢（需维护索引并比较两次）                            |
| **适用场景**  | 需要保持相等元素原始顺序时；多关键字排序的中间步骤                   | 大多数通用排序（不关心相等元素顺序） | 不想用 `stable_sort` 但需要稳定性的兼容场景（如 C++98 之前） |

### ⚠️ 何时必须用 `stable_sort`？
- **多关键字排序**：如上例，先排次要关键字，再排主要关键字，利用稳定性保证最终顺序。
- **保留输入顺序**：题目要求“若分数相同，按输入顺序输出”时，直接对分数用稳定排序即可，无需额外字段。
- **渐进式排序**：在 GUI 中，用户先按一列排序，再按另一列排序，稳定排序能保留第一列的有序性。

---

## 4️⃣ 高级应用与变体

### 场景 A：与 `std::sort` 混合使用
有时先对整体用 `std::sort` 快速排序，再对关键部分用 `stable_sort` 微调，但需注意性能权衡。

### 场景 B：对 `std::list` 的稳定排序
`std::list` 提供了自己的 `sort` 成员函数，且**保证稳定**（C++11 起）。但 `std::stable_sort` 无法用于 `list`，因为它需要随机访问迭代器。

```cpp
list<int> lst = {5, 2, 9, 1, 5};
lst.sort(); // 升序稳定排序
lst.sort(greater<int>()); // 降序稳定排序
```

### 场景 C：使用 `std::pair` 或 `std::tuple` 模拟稳定性
如果不便使用 `stable_sort`，可以在元素中绑定原始索引，然后按主要关键字和索引一起排序：

```cpp
vector<int> data = {5, 2, 9, 1, 5};
vector<pair<int, size_t>> indexed;
for (size_t i = 0; i < data.size(); ++i) indexed.emplace_back(data[i], i);

sort(indexed.begin(), indexed.end(), [](const auto& a, const auto& b) {
    if (a.first != b.first) return a.first < b.first;  // 主要关键字
    return a.second < b.second;                         // 保持原始顺序
});
```

这种方法虽然可行，但 `stable_sort` 更直接高效。

---

## 5️⃣ 常见陷阱与注意事项

| 问题 | 描述 | 解决方案 |
| :--- | :--- | :--- |
| **比较函数写错** | 写了 `a <= b` 而不是 `a < b` | **严禁**使用 `<=` 或 `>=`，必须满足严格弱序。 |
| **误认为稳定排序总是更快** | 在不需要稳定性时使用 `stable_sort`，导致性能下降 | 除非明确需要稳定，否则首选 `std::sort`。 |
| **对 `list` 使用 `std::stable_sort`** | 编译错误（迭代器不匹配） | 改用 `list::sort`。 |
| **忘记稳定性依赖** | 认为稳定排序后元素顺序永远不变，但稳定只保证相等元素相对顺序不变，不保证跨次排序的顺序 | 理解稳定性的定义，结合算法设计。 |

### ❌ 错误示范
```cpp
// 错误：尝试用不稳定排序实现多次排序但期望稳定
sort(students.begin(), students.end(), [](auto& a, auto& b){ return a.age < b.age; });
sort(students.begin(), students.end(), [](auto& a, auto& b){ return a.score > b.score; });
// 相同分数的学生，年龄顺序可能被打乱
```

### ✅ 正确示范
```cpp
// 正确：使用稳定排序保护前一次排序结果
stable_sort(students.begin(), students.end(), [](auto& a, auto& b){ return a.age < b.age; });
stable_sort(students.begin(), students.end(), [](auto& a, auto& b){ return a.score > b.score; });
```

---

## 6️⃣ 性能分析与最佳实践

1.  **算法内核**：`std::stable_sort` 通常实现为 **归并排序** 的变种。
    *   如果有足够的额外内存，它会分配一个临时缓冲区，进行常规归并，时间复杂度 $O(N \log N)$。
    *   如果内存不足，它会采用**就地归并算法**（如原地归并），此时时间复杂度退化为 $O(N \log^2 N)$。
2.  **何时使用**：
    *   ✅ **多关键字排序**：利用稳定性分步排序。
    *   ✅ **保留输入顺序**：题目明确要求相等元素按原序输出。
    *   ✅ **与旧代码交互**：旧代码可能依赖稳定行为。
    *   ❌ **通用排序**：优先 `std::sort` 以获得最佳性能。
3.  **性能权衡**：
    *   若内存充足且数据量不大，`stable_sort` 与 `sort` 差距不明显。
    *   对于超大容器（数百万元素），`sort` 通常比 `stable_sort` 快 20%~50%。

---

### 💡 核心总结
1.  **头文件**：`#include <algorithm>`。
2.  **稳定性**：相等元素的相对顺序在排序后保持不变。
3.  **使用时机**：多关键字排序、需保持原序的场景。
4.  **性能**：可能慢于 `std::sort`，内存开销可能更大。
5.  **口诀**：
    > “稳定排序保顺序，多关键字显神威；
    > 先排次要后主要，两次 stable 最完美；
    > 默认升序可定制，严格弱序要守规；
    > 若问何时弃 sort？只需稳定别犹豫。”

### 🏆 实战代码片段 (Copy-Paste Ready)
```cpp
// 1. 稳定降序
stable_sort(v.begin(), v.end(), greater<int>());

// 2. 多关键字稳定排序：先按分数降序，再按年龄升序
struct Person { string name; int score; int age; };
vector<Person> people = {...};

// 方法 A（两步稳定排序）
stable_sort(people.begin(), people.end(),
            [](const Person& a, const Person& b) { return a.age < b.age; });
stable_sort(people.begin(), people.end(),
            [](const Person& a, const Person& b) { return a.score > b.score; });

// 方法 B（单次排序 - 若使用 sort 则不稳定，但 stable_sort 仍然稳定！）
// 注意：单次排序同样保证稳定，但需确保比较函数只比较主要关键字，次要关键字不参与比较。
// 这样相同分数的相对顺序（由之前排序决定）会被保持。
// 但上述两步法更清晰通用。

// 3. 保留输入顺序（直接按分数稳定排序）
stable_sort(people.begin(), people.end(),
            [](const Person& a, const Person& b) { return a.score > b.score; });
// 相同分数的人保持输入顺序

// 4. 对 list 使用稳定排序（成员函数）
list<int> lst = {5, 2, 9, 1, 5};
lst.sort(); // 稳定升序
```

---

希望这份指南能帮助您深入理解并正确使用 `std::stable_sort`！如果有任何疑问，欢迎继续探讨。