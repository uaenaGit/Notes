---
created: 2026-03-06T20:37
updated: 2026-03-06T20:37
---
这是一份为您精心整理的 **C++ `std::fill` 全方位方法详解**。

`std::fill` 是 C++ 标准模板库（STL）中 `<algorithm>` 头文件下的一个**高效填充工具**。它能将指定范围内的所有元素赋值为同一个值，常用于数组初始化、重置容器状态或批量赋值。相比手写 `for` 循环，它语义更清晰，且在某些编译器优化下性能更佳。

这份指南严格遵循 C++11 及以上标准，**重点解析了其参数细节、与 `memset` 的区别以及常见陷阱**。

---

# 📚 C++ `std::fill` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // 必须包含此头文件
#include <array>

using namespace std;
```

> **核心特性速览**：
> 1. **范围操作**：基于迭代器 `[first, last)` 工作，适用于所有标准容器及原生数组。
> 2. **类型安全**：支持任意数据类型（int, double, string, 自定义结构体），不像 `memset` 仅限字节操作。
> 3. **语义清晰**：代码意图一目了然（“填充”），优于晦涩的循环。
> 4. **性能优秀**：现代编译器通常会将其优化为高效的内存设置指令（如 `memset` 或 SIMD 指令）。
> 5. **左闭右开**：遵循 STL 惯例，覆盖 `[first, last)` 区间，**不包含** `last`。

---

## 1️⃣ 函数原型与参数 (Function Signature)

| 形式 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`void fill(ForwardIterator first, ForwardIterator last, const T& value)`** | `first`: 起始迭代器`last`: 结束迭代器（开区间）`value`: 要填充的值 | `void` | 将范围 `[first, last)` 内的所有元素赋值为 `value`。 |

> **注意**：迭代器必须是**前向迭代器**（Forward Iterator）或更强（如双向、随机访问）。`vector`, `array`, `deque`, `list`, 原生数组均支持。

---

## 2️⃣ 标准用法模板 (The Golden Patterns)

### 💻 场景 A：填充原生数组
这是替代 `memset` 的最佳方案，特别是对于非 `char`/`int` 类型或需要非 0/-1 值时。

```cpp
int main() {
    int arr[10];
    
    // 将整个数组填充为 5
    // 注意：arr + 10 指向数组末尾的下一个位置
    fill(arr, arr + 10, 5); 
    
    // 输出验证：5 5 5 5 5 5 5 5 5 5
    for (int x : arr) cout << x << " ";
    cout << endl;
    
    // 填充部分区域：索引 2 到 5 (不含 5)，即 arr[2], arr[3], arr[4]
    fill(arr + 2, arr + 5, 99); 
    // 结果：5 5 99 99 99 5 5 5 5 5
    
    return 0;
}
```

### 💻 场景 B：填充 `std::vector`
常用于重置 vector 内容或初始化特定区间。

```cpp
int main() {
    vector<int> v(10, 0); // 初始化为 10 个 0
    
    // 全部填充为 -1
    fill(v.begin(), v.end(), -1);
    
    // 填充前 5 个元素为 100
    fill(v.begin(), v.begin() + 5, 100);
    // 结果：100 100 100 100 100 -1 -1 -1 -1 -1
    
    return 0;
}
```

### 💻 场景 C：填充 `std::string` 或其他容器
`fill` 不仅限于数字，它可以处理任何可赋值的类型。

```cpp
int main() {
    string s = "hello world";
    
    // 将前 5 个字符填充为 '*'
    fill(s.begin(), s.begin() + 5, '*');
    // 结果："***** world"
    
    vector<string> vs(3, "old");
    // 将所有字符串改为 "new"
    fill(vs.begin(), vs.end(), "new");
    
    return 0;
}
```

---

## 3️⃣ 深度对比：`std::fill` vs `memset`

这是 C++ 开发者最容易混淆的地方。**请优先使用 `std::fill`**，除非你在进行极端的底层字节操作。

| 特性 | `std::fill` (推荐) | `memset` (C 风格，需谨慎) |
| :--- | :--- | :--- |
| **头文件** | `<algorithm>` | `<cstring>` |
| **工作原理** | 调用元素的**赋值运算符** (`=`) | 按**字节** (byte) 复制内存 |
| **类型安全** | **高**。支持 int, double, string, 类等 | **低**。仅对 POD (平凡数据类型) 安全 |
| **填充值限制** | 可以是**任意值** (如 1, 5, -100, "abc") | 只能填 **0** 或 **-1** (因为按字节填)*(注：填 1 会变成 16843009)* |
| **自定义类型** | **支持** (如 `struct Point`) | **不支持** (会导致未定义行为) |
| **性能** | 编译器通常优化为 `memset` (当类型简单且值为 0/-1 时) | 极快，但仅限于字节操作 |
| **可读性** | 高 (`fill(..., 5)`) | 低 (`memset(..., 5, size)`) |

### ⚠️ `memset` 的经典陷阱
```cpp
int arr[5];
// ❌ 错误！想把数组全设为 1
memset(arr, 1, sizeof(arr)); 
// 实际结果：每个字节变成 0x01
// int 是 4 字节：0x01010101 = 16843009，而不是 1！

