---
created: 2026-02-25T23:34
updated: 2026-02-27T11:19
---
`std::vector` 是 C++ 标准模板库（STL）中最常用、最强大的**动态数组**容器。它封装了动态大小的数组，能够自动管理内存，支持随机访问，并在末尾高效地添加/删除元素。

以下是 `std::vector` 的详细介绍，包括核心特性、构造方法、常用操作、内存机制及代码示例。

---

### 1. 核心特性
- **连续存储**：元素在内存中连续存放，支持指针算术和缓存友好访问。
- **动态扩容**：当空间不足时，自动分配更大的内存块并迁移数据（通常是 2 倍扩容）。
- **随机访问**：支持 `[]` 和 `at()`，访问时间复杂度为 $O(1)$。
- **尾部高效**：在末尾 `push_back` / `pop_back` 的均摊时间复杂度为 $O(1)$。
- **中间低效**：在中间或头部插入/删除元素需要移动后续所有元素，复杂度为 $O(N)$。

**头文件**：
```cpp
#include <vector>
using namespace std;
```

---

### 2. 构造函数 (Constructors)
`vector` 提供了多种创建方式，理解它们对性能优化很重要。

| 构造方式 | 代码示例 | 说明 |
| :--- | :--- | :--- |
| **默认构造** | `vector<int> v1;` | 创建一个空 vector，大小为 0。 |
| **填充构造** | `vector<int> v2(5, 10);` | 创建大小为 5 的 vector，所有元素初始化为 10。 |
| **范围构造** | `vector<int> v3(v2.begin(), v2.end());` | 从另一个容器的迭代器范围复制初始化。 |
| **拷贝构造** | `vector<int> v4(v2);` | 深拷贝另一个 vector。 |
| **移动构造** | `vector<int> v5(move(v2));` | **C++11**：窃取 v2 的资源，v2 变为空（高效，无内存复制）。 |
| **列表初始化** | `vector<int> v6{1, 2, 3};` | **C++11**：使用初始化列表直接赋值。 |

---

### 3. 常用成员函数详解

#### A. 容量与大小 (Capacity & Size)
区分 `size()` 和 `capacity()` 是理解 vector 性能的关键。
- `size()`: 当前实际元素个数。
- `capacity()`: 当前分配的总内存空间能容纳的元素个数（未使用的空间不销毁对象）。
- `empty()`: 判断是否为空。
- `reserve(n)`: **预分配**至少能容纳 n 个元素的内存。**不会改变 size**，但能避免多次扩容带来的性能损耗。
- `resize(n, val)`: 改变容器大小。如果 n > size，新元素初始化为 val；如果 n < size，多余元素被销毁。

```cpp
vector<int> v;
v.reserve(100); // 预分配空间，避免 push_back 时频繁 realloc
cout << v.size() << ", " << v.capacity(); // 输出: 0, 100

v.resize(5, 0); // 大小变为 5，内容为 {0,0,0,0,0}
```

#### B. 元素访问 (Element Access)
- `v[i]`: **最快**，但不检查边界，越界会导致未定义行为（崩溃）。
- `v.at(i)`: 较慢，**会检查边界**，越界抛出 `std::out_of_range` 异常。
- `v.front()`: 返回第一个元素引用。
- `v.back()`: 返回最后一个元素引用。
- `v.data()`: 返回底层数组的原始指针 (`int*`)，可用于 C 风格 API。

#### C. 修改操作 (Modifiers)
- **尾部操作**：
  - `push_back(val)`: 尾部添加元素（若容量不足会自动扩容）。
  - `pop_back()`: 删除尾部元素。
  - `emplace_back(args...)`: **C++11**，直接在尾部构造元素（避免拷贝/移动开销，效率更高）。
  
- **插入与删除**（中间操作，耗时 $O(N)$）：
  - `insert(pos, val)`: 在迭代器 `pos` 位置插入。
  - `erase(pos)`: 删除迭代器 `pos` 位置的元素，返回下一个元素的迭代器。
  - `clear()`: 清空所有元素，size 变为 0，但 capacity 通常不变。

---

### 4. 关键机制：扩容与性能优化

