---
created: 2026-02-25T23:34
updated: 2026-02-28T12:16
---
这是一份为您精心整理的 **C++ `std::vector` 全方位方法详解**。

`std::vector` 是 C++ 标准模板库（STL）中最常用、最强大的**动态数组**容器。它封装了动态大小的数组，能够自动管理内存，支持随机访问，并在末尾高效地添加/删除元素。

这份指南严格遵循 C++11 及以上标准，**重点补充了每个方法的详细参数说明、返回值含义以及具体的代码示例**。

---

# 📚 C++ `std::vector` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // sort, find 等算法需要
#include <numeric>   // iota 等需要

using namespace std;
```

> **核心特性速览**：
> 1. **连续存储**：元素在内存中连续存放，支持指针算术和缓存友好访问。
> 2. **动态扩容**：空间不足时自动分配更大内存（通常 2 倍扩容）。
> 3. **随机访问**：支持 `[]` 和 `at()`，访问时间复杂度 $O(1)$。
> 4. **尾部高效**：`push_back` / `pop_back` 均摊 $O(1)$。
> 5. **中间低效**：中间插入/删除需移动元素，复杂度 $O(N)$。

---

## 1️⃣ 构造与初始化 (Construction & Initialization)
`vector` 提供了多种创建方式，理解它们对性能优化很重要。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`vector()`** | 无 | - | 默认构造，生成空 vector。 |
| **`vector(size_t n)`** | `n`: 元素个数 | - | 构造包含 `n` 个元素的 vector，值初始化为默认值 (如 0)。 |
| **`vector(size_t n, const T& val)`** | `n`: 个数`val`: 初始值 | - | 构造包含 `n` 个 `val` 的 vector。 |
| **`vector(InputIt first, InputIt last)`** | `first`, `last`: 迭代器范围 | - | 范围构造，从 `[first, last)` 复制元素。 |
| **`vector(const vector& other)`** | `other`: 另一个 vector | - | 拷贝构造，深拷贝。 |
| **`vector(vector&& other)`** | `other`: 右值引用 (C++11) | - | 移动构造，窃取资源，`other` 变为空。 |
| **`vector(initializer_list<T> init)`** | `init`: 初始化列表 (C++11) | - | 列表构造，如 `{1, 2, 3}`。 |
**二维`vector`初始化：**

在 C++ 中，初始化 `vector` 二维数组（即 `vector<vector<T>>`）有几种常用方法，取决于你是否知道行列数以及是否需要特定初始值。

以下是 **5 种最常用**的初始化方式：

---

 1️⃣ 指定行列数 + 初始值（最常用）
这是动态规划（DP）或需要固定大小矩阵时的标准写法。
**语法**：`vector<vector<T>> 名字(行数, vector<T>(列数, 初始值));`

```cpp
#include <vector>
using namespace std;

int main() {
    int rows = 3;
    int cols = 4;
    int init_val = 0;

    // 创建一个 3行4列 的二维数组，所有元素初始化为 0
    vector<vector<int>> matrix(rows, vector<int>(cols, init_val));

    // 验证
    // matrix[0] 是 vector<int>(4, 0)
    // matrix[1] 是 vector<int>(4, 0)
    // ...
    
    return 0;
}
```
> **适用场景**：DP 表格、网格地图、需要预分配空间的场景。

---

 2️⃣ 使用初始化列表（已知具体数据）
如果你已经知道具体的数值，可以直接用 `{}` 赋值。
**注意**：这种方式创建的二维数组，每一行的列数可以不同（不规则矩阵）。

```cpp
int main() {
    // 直接初始化
    vector<vector<int>> matrix = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    // 或者不规则矩阵（锯齿状数组）
    vector<vector<int>> jagged = {
        {1, 2},       // 第 0 行 2 列
        {3, 4, 5, 6}, // 第 1 行 4 列
        {7}           // 第 2 行 1 列
    };

    return 0;
}
```
> **适用场景**：测试用例、硬编码的小矩阵、图论中的邻接表。

---

 3️⃣ 先定义大小，后逐行赋值
如果你需要先创建空壳，再在循环中填充数据。

```cpp
int main() {
    int n = 3;
    // 先创建 n 个空的 vector
    vector<vector<int>> matrix(n); 

    for (int i = 0; i < n; ++i) {
        // 为每一行单独分配大小并初始化
        matrix[i].resize(5, -1); // 第 i 行变为 5 列，初始值为 -1
        
        // 或者手动 push_back
        // matrix[i].push_back(i * 10);
    }

    return 0;
}
```
> **适用场景**：每一行的列数不一样，且需要在运行时动态决定。

---

 4️⃣ 动态扩容（类似 Python 的 append）
完全动态地构建，不需要预先知道大小。

```cpp
int main() {
    vector<vector<int>> matrix;

    // 添加第一行
    vector<int> row1 = {1, 2, 3};
    matrix.push_back(row1);

    // 添加第二行（直接构造）
    matrix.push_back({4, 5, 6});

    // 添加第三行（手动构建）
    vector<int> row3;
    row3.push_back(7);
    row3.push_back(8);
    matrix.push_back(row3);

    return 0;
}
```
> **适用场景**：数据流处理、不确定总行数的场景。

---

 5️⃣ 特殊技巧：快速创建全 0 或全 1 矩阵
在算法题中，经常需要快速创建一个 $N \times N$ 的全 0 矩阵。

```cpp
int n = 100;
// 创建 100x100 的全 0 矩阵
vector<vector<int>> dp(n, vector<int>(n, 0));

