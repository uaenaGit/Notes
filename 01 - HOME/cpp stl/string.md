C++ 的 `std::string`（定义在 `<string>` 头文件中）提供了丰富的方法来操作字符串。以下是 **常用方法的分类整理**，附带简要说明和示例，适用于 C++11 及以上标准。
## 📌 前置说明

- 所有代码需包含：`#include <iostream>` 和 `#include <string>`
- 使用命名空间：`using namespace std;`
- 编译标准：C++11 或更高

### 1️⃣ 构造与赋值方法
|方法|参数说明|功能|
|---|---|---|
|`string()`|无|默认构造空字符串|
|`string(const char* s)`|C 风格字符串|从 C 字符串构造|
|`string(const string& str)`|另一个 string 对象|拷贝构造|
|`string(size_t n, char c)`|n: 个数, c: 字符|构造由 n 个 c 组成的字符串|
|`operator=`|string / const char* / char|赋值操作|
|`assign(...)`|多种重载（见示例）|赋值，支持指定长度或重复字符|
#### 💻 代码示例
```cpp
#include <iostream>
#include <string>

using namespace std;

int main() {
    // 构造
    string s1;                      // ""
    string s2 = "Hello";            // "Hello"
    string s3(s2);                  // "Hello" (拷贝)
    string s4(5, 'A');              // "AAAAA"
    
    // 赋值
    s1 = "New";                     // 赋值 C 字符串
    s1 = s2;                        // 赋值 string
    s1.assign("Assigned");          // assign(string)
    s1.assign(3, 'X');              // "XXX"
    s1.assign("Hello World", 5);    // "Hello" (取前5个字符)

    cout << "s1: " << s1 << endl;   // Hello
    cout << "s4: " << s4 << endl;   // AAAAA
    return 0;
}
```

### 2️⃣ 访问与转换方法
| 方法               | 参数说明           | 功能                         |
| ---------------- | -------------- | -------------------------- |
| `operator[]`     | size_t pos     | 返回 pos 处字符（无边界检查）          |
| `at(size_t pos)` | pos: 位置        | 返回 pos 处字符（越界抛出异常）         |
| `front()`        | 无              | 返回首字符（C++11）               |
| `back()`         | 无              | 返回末尾字符（C++11）              |
| `c_str()`        | 无              | 返回以 `\0` 结尾的 `const char*` |
| `data()`         | 无              | 返回字符指针（C++11 起也带 `\0`）     |
| `to_string()`    | 各种数值类型（整型、浮点型） | `std::string`，表示数值的字符串形式   |
```cpp
#include <iostream>
#include <string>

using namespace std;

int main() {
    string s = "Hello";
    // 访问
    cout << "s[0]: " << s[0] << endl;        // H
    cout << "s.at(1): " << s.at(1) << endl;  // e
    cout << "front: " << s.front() << endl;  // H
    cout << "back: " << s.back() << endl;    // o
    
    // 转换
    printf("C-style: %s\n", s.c_str());      // Hello
    const char* p = s.data();
    cout << "Data: " << p << endl;           // Hello

    return 0;
}
```

### 3️⃣ 容量与状态方法
|方法|参数说明|功能|
|---|---|---|
|`size()` / `length()`|无|返回字符个数（等价）|
|`empty()`|无|判断是否为空（`size() == 0`）|
|`capacity()`|无|当前分配的存储容量|
|`max_size()`|无|理论最大长度（系统限制）|
|`clear()`|无|清空内容（`size()` 变为 0）|
```cpp
#include <iostream>
#include <string>

using namespace std;

int main() {
    string s = "Hello";

    cout << "Size: " << s.size() << endl;        // 5
    cout << "Length: " << s.length() << endl;    // 5
    cout << "Empty? " << s.empty() << endl;      // 0 (false)
    cout << "Capacity: " << s.capacity() << endl; // ≥5
    cout << "Max size: " << s.max_size() << endl;

    s.clear();
    cout << "After clear, size: " << s.size() << endl; // 0
    cout << "Now empty? " << s.empty() << endl;        // 1 (true)
    
    return 0;
}
```
### 4️⃣ 修改操作方法（拼接、插入、删除、替换）
|方法|参数说明|功能|
|---|---|---|
|`+=`|string / const char* / char|拼接内容|
|`append(...)`|多种重载|追加字符串或字符|
|`push_back(char c)`|c: 字符|在末尾添加一个字符|
|`insert(...)`|pos/iterator + 内容|在指定位置插入|
|`erase(...)`|pos+len 或 iterator 范围|删除字符|
|`replace(...)`|pos+len + 新内容|替换子串|
|`pop_back()`|无|移除最后一个字符（C++11）|
```cpp
#include <iostream>
#include <string>

using namespace std;

int main() {
    string s = "Hi";
  
    // 拼接
    s += " World";                // "Hi World"
    s.append("!");                // "Hi World!"
    s.push_back('?');             // "Hi World!?"
  
    // 插入
    s.insert(2, ",");             // "Hi, World!?"

    // 删除
    s.erase(0, 3);                // 删除 "Hi," → " World!?"

    // 替换
    s.replace(1, 5, "C++");       // " C++!?"

    // 移除末尾
    s.pop_back();                 // " C++!

    cout << "Final: \"" << s << "\"" << endl; // " C++!

    return 0;
}
```

