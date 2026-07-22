---
created: 2026-03-16T16:51
updated: 2026-03-21T16:26
---
这是一份为您精心整理的 **C++ STL `std::unique` 与 `vector::erase` 去重全方位指南**。

在 C++ 中，去除容器（如 `vector`）中的重复元素是一个经典操作。许多初学者误以为调用一个函数就能完成，但实际上需要 **“排序 + Unique + Erase”** 的三步组合拳。`std::unique` 负责“逻辑去重”，而 `erase` 负责“物理删除”。

这份指南严格遵循 C++11 及以上标准，**重点解析了两者配合的底层原理、常见陷阱以及高级自定义去重技巧**。

---

# 📚 C++ `unique` & `erase` 去重完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // 必须包含：sort, unique
#include <iterator>  // 可选：用于迭代器操作

using namespace std;
```

> **核心特性速览**：
> 1. **两步走策略**：`unique` 不改变容器大小，只移动元素；`erase` 真正截断容器。
> 2. **相邻原则**：`std::unique` **仅去除相邻的重复元素**。若数据无序，必须先 `sort`。
> 3. **类型通用**：支持所有可比较类型（int, string, struct），只要定义了 $==$ 运算符。
> 4. **高效性**：时间复杂度 $O(N)$ (unique) + $O(K)$ (erase)，整体由排序主导 $O(N \log N)$。
> 5. **迭代器返回**：`unique` 返回的是“新逻辑结尾”的迭代器，这是连接 `erase` 的关键桥梁。

---

## 1️⃣ 函数原型与参数详解

### 🔹 `std::unique` (算法库)
| 形式 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`ForwardIterator unique(ForwardIterator first, ForwardIterator last)`** | `first`: 起始迭代器`last`: 结束迭代器（开区间） | **迭代器** | 移除范围内**相邻**的重复元素，将唯一元素移至前端。**返回指向“新逻辑结尾”下一个位置的迭代器**。 |
| **`unique(..., BinaryPredicate pred)`** | `pred`: 自定义比较函数 | **迭代器** | 根据自定义规则判断“重复”（如忽略大小写、绝对值相等）。 |

> **关键机制**：它通过遍历，发现重复元素时，用后面的非重复元素**覆盖**前面的重复元素。容器的大小 (`size()`) **不会改变**，尾部会残留旧数据。

### 🔹 `vector::erase` (容器成员函数)
| 形式 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`iterator erase(const_iterator first, const_iterator last)`** | `first`: 删除起始位置`last`: 删除结束位置（开区间） | **迭代器** | 从容器中**物理删除** `[first, last)` 范围内的元素，后续元素前移，**size 减小**。 |

---

## 2️⃣ 标准用法模板 (The Golden Pattern)

这是 C++ 中去重的**标准范式**，适用于 99% 的场景。

### 💻 场景 A：基础去重 (整数/字符串)
**口诀：先排序，再 Unique，最后 Erase。**

```cpp
int main() {
    vector<int> nums = {4, 1, 2, 1, 3, 2, 4};

    // 第 1 步：排序 (至关重要！unique 只能去重相邻元素)
    sort(nums.begin(), nums.end());
    // 此时 nums: {1, 1, 2, 2, 3, 4, 4}

    // 第 2 步：Unique (逻辑去重)
    // it 指向去重后有效数据的“下一个位置” (即第一个冗余元素)
    auto it = unique(nums.begin(), nums.end());
    // 此时内存布局可能是: {1, 2, 3, 4, ?, ?, ?} 
    // it 指向索引 4 (第一个 '?')

    // 第 3 步：Erase (物理删除)
    // 删除从 it 到末尾的所有“脏数据”
    nums.erase(it, nums.end());

    // 验证结果: 1 2 3 4
    for (int x : nums) cout << x << " ";
    cout << "\nSize: " << nums.size() << endl;

    return 0;
}
```

### 💻 场景 B：部分区间去重
如果你只想对 `vector` 的一部分进行去重（例如前 10 个元素）：

```cpp
vector<int> v(20);
// ... 填充数据 ...

// 仅对前 10 个元素排序
sort(v.begin(), v.begin() + 10);

