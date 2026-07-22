---
created: 2026-02-25T23:42
updated: 2026-03-06T14:36
---
这是一份为您精心整理的 **C++ `std::map` 全方位方法详解**。

`std::map` 是基于**红黑树**实现的**有序关联容器**，存储的是 **键值对 (Key-Value Pairs)**。它的核心特性是：**按键自动排序**且**键唯一**。

如果你需要根据“键”快速查找“值”，并且希望数据保持有序，`std::map` 是首选。

---

# 📚 C++ `std::map` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>

using namespace std;
```

> **核心特性速览**：
> 1. **键值对存储**：元素类型为 `std::pair<const Key, T>`。
> 2. **键唯一**：同一个键只能存在一个值（后插入的会覆盖或插入失败）。
> 3. **自动排序**：默认按键从小到大排序（可自定义）。
> 4. **查找效率**：查找、插入、删除均为 $O(\log N)$。
> 5. **键不可改**：`Key` 部分是 `const` 的，不能修改键（会破坏树结构），只能修改值 `T`。

---

## 1️⃣ 构造与模板定义 (Construction & Template)
`map` 的模板定义包含四个参数，最常用的是前两个。

| 方法/定义                                  | 参数详解                                                           | 返回值 | 功能说明                                  |
| :------------------------------------- | :------------------------------------------------------------- | :-- | :------------------------------------ |
| **`template<...>`**                    | `Key`: 键类型`T`: 值类型`Compare`: 比较函数 (默认 `less<Key>`)`Alloc`: 分配器 | -   | 定义 map 类型。元素类型为 `pair<const Key, T>`。 |
| **`map()`**                            | 无                                                              | -   | 默认构造，生成空 map。                         |
| **`map(InputIt first, InputIt last)`** | `first`, `last`: 迭代器范围                                         | -   | 范围构造，从一对对 `{key, value}` 中初始化。        |
| **`map(initializer_list<pair> init)`** | `init`: 初始化列表 (C++11)                                          | -   | 列表构造，如 `{{1, "a"}, {2, "b"}}`。        |
| **`map(const map& other)`**            | `other`: 另一个 map                                               | -   | 拷贝构造。                                 |
| **`map(map&& other)`**                 | `other`: 右值引用 (C++11)                                          | -   | 移动构造，窃取资源。                            |
| **`map(Compare comp)`**                | `comp`: 自定义比较函数                                                | -   | 使用自定义排序规则构造（常用于按键降序）。                 |

### 💻 代码示例
```cpp
int main() {
    // 1. 默认构造 (按键升序)
    map<int, string> m1;
    
    // 2. 初始化列表
    map<string, int> m2{ {"apple", 1}, {"banana", 2}, {"apple", 10} }; 
    // 注意：重复键 "apple"，后者会被忽略或覆盖取决于构造实现，通常保留第一个或最后插入逻辑视具体构造函数而定，
    // 但在 initializer_list 中，重复键的行为是实现定义的，通常建议避免重复。
    // 实际运行中，m2 大小为 2 ("apple":1, "banana":2) 或 ("apple":10)，标准规定若重复，后面的覆盖前面的（对于 insert）, 
    // 但 initializer_list 构造等价于多次 insert，所以 "apple" 最终值是 10 (如果实现是逐个insert) 或者 1 (如果去重)。
    // 修正：initializer_list 构造等价于 insert 范围，若 key 重复，第一个插入成功，后续 insert(key, val) 失败。
    // 所以 m2["apple"] 通常是 1。
    
    // 3. 自定义比较 (按键降序)
    map<int, string, greater<int>> m3{ {3, "c"}, {1, "a"}, {2, "b"} };
    // 遍历顺序: 3->2->1
    
    // 4. 范围构造
    vector<pair<char, int>> v = {{'a', 1}, {'b', 2}};
    map<char, int> m4(v.begin(), v.end());

    cout << "m2 size: " << m2.size() << endl; 
    return 0;
}
```

---

## 2️⃣ 容量与状态 (Capacity & State)

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`size()`** | 无 | `size_t` | 返回键值对个数。 |
| **`empty()`** | 无 | `bool` | 若为空返回 `true`。 |
| **`max_size()`** | 无 | `size_t` | 理论最大容量。 |
| **`clear()`** | 无 | `void` | 清空所有键值对。 |

### 💻 代码示例
```cpp
int main() {
    map<int, int> m = {{1, 10}, {2, 20}};
    cout << "Size: " << m.size() << ", Empty: " << m.empty() << endl;
    m.clear();
    cout << "After clear, Size: " << m.size() << endl;
    return 0;
}
```

---

## 3️⃣ 元素访问与插入 (Element Access & Insertion)
这是 `map` 最常用的功能，特别是 `operator[]` 和 `insert` 的区别。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`operator[]`** | `key`: 键 | `T&` (值的引用) | **最常用**。若 `key` 存在，返回对应的值引用。若 `key` **不存在**，**自动插入**该键，值初始化为默认值 (如 0, "")，并返回引用。⚠️ **副作用**：可能改变 map 大小。 |
| **`at(key)`** | `key`: 键 | `T&` | 返回 `key` 对应的值引用。**若 key 不存在，抛出 `out_of_range` 异常**。不插入新元素。 |
| **`insert(pair)`** | `val`: `pair<const Key, T>` | `pair<iterator, bool>` | 插入键值对。`bool`: `true`=成功，`false`=键已存在（插入失败）。`iterator`: 指向该键的迭代器。 |
| **`insert_or_assign(key, val)`** | `key`, `val` (C++17) | `pair<iterator, bool>` | 若 `key` 存在则**更新**值，不存在则**插入**。返回 `bool` 表示是插入 (`true`) 还是更新 (`false`)。 |
| **`emplace(key_args..., val_args...)`** | 构造参数的列表 (C++11) | `pair<iterator, bool>` | 原地构造键值对，避免拷贝开销。若键存在则失败。 |
| **`try_emplace(key, val_args...)`** | `key`, 值的构造参数 (C++17) | `pair<iterator, bool>` | 类似 `emplace`，但若键存在，**不会构造值对象**（更高效）。 |

### 💡 `operator[]` vs `insert` vs `at`
- **只想读取**：用 `at()` (安全) 或 `find()`。
- **想读取，没有就创建**：用 `operator[]` (方便但有副作用)。
- **想插入，已有则不操作**：用 `insert()`。
- **想插入，已有则更新**：用 `insert_or_assign()` (C++17) 或 `operator[]`。

### 💻 代码示例
```cpp
int main() {
    map<string, int> scores;
    
    // 1. operator[] (不存在则创建)
    scores["Alice"] = 90;      // 插入 Alice:90
    scores["Alice"] = 95;      // 修改 Alice:95
    int b = scores["Bob"];     // 插入 Bob:0 (默认值), b=0
    
    // 2. at (不存在则抛异常)
    try {
        scores.at("Charlie") = 80; // 抛出 out_of_range，因为 Charlie 不存在
    } catch (...) {
        cout << "Charlie not found, cannot use at().\n";
    }
    scores.insert({"Charlie", 80}); // 先插入
    scores.at("Charlie") = 85;      // 现在可以了
    
    // 3. insert (存在则失败)
    auto ret = scores.insert({"Alice", 100}); 
    if (!ret.second) {
        cout << "Insert Alice failed, current score: " << ret.first->second << endl; // 95
    }
    
    // 4. insert_or_assign (C++17, 存在则更新)
    scores.insert_or_assign("Dave", 70); // 插入
    scores.insert_or_assign("Dave", 75); // 更新为 75
    
    // 5. 遍历输出 (自动按名字排序)
    for (const auto& p : scores) {
        cout << p.first << ": " << p.second << ", "; 
        // 输出: Alice: 95, Bob: 0, Charlie: 85, Dave: 75
    }
    cout << endl;
    
    return 0;
}
```

---

## 4️⃣ 查找与删除 (Search & Erase)

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`find(key)`** | `key`: 键 | `iterator` | 查找键。找到返回迭代器，未找到返回 `end()`。 |
| **`count(key)`** | `key`: 键 | `size_t` | 统计键的个数。对于 `map`，返回 **0** 或 **1**。常用于判断键是否存在。 |
| **`erase(key)`** | `key`: 键 | `size_t` | 删除指定键的元素。返回删除个数 (0 或 1)。 |
| **`erase(it)`** | `it`: 迭代器 | `iterator` (C++11) | 删除迭代器指向的元素。返回下一个迭代器。 |
| **`erase(first, last)`** | `first`, `last`: 迭代器范围 | `iterator` | 删除范围内的元素。 |
| **`equal_range(key)`** | `key`: 键 | `pair<iter, iter>` | 返回 `{lower_bound, upper_bound}`。对于 `map`，若存在则两个迭代器相邻。 |

### 💻 代码示例
```cpp
int main() {
    map<int, string> m = {{1, "one"}, {2, "two"}, {3, "three"}};
    
    // 1. 查找
    if (m.count(2)) {
        cout << "Key 2 exists.\n";
    }
    
    auto it = m.find(3);
    if (it != m.end()) {
        cout << "Found 3: " << it->second << "\n"; // three
    }
    
    // 2. 删除
    m.erase(1);          // 按键删除
    m.erase(it);         // 按迭代器删除
    
    // 3. 遍历删除
    m.insert({4, "four"}, {5, "five"});
    for (auto it = m.begin(); it != m.end(); ) {
        if (it->first % 2 == 0) { // 删除偶数键
            it = m.erase(it);
        } else {
            ++it;
        }
    }
    // 剩下: 3, 5
    
    return 0;
}
```

---

## 5️⃣ 顺序查找与边界 (Ordered Search)
利用红黑树的有序性进行范围查询，这是 `map` 相比 `unordered_map` 的最大优势。

| 方法 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`lower_bound(key)`** | `key`: 键 | `iterator` | 返回**第一个键大于等于** (`>=`) `key` 的迭代器。 |
| **`upper_bound(key)`** | `key`: 键 | `iterator` | 返回**第一个键大于** (`>`) `key` 的迭代器。 |
| **`equal_range(key)`** | `key`: 键 | `pair<iter, iter>` | 返回键等于 `key` 的范围（通常只有一个元素）。 |

### 💡 应用场景
- **范围统计**：统计分数在 `[60, 90]` 之间的人数。
- **字典序查找**：查找所有以 "app" 开头的单词（配合 `lower_bound("app")` 和 `upper_bound("apq")`）。

### 💻 代码示例
```cpp
int main() {
    map<int, string> m = {
        {10, "A"}, {20, "B"}, {30, "C"}, {40, "D"}, {50, "E"}
    };
    
    // 查找键 >= 25 的第一个元素
    auto it_low = m.lower_bound(25); 
    if (it_low != m.end()) {
        cout << ">= 25: " << it_low->first << " -> " << it_low->second << endl; // 30 -> C
    }
    
    // 查找键 > 30 的第一个元素
    auto it_up = m.upper_bound(30);
    if (it_up != m.end()) {
        cout << "> 30: " << it_up->first << " -> " << it_up->second << endl; // 40 -> D
    }
    
    // 遍历区间 [20, 40] (包含 20 和 40)
    // 范围: [lower_bound(20), upper_bound(40))
    auto start = m.lower_bound(20);
    auto end = m.upper_bound(40);
    
    cout << "Range [20, 40]: ";
    for (auto it = start; it != end; ++it) {
        cout << "[" << it->first << ":" << it->second << "] "; 
        // 输出: [20:B] [30:C] [40:D]
    }
    cout << endl;
    
    return 0;
}
```

---

## 6️⃣ 迭代与自定义类型 (Iteration & Custom Types)

### A. 迭代器
`map` 的元素是 `pair<const Key, T>`。
- `it->first`: **键 (const，不可改)**
- `it->second`: 值 (可改)

```cpp
for (auto& p : m) {
    // p.first = 10; // ❌ 错误！键是 const 的
    p.second = "New Value"; // ✅ 正确！可以修改值
}
```

### B. 自定义键类型
如果 `Key` 是自定义类，必须重载 `<` 运算符或提供比较仿函数。

```cpp
struct Date {
    int year, month, day;
    // 重载 < 用于排序
    bool operator<(const Date& other) const {
        if (year != other.year) return year < other.year;
        if (month != other.month) return month < other.month;
        return day < other.day;
    }
};