#### 为什么需要 `reserve`？
当 `vector` 空间不足时，它会：
1. 分配一块更大的新内存（通常是当前的 1.5 倍或 2 倍）。
2. 将旧数据**拷贝/移动**到新内存。
3. 释放旧内存。

如果在循环中大量 `push_back` 而不 `reserve`，会导致多次内存重分配和数据拷贝，严重影响性能。

**优化示例**：
```cpp
// ❌ 低效：可能触发多次扩容和内存拷贝
vector<int> v1;
for (int i = 0; i < 10000; ++i) {
    v1.push_back(i);
}

// ✅ 高效：只分配一次内存
vector<int> v2;
v2.reserve(10000); 
for (int i = 0; i < 10000; ++i) {
    v2.push_back(i);
}
```

#### `swap` 技巧：收缩内存
`vector` 删除元素后，`capacity` 通常不会减小。如果想释放多余内存：
```cpp
vector<int>(v).swap(v); 
// 或者 C++11: v.shrink_to_fit(); (非强制，取决于实现)
```

---

### 5. 综合代码示例

```cpp
#include <iostream>
#include <vector>
#include <algorithm> // for copy
#include <numeric>   // for iota

using namespace std;

int main() {
    // 1. 初始化
    vector<int> nums = {1, 2, 3, 4, 5};
    vector<string> strs(3, "hello"); // {"hello", "hello", "hello"}

    // 2. 访问与修改
    nums.push_back(6);          // {1, 2, 3, 4, 5, 6}
    nums[0] = 10;               // 修改第一个元素
    nums.pop_back();            // 移除 6
    
    // 安全访问
    try {
        cout << nums.at(10) << endl; // 抛出异常
    } catch (const out_of_range& e) {
        cout << "越界访问捕获!" << endl;
    }

    // 3. 迭代器遍历
    for (auto it = nums.begin(); it != nums.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;

    // 4. 范围 for 循环 (C++11)
    for (int n : nums) {
        cout << n << " ";
    }
    cout << endl;

    // 5. 插入与删除 (中间操作)
    // 在索引 1 处插入 99
    nums.insert(nums.begin() + 1, 99); 
    
    // 删除索引 1 处的元素 (即刚才插入的 99)
    // erase 返回下一个元素的迭代器，防止迭代器失效
    nums.erase(nums.begin() + 1); 

    // 6. 高级用法：emplace_back (原地构造)
    vector<vector<int>> matrix;
    matrix.emplace_back(3, 0); // 直接构造一个包含3个0的vector，无需临时对象

    // 7. 获取原始指针 (用于 C API)
    int* raw_ptr = nums.data();
    
    // 8. 算法配合 (如排序)
    sort(nums.begin(), nums.end());

    return 0;
}
```

---

### 6. 常见陷阱与注意事项

1. **迭代器失效 (Iterator Invalidation)**
   - **插入/删除元素**（除了 `push_back` 且未扩容的情况）会导致指向该位置及之后元素的迭代器失效。
   - **扩容**（`push_back` 导致 capacity 增加）会导致**所有**迭代器、指针、引用失效。
   - **对策**：执行插入/删除后，不要继续使用旧的迭代器，应使用函数返回值（如 `erase` 返回的迭代器）重新获取。

2. **`bool` 特化**
   - `std::vector<bool>` 是一个特殊的模板特化版本，为了节省空间，它每个 bool 只占 1 个 bit。
   - **缺点**：`operator[]` 返回的不是 `bool&` 引用，而是一个代理对象。不能直接取地址 `&v[0]`。
   - **建议**：如果需要存布尔值且需要引用语义，请使用 `std::vector<char>` 或 `std::deque<bool>`。

3. **二维 Vector 初始化**
   ```cpp
   // 正确：创建 3行4列 的矩阵，初始值为 0
   vector<vector<int>> mat(3, vector<int>(4, 0));
   ```

### 总结
`std::vector` 是 C++ 中的首选容器。
- **何时使用**：需要随机访问、主要在尾部增删、对缓存命中率要求高。
- **何时避免**：需要在头部或中间频繁插入/删除（改用 `std::deque` 或 `std::list`）。
- **最佳实践**：已知大致大小时，务必使用 `reserve()` 预分配内存。