// 仅对前 10 个元素 unique
auto it = unique(v.begin(), v.begin() + 10);

// 删除这部分产生的冗余 (注意范围)
v.erase(it, v.begin() + 10); 
// 注意：这里 erase 的结束位置是原区间的末尾，不是 v.end()
```

---

## 3️⃣ 深度原理解析：为什么不能只用 Unique？

这是面试和考试中最常考的知识点。

### 🧐 内存变化图解
假设 `vector<int> v = {1, 1, 2}`，容量为 3。

| 步骤 | 操作 | 内存状态 (Index 0, 1, 2) | `v.size()` | `v` 的有效内容 |
| :--- | :--- | :--- | :--- | :--- |
| **初始** | - | `[1, 1, 2]` | 3 | `{1, 1, 2}` |
| **Sort** | `sort` | `[1, 1, 2]` | 3 | `{1, 1, 2}` |
| **Unique** | `unique` | `[1, 2, 2]` | **3 (不变)** | **逻辑上**是 `{1, 2}`，但 Index 2 仍保留旧值 `2` |
| **返回** | `it` | `it` 指向 Index 2 | - | - |
| **Erase** | `erase(it, end)` | `[1, 2]` | **2 (变小)** | `{1, 2}` (干净的数据) |

> **结论**：如果不执行 `erase`，当你遍历 `v` 时，依然会访问到 Index 2 的那个残留的 `2`，导致去重失败。`unique` 只是把不重复的元素“搬”到了前面，并没有“删”掉后面的东西。

---

## 4️⃣ 高级应用：自定义去重规则

`std::unique` 允许传入第三个参数：**二元谓词 (Binary Predicate)**。当两个元素被判定为“相等”时，后者被视为重复并被移除。

### ⚠️ 重要前提
如果你使用了自定义比较函数 `pred(a, b)`，那么你的 **`sort` 也必须使用相同的逻辑**（或者确保数据已经按照该逻辑排好序，使得“相等”的元素相邻）。

### 💻 场景 A：忽略大小写去重 (字符串)
```cpp
vector<string> words = {"Apple", "apple", "Banana", "banana", "Cat"};

// 自定义比较：忽略大小写视为相等
auto caseInsensitiveEqual = [](const string& a, const string& b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) {
        if (tolower(a[i]) != tolower(b[i])) return false;
    }
    return true;
};

// 1. 排序 (必须使用同样的逻辑，这里简化处理，实际需自定义 sort 比较器)
// 为了演示 unique，假设我们已经手动排好序让相同单词相邻：
// {"Apple", "apple", "Banana", "banana", "Cat"} 
// 注意：如果 sort 不区分大小写，"Apple" 和 "apple" 会相邻。

sort(words.begin(), words.end(), [](const string& a, const string& b){
    string la = a, lb = b;
    transform(la.begin(), la.end(), la.begin(), ::tolower);
    transform(lb.begin(), lb.end(), lb.begin(), ::tolower);
    return la < lb;
});

// 2. Unique (传入自定义相等判断)
auto it = unique(words.begin(), words.end(), caseInsensitiveEqual);

// 3. Erase
words.erase(it, words.end());

// 结果: Apple, Banana, Cat (保留了每组中的第一个)
```

### 💻 场景 B：结构体去重 (根据特定字段)
```cpp
struct Person {
    int id;
    string name;
    // 构造函数方便初始化
    Person(int i, string n) : id(i), name(n) {}
};

vector<Person> people = {{1, "Alice"}, {1, "Alice"}, {2, "Bob"}, {1, "Alice"}};

// 1. 排序 (按 id 排序，使相同 id 相邻)
sort(people.begin(), people.end(), [](const Person& a, const Person& b) {
    return a.id < b.id;
});

// 2. Unique (只要 id 相同视为重复)
auto it = unique(people.begin(), people.end(), [](const Person& a, const Person& b) {
    return a.id == b.id;
});

// 3. Erase
people.erase(it, people.end());

