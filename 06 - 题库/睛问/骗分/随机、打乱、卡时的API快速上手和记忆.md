---
created: 2026-03-20T14:19
updated: 2026-03-20T14:53
---
## 随机
```cpp
#include <iostream>
#include <cstdlib>
#include <ctime>

using namespace std;

int main()
{
	cout << "Rand_max:" << RAND_MAX << endl;	
	srand(time(0)); // 初始化随机种子
	
	int x = rand(); // 
	int l = 10, r = 20; 
	int y = rand() % (r - l + 1) + l; // 生成[l,r]之间的随机数
	cout << y << '\n';
	return 0;
}
```
生成 `l ~ r`：

```cpp
rand() % (r - l + 1) + l
```

这个式子非常常用，最好直接记住。  
比如生成 `10 ~ 20` 之间的随机数：

```cpp
rand() % (20 - 10 + 1) + 10
```

## 打乱

```cpp
#include <iostream>
#include <cstdlib>
#include <ctime>
//#include <algorithm>

using namespace std;

void shuffle_array(int a[], int n) {
	for (int i = n - 1; i > 0; i--) { // 注意 i > 0 不是 i >= 0
		int j = rand() % (i + 1);
		swap(a[i], a[j]);
	}
}

int main()
{
	srand(time(0)); // 生成随机数种子
	int a[] = {0, 1, 2, 4, 5, 6};
	int n = sizeof(a) / sizeof(a[0]);
	
	shuffle_array(a, n);
	
	for (int i = 0; i < n; i++) {
		cout << a[i] << ' ';
	}
	cout << '\n';
	
	return 0;
}
```
这段代码的核心就两句：

```cpp
int j = rand() % (i + 1);
swap(a[i], a[j]);
```

也就是说，当前枚举到 `i` 时，就从 `0 ~ i` 之间随机选一个位置 `j`，然后交换。  
这样一路往前处理，最后整个数组就被打乱了。

## 卡时间

这里说的“卡时间”，不是单纯为了看程序跑了多少秒，而是指：  
**在一些贪心 + 随机、随机化搜索、反复尝试的做法里，给程序设一个时间上限，时间快到了就立刻停，避免某个 case 上跑太久导致超时。**

这种写法通常出现在下面这些场景里：

- 不断随机交换、随机调整答案
- 不断生成方案，保留当前最优
- 贪心不太稳，于是套一层随机反复试
- 某些数据点特别难搞，不能无休止地跑下去

这类程序往往不是固定跑多少次，而是：  
**有时间就继续做，时间快到了就停。**

最常见的写法是用 `clock()`。

```cpp
#include <bits/stdc++.h> // 万能头

using namespace std;

void shuffle_array(int a[], int n) {
	for (int i = n - 1; i > 0; i--) { // 注意 i > 0 不是 i >= 0
		int j = rand() % (i + 1);
		swap(a[i], a[j]);
	}
}


int main()
{
	clock_t st = clock();
	srand(time(0)); // 生成随机数种子
	int a[] = {0, 1, 2, 4, 5, 6};
	int n = sizeof(a) / sizeof(a[0]);
	
	while (1.0 * (clock() - st) / CLOCKS_PER_SEC < 0.95) {
		// 不断随机尝试
		// 比如随机交换、随机打乱、随机贪心、更新答案等
		shuffle_array(a, n);
	}
	for (int i = 0; i < n; i++) {
		cout << a[i] << ' ';
	}
	cout << '\n';
	
	cout << "时间快到了，停止随机尝试" << '\n';
	
	return 0;
}
```

这里最关键的是这句：

```cpp
1.0 * (clock() - st) / CLOCKS_PER_SEC < 0.95
```

它表示：从开始到现在，经过的时间还不到 `0.95` 秒，就继续跑。  
一旦快到这个上限，就退出循环。

为什么经常写成 `0.95`、`1.8`、`1.9` 这种数？  
因为你不能真的把时间顶到时限边缘。程序除了随机部分，还要读入、输出、做别的处理，所以一般都会**预留一点余量**。  
否则卡得太死，就很容易直接 TLE。

