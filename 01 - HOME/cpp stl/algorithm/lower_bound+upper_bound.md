---
created: 2026-03-08T16:36
updated: 2026-03-09T00:01
---
这是一份为您精心整理的 **C++ `std::lower_bound` 与 `std::upper_bound` 全方位方法详解**。

这两个函数是 C++ STL 算法库（`<algorithm>`）中基于**二分查找**实现的“双子星”。它们的时间复杂度均为 **$O(\log n)$**，是处理有序数据、统计频次、查找边界的利器。

这份指南严格遵循 C++11 及以上标准，**重点补充了每个方法的详细参数说明、返回值含义、边界行为以及具体的代码示例**。

---

# 📚 C++ `lower_bound` & `upper_bound` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // 必须包含此头文件

using namespace std;
```

> **核心特性速览**：
> 1. **前提条件**：操作的数据序列**必须是有序的**（默认升序）。若无序，结果未定义。
> 2. **时间复杂度**：$O(\log n)$，远快于线性查找 $O(n)$。
> 3. **返回值**：返回的是**迭代器**（Iterator），指向满足条件的第一个元素位置。
> 4. **左闭右开**：查找范围通常为 `[first, last)`，即包含 `first`，不包含 `last`。

---

## 1️⃣ 核心概念对比 (Concept Comparison)

这是理解两者的关键：**它们都在找“第一个”满足条件的元素，但条件不同。**

| 特性 | `lower_bound` (下界) | `upper_bound` (上界) |
| :--- | :--- | :--- |
| **查找条件** | 第一个 **大于等于** (`>=`) 目标值的元素 | 第一个 **严格大于** (`>`) 目标值的元素 |
| **数学表达** | $\min \{ x \mid x \ge target \}$ | $\min \{ x \mid x > target \}$ |
| **若值存在** | 返回该值**第一次**出现的位置 | 返回该值**最后一次**出现位置的**下一位** |
| **若值不存在** | 返回第一个比它大的元素位置 | 返回第一个比它大的元素位置 (同左) |
| **若所有值都小** | 返回 `end()` | 返回 `end()` |
| **典型用途** | 判断是否存在、查找左边界、插入位置 | 查找右边界、计算元素个数 |

---

## 2️⃣ 函数签名与参数详解 (Function Signatures)

### 🔹 `std::lower_bound`
```cpp
// 版本 1: 默认比较 (使用 operator<)
template< class ForwardIt, class T >
ForwardIt lower_bound( ForwardIt first, ForwardIt last, const T& value );

// 版本 2: 自定义比较函数 (Comp)
template< class ForwardIt, class T, class Compare >
ForwardIt lower_bound( ForwardIt first, ForwardIt last, const T& value, Compare comp );
```

### 🔹 `std::upper_bound`
```cpp
// 版本 1: 默认比较 (使用 operator<)
template< class ForwardIt, class T >
ForwardIt upper_bound( ForwardIt first, ForwardIt last, const T& value );

