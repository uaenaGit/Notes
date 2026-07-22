---
created: 2026-02-26T09:38
updated: 2026-02-26T09:39
---
## `std::string::substr` 用法详解

`substr` 是 C++ `std::string` 类中最常用的成员函数之一，用于**提取子字符串**。

### 1. 函数原型

```cpp
#include <string>

std::string substr (size_t pos = 0, size_t len = npos) const;
```

- **`pos`**: 起始位置的下标（从 0 开始）。默认值为 0。
- **`len`**: 要截取的字符个数。默认值为 `npos`（表示直到字符串末尾）。
- **返回值**: 一个新的 `std::string` 对象，包含提取的子串。

---

### 2. 基本用法示例

#### A. 截取指定长度
```cpp
std::string s = "Hello World";
std::string sub = s.substr(0, 5); 
// 结果: "Hello" (从下标0开始，取5个字符)
```

#### B. 截取到末尾
```cpp
std::string s = "Hello World";
std::string sub = s.substr(6); 
// 结果: "World" (从下标6开始，直到结束)
// 等价于 s.substr(6, std::string::npos)
```

#### C. 超出长度的处理
如果 `len` 超过了剩余字符数，它会自动截取到末尾，**不会报错**。
```cpp
std::string s = "ABC";
std::string sub = s.substr(1, 100); 
// 结果: "BC" (虽然请求100个，但只剩2个，只取2个)
```

#### D. 异常处理
如果 `pos` 超过了字符串长度，会抛出 `std::out_of_range` 异常。
```cpp
std::string s = "ABC";
try {
    std::string sub = s.substr(5); // ❌ 抛出异常，因为下标5不存在
} catch (const std::out_of_range& e) {
    // 处理错误
}
```

---

### 3. 时间复杂度 (关键！)

**时间复杂度**: **$O(K)$**
其中 $K$ 是**截取出来的子串长度**（即实际返回的字符串长度）。

**空间复杂度**: **$O(K)$**
因为它会**分配新的内存**并**复制**字符到新字符串中。

#### 详细分析：
1.  **内存分配**: `substr` 返回的是一个**全新的 `std::string` 对象**。它必须在堆上分配足够的内存来存储子串。
2.  **字符复制**: 它需要将原字符串中的 $K$ 个字符逐个拷贝到新分配的内存中。
3.  **与原串长度 $N$ 的关系**: 
    - 操作耗时与**原字符串总长度 $N$ 无关**。
    - 操作耗时只与**截取的长度 $K$ 成正比**。
    - 截取 "Hello" (5 chars) 从 "A...Z" (1000 chars) 中和从 "Hello World" (11 chars) 中，耗时几乎一样。

---

### 4. 性能陷阱与优化建议

由于 `substr` 涉及**内存分配**和**数据拷贝**，在高频调用或处理大字符串时，它可能成为性能瓶颈。

#### ❌ 性能陷阱：循环中频繁截取
```cpp
// 低效写法：每次循环都分配新内存
for (int i = 0; i < n; ++i) {
    std::string part = s.substr(i, 1); // O(1) 但分配开销大
    process(part);
}
```
**问题**: 如果循环 $N$ 次，总复杂度是 $O(N)$，但会有 $N$ 次微小的内存分配/释放，开销很大。

#### ✅ 优化方案 1：使用 `string_view` (C++17 推荐)
`std::string_view` 是一个**非拥有**的字符串视图，它**不复制数据**，只记录指针和长度。
```cpp
#include <string_view>

// 零拷贝，复杂度 O(1)
for (int i = 0; i < n; ++i) {
    std::string_view part = std::string_view(s).substr(i, 1); 
    process(part); // 如果 process 支持 string_view
}
```
- **时间复杂度**: $O(1)$ (仅修改指针和长度)
- **空间复杂度**: $O(1)$ (无新内存分配)
- **注意**: 确保原字符串 `s` 的生命周期长于 `string_view`，否则会出现悬空指针。

#### ✅ 优化方案 2：传递下标范围
如果可能，直接传递原始字符串和下标范围给函数，避免创建子串。
```cpp
void process(const std::string& s, size_t start, size_t len);

// 调用
process(s, i, 1); 
```

---

### 5. 常见应用场景

#### A. 文件扩展名提取
```cpp
std::string filename = "data.txt";
size_t dotPos = filename.find('.');
if (dotPos != std::string::npos) {
    std::string ext = filename.substr(dotPos); // ".txt"
}
```

#### B. 分割字符串 (配合 find)
```cpp
std::string s = "apple,banana,cherry";
size_t pos = s.find(',');
std::string first = s.substr(0, pos);       // "apple"
std::string rest = s.substr(pos + 1);       // "banana,cherry"
```

#### C. 去掉首尾字符
```cpp
std::string s = "(hello)";
std::string content = s.substr(1, s.length() - 2); // "hello"
```

---

### 6. 总结对比表

| 特性 | `std::string::substr` | `std::string_view::substr` (C++17) |
| :--- | :--- | :--- |
| **返回值类型** | `std::string` (新对象) | `std::string_view` (视图) |
| **是否拷贝数据** | ✅ 是 (深拷贝) | ❌ 否 (浅拷贝/引用) |
| **时间复杂度** | $O(K)$ (K为子串长度) | $O(1)$ |
| **空间复杂度** | $O(K)$ (新分配内存) | $O(1)$ |
| **内存安全** | 独立生命周期，安全 | 依赖原字符串，需小心生命周期 |
| **适用场景** | 需要长期保存子串、修改子串 | 临时读取、解析、高性能场景 |

**一句话建议**：
如果需要**保存**或**修改**子串，用 `substr`；如果只是**临时读取**或**解析**且追求高性能，优先用 C++17 的 `std::string_view`。