// ✅ 正确做法 (任意值)
fill(arr, arr + 5, 1); 

// ✅ memset 仅在这些情况安全：
memset(arr, 0, sizeof(arr)); // 全 0 (0x00000000)
memset(arr, -1, sizeof(arr)); // 全 -1 (0xFFFFFFFF)
```

---

## 4️⃣ 高级应用与变体

### 场景 A：配合 `std::vector` 的 `resize`
如果你需要一个全新大小的 vector 并填满值，可以直接用构造函数；但如果是在现有 vector 上操作：

```cpp
vector<int> v;
v.resize(100); // 先分配空间（默认初始化为 0）
fill(v.begin(), v.end(), 7); // 再统一填充为 7
```
*注：`vector<int> v(100, 7)` 通常比上面两步更高效，因为它只分配一次。`fill` 更适合**复用**已存在的容器。*

### 场景 B：填充二维数组（行级填充）
`fill` 是一次性的线性操作。对于二维结构，通常需要循环调用，或者利用一维化技巧。

```cpp
// 方法 1：逐行填充 (清晰)
int matrix[3][4];
for (int i = 0; i < 3; ++i) {
    fill(matrix[i], matrix[i] + 4, -1);
}

// 方法 2：利用连续内存 (极客技巧，仅限原生数组)
// 二维原生数组在内存是连续的，可以一次性填充
fill(&matrix[0][0], &matrix[0][0] + 3 * 4, -1);
```
> **注意**：`vector<vector<int>>` **不能**使用方法 2，因为每一行内存不连续。

### 场景 C：C++11 `std::array`
```cpp
array<int, 5> arr;
fill(arr.begin(), arr.end(), 42);
// 或者使用 fill_n (见下文)
```

---

## 5️⃣ 相关兄弟函数：`std::fill_n`

如果你知道要填充的**数量**，而不是结束迭代器，可以使用 `std::fill_n`。

| 函数 | 原型 | 说明 |
| :--- | :--- | :--- |
| **`fill_n`** | `OutputIterator fill_n(OutputIterator first, Size n, const T& value)` | 从 `first` 开始，填充 **n** 个元素。返回指向最后一个填充元素之后的迭代器。 |

**示例**：
```cpp
int arr[10];
// 从 arr 开始，填充 5 个元素为 9
fill_n(arr, 5, 9); 
// 等价于 fill(arr, arr + 5, 9);
```

---

## 6️⃣ 常见陷阱与注意事项

| 问题 | 描述 | 解决方案 |
| :--- | :--- | :--- |
| **迭代器越界** | `last` 超出了容器范围 | 确保 `last` 是有效的“尾后”迭代器（如 `v.end()` 或 `arr + N`）。 |
| **空范围** | `first == last` | 函数什么都不做，安全，不会报错。 |
| **const 容器** | 尝试填充 `const vector` | 编译错误。`fill` 需要修改元素，容器不能是 `const`。 |
| **输入迭代器** | 对 `istream_iterator` 使用 `fill` | 编译错误。`fill` 需要**前向迭代器**（可多次读写），输入迭代器只能读一次。 |

---

## 7️⃣ 性能分析与最佳实践

1. **编译器优化**：
   - 当你用 `fill` 填充 `int` 或 `char` 数组为 `0` 或 `-1` 时，现代编译器（GCC, Clang, MSVC）几乎总是将其优化为汇编层面的 `memset` 指令，性能与手写 `memset` **完全一致**。
   - 对于其他值或复杂类型，它会生成高效的循环，有时甚至使用 SIMD 指令（如 AVX）批量赋值。

2. **何时使用**：
   - ✅ **初始化/重置**：比赛或算法中快速重置 `dist[]`, `visited[]` 数组。
   - ✅ **非 0/-1 赋值**：需要填充 1, 100, -5 等值时，**必须**用 `fill`。
   - ✅ **复杂类型**：填充 `string`, `struct`, `class` 对象时。
   - ❌ **动态扩容**：如果需要改变容器大小，请用 `resize` 或构造函数，不要用 `fill` 去填未分配的空间。

---

### 💡 核心总结
1. **头文件**：`#include <algorithm>`。
2. **核心优势**：**类型安全**，支持**任意值**，替代危险的 `memset`。
3. **区间规则**：`[first, last)`，左闭右开。
4. **性能**：不要担心性能，它和 `memset` 一样快（在简单类型上），且更安全。
5. **口诀**：
   > “批量赋值用 Fill，类型安全不用愁；
   > 莫用 Memset 乱填数，除了 0 和 -1 皆出错；
   > 迭代器，分左右，左闭右开记心头。”

### 🏆 实战代码片段 (Copy-Paste Ready)
```cpp
// 快速重置 DP 数组为 -1 (记忆化搜索常用)
int dp[1005][1005];
fill(&dp[0][0], &dp[0][0] + 1005 * 1005, -1);

// 快速重置 visited 数组为 false
bool visited[1000];
fill(visited, visited + 1000, false);

// 重置 vector
vector<long long> dist(n, INF);
// ... 算法运行后 ...
fill(dist.begin(), dist.end(), INF); // 恢复初始状态
```