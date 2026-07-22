---
created: 2026-03-19T18:05
updated: 2026-03-19T18:05
---
这是一份为您精心整理的 **C++ `std::sort` 全方位方法详解**。

`std::sort` 是 C++ 标准模板库（STL）中 `<algorithm>` 头文件下的**排序神器**。它通常采用 **IntroSort**（混合排序：快速排序 + 堆排序 + 插入排序），保证了在最坏情况下也能达到 $O(N \log N)$ 的时间复杂度，且常数因子极小，速度远快于手写的快速排序或归并排序。

这份指南严格遵循 C++11 及以上标准，**重点解析了自定义排序规则、稳定性问题以及与 `qsort` 的区别**。

---

# 📚 C++ `std::sort` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // 必须包含此头文件
#include <functional> // 用于 std::greater

using namespace std;
```

> **核心特性速览**：
> 1. **高效稳定**：平均和最坏时间复杂度均为 $O(N \log N)$。
> 2. **灵活定制**：支持通过 Lambda 表达式、函数指针或仿函数轻松定义排序规则。
> 3. **原地排序**：不需要额外的内存空间（除了递归栈）。
> 4. **非稳定性**：**注意！** `std::sort` **不保证** 相等元素的相对顺序（若需稳定排序，请用 `std::stable_sort`）。
> 5. **迭代器要求**：需要 **随机访问迭代器**（Random Access Iterator），因此适用于 `vector`, `array`, 原生数组，但**不适用于** `list`（`list` 有自己的 `.sort()` 成员函数）。

---

## 1️⃣ 函数原型与参数 (Function Signature)

| 形式 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`void sort(RandomIt first, RandomIt last)`** | `first`: 起始迭代器`last`: 结束迭代器（开区间） | `void` | 使用默认比较器（`operator<`，即**升序**）排序。 |
| **`void sort(RandomIt first, RandomIt last, Compare comp)`** | `comp`: 自定义比较函数/对象签名：`bool cmp(const T& a, const T& b)` | `void` | 使用自定义规则排序。**规则**：若 `comp(a, b)` 为 `true`，则 `a` 排在 `b` 前面。 |

> **关键逻辑**：比较函数 `comp(a, b)` 返回 `true` 意味着 **"a 应该排在 b 之前"**。
> *   升序：`a < b` (小的在前)
> *   降序：`a > b` (大的在前)

---

## 2️⃣ 标准用法模板 (The Golden Patterns)

### 💻 场景 A：基础排序（原生数组 & Vector）
默认行为是**从小到大**排序。

```cpp
int main() {
    // 1. 原生数组
    int arr[] = {5, 2, 9, 1, 5, 6};
    int n = sizeof(arr) / sizeof(arr[0]);
    
    // 升序排列
    sort(arr, arr + n); 
    // 结果: 1 2 5 5 6 9

    // 2. std::vector
    vector<int> v = {5, 2, 9, 1, 5, 6};
    
    // 升序排列
    sort(v.begin(), v.end());
    // 结果: 1 2 5 5 6 9
    
    return 0;
}
```

### 💻 场景 B：降序排序（两种写法）
想要**从大到小**？你有两个选择。

**写法 1：使用 `std::greater<T>()` (推荐，语义清晰)**
```cpp
vector<int> v = {5, 2, 9, 1};
// 需要包含 <functional>
sort(v.begin(), v.end(), greater<int>()); 
// 结果: 9 5 2 1
```

**写法 2：使用 Lambda 表达式 (灵活，C++11 起)**
```cpp
vector<int> v = {5, 2, 9, 1};
// [] 捕获列表，(int a, int b) 参数，{ return a > b; } 函数体
sort(v.begin(), v.end(), [](int a, int b) {
    return a > b; 
});
// 结果: 9 5 2 1
```

### 💻 场景 C：自定义结构体/类排序 (高频考点)
这是算法竞赛和实际开发中最常用的场景。假设我们要对“学生”进行排序：先按分数降序，若分数相同则按年龄升序。

```cpp
struct Student {
    string name;
    int score;
    int age;
};

