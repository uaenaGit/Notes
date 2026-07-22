---
created: 2026-02-25T17:21
updated: 2026-02-25T18:53
---
`snprintf` 是 **C 标准库**中的格式化输出函数，是 `sprintf` 的**安全版本**，用于将格式化数据写入字符串缓冲区，并**防止缓冲区溢出**。

---

### 函数原型

```c
#include <stdio.h>

int snprintf(char *str, size_t size, const char *format, ...);
```

---
### 参数说明

| 参数       | 类型             | 说明                  |
| -------- | -------------- | ------------------- |
| `str`    | `char *`       | 目标字符数组指针            |
| `size`   | `size_t`       | 缓冲区**总大小**（包括 `\0`） |
| `format` | `const char *` | 格式字符串               |
| `...`    | 可变参数           | 与格式说明符对应的值          |

---
### 返回值

|情况|返回值|说明|
|---|---|---|
|**成功（未截断）**|写入的字符数（不含 `\0`）|返回值 < `size`|
|**成功（被截断）**|完整输出所需的字符数|返回值 ≥ `size`|
|**失败**|负值|编码错误等|

**关键特性**：返回值是**完整输出所需的字符数**，可用于检测是否发生截断。

---
### 基本示例
```c
#include <stdio.h>

int main() {
    char buffer[20];
    int num = 42;
    float pi = 3.14159;
    
    // 正常情况
    int ret = snprintf(buffer, sizeof(buffer), "数字: %d, 圆周率: %.2f", num, pi);
    // buffer: "数字: 42, 圆周率: 3.14"
    // ret: 22
    
    printf("%s\n", buffer);
    printf("完整长度: %d\n", ret);
    
    return 0;
}
```
---
### 安全特性演示
```c
// ❌ sprintf - 缓冲区溢出风险
char buf1[10];
sprintf(buf1, "%s", "这是一个非常长的字符串会溢出");  // 危险！

// ✅ snprintf - 自动截断保护
char buf2[10];
int ret = snprintf(buf2, sizeof(buf2), "%s", "这是一个非常长的字符串会溢出");
// buf2: "这是一个非\0"（自动截断并添加\0）
// ret: 实际需要的长度（>10，可检测截断）

if (ret >= sizeof(buf2)) {
    printf("警告：输出被截断！\n");
}
```
---
### 返回值检测截断
```c
char buffer[50];
int ret = snprintf(buffer, sizeof(buffer), "%s", long_string);

if (ret < 0) {
    // 编码错误
    printf("错误：编码问题\n");
} else if (ret >= sizeof(buffer)) {
    // 输出被截断
    printf("警告：缓冲区太小，需要 %d 字节\n", ret + 1);
} else {
    // 成功，完整输出
    printf("成功：写入 %d 字符\n", ret);
}
```
---
### `sprintf` vs `snprintf` 对比
| 特性      | `sprintf` | `snprintf` |
| ------- | --------- | ---------- |
| 缓冲区大小参数 | ❌ 无       | ✅ 有        |
| 溢出保护    | ❌ 无       | ✅ 自动截断     |
| 返回值     | 写入字符数     | 完整输出所需字符数  |
| 安全性     | ❌ 不安全     | ✅ 安全       |
| C 标准    | C89       | C99        |
| 推荐度     | ❌ 避免使用    | ✅ 推荐使用     |

---
### 常用格式说明符
|格式符|说明|示例|
|---|---|---|
|`%d`|十进制整数|`42`|
|`%u`|无符号整数|`42`|
|`%x` / `%X`|十六进制|`2a` / `2A`|
|`%f`|浮点数|`3.14`|
|`%s`|字符串|`"hello"`|
|`%c`|字符|`'A'`|
|`%p`|指针地址|`0x7fff...`|
|`%%`|百分号|`%`|
|`%02d`|补零整数|`05`|
|`%.2f`|保留小数|`3.14`|

---
### 实际应用示例
#### 1. 生成文件名
```c
char filename[256];
snprintf(filename, sizeof(filename), "data_%03d.txt", file_id);
// 结果: data_001.txt
```
#### 2. 构建日志消息
```c
char log_msg[512];
snprintf(log_msg, sizeof(log_msg), 
         "[ERROR] Code: %d, Message: %s", error_code, error_msg);
```
#### 3. 数字格式化
```c
char num_str[20];
snprintf(num_str, sizeof(num_str), "%d", 12345);
```
#### 4. 拼接字符串（检测截断）
```c
char buffer[100];
int ret = snprintf(buffer, sizeof(buffer), "%s - %s", str1, str2);

if (ret >= sizeof(buffer)) {
    // 处理截断情况
}
```
### 常见陷阱
|陷阱|说明|解决方案|
|---|---|---|
|`size` 忘记算 `\0`|`size` 必须包含终止符|使用 `sizeof(buffer)`|
|忽略返回值|无法检测截断|始终检查返回值|
|重复使用返回值|截断后返回值仍是完整长度|理解返回值含义|
|嵌套调用|`snprintf` 返回值用于下一次调用|仔细计算剩余空间|
### C++ 替代方案
| 方案                    | 代码示例                         | 说明        |
| --------------------- | ---------------------------- | --------- |
| `std::to_string`      | `std::to_string(42)`         | 数字转字符串    |
| `std::stringstream`   | `ss << "num: " << 42`        | 流式拼接      |
| `std::format` (C++20) | `std::format("{}:{}", h, m)` | 类似 Python |
| `fmt::format`         | `fmt::format("{}:{}", h, m)` | 第三方库      |
[[stringstream]] 介绍