// 结果：保留了 id=1 的第一个出现，id=2 的一个。
```

---

## 5️⃣ 常见陷阱与注意事项

| 陷阱 | 描述 | 解决方案 |
| :--- | :--- | :--- |
| **忘记排序** | 直接对无序数组调用 `unique`。 | **必须先 `sort`**。`{1, 2, 1}` 经 `unique` 后仍是 `{1, 2, 1}`，因为两个 1 不相邻。 |
| **忘记 Erase** | 只调用了 `unique`，认为去重完成。 | 必须配合 `v.erase(it, v.end())`，否则 `size()` 不变，遍历会读出脏数据。 |
| **链表 (list) 误用** | 对 `std::list` 使用 `std::unique` 算法。 | `std::list` 有成员函数 `lst.unique()`，它可以直接删除节点，**不需要**也不支持配合 `erase` 使用（因为它内部已处理删除）。但仍需先 `lst.sort()`。 |
| **迭代器失效** | 在 `unique` 返回的迭代器之后继续操作原容器逻辑。 | `unique` 后，只有 `[begin, it)` 是有效数据，之后的数据是未定义的残留。 |
| **空容器** | 对空容器调用。 | 安全。`begin() == end()`，`unique` 直接返回 `end()`，`erase` 无事发生。 |

---

## 6️⃣ 性能分析与最佳实践

1.  **时间复杂度**：
    *   `sort`: $O(N \log N)$ (主导因素)
    *   `unique`: $O(N)$ (线性扫描，每个元素最多移动一次)
    *   `erase`: $O(K)$ (K 为删除元素个数，涉及内存移动)
    *   **总计**: $O(N \log N)$。这是基于比较的去重方法的最优复杂度。

2.  **空间复杂度**：
    *   $O(1)$ (原地操作，除了排序所需的栈空间)。

3.  **替代方案对比**：
    *   **`set` / `unordered_set`**:
        *   优点：自动去重，无需手动三步走。
        *   缺点：额外内存开销，构造成本高 ($O(N \log N)$ 或 $O(N)$ 但常数大)，且会**打乱原有顺序** (除非用 `set` 且接受排序结果)。
        *   **建议**：如果需要**保留原顺序**且**不去排序**，可以使用 `unordered_set` 辅助遍历去重（$O(N)$ 时间，$O(N)$ 空间），但对于大多数算法题，**Sort + Unique + Erase** 是最节省内存且速度极快的首选。

---

### 💡 核心总结
1.  **标准流程**：`sort` $\rightarrow$ `unique` $\rightarrow$ `erase`。
2.  **Unique 本质**：它是**搬运工**，不是清洁工。它返回新边界，不改 size。
3.  **Erase 本质**：它是**清洁工**，负责截断容器，释放多余空间。
4.  **自定义规则**：`unique` 支持谓词，但务必保证**排序逻辑**与**去重逻辑**一致。
5.  **口诀**：
    > “去重先排序，Unique 搬前头，
    > 返回新界标，Erase 截后头。
    > 若不截尾巴，尺寸仍依旧，
    > 脏数据残留，程序必出错。”

### 🏆 实战代码片段 (Copy-Paste Ready)

```cpp
// 1. 基础整数去重
void removeDuplicates(vector<int>& nums) {
    sort(nums.begin(), nums.end());
    nums.erase(unique(nums.begin(), nums.end()), nums.end());
}

// 2. 字符串忽略大小写去重
void removeCaseInsensitiveDuplicates(vector<string>& strs) {
    // 排序：忽略大小写
    sort(strs.begin(), strs.end(), [](const string& a, const string& b) {
        string la = a, lb = b;
        transform(la.begin(), la.end(), la.begin(), ::tolower);
        transform(lb.begin(), lb.end(), lb.begin(), ::tolower);
        return la < lb;
    });
    // 去重：忽略大小写
    auto it = unique(strs.begin(), strs.end(), [](const string& a, const string& b) {
        if (a.size() != b.size()) return false;
        for (size_t i = 0; i < a.size(); ++i)
            if (tolower(a[i]) != tolower(b[i])) return false;
        return true;
    });
    strs.erase(it, strs.end());
}

// 3. List 专用 (不需要 erase)
void removeListDuplicates(list<int>& lst) {
    lst.sort();       // list 成员函数 sort
    lst.unique();     // list 成员函数 unique (直接删除节点)
}
```

掌握这套组合拳，你就能在 C++ 中游刃有余地处理任何去重需求！