vector<Student> students = {
    {"Alice", 90, 20},
    {"Bob", 90, 19},
    {"Charlie", 85, 21}
};

// 方法：使用 Lambda 表达式作为第三个参数
sort(students.begin(), students.end(), [](const Student& a, const Student& b) {
    if (a.score != b.score) {
        return a.score > b.score; // 分数高的在前 (降序)
    }
    return a.age < b.age; // 分数相同时，年龄小的在前 (升序)
});

// 结果顺序: Bob(90,19), Alice(90,20), Charlie(85,21)
```

> **技巧**：也可以重载结构体的 `<` 运算符，然后直接调用 `sort(begin, end)`，但 Lambda 方式更灵活，无需修改结构体定义。

---

## 3️⃣ 深度对比：`std::sort` vs `std::stable_sort` vs `qsort`

| 特性 | `std::sort` (推荐) | `std::stable_sort` | `qsort` (C 风格) |
| :--- | :--- | :--- | :--- |
| **稳定性** | **不稳定** (相等元素顺序可能改变) | **稳定** (相等元素保持原相对顺序) | 不稳定 |
| **时间复杂度** | $O(N \log N)$ (最坏也是) | $O(N \log^2 N)$ 或 $O(N \log N)$ (取决于内存) | 平均 $O(N \log N)$，最坏 $O(N^2)$ |
| **速度** | **最快** (常数项小) | 稍慢 (为了维持稳定性) | 慢 (涉及函数指针回调开销) |
| **类型安全** | **高** (模板推导，类型检查) | **高** | **低** (需 `void*` 强转，易出错) |
| **用法难度** | 简单 (支持 Lambda) | 简单 | 繁琐 (需写独立的 `cmp` 函数) |
| **适用场景** | 绝大多数排序需求 | 需要保留相等元素原始顺序时 (如多关键字排序的第二步) | 维护旧 C 代码 |

### ⚠️ 什么时候必须用 `stable_sort`？
当你进行**多关键字排序**，且希望通过**多次排序**来实现时。
*   例如：先按“姓名”排，再按“分数”排。如果用 `stable_sort` 排分数，分数相同的人会自动保持姓名的顺序。
*   或者：题目明确要求“若分数相同，按输入顺序输出”。

---

## 4️⃣ 高级应用与变体

### 场景 A：部分排序 (`std::partial_sort`)
如果你只需要**前 K 个**最小（或最大）的元素，而不需要整个数组有序，`partial_sort` 更快。

```cpp
vector<int> v = {9, 5, 2, 1, 8, 7};
// 只保证前 3 个元素是最小的且有序，后面的元素顺序未定义
partial_sort(v.begin(), v.begin() + 3, v.end());

// 结果可能是: 1 2 5 [乱序的剩余元素...]
// 复杂度: O(N log K)，当 K 很小时比全排序快得多
```

### 场景 B：第 K 大/小元素 (`std::nth_element`)
如果你只想知道**第 K 小的元素是谁**，或者想把数组分成“比 K 小”和“比 K 大”两部分，不需要内部有序。

```cpp
vector<int> v = {9, 5, 2, 1, 8, 7};
// 将第 3 小的元素放到索引 2 的位置 (v[2])
// 左边都比它小，右边都比它大 (内部无序)
nth_element(v.begin(), v.begin() + 2, v.end());

