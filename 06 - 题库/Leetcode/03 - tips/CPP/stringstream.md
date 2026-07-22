---
created: 2026-02-25T18:53
updated: 2026-02-25T19:30
---
`std::stringstream` 是 C++ 标准库 `<sstream>` 中提供的类，它允许像操作文件流（`cin`/`cout`）一样操作**内存中的字符串**。

---
### 1. 核心头文件与分类
```cpp
#include <sstream>   // 必须包含
#include <string>
#include <iostream>
```

| 类名                   | 功能            | 对应文件流      |
| -------------------- | ------------- | ---------- |
| `std::stringstream`  | 可读可写 (最常用)    | `fstream`  |
| `std::ostringstream` | 只写 (用于拼接/格式化) | `ofstream` |
| `std::istringstream` | 只读 (用于**解析**) | `ifstream` |

---
### 2. 核心用法一：数值与字符串互转 (类型转换)
这是 `stringstream` 最经典的用途，替代 C 语言的 `sprintf`/`atoi`。
#### A. 任意类型 -> 字符串
```cpp
#include <sstream>
#include <string>

int main() {
    int num = 42;
    double pi = 3.14159;
    
    std::ostringstream oss;
    oss << "数字: " << num << ", 圆周率: " << pi;
    
    std::string result = oss.str(); 
    // result: "数字: 42, 圆周率: 3.14159"
    
    return 0;
}
```
示例：用 `stringstream` 替代
```cpp
// 原代码
std::ostringstream oss;
oss << "Hello" << 123;
std::string s = oss.str();

// 替换后 (完全可行)
std::stringstream ss; 
ss << "Hello" << 123;
std::string s = ss.str();
```
#### B. 字符串 -> 任意类型
```cpp
#include <sstream>
#include <string>

int main() {
    std::string str = "12345";
    int num;
    
    std::istringstream iss(str);
    if (iss >> num) {
        // num 现在是整数 12345
    }
    
    // 解析混合内容
    std::string data = "100 200.5 hello";
    int a; double b; std::string c;
    std::istringstream iss2(data);
    iss2 >> a >> b >> c; 
    // a=100, b=200.5, c="hello"
    
    return 0;
}
```
示例：用 `stringstream` 替代
```cpp
// 原代码
std::string data = "42 3.14";
std::istringstream iss(data);
int a; double b;
iss >> a >> b;

// 替换后 (完全可行)
std::string data = "42 3.14";
std::stringstream ss(data); // 构造函数同样支持传入初始字符串
int a; double b;
ss >> a >> b;
```

---
### 3. 核心用法二：格式化输出 (控制精度/宽度)
相比 `to_string`，`stringstream` 的最大优势是可以**精细控制格式**（如保留小数位、补零、十六进制等）。
```cpp
#include <iostream>   // 用于 std::cout
#include <sstream>    // 用于 std::ostringstream
#include <iomanip>    // 用于 setprecision, setw, setfill
#include <windows.h>
  
int main() {
    SetConsoleOutputCP(65001);
    double value = 3.1415926;
    int id = 7;
    std::ostringstream oss;
    
    // 1. 保留 2 位小数
    oss << std::fixed << std::setprecision(2) << value;

    // 【关键步骤】使用 .str() 获取字符串并输出
    std::string result1 = oss.str();

    std::cout << "1. 保留2位小数: " << result1 << std::endl;
    // 输出: 1. 保留2位小数: 3.14

    // 2. 创建新流 (或者清空 oss: oss.str(""); oss.clear();)
    std::ostringstream oss2;

    // 3. 补零 (宽度为 4，不足补 0)
    oss2 << std::setfill('0') << std::setw(4) << id;

    // 【关键步骤】获取并输出
    std::cout << "2. 补零格式化: " << oss2.str() << std::endl;
    // 输出: 2. 补零格式化: 0007

    // 4. 十六进制
    std::ostringstream oss3;
    oss3 << std::hex << 255;

    // 【关键步骤】直接嵌入到 cout 中输出
    std::cout << "3. 十六进制: " << oss3.str() << std::endl;
    // 输出: 3. 十六进制: ff

    // 额外演示：拼接成一个完整的句子
    std::ostringstream final_oss;
    final_oss << "ID是" << oss2.str() << "，圆周率约为" << oss.str() << "，255的十六进制是" << oss3.str();

    std::cout << "\n4. 综合拼接: " << final_oss.str() << std::endl;
    // 输出: 4. 综合拼接: ID是0007，圆周率约为3.14，255的十六进制是ff

    return 0;
}
```

---
### 4. 核心用法三：字符串分割 (Split)
C++ 标准库没有直接的 `split` 函数，`stringstream` 是实现按空格/分隔符分割的最常用方法。
- `std::cin` 在读取字符串（`std::string` 或 `char[]`）时，**遇到空格、制表符（Tab）或换行符就会停止读取**
- 要读取包含空格的整行文字，必须使用 **`std::getline`** 函数。
#### 按空格分割
```cpp
#include <sstream>
#include <vector>
#include <string>

std::vector<std::string> split_by_space(const std::string& input) {
    std::istringstream iss(input);
    std::vector<std::string> tokens;
    std::string token;
    
    // >> 运算符默认以空格、制表符、换行符为分隔符
    while (iss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}
// 输入: "Hello World  C++"
// 输出: ["Hello", "World", "C++"] (自动忽略多余空格)
```

---
#### 按自定义分隔符分割 (如逗号)
```cpp
#include <sstream>
#include <vector>
#include <string>

std::vector<std::string> split_by_comma(const std::string& input) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream iss(input);
    
    // 使用 getline 指定分隔符
    while (std::getline(iss, token, ',')) {
        tokens.push_back(token);
    }
    return tokens;
}
// 输入: "apple,banana,cherry"
// 输出: ["apple", "banana", "cherry"]
```

---
### 5. 高级技巧：清空与复用
```cpp
std::stringstream ss;

// 第一次使用
ss << 100;
std::string s1 = ss.str(); // "100"

// ❌ 错误做法：直接再次写入
ss << 200; 
// 结果会是 "100200" (追加模式)

// ✅ 正确做法：清空
ss.str("");           // 清空字符串内容
ss.clear();           // 重置错误标志 (eofbit, failbit 等)

ss << 200;
std::string s2 = ss.str(); // "200"
```

---
### 总结

- **简单数字转字符串** → 用 `std::to_string`。
- **复杂格式化 (补零、精度)** → 用 `std::stringstream` (或 C++20 `std::format`)。
- **解析字符串 (Split, 提取数字)** → 用 `std::istringstream`。
- **替代 `sprintf`** → 用 `std::ostringstream` 以获得类型安全和内存安全。