---
created: 2026-02-27T11:10
updated: 2026-02-27T11:15
---
在 C++ 中，`std::copy` 是 `<algorithm>` 库中最基础且最重要的算法之一。它的核心作用是**将元素从一个范围复制到另一个范围**。

很多初学者容易在这里踩坑（主要是目标空间未分配导致崩溃），因此理解其**参数约束**和**返回值用途**至关重要。

---

### 1. 函数原型与头文件

```cpp
#include <algorithm>

template< class InputIt, class OutputIt >
OutputIt copy( InputIt first, InputIt last, OutputIt d_first );
```

- **头文件**：`#include <algorithm>`
- **C++ 版本**：C++98 起支持，C++11 及以后支持移动语义优化（如果迭代器支持）。

---

### 2. 参数详解

| 参数 | 类型 | 含义 | **关键约束** |
| :--- | :--- | :--- | :--- |
| `first` | `InputIt` | 输入范围的**起始**迭代器 | 必须有效，指向可读取的元素。 |
| `last` | `InputIt` | 输入范围的**结束**迭代器 | **左闭右开**区间 `[first, last)`，即不包含 `last` 指向的元素。 |
| `d_first` | `OutputIt` | 输出范围的**起始**迭代器 | **最重要！** 目标位置必须有**足够的已分配空间**容纳所有复制的元素，否则会导致**未定义行为（崩溃）**。 |

#### ⚠️ 核心警告：关于 `d_first`
`std::copy` **不会**自动调整目标容器的大小。
- ❌ **错误**：目标 `vector` 为空，直接传 `vec.begin()`。
- ✅ **正确**：目标 `vector` 先 `resize` 或 `reserve` + 使用插入迭代器。

---

### 3. 返回值详解

- **返回类型**：`OutputIt`（与第三个参数类型相同）。
- **返回值含义**：指向**目标范围中最后一个被复制元素之后**的迭代器。
  - 数学表达：返回 `d_first + (last - first)`。
  - 形象理解：它指向“下一个可以写入的位置”。

#### 💡 返回值的典型用途
1. **链式操作**：连续复制多段数据到同一容器的不同位置。
2. **获取结束位置**：知道数据复制到了哪里，方便后续操作（如填充、截断）。

---

### 4. 使用场景与代码示例

#### 场景一：复制到预分配空间的容器（标准用法）
这是最高效的用法，适用于已知目标大小的情况。

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> src = {1, 2, 3, 4, 5};
    
    // 1. 必须预先分配空间！
    std::vector<int> dest(src.size()); 
    
    // 2. 执行复制
    // 返回值 it 指向 dest.end()
    auto it = std::copy(src.begin(), src.end(), dest.begin());
    
    // 3. 利用返回值验证
    if (it == dest.end()) {
        std::cout << "复制完成，正好填满。\n";
    }

    // 输出: 1 2 3 4 5
    for (int n : dest) std::cout << n << " ";
    return 0;
}
```

#### 场景二：复制到动态增长的容器（配合 `back_inserter`）
如果你不想手动 `resize`，或者目标容器需要**追加**数据，必须使用 `std::back_inserter`。它会返回一个特殊的迭代器，每次赋值时自动调用 `push_back`。

```cpp
#include <iterator> // 需要包含此头文件

std::vector<int> src = {1, 2, 3};
std::vector<int> dest = {10, 20}; // 原有数据

// 自动扩容，将 src 追加到 dest 后面
std::copy(src.begin(), src.end(), std::back_inserter(dest));

// dest 现在是: {10, 20, 1, 2, 3}
```

#### 场景三：利用返回值进行链式复制
将不同的源数据段连续复制到目标容器的不同位置。

```cpp
std::vector<int> part1 = {1, 2};
std::vector<int> part2 = {3, 4};
std::vector<int> buffer(4); // 预分配足够空间

// 第一次复制：从 buffer 开头开始
auto next_pos = std::copy(part1.begin(), part1.end(), buffer.begin());

// 第二次复制：从上一次结束的位置继续
std::copy(part2.begin(), part2.end(), next_pos);

// buffer: {1, 2, 3, 4}
```

#### 场景四：数组与容器互拷
`std::copy` 同样适用于原生数组，因为数组名退化为指针，指针也是迭代器。

```cpp
int arr[] = {10, 20, 30};
std::vector<int> vec(3);

// 数组 -> vector
std::copy(std::begin(arr), std::end(arr), vec.begin());

// vector -> 数组
int arr2[3];
std::copy(vec.begin(), vec.end(), arr2);
```

---

### 5. 特殊情况：重叠区间 (`std::copy` vs `std::copy_backward`)

如果在**同一个容器**内复制，且**源范围和目标范围有重叠**，`std::copy` 的行为是**未定义的**（可能会覆盖还没读取的数据）。

- **情况 A：目标在源之后（重叠）**
  - ❌ `std::copy`：危险！前面的数据会覆盖后面的源数据。
  - ✅ **`std::copy_backward`**：从后往前拷，安全。
  
- **情况 B：目标在源之前（重叠）**
  - ✅ `std::copy`：安全！从前往后拷没问题。
  - ❌ `std::copy_backward`：危险！

**示例：向右移动元素（目标在源之后）**
```cpp
std::vector<int> v = {1, 2, 3, 4, 5};
// 想把前3个元素 {1, 2, 3} 移动到索引 2, 3, 4 的位置
// 如果用 copy: v[2]=1, v[3]=2, v[4]=3 (此时v[4]原值5丢失，但逻辑上可能出错，标准规定未定义)
// 正确做法：
std::copy_backward(v.begin(), v.begin() + 3, v.begin() + 5);
// 结果：{1, 2, 1, 2, 3} (注意：前两个元素没变，后面被覆盖了)
```

---

### 6. 性能与底层优化

- **平凡类型优化**：如果迭代器指向的是**平凡可复制类型**（如 `int`, `double`, POD 结构体），且迭代器是普通指针，现代编译器（GCC, Clang, MSVC）会将 `std::copy` 优化为底层的 `memcpy` 调用，速度极快。
- **移动语义**：如果复制的是 C++11 及以上的非平凡类型（如 `std::string`, `std::vector`），且输入迭代器是移动迭代器（`std::make_move_iterator`），`std::copy` 会执行**移动构造**而不是拷贝构造，显著提升性能。

```cpp
// 移动复制示例
std::vector<std::string> src = {"hello", "world"};
std::vector<std::string> dest(2);

// 将 src 的内容“移动”到 dest，src 中的字符串将变为空
std::copy(std::make_move_iterator(src.begin()), 
          std::make_move_iterator(src.end()), 
          dest.begin());
```

---

### 7. 总结速查表

| 特性 | 说明 |
| :--- | :--- |
| **功能** | 范围复制 `[first, last)` → `[d_first, d_first + n)` |
| **前置条件** | **目标空间必须已分配**（除非用 `back_inserter`） |
| **返回值** | 指向目标区域末尾的迭代器（可用于链式调用） |
| **重叠处理** | 若目标在源之后且重叠，**必须**用 `std::copy_backward` |
| **性能** | 平凡类型自动优化为 `memcpy`；支持移动语义 |
| **常见错误** | 对空 `vector` 直接使用 `begin()` 作为目标 -> **Crash** |

**一句话口诀**：
> “Copy 不建房，目标要预留；若要自动长，背插器来救；重叠向后拷，返回值好求。”