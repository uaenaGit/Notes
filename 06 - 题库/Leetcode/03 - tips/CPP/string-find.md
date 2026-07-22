---
created: 2026-02-27T11:24
updated: 2026-02-27T11:24
---
`std::string::find` 是 C++ `std::string` 类中最常用的成员函数之一，用于**在字符串中查找子串或字符第一次出现的位置**。

它的核心特点是：**找到返回索引（下标），找不到返回一个特殊的常量 `std::string::npos`**。

---

### 1. 函数原型与重载
`find` 有多个重载版本，可以查找字符、字符串、C-style 字符串等。

```cpp
#include <string>

// 1. 查找子串 (最常用)
size_t find(const string& str, size_t pos = 0) const noexcept;

// 2. 查找 C 风格字符串 ("abc")
size_t find(const char* s, size_t pos = 0) const;

// 3. 查找单个字符 ('a')
size_t find(char c, size_t pos = 0) const noexcept;

// 4. 查找 C 字符串的前 n 个字符
size_t find(const char* s, size_t pos, size_t n) const;
```

#### 参数详解
| 参数 | 类型 | 含义 | 默认值 |
| :--- | :--- | :--- | :--- |
| `str` / `s` / `c` | `string` / `char*` / `char` | **要查找的目标**。可以是子串、C 字符串或单个字符。 | 无 |
| `pos` | `size_t` | **开始搜索的位置**（下标）。从该位置往后找。 | `0` (从头开始) |
| `n` | `size_t` | (仅针对 `char*` 重载) 只匹配 `s` 的前 `n` 个字符。 | 无 |

#### 返回值
- **找到**：返回目标第一次出现的**起始下标**（`size_t` 类型，从 0 开始）。
- **未找到**：返回 **`std::string::npos`**。
  - `npos` 是一个静态常量，通常定义为 `size_t` 的最大值（即 `-1` 的无符号表示，约为 $4 \times 10^9$ 或 $1.8 \times 10^{19}$）。

---

### 2. 核心用法与代码示例

#### 场景 A：查找子串
```cpp
#include <iostream>
#include <string>

using namespace std;

int main() {
    string text = "Hello World, Welcome to C++";
    string target = "World";

    // 从默认位置 0 开始查找
    size_t pos = text.find(target);

    if (pos != string::npos) {
        cout << "找到了! 位置在下标: " << pos << endl; // 输出: 6
        // 验证: H(0)e(1)l(2)l(3)o(4) (5)W(6)...
    } else {
        cout << "没找到!" << endl;
    }

    return 0;
}
```

#### 场景 B：查找单个字符
```cpp
string email = "user@example.com";
char atSymbol = '@';

size_t pos = email.find(atSymbol);

if (pos != string::npos) {
    string username = email.substr(0, pos); // 截取 @ 之前的部分
    cout << "用户名: " << username << endl;  // 输出: user
}
```

#### 场景 C：指定起始位置 (`pos` 参数)
如果你想查找**第二次**出现的位置，可以先找到第一次的位置，然后从 `pos + 1` 开始继续找。

```cpp
string text = "apple, banana, apple, cherry";
string target = "apple";

// 1. 找第一次
size_t pos1 = text.find(target); 
// pos1 = 0

// 2. 找第二次 (从 pos1 + 1 开始)
size_t pos2 = text.find(target, pos1 + 1); 
// pos2 = 14

// 3. 找第三次 (从 pos2 + 1 开始)
size_t pos3 = text.find(target, pos2 + 1); 
// pos3 = npos (没找到了)

cout << "第二次出现位置: " << pos2 << endl;
```

#### 场景 D：查找 C 字符串的一部分
```cpp
string text = "The quick brown fox";
// 只查找 "qui" (取 "quick" 的前3个字符)
size_t pos = text.find("quick", 0, 3); 

if (pos != string::npos) {
    cout << "找到 'qui' 在位置: " << pos << endl; // 输出: 4
}
```