### 5️⃣ 子串与查找方法
| 方法                                         | 参数说明             | 功能                    |
| ------------------------------------------ | ---------------- | --------------------- |
| `substr(size_t pos, size_t len = npos)`    | pos: 起始, len: 长度 | 提取子串                  |
| `find(...)`                                | 子串/字符, 起始位置      | 正向查找（返回位置）            |
| `rfind(...)`                               | 同上               | 从后往前查找                |
| `find_first_of(...)`                       | 字符集, 起始          | 找任意一个匹配字符首次出现         |
| `find_first_not_of(...)`                   | 字符集, 起始          | 找第一个不匹配字符             |
| `copy(char* dest, size_t len, size_t pos)` | 目标数组, 长度, 起始     | 复制子串到 C 数组（不自动加 `\0`） |
>⚠️ 所有查找函数未找到时返回 `string::npos`
```cpp
#include <iostream>
#include <string>
#include <cstring> // for memset

using namespace std; 

int main() {
    string s = "Hello World";
    
    // 子串
    string sub = s.substr(6, 5);  // "World"
    cout << "Substr: " << sub << endl;

    // 查找
    size_t p1 = s.find("World");           // 6
    size_t p2 = s.rfind('o');              // 7
    size_t p3 = s.find_first_of("aeiou");  // 1 ('e')
    size_t p4 = s.find_first_not_of("Helo "); // 6 ('W')

    cout << "find: " << p1 << ", rfind: " << p2 << endl;
    cout << "first vowel: " << p3 << ", first not in set: " << p4 << endl;

  
    // copy 到 C 数组
    char buffer[10];
    memset(buffer, 0, sizeof(buffer)); // 初始化
    s.copy(buffer, 5, 0); // 复制前5个字符到 buffer
    cout << "Copied: " << buffer << endl; // "Hello"

    // 判断是否存在
    if (s.find("xyz") == string::npos) {
        cout << "\"xyz\" not found" << endl;
    }

    return 0;
}
```
### 6️⃣ 比较与迭代方法
| 方法                             | 参数说明                 | 功能            |
| ------------------------------ | -------------------- | ------------- |
| `compare(...)`                 | string / 子串          | 比较（返回 -1/0/1） |
| `operator==, !=, <, <=, >, >=` | string / const char* | 字典序比较         |
| `begin()`, `end()`             | 无                    | 正向迭代器         |
| `rbegin()`, `rend()`           | 无                    | 反向迭代器         |
```cpp
#include <iostream>
#include <string>

using namespace std;

int main() {
    string a = "apple";
    string b = "banana";
    
    // 比较
    cout << "a == b? " << (a == b) << endl;     // 0
    cout << "a < b? " << (a < b) << endl;       // 1

    cout << "compare: " << a.compare(b) << endl; // -1
  
    // 迭代
    string s = "Hi";
    cout << "Forward: ";

    for (auto it = s.begin(); it != s.end(); ++it) {
        cout << *it;
    }

    cout << endl; // Hi
    cout << "Reverse: ";

    for (auto rit = s.rbegin(); rit != s.rend(); ++rit) {
        cout << *rit;
    }

    cout << endl; // iH
  
    // 范围 for（推荐）
    cout << "Range-for: ";
    for (char c : s) cout << c; // Hi

    cout << endl;
    return 0;
}
```
