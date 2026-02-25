---
created: 2026-02-25T17:10
updated: 2026-02-25T17:18
---
`__builtin_popcount` 是 **GCC 和 Clang 编译器**提供的内置函数，用于计算整数的二进制表示中 **1 的个数**（汉明重量/Hamming Weight）。
### 函数原型
|函数|参数类型|返回值|说明|
|---|---|---|---|
|`__builtin_popcount`|`unsigned int`|`int`|32位整数|
|`__builtin_popcountl`|`unsigned long`|`int`|long 类型|
|`__builtin_popcountll`|`unsigned long long`|`int`|64位整数|
```c
int __builtin_popcount(unsigned int x); 
int __builtin_popcountl(unsigned long x); 
int __builtin_popcountll(unsigned long long x);
```
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
### 典型应用场景
```
```