int main() {
    map<Date, string> events;
    events.insert({{2023, 1, 1}, "New Year"});
    events.insert({{2023, 12, 25}, "Christmas"});
    
    // 自动按日期排序
    for (const auto& p : events) {
        cout << p.first.year << "-" << p.first.month << "-" << p.first.day 
             << ": " << p.second << endl;
    }
    return 0;
}
```

---

## 7️⃣ `map` vs `unordered_map` vs `vector` 终极对比

| 特性        | `std::map`               | `std::unordered_map` | `std::vector<pair>` |
| :-------- | :----------------------- | :------------------- | :------------------ |
| **底层结构**  | **红黑树**                  | **哈希表**              | 动态数组                |
| **键顺序**   | **有序** (自动排序)            | **无序** (随机)          | 插入顺序 (需手动 sort)     |
| **键唯一性**  | 唯一                       | 唯一                   | 可重复                 |
| **查找复杂度** | $O(\log N)$              | **平均 $O(1)$** ⚡      | $O(N)$              |
| **范围查询**  | **✅ 支持** (`lower_bound`) | ❌ 不支持                | ✅ 支持 (需排序)          |
| **内存占用**  | 高 (指针开销)                 | 较高 (桶开销)             | 低                   |
| **适用场景**  | 需要**有序**、范围查找、字典序遍历      | 仅需**快速查找/计数**，不在乎顺序  | 数据量小、需下标访问、遍历多查找少   |

---

### 💡 核心总结
1. **键值对**：记住元素是 `pair<const Key, T>`，键不可改，值可改。
2. **`operator[]` 陷阱**：`m[key]` 在键不存在时会**自动插入**默认值。如果只是想检查是否存在，请用 `count()` 或 `find()`，避免意外扩容。
3. **有序优势**：如果需要“查找大于 X 的最小键”或“遍历排序后的数据”，`map` 是唯一选择。
4. **性能选择**：
   - 只要查得快，不要顺序 $\rightarrow$ `unordered_map`。
   - 要顺序或范围查 $\rightarrow$ `map`。
5. **C++17 新特性**：推荐使用 `insert_or_assign` 和 `try_emplace`，语义更清晰且性能更好。

**一句话口诀**：
> “键值配对 Map 存，红黑树上自动排；
> 方括号写慎插入，范围查找它最强。”