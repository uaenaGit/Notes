---
created: 2026-02-25T17:10
updated: 2026-02-25T17:24
---
`__builtin_popcount` 是 **GCC 和 Clang 编译器**提供的内置函数，用于计算整数的二进制表示中 **1 的个数**（汉明重量/Hamming Weight）。

---
### 函数原型
| 函数                     | 参数类型                 | 返回值   | 说明      |
| ---------------------- | -------------------- | ----- | ------- |
| `__builtin_popcount`   | `unsigned int`       | `int` | 32位整数   |
| `__builtin_popcountl`  | `unsigned long`      | `int` | long 类型 |
| `__builtin_popcountll` | `unsigned long long` | `int` | 64位整数   |
```c
int __builtin_popcount(unsigned int x); 
int __builtin_popcountl(unsigned long x); 
int __builtin_popcountll(unsigned long long x);
```
```c
// 纯C手动实现（Brian Kernighan算法）
int popcount(unsigned int x) {
    int count = 0;
    while (x) {
        x &= (x - 1);
		count++;
    }
    return count;
}
```

---
### 使用示例
```c
#include <iostream>
using namespace std;

int main() {
    cout << __builtin_popcount(5) << endl;    // 5 = 101₂，输出 2
    cout << __builtin_popcount(7) << endl;    // 7 = 111₂，输出 3
    cout << __builtin_popcount(0) << endl;    // 输出 0
    cout << __builtin_popcount(-1) << endl;   // 全1，输出 32
    
    // 64位版本
    cout << __builtin_popcountll(0xFFFFFFFFFFFFFFFFULL) << endl;  // 输出 64
    
    return 0;
}
```

---
### 典型应用场景
```cpp
// 1. 算法竞赛 - 位掩码枚举
for (int mask = 0; mask < (1<<n); mask++) {
    if (__builtin_popcount(mask) == k) {
        // 处理恰好k个1的状态
    }
}

// 2. 计算集合交集大小
int intersection_size = __builtin_popcount(setA & setB);

// 3. 判断2的幂
bool is_power_of_two = (x > 0) && (__builtin_popcount(x) == 1);

// 4. 二进制中1的奇偶性（奇校验）
bool odd_parity = __builtin_popcount(x) & 1;

// 5. 你的二进制手表问题
if (__builtin_popcount(h) + __builtin_popcount(m) == turnedOn) {
    // 符合条件的时间
}
```

---
### 注意事项
|注意点|说明|
|---|---|
|有符号数|建议转为 `unsigned` 再计算|
|类型匹配|32位用 `popcount`，64位用 `popcountll`|
|MSVC兼容|Windows/MSVC 需用 `__popcnt`|
|C++20优先|新项目建议用 `std::popcount`|
|编译选项|x86需 `-mpopcnt` 启用硬件指令|

---
### C++20 标准替代

C++20 引入了标准库函数，推荐优先使用：
```cpp
#include <bit>
int count = std::popcount(x); // C++20 标准，跨平台
```