// 结果示例: 1 2 5 9 8 7 (5 在中间，左边<5, 右边>5)
// 复杂度: 平均 O(N)，非常快！常用于找中位数
```

### 场景 C：逆序迭代器 (一行代码实现降序)
利用 `rbegin()` 和 `rend()` 也可以实现降序，但这实际上是“把升序的结果反向看待”。

```cpp
vector<int> v = {1, 5, 2};
// 对反向迭代器范围排序 (相当于把原数组倒过来排升序)
sort(v.rbegin(), v.rend()); 
// 结果: 5 2 1 (降序)
```

---

## 5️⃣ 常见陷阱与注意事项

| 问题 | 描述 | 解决方案 |
| :--- | :--- | :--- |
| **比较函数写错** | 写了 `a <= b` 而不是 `a < b` | **严禁**在比较函数中使用 `<=` 或 `>=`。必须满足**严格弱序** (Strict Weak Ordering)。若 `a==b` 必须返回 `false`，否则可能导致死循环或 RE (Runtime Error)。 |
| **容器选错** | 对 `std::list` 使用 `std::sort` | 编译错误。`list` 不支持随机访问迭代器。请使用 `myList.sort()` 成员函数。 |
| **迭代器越界** | `last` 参数写错 | 确保第二个参数是 `end()` 或 `arr + N`，不能是最后一个元素的迭代器。 |
| **Lambda 捕获** | 在 Lambda 中引用了局部变量但未捕获 | 如果比较逻辑依赖外部变量，记得写 `[=]` 或 `[&]` 捕获。例如：`sort(..., [&](int a, int b){ return a > threshold; });` |

### ❌ 错误示范 (会导致崩溃)
```cpp
// 错误：使用了 <=，当 a==b 时返回 true，违反严格弱序
sort(v.begin(), v.end(), [](int a, int b) {
    return a <= b; 
});
```

### ✅ 正确示范
```cpp
// 正确：仅当 a 严格小于 b 时返回 true
sort(v.begin(), v.end(), [](int a, int b) {
    return a < b; 
});
```

---

## 6️⃣ 性能分析与最佳实践

1.  **算法内核**：C++ STL 的 `sort` 通常实现为 **IntroSort**。
    *   开始使用 **快速排序** (Quick Sort)。
    *   当递归深度过深时，切换到 **堆排序** (Heap Sort) 以避免 $O(N^2)$ 的最坏情况。
    *   当分段很小（如小于 16 个元素）时，切换到 **插入排序** (Insertion Sort) 以提高缓存命中率。
2.  **何时使用**：
    *   ✅ **通用排序**：99% 的场景首选 `std::sort`。
    *   ✅ **找第 K 大**：使用 `nth_element` (比全排序快)。
    *   ✅ **只要前 K 个**：使用 `partial_sort`。
    *   ✅ **需要稳定性**：使用 `std::stable_sort`。
    *   ❌ **链表**：使用 `list::sort`。
    *   ❌ **极度简单的整数且范围小**：考虑计数排序 (Counting Sort)，但这需要手写。

---

### 💡 核心总结
1.  **头文件**：`#include <algorithm>`。
2.  **默认行为**：升序 (`<`)。
3.  **降序技巧**：`greater<T>()` 或 `rbegin(), rend()` 或 Lambda `a > b`。
4.  **严格弱序**：比较函数**绝对不能**带等号 (`<=`)。
5.  **口诀**：
    > “默认排序是升序，降序 greater 来相助；
    > 结构体排 Lambda 写，严格小于莫含糊；
    > 链表不能用此法，成员 sort 才靠谱；
    > 若要稳定保顺序，stable_sort 来补路。”

### 🏆 实战代码片段 (Copy-Paste Ready)
```cpp
// 1. 快速降序
sort(v.begin(), v.end(), greater<int>());

// 2. 复杂结构体排序 (分数降序，ID 升序)
struct Node { int id, score; };
sort(nodes.begin(), nodes.end(), [](const Node& a, const Node& b) {
    if (a.score != b.score) return a.score > b.score;
    return a.id < b.id;
});

// 3. 找第 K 大元素 (K=3, 即索引 2)
nth_element(v.begin(), v.begin() + 2, v.end(), greater<int>());
int kth_max = v[2];

// 4. 只要前 5 个最小的
partial_sort(v.begin(), v.begin() + 5, v.end());
```