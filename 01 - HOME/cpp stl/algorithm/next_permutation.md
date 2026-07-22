---
created: 2026-03-06T20:27
updated: 2026-03-06T20:27
---
这是一份为您精心整理的 **C++ `std::next_permutation` 全方位方法详解**。

`std::next_permutation` 是 C++ 标准模板库（STL）中 `<algorithm>` 头文件下的一个**神器级函数**。它能以极高的效率生成序列的**下一个字典序排列**，将原本需要几十行递归代码才能完成的全排列问题，简化为寥寥几行。

这份指南严格遵循 C++11 及以上标准，**重点解析了其内部原理、标准用法模板以及常见陷阱**。

---

# 📚 C++ `std::next_permutation` 完全指南 (C++11+)

### 📌 前置准备
```cpp
#include <iostream>
#include <vector>
#include <algorithm> // 必须包含此头文件
#include <numeric>   // 用于 std::iota 生成初始序列

using namespace std;
```

> **核心特性速览**：
> 1. **字典序驱动**：严格按照字典序（从小到大）生成下一个排列。
> 2. **原地修改**：直接修改传入的序列，不创建新容器。
> 3. **循环闭合**：当已是最大排列时，自动重置为最小排列并返回 `false`。
> 4. **高效性**：均摊时间复杂度 $O(1)$，最坏 $O(N)$，远优于手写递归。
> 5. **去重支持**：天然支持重复元素，不会生成重复的排列。

---

## 1️⃣ 函数原型与参数 (Function Signature)
`next_permutation` 有两种重载形式，分别适用于默认比较和自定义比较。

| 形式 | 参数详解 | 返回值 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **`bool next_permutation(BidirectionalIterator first, BidirectionalIterator last)`** | `first`: 起始迭代器`last`: 结束迭代器（开区间） | `true`: 成功找到下一个排列`false`: 当前已是最大排列，已重置为最小 | 使用元素类型的默认 `<` 运算符进行比较。 |
| **`bool next_permutation(BidirectionalIterator first, BidirectionalIterator last, Compare comp)`** | `comp`: 自定义比较函数/对象 | 同上 | 使用自定义规则判断“小于”。常用于结构体或特殊排序规则。 |

> **注意**：迭代器必须是**双向迭代器**（Bidirectional Iterator），`vector`、`string`、`deque`、数组均支持，但 `forward_list` 不支持。

---

## 2️⃣ 标准用法模板 (The Golden Pattern)
这是使用 `next_permutation` 生成**全排列**的标准“三板斧”。**缺一不可**。

### 💻 代码示例：生成数字全排列
```cpp
int main() {
    vector<int> nums = {3, 1, 2}; // 初始顺序可以是乱的

    // 【第一步】排序！排序！排序！
    // 必须先从“最小字典序”开始，否则会漏掉前面的排列
    sort(nums.begin(), nums.end()); 

    // 【第二步】do-while 循环
    do {
        // 处理当前排列
        for (int x : nums) cout << x << " ";
        cout << endl;
        
    // 【第三步】生成下一个
    // 若成功生成下一个，返回 true 继续循环；
    // 若已是最后一个（如 3 2 1），返回 false 并重置为 1 2 3，循环结束
    } while (next_permutation(nums.begin(), nums.end()));

    return 0;
}
```

**输出结果**：
```text
1 2 3
1 3 2
2 1 3
2 3 1
3 1 2
3 2 1
```

### ⚠️ 致命陷阱：忘记排序
如果你去掉 `sort`，直接从 `{3, 1, 2}` 开始：
- 程序会从 `3 1 2` 开始找“比它大”的下一个。
- **结果**：`1 2 3` 和 `1 3 2` 这两个比 `3 1 2` 小的排列将**永远被遗漏**。
- **结论**：**除非你确定当前序列已经是最小字典序，否则必须先 `sort`。**

---

## 3️⃣ 内部原理：它是如何工作的？
理解原理有助于调试和应对变种题目。`next_permutation` 通过以下三步找到下一个排列（以 `1 5 4 3 2` 为例）：

1. **查找分界点（从右向左）**：
   - 寻找第一对相邻元素 `(i, i+1)`，满足 `nums[i] < nums[i+1]`。
   - 在 `1 5 4 3 2` 中，`1 < 5`，所以 `i` 指向 `1`。
   - *如果找不到这样的 `i`（整个序列降序），说明已是最大排列。*

2. **查找交换对象（从右向左）**：
   - 在 `i` 右侧的部分（`5 4 3 2`）中，寻找**第一个**比 `nums[i]` **大**的元素 `nums[j]`。
   - 在 `5 4 3 2` 中，比 `1` 大的最小数是 `2`（最右边的那个），所以 `j` 指向 `2`。