// 版本 2: 自定义比较函数 (Comp)
template< class ForwardIt, class T, class Compare >
ForwardIt upper_bound( ForwardIt first, ForwardIt last, const T& value, Compare comp );
```

### 📝 参数说明
| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `first`, `last` | 迭代器 | 定义查找的范围 `[first, last)`。通常是 `vec.begin()` 和 `vec.end()`。 |
| `value` | T | 要查找的目标值。 |
| `comp` | 函数对象 | **(可选)** 自定义比较规则。签名应为 `bool comp(const Type &a, const Type &b)`。注意：该函数应在 `a < b` 时返回 `true`。对于降序数组，需传入 `greater<T>()`。 |

### ↩️ 返回值
- **成功**：返回指向**第一个**满足条件元素的迭代器。
- **失败**：若范围内所有元素都不满足条件（即所有元素都小于 `value`），返回 `last` (通常是 `end()`)。

---

## 3️⃣ 图解与代码示例 (Visual & Examples)

假设我们有一个升序数组：
`nums = {1, 3, 5, 5, 5, 7, 9}`
索引：`0, 1, 2, 3, 4, 5, 6`
目标值：`target = 5`

### 💻 场景一：标准升序查找

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    vector<int> nums = {1, 3, 5, 5, 5, 7, 9};
    int target = 5;

    // 1. lower_bound: 找第一个 >= 5 的数
    auto low = lower_bound(nums.begin(), nums.end(), target);
    
    // 2. upper_bound: 找第一个 > 5 的数
    auto high = upper_bound(nums.begin(), nums.end(), target);

    // 输出结果
    cout << "Array: {1, 3, 5, 5, 5, 7, 9}" << endl;
    cout << "Target: " << target << endl;
    
    if (low != nums.end()) {
        cout << "lower_bound value: " << *low << " (Index: " << (low - nums.begin()) << ")" << endl;
        // 预期: 值 5, 索引 2 (第一个 5)
    } else {
        cout << "lower_bound: Not found (all smaller)" << endl;
    }

    if (high != nums.end()) {
        cout << "upper_bound value: " << *high << " (Index: " << (high - nums.begin()) << ")" << endl;
        // 预期: 值 7, 索引 5 (第一个比 5 大的数)
    } else {
        cout << "upper_bound: Not found (all <= target)" << endl;
    }

    return 0;
}
```

**🔍 图解分析**：
```text
索引：   0   1   2   3   4   5   6
数值：  [1,  3,  5,  5,  5,  7,  9]
                  ^               ^
                  |               |
           lower_bound       upper_bound
           (第一个>=5)       (第一个>5)
           返回索引 2        返回索引 5
```

---

### 💡 黄金组合技巧：统计元素出现次数

利用 `upper_bound` 和 `lower_bound` 的差值，可以瞬间算出某个元素在有序数组中出现的次数。

**公式**：`count = upper_bound(...) - lower_bound(...)`

```cpp
    // 接上面的代码
    int count = high - low; // 迭代器相减得到距离
    cout << "Number of " << target << ": " << count << endl; 
    // 输出: 3 (因为索引 5 - 索引 2 = 3)
```

---

### 💻 场景二：判断元素是否存在

如果你想检查 `target` 是否在数组中：

```cpp
    auto it = lower_bound(nums.begin(), nums.end(), target);
    
    // 检查两个条件：
    // 1. it 没有越界 (it != end)
    // 2. 指向的值确实等于 target (防止 target 比所有数都大，返回了 end，或者返回了比 target 大的数)
    if (it != nums.end() && *it == target) {
        cout << "Found " << target << " at index " << (it - nums.begin()) << endl;
    } else {
        cout << target << " not found." << endl;
    }
```

---

### 💻 场景三：降序数组的处理

如果数组是降序排列 `{9, 7, 5, 5, 5, 3, 1}`，必须传入自定义比较器 `greater<int>()`，否则二分查找逻辑会失效。

```cpp
    vector<int> nums_desc = {9, 7, 5, 5, 5, 3, 1};
    int target = 5;

    // 注意第三个参数：greater<int>()
    // 在降序中，lower_bound 找的是第一个 <= target 的元素 (逻辑反转)
    // 具体行为取决于 comp(a, b) 的定义。
    // 使用 greater 时：
    // lower_bound 找第一个 "不满足 (element > value)" 的元素，即第一个 element <= value
    // upper_bound 找第一个 "不满足 (element >= value)" 的元素，即第一个 element < value
    
    auto low = lower_bound(nums_desc.begin(), nums_desc.end(), target, greater<int>());
    auto high = upper_bound(nums_desc.begin(), nums_desc.end(), target, greater<int>());

    // 验证
    // low 应该指向第一个 5 (索引 2)
    // high 应该指向 3 (索引 5)
    
    if (low != nums_desc.end()) 
        cout << "Desc Lower: " << *low << " (Index: " << (low - nums_desc.begin()) << ")" << endl;
    
    if (high != nums_desc.end()) 
        cout << "Desc Upper: " << *high << " (Index: " << (high - nums_desc.begin()) << ")" << endl;
        
    // 个数计算依然有效
    cout << "Count: " << (high - low) << endl;
```

