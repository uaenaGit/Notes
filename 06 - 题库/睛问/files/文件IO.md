---
created: 2026-03-07T16:23
updated: 2026-03-07T16:28
---
一些学校可能会要求考生直接从文件进行输入，或者输出结果到文件，这时候我们需要在正式输入输出前（例如可以在 `main` 函数开头）多加两行：
```cpp
freopen("input.txt", "r", stdin);
freopen("output.txt", "w", stdout);
```
`freopen` 是 `cstdio`（或 `stdio.h`） 头文件下的函数，可以用来文件输入输出。它有三个参数，分别表示：

- 文件路径：需要读取或者写入的文件路径
- 模式：对文件进行输入（`r`）还是输出（`w`）
- 文件流：不需要知道概念，只需要知道输入用 `stdin`（标准输入流），输出用 `stdout`（标准输出流）

所以上面的示例代码的第一行就表示了从 `input.txt` 这个文件中进行输入（使用了 `r` 和 `stdin`），而第二行则表示了将输出写入到 `output.txt` 这个文件中（使用了 `w` 和 `stdout`）。

举例来说，假设我们有一个解决 `A + B` 问题的代码：
```cpp
#include <cstdio>
int main() {
    int a, b;
    scanf("%d%d", &a, &b);
    printf("%d", a + b);
    return 0;
}
```
那么我们只需要在 `main` 函数开头加上两行，就可以改造为文件输入输出的版本：
```cpp
#include <cstdio>
int main() {
    freopen("input.txt", "r", stdin);    // 从input.txt中读取数据
    freopen("output.txt", "w", stdout);  // 写入数据到output.txt中
    int a, b;
    scanf("%d%d", &a, &b);
    printf("%d", a + b);
    return 0;
}
```
测试：
1. 将上面的 `C/C++` 代码保存在电脑上
2. 在和 `C/C++` 代码文件的相同路径下新建名字为 `input.txt` 的文件（或者你喜欢的其他名字和后缀）作为输入文件
3. 打开 input.txt 文件，填进去 `1 2`，保存
4. 运行该 `C/C++` 代码，查看是否在相同路径下生成了名为 `output.txt` 文件（可能有的系统会要求权限，这时候需要同意一下权限）
5. 打开 `output.txt` 文件，查看结果是否为 `3`
以下是可以进一步操作的步骤：
6. 删除 `output.txt` 文件，然后将输出的这行 `freopen` 注释掉，再运行代码，这时候输出会打印在黑框框命令行里，而不是文件中
7. 将 `input.txt` 文件移动到其他路径下，例如放在 D 盘的名字叫 `测试路径` 的文件夹下，然后将输入这行 `freopen` 的第一个参数改为这个文件的绝对路径（例如 `freopen("D:\\测试路径\\input.txt", "r", stdin)`），然后运行代码，这时候应该仍然能正常运行
8. 将输入这行 `freopen` 注释掉，再运行代码，这时候输入不再从文件中读取，我们需要手动在黑框框命令行里输入数据，然后回车后得到正确结果。如果输出这行的 `freopen` 已经被注释，得到的结果会在黑框框命令行内；如果没有被注释，那么结果会写入到 `output.txt` 文件中
9. 将 `scanf/printf` 改成其他输入输出函数，例如 `getchar`、`getline`、`cin`、`cout` 等等，都应该能达到预期结果
