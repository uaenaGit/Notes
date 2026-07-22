---
难度: 简单
情况: N(不会)
日期: 2026-03-20 21:38
分类: 暴力, 动态规划
tags:
  - 睛问
备注: next_permutation；状态压缩dp
created: 2026-03-20T21:36
updated: 2026-03-20T23:19
---

> 🔗[0 - 暴力next_permutation模版](https://sunnywhy.com/camp/3415/model/3591?itemId=4202)

## 📌 题目描述
> （请在此处粘贴题目描述）

### 题目描述
有 10 张卡片，每张卡片上写有一个不同的整数。你需要将这些卡片排成一排。给定一个整数 $K$，要求排列中任意相邻两张卡片上的数字之差的绝对值不超过 $K$。求满足条件的排列有多少种。

注意：卡片上的整数互不相同。

### 输入描述
输入共两行。
- 第一行包含一个整数 $K$（$0 \le K \le 10^9$），表示相邻数字差的最大允许值。
- 第二行包含 10 个不同的整数 $a_1,a_2,\dots,a_{10}$（$-10^9 \le a_i \le 10^9$），表示每张卡片上的数字。

### 输出描述
输出一个整数，表示满足条件的排列数。

### 样例 1
**输入**
1
1 2 3 4 5 6 7 8 9 10


**输出**
2

**解释**
给定的 10 张卡片上的数字是从 1 到 10 的连续整数，$K=1$。要求相邻数字差的绝对值不超过 1，因此只有严格递增 $(1,2,3,\dots,10)$ 和严格递减 $(10,9,8,\dots,1)$ 两种排列满足条件。

## 💡 解题思路 
解题思路：`状态压缩 DP`

由于只有 10 张卡片，我们可以用一个二进制数来表示哪些卡片已经被使用，进而通过动态规划来计数所有满足相邻限制的排列。

具体来说，令 `dp[mask][last]` 表示当前已经使用的卡片集合为 `mask`（`mask` 的二进制位中为 1 的位表示对应的卡片已用），且排列的最后一张卡片是第 `last` 张（`last` 是卡片在输入数组中的下标）时的方案数。

初始时，我们只使用一张卡片，因此对于每个 $i$：
$$
dp[1 << i][i] = 1
$$

接下来考虑如何扩展状态。假设当前状态为 $(mask, last)$，其方案数为 $dp[mask][last]$。我们想要在排列的末尾再添加一张卡片，那么就需要从尚未使用的卡片中选一张 `nxt`（即 `nxt` 满足 `mask` 的第 `nxt` 位为 0），并且要求新卡片上的数字与当前最后一张卡片上的数字之差的绝对值不超过 $K$，即：
$$
|a[last] - a[nxt]| \le K
$$
如果满足条件，那么我们就可以将 `nxt` 接在 `last` 后面，得到一个新的状态 $(mask | (1 << nxt), nxt)$，并将 $dp[mask][last]$ 加到 $dp[mask | (1 << nxt)][nxt]$ 上。

我们从小到大枚举所有 `mask`（从只包含一个元素到包含所有元素），并对于每个 `mask` 枚举可能的 `last`（要求 `last` 在 `mask` 中）和 `nxt`（要求 `nxt` 不在 `mask` 中），逐步计算出所有状态的值。最终，当 `mask` 为全 1（即 $(1 << 10) - 1$）时，所有 `last` 对应的 $dp[mask][last]$ 之和就是满足条件的排列总数。
## 💻 代码实现
> my answer

暴力枚举:
```cpp
#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;

int main() {
    int K;
    cin >> K;  // 输入最大允许的相邻差值
    vector<int> a(10);  // 存储10张卡片上的数字
    for (int i = 0; i < 10; i++) {
        cin >> a[i];  // 输入卡片上的数字
    }

    sort(a.begin(), a.end()); // 必须先排序，不然next_permutation会从中间状态开始执行，导致漏解

    // 使用 next_permutation 枚举所有排列
    int count = 0;  // 计数符合条件的排列数
    do {
        bool valid = true;
        // 检查相邻数字的差值是否符合条件
        for (int i = 0; i < 9; i++) {
            if (abs(a[i] - a[i + 1]) > K) {
                valid = false;  // 如果某个相邻数字的差值超过K，标记无效
                break;
            }
        }
        if (valid) {
            count++;  // 如果满足条件，增加计数
        }
    } while (next_permutation(a.begin(), a.end()));  // 获取下一个排列

    cout << count << endl;  // 输出符合条件的排列数

    return 0;
}
```

- **时间复杂度**：$O(10!)$
这段代码的核心是用 `next_permutation` 枚举 10 个元素的全排列，再逐个检查排列是否合法，我们可以拆解计算：

- **全排列枚举**：10 个不同元素的全排列总数是 10!=3628800（约 363 万次循环）。
- **单次排列检查**：每个排列需要遍历 9 对相邻元素（`i从0到8`），做一次绝对值差判断，这是 O(1) 操作（因为固定检查 9 次，和输入规模无关）。
- **排序操作**：`sort(a.begin(), a.end())` 对 10 个元素排序，时间复杂度是 O(10log10)，属于常数级，可忽略。

因此**总时间复杂度**：O(10!×1)=O(10!)≈3.6×106（常数级时间复杂度，因为 10 是固定值）。

> 补充：如果卡片数量是变量 n（而非固定 10），时间复杂度会写成 O(n!)，这是指数级复杂度，但本题中 n=10 是固定值，所以实际运行效率很高（363 万次循环在 C++ 中毫秒级就能完成）。

- **空间复杂度**：$O(1)$

> to optimize

状态压缩dp:
```cpp
#include <iostream>
#include <vector>
using namespace std;

const int MAXN = 10; 
vector<int> a(MAXN); 
// dp[mask][last]: 
// mask: 一个二进制数，表示“已经使用了哪些卡片”。第 i 位为 1 表示第 i 张卡片已用。
// last: 表示当前排列的“最后一张卡片”的下标。
// 值：满足上述状态的合法排列方案数。
vector<vector<int>> dp(1 << MAXN, vector<int>(MAXN, 0)); 
int main() {
    cin >> K;
    for (int i = 0; i < MAXN; ++i) {
        cin >> a[i];
    }
    // 初始化：只选一张卡片作为排列的第一个
    for (int i = 0; i < MAXN; ++i) {
        dp[1 << i][i] = 1;
    }
    int fullMask = (1 << MAXN) - 1;  // 全集掩码，表示所有卡片都被使用
	for (int mask = 1; mask <= fullMask; ++mask) {      // 从小到大枚举所有可能的卡片集合
		for (int last = 0; last < MAXN; ++last) {       // 枚举当前集合的最后一张卡片是谁
			if (!(mask & (1 << last))) continue;        // 剪枝：如果 last 不在 mask 里，跳过
			int cur = dp[mask][last];                   // 取出到达这个状态的方案数
			if (cur == 0) continue;                     // 剪枝：如果方案数为 0，没必要往下推
			
			// 尝试在末尾接上一张新卡片 nxt
			for (int nxt = 0; nxt < MAXN; ++nxt) {      
				if (mask & (1 << nxt)) continue;        // 剪枝：如果 nxt 已经用过了，跳过
				
				// 检查限制条件：相邻差值 <= K
				int diff = abs(a[last] - a[nxt]);       
				if (diff <= K) {                        
					// 状态转移：
					// 新状态：mask | (1 << nxt) (把 nxt 加入集合)
					// 新结尾：nxt
					// 方案数累加：加上当前的方案数 cur
					dp[mask | (1 << nxt)][nxt] += cur;  
				}
			}
		}
	}
    int ans = 0;
    for (int i = 0; i < MAXN; ++i) {
        ans += dp[fullMask][i];                         // 累加所有卡片都使用且以任意卡片结尾的排列数
		// 我们不知道最后停在谁手上，所以要把以任意卡片 i 结尾的所有情况加起来。
    }
    cout << ans << '\n';
    return 0;
}
```

- **时间复杂度**：$O(2^{10} * 10 * 10)$
- **空间复杂度**：$O(...)$

>✨ tips

> others' answer

- **时间复杂度**：$O(...)$
- **空间复杂度**：$O(...)$

>✨ tips

## 🔁 复盘与扩展
> 关键点：

> 易错点：

## 🔗 相关题目


> ⏱️ 本次耗时：____ 分钟