如果你不想每次都写这么长，也可以封装一下：
```cpp
double get_time() {
    return 1.0 * clock() / CLOCKS_PER_SEC;
}
```

```cpp
#include <bits/stdc++.h> // 万能头

using namespace std;

void shuffle_array(int a[], int n) {
	for (int i = n - 1; i > 0; i--) { // 注意 i > 0 不是 i >= 0
		int j = rand() % (i + 1);
		swap(a[i], a[j]);
	}
}

double get_time()
{
	return 1.0 * clock() / CLOCKS_PER_SEC;
}


int main()
{
	double st = get_time();
	srand(time(0)); // 生成随机数种子
	int a[] = {0, 1, 2, 4, 5, 6};
	int n = sizeof(a) / sizeof(a[0]);
	
	while (get_time() - st < 0.95) {
		// 不断随机尝试
		// 比如随机交换、随机打乱、随机贪心、更新答案等
		shuffle_array(a, n);
	}
	for (int i = 0; i < n; i++) {
		cout << a[i] << ' ';
	}
	cout << '\n';
	
	cout << "时间快到了，停止随机尝试" << '\n';
	
	return 0;
}
```

## 综合

实际写题时，随机、打乱、卡时间往往是组合出现的。  
尤其是在一些“先随便构造一个解，然后不停随机调整，能变好就更新”的做法里，这三个东西经常一起出现。

下面给一个简单的综合例子：  
先随机生成一个排列，不断打乱，然后记录其中某个最优结果；时间快到了就退出。
```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    srand(time(0));
    clock_t st = clock();

    vector<int> best;
    int best_score = -1;

    while (1.0 * (clock() - st) / CLOCKS_PER_SEC < 0.95) {
        vector<int> v;
        for (int i = 1; i <= 10; i++) v.push_back(i);

        for (int i = (int)v.size() - 1; i > 0; i--) {
            int j = rand() % (i + 1);
            swap(v[i], v[j]);
        }

        int score = 0;
        for (int i = 0; i < 10; i++) {
            score += abs(v[i] - (i + 1));
        }

        if (score > best_score) {
            best_score = score;
            best = v;
        }
    }

    cout << "best score = " << best_score << '\n';
    for (int x : best) {
        cout << x << ' ';
    }
    cout << '\n';

    return 0;
}
```
这段代码是一个使用**随机化算法（蒙特卡洛方法）**来尝试寻找特定排列，使得某个“得分”最大化的程序。

具体来说，它的目标是在 1 到 10 的全排列中，找到一个排列 $v$，使得 $\sum_{i=0}^{9} |v[i] - (i+1)|$ 的值最大。

下面是详细的代码逻辑解释：

### 1. 头文件与命名空间
```cpp
#include <bits/stdc++.h>
using namespace std;
```
- 引入所有标准 C++ 库。
- 使用 `std` 命名空间，方便直接调用 `vector`, `cout`, `rand` 等。

### 2. 初始化随机数种子和计时器
```cpp
srand(time(0));
clock_t st = clock();
```
- `srand(time(0))`：使用当前时间作为随机数种子，确保每次运行程序产生的随机序列不同。
- `clock()`：记录程序开始运行的时间点，用于控制运行时长。

### 3. 变量定义
```cpp
vector<int> best;
int best_score = -1;
```
- `best`：用来存储目前为止找到的得分最高的那个排列。
- `best_score`：记录最高得分，初始化为 -1。

### 4. 主循环（时间限制）
```cpp
while (1.0 * (clock() - st) / CLOCKS_PER_SEC < 0.95) {
    // ...
}
```
- 这是一个**基于时间的循环**。
- 只要程序运行时间小于 **0.95 秒**，循环就会一直执行。
- `CLOCKS_PER_SEC` 是每秒的时钟滴答数。
- 这种写法常见于算法竞赛（如 Codeforces, AtCoder），因为题目通常限制运行时间为 1 秒或 2 秒，程序员会利用剩余时间尽可能多地尝试随机解，以期望找到最优解或近似最优解。