---

### 3. 常见实战模式

#### 模式 1：循环查找所有出现位置
```cpp
string text = "foo bar foo baz foo";
string target = "foo";
size_t pos = 0;

while ((pos = text.find(target, pos)) != string::npos) {
    cout << "找到 'foo' 在位置: " << pos << endl;
    
    // 关键：必须移动 pos，否则死循环！
    // 移动 1 位可以查找重叠部分 (如 "aaa" 找 "aa")
    // 移动 target.length() 跳过当前匹配
    pos += 1; 
}
```

#### 模式 2：判断是否包含子串 (C++11 之前常用)
虽然 C++11 引入了 `strstr` 风格的逻辑，但 `find` 依然是标准写法。
```cpp
bool contains(const string& haystack, const string& needle) {
    return haystack.find(needle) != string::npos;
}

// C++17 起可以直接用: haystack.contains(needle)
```

#### 模式 3：解析路径或 URL
```cpp
string path = "/home/user/documents/file.txt";
size_t lastSlash = path.rfind('/'); // rfind 是反向查找，找最后一次出现

if (lastSlash != string::npos) {
    string filename = path.substr(lastSlash + 1);
    cout << "文件名: " << filename << endl; // 输出: file.txt
}
```

---

### 4. ⚠️ 重要注意事项与陷阱

#### 陷阱 1：错误地检查返回值
由于 `npos` 是 `size_t` (无符号整数) 的最大值，**千万不要**用 `int` 接收返回值，也不要直接和 `-1` 比较（虽然通常能工作，但不规范）。

```cpp
// ❌ 错误写法
int pos = text.find("abc"); 
if (pos == -1) { ... } // 警告：有符号/无符号比较

// ✅ 正确写法
size_t pos = text.find("abc");
if (pos == string::npos) { ... }
```

#### 陷阱 2：空字符串查找
如果查找的目标是空字符串 `""`，`find` 会返回 `pos` 参数的值（因为空串在任何位置都算匹配）。
```cpp
string s = "hello";
cout << s.find("", 0); // 输出: 0
cout << s.find("", 5); // 输出: 5 (在末尾也算)
cout << s.find("", 6); // 输出: npos (越界了)
```

#### 陷阱 3：性能问题
`find` 的时间复杂度通常是 $O(N \times M)$（N 是主串长度，M 是子串长度）。对于极长的文本和复杂的匹配需求，可能需要更高级的算法（如 KMP），但在日常业务逻辑中 `find` 足够快且经过高度优化。

---

### 5. 相关函数对比

| 函数 | 方向 | 用途 |
| :--- | :--- | :--- |
| `find` | 从前向后 | 找**第一次**出现的位置 |
| `rfind` | 从后向前 | 找**最后一次**出现的位置 (常用于获取文件后缀、最后一级路径) |
| `find_first_of` | 从前向后 | 找**任意一个**属于指定集合的字符 (如找第一个标点符号) |
| `find_last_of` | 从后向前 | 找**任意一个**属于指定集合的字符 |
| `find_first_not_of` | 从前向后 | 找**第一个不**属于指定集合的字符 (常用于去除前导空格) |

**示例：去除前后空格**
```cpp
string s = "   hello world   ";

// 找第一个不是空格的字符
size_t start = s.find_first_not_of(" ");
// 找最后一个不是空格的字符
size_t end = s.find_last_not_of(" ");

if (start != string::npos) {
    string trimmed = s.substr(start, end - start + 1);
    cout << "[" << trimmed << "]" << endl; // [hello world]
}
```

### 总结
- **核心口诀**：`find` 找不到返回 `npos`，找到返回下标。
- **检查方式**：永远使用 `if (pos != string::npos)`。
- **进阶技巧**：配合 `pos + 1` 实现循环查找，配合 `rfind` 处理路径/后缀。