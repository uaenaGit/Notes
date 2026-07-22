---
created: 2026-02-25 22:42
tags:
  - debug
  - troubleshooting
status: 🔴 进行中
priority: ⭐⭐⭐
updated: 2026-02-25T23:18
---

# 🐛 问题调试记录

## 📋 问题概述
**标题**: 在力扣刷题的过程中，使用了`sort`函数的第三个参数自定义比较规则，但是控制台报错
**发现时间**: 2026-02-25
**影响范围**: 编译不通过

## 📝 问题描述
<!-- 详细描述遇到的问题，包括预期行为和实际行为 -->
在类中的`private`域中写了一个比较函数`cmp`，传给`sort`函数做第三个参数时，报错

## 🖥️ 环境信息
| 项目   | 信息    |
| ---- | ----- |
| 操作系统 | win11 |
| 软件版本 | 无     |
| 相关依赖 | 无     |
| 硬件配置 | 无     |

## 📝 错误日志（或截图）
![image.png](https://cdn.jsdelivr.net/gh/uaenaGit/image-host@main/images20260225225709487.png)

`error: reference to non-static member function must be called sort(nums.begin(), nums.end(), cmp);`

## ✅ 已尝试的解决方案
| 序号  | 方案                      | 结果   | 时间        |
| --- | ----------------------- | ---- | --------- |
| 1   | 将`cmp` 函数放在类的`public`域中 | ❌ 失败 | 2026/2/25 |
| 2   |                         | ❌ 失败 |           |
| 3   |                         | ✅ 成功 |           |

## 🔬 原因分析
### 假设1
- 推测原因: 将 `cmp` 函数放在类内的 `private` 域里
- 验证方法: 将 `cmp` 函数放在类内的 `public` 域
- 验证结果: 报错相同

### 假设2
- 推测原因:
- 验证方法:
- 验证结果:

### 根因
**根本原因**是因为 `cmp` 是一个**非静态成员函数**（non-static member function）。
#### 核心原因解析
1. **非静态成员函数的特性**：  
任何定义在类中且没有 `static` 关键字的函数，都隐含了一个 `this` 指针参数。  
你的 `cmp` 函数实际签名是：
```cpp
bool cmp(Solution* this, PII a, PII b);
```

2.  **`std::sort` 的要求**：
    `std::sort` 需要的比较函数签名是：
    ```cpp
    bool func(PII a, PII b);
    ```
    它只需要**2个参数**。

3.  **冲突**：
    当你把 `cmp` 传给 `sort` 时，编译器==不知道该如何处理那个隐藏的 `this` 指针==（因为没有具体的对象实例来调用它），所以报错：**“引用非静态成员函数必须调用”**（意思是：你不能直接拿这个函数地址，你必须通过对象来调用它，比如 `obj.cmp(a, b)`，但 `sort` 内部没法这么干）。

    *注：即使你把 `cmp` 放到 `public`，只要不加 `static`，错误依然一样。*

---

### ✅ 解决方案（三种任选其一）

#### 方案 1：加上 `static` 关键字（修改最小）
既然 `cmp` 逻辑只依赖传入的参数，不依赖类的成员变量，把它声明为 `static` 即可去掉隐藏的 `this` 指针。

```cpp
class Solution {
private:
    typedef pair<int, int> PII;
    
    // 👇 加上 static
    static bool cmp(PII a, PII b) {
        if (a.first != b.first) {
            return a.first < b.first;
        }
        return a.second < b.second;
    }

public:
    vector<int> sortByBits(vector<int>& arr) {
        // ... 前面代码不变 ...
        sort(nums.begin(), nums.end(), cmp); // 现在可以了
        // ... 后面代码不变 ...
    }
};
```

#### 方案 2：使用 Lambda 表达式（推荐，最现代 C++ 风格）
直接在 `sort` 里面写逻辑，不用额外定义函数，代码更紧凑。

```cpp
class Solution {
private:
    typedef pair<int, int> PII;

public:
    vector<int> sortByBits(vector<int>& arr) {
        int n = arr.size();
        vector<PII> nums;
        for (auto &num : arr) {
            int cnt = __builtin_popcount(num);
            nums.push_back({cnt, num});
        }

        // 👇 直接使用 Lambda 表达式
        sort(nums.begin(), nums.end(), [](const PII& a, const PII& b) {
            if (a.first != b.first) {
                return a.first < b.first;
            }
            return a.second < b.second;
        });

        // ... 后面代码不变 ...
    }
};
```

#### 方案 3：定义为全局函数或私有静态辅助结构体
如果逻辑很复杂，也可以定义一个专门的结构体（Functor），但这题没必要。

## 💡 最终解决方案
<!-- 记录最终解决问题的方法 -->
<!-- 修改前代码 -->
```cpp
class Solution {
private:
    typedef pair<int, int> PII;
    bool cmp(PII a, PII b) {
        if (a.first != b.first) {
            return a.first < b.first;
        } else {
            return a.second < b.second;
        }
    }
public:
    vector<int> sortByBits(vector<int>& arr) {
        int n = arr.size();
        vector<PII> nums;
        for (auto &num : arr) {
            int cnt = __builtin_popcount(num);
            nums.push_back({cnt, num});
        }
        sort(nums.begin(), nums.end(), cmp);
        vector<int> res(n);
        for (int i = 0; i < n; i++) {
            res[i] = nums[i].second;
        }
        return res;
    }
};
```

<!-- 修改后代码 -->
```cpp
class Solution {
private:
    typedef pair<int, int> PII;
    static bool cmp(PII a, PII b) {
        if (a.first != b.first) {
            return a.first < b.first;
        } else {
            return a.second < b.second;
        }
    }
public:
    vector<int> sortByBits(vector<int>& arr) {
        int n = arr.size();
        vector<PII> nums;
        for (auto &num : arr) {
            int cnt = __builtin_popcount(num);
            nums.push_back({cnt, num});
        }
        sort(nums.begin(), nums.end(), cmp);
        vector<int> res(n);
        for (int i = 0; i < n; i++) {
            res[i] = nums[i].second;
        }
        return res;
    }
};
```

## 📚 参考资料
- [链接1]()
- [链接2]()

## 🎯 经验总结
<!-- 记录本次调试的收获和避免复现的方法 -->
- 使用 `sort` 函数的第三个参数时，必须是静态成员函数
- 使用 `lambda` 函数
```cpp
class Solution {
private:
    typedef pair<int, int> PII;
public:
    vector<int> sortByBits(vector<int>& arr) {
        int n = arr.size();
        vector<PII> nums;
        for (auto &num : arr) {
            int cnt = __builtin_popcount(num);
            nums.push_back({cnt, num});
        }
        sort(nums.begin(), nums.end(), [](const PII &a, const PII &b) {
            if (a.first != b.first) {
                return a.first < b.first;
            } else {
                return a.second < b.second;
            }
        });
        vector<int> res(n);
        for (int i = 0; i < n; i++) {
            res[i] = nums[i].second;
        }
        return res;
    }
};
```
-  `sort` 使用
```cpp
vector<int> b(n + 1);
sort(b.begin() + 1, b.end()); // 升序
sort(b.begin() + 1, b.end(), greater<int>()); // 降序
```
## 📎 附件
- [x] 相关截图 ✅ 2026-02-25
- [ ] 日志文件
- [x] 代码片段 ✅ 2026-02-25

---
**最后更新**: 2026-02-25 22:42
## 解决状态
- [ ] ⬜ 未解决
- [ ] 🟠 进行中
- [ ] 🟡 部分解决
- [x] 🟢 已解决 ✅ 2026-02-25