3. **交换并反转**：
   - **交换** `nums[i]` 和 `nums[j]` → 序列变为 `2 5 4 3 1`。
   - **反转** `i+1` 到末尾的部分（使其变为最小序）→ `5 4 3 1` 反转为 `1 3 4 5`。
   - **最终结果**：`2 1 3 4 5`。这就是紧邻的下一个字典序排列。

---

## 4️⃣ 高级应用与自定义规则

### 场景 A：处理重复元素（自动去重）
`next_permutation` 天生智能，如果序列中有重复元素，它**不会**生成重复的排列。

```cpp
vector<int> v = {1, 2, 2};
sort(v.begin(), v.end());
do {
    // 输出：1 2 2, 2 1 2, 2 2 1
    // 只有 3 种，而不是 3! = 6 种
} while (next_permutation(v.begin(), v.end()));
```

### 场景 B：自定义结构体排序
如果存储的是结构体，需要传入第三个参数 `comp`，或者在结构体中重载 `<` 运算符。

```cpp
struct Fruit {
    string name;
    int price;
    // 重载 < 运算符：先比价格，价格相同比名字
    bool operator<(const Fruit& other) const {
        if (price != other.price) return price < other.price;
        return name < other.name;
    }
};

int main() {
    vector<Fruit> fruits = {{"Apple", 10}, {"Banana", 5}, {"Cherry", 10}};
    sort(fruits.begin(), fruits.end());
    
    do {
        // 按自定义规则生成下一个排列
    } while (next_permutation(fruits.begin(), fruits.end()));
    
    return 0;
}
```

### 场景 C：反向生成（上一个排列）
如果需要**从大到小**生成排列，可以使用兄弟函数 `std::prev_permutation`。
- **用法**：先排成**降序**（最大字典序），然后用 `do-while(prev_permutation(...))`。

```cpp
vector<int> v = {1, 2, 3};
// 先排成最大序
sort(v.begin(), v.end(), greater<int>()); 

do {
    // 输出：3 2 1, 3 1 2, ..., 1 2 3
} while (prev_permutation(v.begin(), v.end()));
```

---

## 5️⃣ `next_permutation` vs 手写递归

| 特性 | `std::next_permutation` | 手写 DFS 递归 |
| :--- | :--- | :--- |
| **代码量** | 极少（3-5 行） | 较多（10-20 行） |
| **易错性** | 低（库函数保证正确） | 高（回溯、状态恢复易错） |
| **去重处理** | **自动处理** | 需手动写 `used` 数组或 `set` 去重 |
| **灵活性** | 只能按字典序 | 可随意定义搜索顺序、剪枝策略 |
| **性能** | 极快（均摊 $O(1)$） | 取决于剪枝效果 |
| **适用场景** | 全排列枚举、字典序问题 | 需要复杂剪枝、非字典序搜索 |

> **建议**：如果是纯粹的全排列枚举题目（如 NOIP/ACM 基础题），**优先使用 `next_permutation`**，既快又稳。只有在需要复杂剪枝（如数独、N皇后）时，才手写 DFS。

---

## 6️⃣ 常见面试题与实战

1.  **“下一个排列” (LeetCode 31)**：
    - 题目要求实现 `next_permutation` 的功能。如果你知道上述的“三步走”原理，可以直接模拟实现。
    
2.  **第 K 个排列**：
    - 虽然可以用数学方法 $O(N)$ 求解，但在 $N$ 较小（如 $N \le 9$）时，直接循环调用 $K-1$ 次 `next_permutation` 也是可行的解法。

3.  **字符串全排列**：
    - 直接作用于 `std::string`，因为 `string` 支持双向迭代器。
    ```cpp
    string s = "ABC";
    sort(s.begin(), s.end());
    do {
        cout << s << endl;
    } while (next_permutation(s.begin(), s.end()));
    ```

---

### 💡 核心总结
1. **头文件**：`#include <algorithm>`。
2. **黄金法则**：**先 `sort` 升序，再 `do-while` 循环**。
3. **返回值**：`true` 表示还有下一个，`false` 表示已轮回重置。
4. **去重**：天然支持重复元素，无需额外操作。
5. **原理**：**找拐点 -> 找交换值 -> 交换 -> 反转后缀**。

**一句话口诀**：
> “全排列，不用慌，Algorithm 里找帮忙；
> 先排序，后循环，Do-While 保平安；
> 有重复，自动去，字典序里它最强。”