// 创建 100x100 的全 -1 矩阵 (常用于记忆化搜索标记)
vector<vector<int>> memo(n, vector<int>(n, -1));
```

---

 ⚠️ 常见错误与注意事项

 ❌ 错误 1：访问越界
```cpp
vector<vector<int>> v(3, vector<int>(3));
v[3][0] = 1; // ❌ 崩溃！行下标最大是 2
v[0][3] = 1; // ❌ 崩溃！列下标最大是 2
```

 ❌ 错误 2：混淆 `resize` 和构造函数
```cpp
vector<vector<int>> v;
v.resize(3);      // 现在有 3 行，但每行是空的 (size=0)
v[0][0] = 1;      // ❌ 崩溃！因为 v[0] 还没有列空间

// ✅ 正确做法：
v[0].resize(3);   // 给第 0 行分配 3 列
v[0][0] = 1;      // ✅ 正常
```

 💡 性能提示
- **连续内存？** `vector<vector<int>>` **不是**连续内存。每一行都是一个独立的 `vector` 对象，分散在堆的不同位置。
- **缓存友好性**：如果需要极高的性能（如图像处理、大规模矩阵运算），建议使用**一维 `vector` 模拟二维**：
  ```cpp
  // 模拟 3行4列
  vector<int> mat(3 * 4, 0); 
  // 访问 (i, j)
  int val = mat[i * 4 + j]; 
  ```
  这样内存是连续的，缓存命中率更高。但在一般算法题中，`vector<vector<int>>` 足够方便且够用。

 总结速查表

| 需求            | 代码示例                                               |
| :------------ | :------------------------------------------------- |
| **固定大小 + 初值** | `vector<vector<int>> v(n, vector<int>(m, 0));`     |
| **已知数据**      | `vector<vector<int>> v = {{1,2}, {3,4}};`          |
| **动态加行**      | `v.push_back({1, 2, 3});`                          |
| **记忆化搜索专用**   | `vector<vector<int>> memo(n, vector<int>(2, -1));` |


### 💻 代码示例
```cpp
int main() {
    // 1. 默认构造
    vector<int> v1; 
    
    // 2. 指定大小 (默认初始化)
    vector<int> v2(5);        // {0, 0, 0, 0, 0}
    
    // 3. 指定大小和初始值
    vector<int> v3(5, 10);    // {10, 10, 10, 10, 10}
    
    // 4. 范围构造
    vector<int> v4(v3.begin(), v3.begin() + 3); // {10, 10, 10}
    
    // 5. 初始化列表 (最常用)
    vector<int> v5{1, 2, 3, 4, 5};
    
    // 6. 移动构造 (高效)
    vector<int> v6 = move(v5); // v5 变为空，v6 拥有数据
    
    cout << "v3 size: " << v3.size() << endl;
    return 0;
}
```

---

## 2️⃣ 容量与状态 (Capacity & State)
区分 `size()` 和 `capacity()` 是理解 vector 性能的关键。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`size()`** | 无 | `size_t` | 返回当前实际元素个数。 |
| **`empty()`** | 无 | `bool` | 若为空 (`size()==0`) 返回 `true`。 |
| **`capacity()`** | 无 | `size_t` | 返回当前已分配内存可容纳的元素总数（不含未分配空间）。 |
| **`max_size()`** | 无 | `size_t` | 返回理论最大长度限制。 |
| **`reserve(size_t n)`** | `n`: 期望容量 | `void` | **预分配**至少 `n` 个元素的空间。若 `n > capacity` 则扩容，否则不做操作。**不改变 size**。 |
| **`resize(size_t n)`****`resize(size_t n, const T& val)`** | `n`: 新长度`val`: 填充值 (默认构造) | `void` | 改变容器大小。若 `n > size`，新增元素初始化为 `val`；若 `n < size`，截断多余元素。 |
| **`shrink_to_fit()`** | 无 | `void` (C++11) | 请求释放未使用的内存，使 `capacity` 等于 `size` (非强制，取决于实现)。 |
| **`clear()`** | 无 | `void` | 清空所有元素，`size` 变为 0，但 `capacity` 通常保持不变。 |

### 💡 性能提示
- 在循环中大量 `push_back` 前，务必使用 `reserve()` 预分配空间，避免多次内存重分配和数据拷贝。

### 💻 代码示例
```cpp
int main() {
    vector<int> v;
    
    // 预分配空间，避免频繁扩容
    v.reserve(100); 
    cout << "Size: " << v.size() << ", Cap: " << v.capacity() << endl; // 0, 100
    
    // 改变大小
    v.resize(5, 1);      // {1, 1, 1, 1, 1}, size=5
    v.resize(3);         // {1, 1, 1}, size=3 (截断)
    
    // 清空
    v.clear();           // size=0, cap 仍为 100
    
    // 收缩内存 (可选)
    v.shrink_to_fit();   // 请求 cap 变为 0
    
    return 0;
}
```

---

## 3️⃣ 元素访问 (Element Access)
用于获取或修改特定位置的元素。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`operator[]`** | `pos`: 下标 | `T&` | 返回 `pos` 处元素引用。**不检查边界**，越界行为未定义 (最快)。 |
| **`at(size_t pos)`** | `pos`: 下标 | `T&` | 返回 `pos` 处元素引用。**检查边界**，越界抛出 `out_of_range` 异常。 |
| **`front()`** | 无 | `T&` | 返回第一个元素引用 (C++11)。等价于 `v[0]`。 |
| **`back()`** | 无 | `T&` | 返回最后一个元素引用 (C++11)。等价于 `v[v.size()-1]`。 |
| **`data()`** | 无 | `T*` (C++11) | 返回底层数组的原始指针。可用于 C 风格 API 或 `memcpy`。 |

### 💻 代码示例
```cpp
int main() {
    vector<int> v = {10, 20, 30, 40, 50};
    
    // 访问
    int a = v[0];        // 10 (快，不安全)
    int b = v.at(1);     // 20 (安全，稍慢)
    
    // 首尾
    cout << "First: " << v.front() << ", Last: " << v.back() << endl;
    
    // 修改
    v[0] = 100;
    v.back() = 500;
    
    // 获取原始指针
    int* ptr = v.data();
    // 可用于 C 函数: some_c_func(ptr, v.size());
    
    try {
        v.at(100); // 抛出异常
    } catch (...) {
        cout << "Out of range!" << endl;
    }
    
    return 0;
}
```

---

## 4️⃣ 修改操作 (Modifiers)
增删改的核心操作。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`assign(...)`** | `n, val` 或 迭代器范围 | `void` | 用新内容替换当前所有内容。 |
| **`push_back(const T& val)`** | `val`: 值 | `void` | 在末尾添加元素。若容量不足自动扩容。 |
| **`emplace_back(args...)`** | `args`: 构造参数 (C++11) | `void` | **原地构造**末尾元素。避免拷贝/移动开销，效率更高。 |
| **`pop_back()`** | 无 | `void` | 移除末尾元素。 |
| **`insert(pos, val)`** | `pos`: 迭代器位置`val`: 值 (或 `n, val`) | `iterator` | 在 `pos` 之前插入元素。返回指向新插入元素的迭代器。 |
| **`emplace(pos, args...)`** | `pos`: 迭代器`args`: 构造参数 | `iterator` | 在 `pos` 之前原地构造元素。 |
| **`erase(pos)`****`erase(first, last)`** | `pos`: 迭代器`first`, `last`: 范围 | `iterator` | 删除元素。返回**下一个**元素的迭代器。 |
| **`swap(vector& other)`** | `other`: 另一个 vector | `void` | 交换两个 vector 内容 ($O(1)$)。 |

### 💡 迭代器失效警告
- `push_back` / `emplace_back`: 若导致扩容，**所有**迭代器、指针、引用失效。
- `insert` / `erase`: 插入点/删除点及之后的所有迭代器失效。

### 💻 代码示例
```cpp
int main() {
    vector<int> v = {1, 2, 3};
    
    // 尾部操作
    v.push_back(4);
    v.emplace_back(5); // 直接构造，等价于 push_back(5)
    v.pop_back();      // 移除 5
    
    // 插入 (在索引 1 处插入 99)
    auto it = v.insert(v.begin() + 1, 99); // {1, 99, 2, 3, 4}
    cout << "Inserted at: " << *it << endl;
    
    // 删除 (删除索引 1 处的元素)
    it = v.erase(v.begin() + 1); // 返回指向 2 的迭代器
    cout << "Next element: " << *it << endl; // 2
    
    // 范围删除
    v.erase(v.begin() + 1, v.begin() + 3); // 删除 2, 3
    
    // 遍历删除模式 (安全)
    v = {1, 2, 3, 4, 5};
    for (auto it = v.begin(); it != v.end(); ) {
        if (*it % 2 == 0) {
            it = v.erase(it); // erase 返回下一个有效迭代器
        } else {
            ++it;
        }
    }
    // v: {1, 3, 5}
    
    return 0;
}
```

---

## 5️⃣ 迭代器 (Iterators)
用于遍历容器。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`begin()` / `end()`** | 无 | `iterator` | 正向迭代器，指向首/尾后一位。 |
| **`rbegin()` / `rend()`** | 无 | `reverse_iterator` | 反向迭代器，指向尾/首前一位。 |
| **`cbegin()` / `cend()`** | 无 | `const_iterator` | 只读正向迭代器 (C++11)。 |
| **`crbegin()` / `crend()`** | 无 | `const_reverse_iterator` | 只读反向迭代器 (C++11)。 |

### 💻 代码示例
```cpp
int main() {
    vector<int> v = {10, 20, 30};
    
    // 正向遍历
    for (auto it = v.begin(); it != v.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;
    
    // 反向遍历
    for (auto rit = v.rbegin(); rit != v.rend(); ++rit) {
        cout << *rit << " "; // 30 20 10
    }
    cout << endl;
    
    // 范围 for (推荐)
    for (int x : v) cout << x << " ";
    cout << endl;
    
    return 0;
}
```

---

## 6️⃣ 算法配合 (Algorithms Integration)
`vector` 与 `<algorithm>` 库配合使用非常强大。

| 算法 | 功能 | 示例 |
| :--- | :--- | :--- |
| **`sort`** | 排序 | `sort(v.begin(), v.end());` |
| **`find`** | 查找 | `auto it = find(v.begin(), v.end(), val);` |
| **`unique`** | 去重 (需先排序) | `v.erase(unique(v.begin(), v.end()), v.end());` |
| **`reverse`** | 反转 | `reverse(v.begin(), v.end());` |
| **`accumulate`** | 求和 | `int sum = accumulate(v.begin(), v.end(), 0);` |

### 💻 代码示例
```cpp
int main() {
    vector<int> v = {5, 2, 9, 2, 1};
    
    // 排序
    sort(v.begin(), v.end()); // {1, 2, 2, 5, 9}
    
    // 去重 (unique 只移动元素，不改变 size，需配合 erase)
    auto last = unique(v.begin(), v.end()); 
    v.erase(last, v.end()); // {1, 2, 5, 9}
    
    // 查找
    auto it = find(v.begin(), v.end(), 5);
    if (it != v.end()) cout << "Found 5\n";
    
    // 求和
    int sum = accumulate(v.begin(), v.end(), 0); // 17
    
    // 反转
    reverse(v.begin(), v.end()); // {9, 5, 2, 1}
    
    return 0;
}
```

---

## 7️⃣ `vector` vs `list` vs `deque` 终极对比

| 特性 | `std::vector` | `std::list` | `std::deque` |
| :--- | :--- | :--- | :--- |
| **底层结构** | **动态数组** (连续内存) | 双向链表 | 分段连续内存 |
| **随机访问** | **$O(1)$** (极快) | $O(N)$ (不支持) | $O(1)$ (稍慢) |
| **尾部增删** | **$O(1)$** (均摊) | $O(1)$ | $O(1)$ |
| **头部增删** | $O(N)$ (慢) | $O(1)$ | **$O(1)$** |
| **中间增删** | $O(N)$ (需移动) | **$O(1)$** (已知迭代器) | $O(N)$ |
| **缓存友好** | **极高** (连续) | 低 (分散) | 中 |
| **迭代器失效** | 扩容或中间修改时大量失效 | 仅被删元素失效 | 较复杂，中间修改易失效 |
| **适用场景** | **通用首选**，读多写少，随机访问 | 频繁中间插入/删除，不需要随机访问 | 需要两端频繁插入/删除 |

---

### 💡 核心总结
1. **首选容器**：在没有特殊需求（如频繁中间插入）时，**永远优先选择 `vector`**。
2. **性能优化**：已知大致大小时，务必使用 `reserve()` 预分配内存。
3. **删除技巧**：遍历删除时，使用 `it = v.erase(it)` 模式。
4. **去重排序**：`sort` + `unique` + `erase` 是标准去重三板斧。
5. **陷阱**：
   - 不要保存 `vector` 的迭代器或指针长期有效，扩容会导致它们失效。
   - `vector<bool>` 是特化版本，节省空间但行为怪异（不能取地址），尽量避免使用，可用 `vector<char>` 代替。

**一句话口诀**：
> “连续内存 Vector 强，随机访问它最棒；
> 预留空间 reserve 好，尾部增删效率高；
> 中间若要频繁插，列表 List 来帮忙。”