---

## 4️⃣ 常见陷阱与注意事项 (Pitfalls)

| 陷阱 | 描述 | 解决方案 |
| :--- | :--- | :--- |
| **未排序** | 对无序数组使用，结果随机且错误。 | 务必先 `sort(vec.begin(), vec.end())`。 |
| **返回值解引用** | 直接 `*lower_bound(...)` 而不检查是否等于 `end()`。 | 永远先判断 `if (it != vec.end())`。 |
| **浮点数精度** | 对 `double` 使用相等判断 (`*it == target`)。 | 使用误差范围 `abs(*it - target) < 1e-9`。 |
| **降序忘记传参** | 降序数组直接使用默认参数。 | 必须传入 `greater<Type>()` 作为第四个参数。 |
| **空容器** | 对空 vector 调用。 | 安全，直接返回 `begin()` (即 `end()`)，但解引用会崩溃。 |

---

## 5️⃣ 性能对比 (Performance)

| 操作 | 线性查找 (`find`) | `lower_bound` / `upper_bound` |
| :--- | :--- | :--- |
| **数据结构要求** | 无序或有序均可 | **必须有序** |
| **时间复杂度** | $O(N)$ | **$O(\log N)$** |
| **适用场景** | 小数据量、无序数据 | 大数据量、多次查询、有序数据 |
| **示例** | 100 万元素，最坏查 100 万次 | 100 万元素，最坏查约 20 次 ($\log_2 10^6 \approx 20$) |

---

## 6️⃣ 总结速查表 (Cheat Sheet)

| 需求 | 代码片段 | 说明 |
| :--- | :--- | :--- |
| **找左边界** (第一个 $\ge$ val) | `lower_bound(begin, end, val)` | 若存在，指向该值首次出现处。 |
| **找右边界** (第一个 $>$ val) | `upper_bound(begin, end, val)` | 指向该值最后一次出现处的**后一位**。 |
| **统计个数** | `upper_bound(...) - lower_bound(...)` | 高效计算重复元素次数。 |
| **判断存在** | `it = lower_bound(...); if(it!=end && *it==val)` | 标准存在性检查。 |
| **降序查找** | `..., val, greater<int>())` | 必须加比较器。 |
| **获取索引** | `it - vec.begin()` | 迭代器转下标。 |
### 💡常用转化
设`nums`为非递减**整数**数组，长为`n`。

| 需求                  | 写法                                                                | 如果不存在                       |
| ------------------- | ----------------------------------------------------------------- | --------------------------- |
| $\geq x$ 的第一个元素的下标  | `lower_bound(nums.begin(), nums.end(), x) - nums.begin()`         | `nums.end() - nums.begin()` |
| $> x$ 的第一个元素的下标     | `lower_bound(nums.begin(), nums.end(), x + 1) - nums.begin()`     | `nums.end() - nums.begin()` |
| $< x$ 的最后一个元素的下标    | `lower_bound(nums.begin(), nums.end(), x) - nums.begin() - 1`     | `-1`                        |
| $\leq x$ 的最后一个元素的下标 | `lower_bound(nums.begin(), nums.end(), x + 1) - nums.begin() - 1` | `-1`                        |


| 需求            | 写法                                                                  |
| ------------- | ------------------------------------------------------------------- |
| $< x$ 的元素个数   | `lower_bounnd(nums.begin(), nums.end(), x) - nums.begin()`          |
| $\le x$ 的元素个数 | `lower_bounnd(nums.begin(), nums.end(), x + 1) - nums.begin()`      |
| $\ge x$ 的元素个数 | `n - (lower_bound(nums.begin(), nums.end(), x) - nums.begin())`     |
| $> x$ 的元素个数   | `n - (lower_bound(nums.begin(), nums.end(), x + 1) - nums.begin())` |


### 💡 核心口诀
> “**Lower 找大于等于，Upper 找大于；**”
> “**两者相减算个数，有序前提莫忘记；**”
> “**若是降序加 Greater，返回之前判 End 际。**”