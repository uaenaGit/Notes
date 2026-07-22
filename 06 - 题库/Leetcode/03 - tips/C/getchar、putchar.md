---
created: 2026-03-05T23:55
updated: 2026-03-05T23:56
---
`getchar()` 和 `putchar()` 是 C 语言标准库 `<stdio.h>` 中用于**单个字符**输入输出的基础函数。它们比 `scanf`/`printf` 更轻量、更快，常用于处理字符流、过滤输入或实现简单的文本处理工具。

> **注意**：在 C++ 中，它们依然可用（包含在 `<cstdio>` 或 `<stdio.h>` 中），但 C++ 风格通常推荐使用 `cin.get()` 和 `cout.put()`。不过在处理底层字符流时，`getchar/putchar` 依然非常高效。

---

### 1. `getchar()` - 读取单个字符

#### 功能
从标准输入（通常是键盘）读取**下一个可用字符**。

#### 原型
```c
int getchar(void);
```
*   **返回值**：
    *   成功：返回读取字符的 **ASCII 码值**（`int` 类型）。
    *   失败/结束：返回 **`EOF`** (End Of File，通常定义为 -1)。
*   **为什么返回 `int` 而不是 `char`？**
    *   为了能够区分“有效字符”（0~255）和“结束标志”（-1）。如果返回 `char`，当文件真正包含值为 -1 的字节时会发生混淆。

#### 典型用法
```c
#include <stdio.h>

int main() {
    int c; // 必须用 int 接收，以便检测 EOF

    printf("请输入字符 (按 Ctrl+D/Z 结束):\n");

    // 循环读取直到遇到 EOF
    while ((c = getchar()) != EOF) {
        // 处理字符 c
        putchar(c); // 立即回显
    }

    return 0;
}
```

#### 常见陷阱：缓冲区残留
`getchar()` 会读取缓冲区中的**每一个**字符，包括你按下的 **回车键 (`\n`)**。
如果你先用了 `scanf("%d", &n);`，然后立刻用 `getchar()`，`getchar()` 会读取到 `scanf` 留下的那个换行符，而不是你期待的新输入。

**解决方法**：在混合使用时，通常需要吃掉换行符。
```c
int n;
scanf("%d", &n);
getchar(); // 吃掉 scanf 留下的 '\n'
char c = getchar(); // 现在读取的是用户新输入的字符
```

---

### 2. `putchar()` - 输出单个字符

#### 功能
将单个字符写入标准输出（通常是屏幕）。

#### 原型
```c
int putchar(int char);
```
*   **参数**：要输出的字符（可以是 `char` 或 `int` ASCII 码）。
*   **返回值**：
    *   成功：返回输出的字符。
    *   失败：返回 `EOF`。

#### 典型用法
```c
#include <stdio.h>

int main() {
    putchar('H');
    putchar('e');
    putchar('l');
    putchar('l');
    putchar('o');
    putchar('\n'); // 换行
    
    // 也可以输出 ASCII 码
    putchar(65); // 输出 'A'
    
    return 0;
}
```

---

### 3. 实战案例：结合使用

#### 案例 A：简单的回声程序 (Echo)
将用户输入的所有字符原样输出，直到遇到文件结束符。

```c
#include <stdio.h>

int main() {
    int c;
    // 逐字符读取并立即写出
    while ((c = getchar()) != EOF) {
        putchar(c);
    }
    return 0;
}
```
*用途*：这是 Linux/Unix 下 `cat` 命令的极简实现原理。

#### 案例 B：过滤特定字符
只输出输入中的大写字母，忽略其他所有字符。

```c
#include <stdio.h>
#include <ctype.h> // 用于 isupper

int main() {
    int c;
    while ((c = getchar()) != EOF) {
        if (isupper(c)) { // 如果是大写字母
            putchar(c);
            putchar('\n'); // 每个大写字母后换行
        }
    }
    return 0;
}
```

#### 案例 C：统计字符数
```c
#include <stdio.h>

int main() {
    long count = 0;
    while (getchar() != EOF) {
        count++;
    }
    printf("总字符数: %ld\n", count);
    return 0;
}
```

---

### 4. `getchar`/`putchar` vs `cin`/`cout` vs `scanf`/`printf`

| 特性 | `getchar` / `putchar` | `scanf` / `printf` | `cin` / `cout` |
| :--- | :--- | :--- | :--- |
| **操作单位** | **单个字符** | 格式化数据 (整数, 浮点, 字符串等) | 对象/数据类型 |
| **速度** | **最快** (无格式解析开销) | 较慢 (需解析格式字符串) | 较慢 (类型安全检查 + 流缓冲) |
| **灵活性** | 低 (只能处理字符) | 高 (强大的格式化能力) | 高 (可扩展，类型安全) |
| **适用场景** | 字符过滤器、逐字处理、高性能IO | 复杂格式输入输出 | C++ 通用开发 |
| **头文件** | `<stdio.h>` 或 `<cstdio>` | `<stdio.h>` 或 `<cstdio>` | `<iostream>` |

### 总结
*   当你需要**逐个处理字符**（如统计字数、转换大小写、过滤敏感词）时，`getchar()` 和 `putchar()` 是最高效、最简洁的选择。
*   当你需要处理**结构化数据**（如日期 `YYYY-MM-DD`、浮点数）时，请使用 `scanf`/`printf` 或 `cin`/`cout`。
*   **关键点**：始终用 `int` 变量接收 `getchar()` 的返回值，以正确判断 `EOF`。