### 5. 生成随机排列 (Fisher-Yates 洗牌算法)
```cpp
vector<int> v;
for (int i = 1; i <= 10; i++) v.push_back(i);

for (int i = (int)v.size() - 1; i > 0; i--) {
    int j = rand() % (i + 1);
    swap(v[i], v[j]);
}
```
- 首先创建一个包含 `1` 到 `10` 的有序向量 `v`。
- 然后使用 **Fisher-Yates 洗牌算法** 将其打乱，生成一个随机的全排列。
  - 从后往前遍历，对于每个位置 `i`，随机选择一个 `0` 到 `i` 之间的索引 `j`，交换 `v[i]` 和 `v[j]`。
  - 这能保证生成的每个排列概率是相等的。

### 6. 计算得分
```cpp
int score = 0;
for (int i = 0; i < 10; i++) {
    score += abs(v[i] - (i + 1));
}
```
- 计算当前排列 `v` 的得分。
- 得分公式：$\sum |v[i] - \text{原始位置值}|$。
  - `v[i]` 是当前位置的数字。
  - `i + 1` 是该位置原本应该有的数字（因为初始是 1, 2, ..., 10）。
  - `abs` 取绝对值。
- **数学含义**：这个分数衡量的是排列中的每个数字偏离其原始位置的距离总和。距离越远，分数越高。

### 7. 更新最优解
```cpp
if (score > best_score) {
    best_score = score;
    best = v;
}
```
- 如果当前随机生成的排列得分比之前记录的最高分还高，就更新 `best_score` 和 `best` 向量。

### 8. 输出结果
```cpp
cout << "best score = " << best_score << '\n';
for (int x : best) {
    cout << x << ' ';
}
cout << '\n';
```
- 程序运行约 0.95 秒后停止循环。
- 输出找到的最大得分以及对应的排列。

---

### 总结与数学背景

**这段代码在做什么？**
它在 0.95 秒内，通过不断随机生成 1~10 的排列，试图找到一个让**“所有数字偏离原位置距离之和”最大**的排列。

**理论上的最优解是什么？**
对于序列 $1, 2, \dots, n$，要使 $\sum |p_i - i|$ 最大，策略通常是**完全反转**或者**前后对调**。
对于 $n=10$：
- 原序列：`1 2 3 4 5 6 7 8 9 10`
- 反转序列：`10 9 8 7 6 5 4 3 2 1`
- 计算得分：
  - $|10-1| + |9-2| + \dots + |1-10|$
  - $= 9 + 7 + 5 + 3 + 1 + 1 + 3 + 5 + 7 + 9 = 50$

**为什么用随机法而不是直接构造？**
- 如果 $n$ 很小（如本题 $n=10$），直接构造反转序列即可得到答案 50，不需要随机。
- 这段代码更像是一个**模板**或**示例**，用于演示如何在时间限制内使用**随机化贪心/模拟退火**的思想来解决那些**难以直接构造最优解**或**解空间巨大**的问题。
- 在 $n=10$ 的情况下，随机法很容易在 0.95 秒内撞出最优解 50（因为 $10! = 3,628,800$，而 0.95 秒大概能跑几百万次循环，覆盖率很高）。

**潜在问题：**
- `rand()` 的质量一般，但在小规模数据下足够使用。
- 如果 $n$ 变大（例如 $n=1000$），纯随机很难找到全局最优解，通常需要结合**模拟退火**（允许一定概率接受更差的解以跳出局部最优）或**遗传算法**。

----
所以这一部分真正需要掌握的，其实就是下面这几类核心写法：

```cpp
srand(time(0));
rand() % (r - l + 1) + l;
```

```cpp
vector<int> v;
for (int i = 1; i <= 10; i++) v.push_back(i);

for (int i = (int)v.size() - 1; i > 0; i--) {
    int j = rand() % (i + 1);
    swap(v[i], v[j]);
}
```

```cpp
clock_t st = clock();
while (1.0 * (clock() - st) / CLOCKS_PER_SEC < limit) {
    // 不断随机尝试
}
```

把这些内容串起来以后，你就能写出很多典型的随机化代码：

- 随机生成数据
- 随机打乱顺序
- 随机反复尝试
- 时间快到时及时停下，避免某些 case 跑超时

这才是“卡时间”在这类题里的真正作用。  
不是为了看程序多优雅，而是为了在评测机动手之前，先自己收手。

