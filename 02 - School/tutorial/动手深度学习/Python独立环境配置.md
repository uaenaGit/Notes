---
title: 动手学深度学习：Python 独立环境配置
created: 2026-10-26
tags:
  - 动手学深度学习
  - Python
  - PyTorch
  - 环境配置
status: 待操作
updated: 2026-10-26T18:50
---

# 动手学深度学习：Python 独立环境配置

> [!abstract] 配置方案
> 保留电脑已有的 **Python 3.12.8**，使用 Python 自带的 `venv` 创建独立环境，暂不安装 Conda。先安装 CPU 版 PyTorch、JupyterLab 和基础科学计算工具，学习数据操作、自动求导与小模型训练。
>
> 本笔记是操作指南，不代表已完成环境创建或依赖安装。下面的命令由自己在 **PowerShell** 中执行。

## 1. 目录与环境如何组织

代码和 Notebook 放在：

```text
D:\Tutorials\D2l-ai
```

Obsidian 用来记录理解、实验结论与疑问；完整代码、数据和 Notebook 放在学习目录。虚拟环境也放在学习目录，不放进 Obsidian 仓库。

```text
D:\Tutorials\D2l-ai\
├── .venv\             # 独立 Python 环境，不放入 Git
├── notebooks\         # 后续按需建立：学习 Notebook
└── scripts\           # 后续按需建立：完整实验脚本
```

上面的 `notebooks` 和 `scripts` 只是组织建议，第一步无需全部创建。

## 2. 创建目录与虚拟环境

打开 PowerShell，依次运行：

```powershell
New-Item -ItemType Directory -Force 'D:\Tutorials\D2l-ai'
Set-Location 'D:\Tutorials\D2l-ai'

python --version
python -m venv .venv
```

运行成功后会出现 `.venv` 文件夹。它保存课程环境的 Python 入口和依赖包，与系统环境隔离。

> [!note] 如果已有同名环境
> 如果目录中已经存在 `.venv`，先确认它是否就是要使用的学习环境，不要为了重试而直接删除。若 `python` 命令不可用，先检查 Python 安装与终端的 PATH 配置。

## 3. 激活并确认环境

```powershell
.\.venv\Scripts\Activate.ps1
```

激活成功后，命令行前面通常会出现 `(.venv)`。用下面的命令确认实际解释器：

```powershell
python -c "import sys; print(sys.executable)"
```

预期路径：

```text
D:\Tutorials\D2l-ai\.venv\Scripts\python.exe
```

### 激活时提示禁止运行脚本

可以只对当前 PowerShell 进程临时调整执行策略，再激活：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

关闭当前 PowerShell 窗口后，这个临时设置失效。若电脑受组织策略管理，以实际策略为准。

也可以不激活，直接使用环境中的 Python，例如：

```powershell
.\.venv\Scripts\python.exe -m pip --version
```

后续凡是 `python ...` 命令，都可以使用这个明确的解释器路径替代。

## 4. 安装基础依赖

以下命令在环境已激活的 PowerShell 中运行。

### 更新 pip

```powershell
python -m pip install --upgrade pip
```

### 安装 CPU 版 PyTorch

```powershell
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

CPU 版足够开始张量、自动求导、线性回归和小型分类实验。前期无需安装 CUDA Toolkit。以后需要 GPU 时，再根据显卡、驱动和 PyTorch 官方要求配置。

安装入口：[PyTorch 官方安装说明](https://pytorch.org/get-started/locally/)。若安装命令或支持版本随时间变化，以官方选择器为准。

### 安装 JupyterLab 与科学计算工具

```powershell
python -m pip install jupyterlab ipykernel numpy pandas matplotlib
```

| 包 | 用途 |
| --- | --- |
| `torch` | 张量、自动求导、神经网络与训练 |
| `torchvision` | 图像数据集、预处理等，后续分类实验使用 |
| `jupyterlab` | 在浏览器中编写和运行 Notebook |
| `ipykernel` | 让 Jupyter 使用当前虚拟环境作为内核 |
| `numpy` | 数组与数值计算 |
| `pandas` | 表格数据读取与处理 |
| `matplotlib` | 绘制曲线和实验结果 |

> [!important] 暂时不要安装 `d2l` 辅助包
> 教材配套的 `d2l` 包可能固定较旧的依赖，与 Python 3.12 产生兼容问题。当前方案适合开始基础学习，并不保证所有教材原始 Notebook 都能直接运行。
>
> 前期先直接使用 PyTorch。遇到 `from d2l import torch as d2l` 时，确认该章节使用了哪些辅助函数，再决定自行实现、替换，或另建兼容教材的环境。不要为解决一个依赖冲突反复降级当前环境。

## 5. 注册内核并启动 JupyterLab

```powershell
python -m ipykernel install --user --name d2l-study --display-name "Python (d2l-study)"
```

这会为当前用户注册一个名为 `Python (d2l-study)` 的 Jupyter 内核入口，指向当前环境；依赖仍安装在 `.venv` 中。

启动：

```powershell
python -m jupyterlab
```

浏览器一般会自动打开。如果没有自动打开，复制终端显示的本机地址到浏览器。

新建 Notebook 时选择 **Python (d2l-study)** 内核。已有 Notebook 也要确认其内核正确。

> [!note] 环境位置改变后
> 如果以后移动学习目录或重建 `.venv`，旧内核入口可能仍指向原路径。应在新环境中重新运行内核注册命令。

## 6. 第一个验证实验

新建 Notebook，把下面代码放进代码单元，按 `Shift + Enter`：

```python
import sys
import torch
import matplotlib.pyplot as plt

print("Python 路径：", sys.executable)
print("PyTorch 版本：", torch.__version__)

# 张量与形状
x = torch.arange(6, dtype=torch.float32).reshape(2, 3)
print("张量：\n", x)
print("形状：", x.shape)

# 自动求导
a = torch.tensor(2.0, requires_grad=True)
y = a ** 2
y.backward()

print("a² 在 a=2 时的梯度：", a.grad.item())
assert a.grad.item() == 4.0

# 绘图
plt.plot([1, 2, 3], [1, 4, 9])
plt.xlabel("x")
plt.ylabel("x squared")
plt.show()
```

### 验收清单

- [ ] `sys.executable` 指向学习目录中的 `.venv`。
- [ ] PyTorch 能正常导入并打印版本。
- [ ] 张量内容为两行三列，形状为 `torch.Size([2, 3])`。
- [ ] 自动求导结果为 `4.0`。
- [ ] 能显示折线图。

CPU 版中 `torch.cuda.is_available()` 返回 `False` 是正常的，不表示环境失败。

## 7. 以后每次开始与结束学习

### 开始学习

每次打开新的 PowerShell 窗口后运行：

```powershell
Set-Location 'D:\Tutorials\D2l-ai'
.\.venv\Scripts\Activate.ps1
python -m jupyterlab
```

若再次遇到脚本策略限制，使用第 3 节的方法，或直接启动：

```powershell
Set-Location 'D:\Tutorials\D2l-ai'
.\.venv\Scripts\python.exe -m jupyterlab
```

不需要每次重新创建环境、安装依赖或注册内核。

### 结束学习

1. 保存 Notebook。
2. 回到运行 Jupyter 的 PowerShell 窗口，按 `Ctrl + C`，按提示关闭服务。
3. 如果需要退出已激活的虚拟环境，运行：

```powershell
deactivate
```

仅关闭浏览器标签不一定会停止 Jupyter 服务。

## 8. 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 提示 `No module named torch` | 在出错的 Notebook 中打印 `sys.executable`，检查是否选错内核；在同一环境安装包 |
| 包装好了，Notebook 仍无法导入 | 确认内核后重启内核；确认安装包时使用的是 `.venv` 的 Python |
| 下载很慢或失败 | 保留完整报错，检查网络与官方安装源；网络超时不一定是 Python 版本问题 |
| 出现 `No matching distribution found` | 检查包名、Python 版本、系统架构与安装源是否支持，不先盲目降级 |
| 教材 `d2l` 包安装冲突 | 暂停安装，保留报错与当前依赖，按第 4 节处理 |
| 激活成功但路径不对 | 以 `sys.executable` 为准，使用明确的 `.venv\Scripts\python.exe` 路径 |

始终优先使用 `python -m pip ...`，让 pip 与当前 Python 对应。

环境跑通后，可保存当前依赖列表以便回顾：

```powershell
python -m pip freeze > requirements.txt
```

这是当前环境的版本记录。CPU 版 PyTorch 的安装源也应一并记录在项目说明中，单独的 `requirements.txt` 不一定完整表达安装来源。

## 9. 我的操作记录

- [ ] 创建学习目录与 `.venv`。
- [ ] 确认解释器路径。
- [ ] 安装 CPU 版 PyTorch。
- [ ] 安装 JupyterLab 与基础工具。
- [ ] 注册并选择内核。
- [ ] 跑通验证实验。

实际操作日期：

实际学习目录：

Python 版本：

PyTorch 版本：

遇到的问题与处理：

## 10. 下一步学习与笔记

环境验收通过后，从《动手学深度学习》PyTorch 版的数据操作与自动求导部分开始。

- [教材入口](https://zh.d2l.ai/)
- [[Python 与张量]]：记录 shape、dtype、device、索引、广播与小实验。
- [[大模型学习路线-跨专业研一到就业]]：查看阶段目标。
- [[知识地图自动同步使用说明]]：查看如何把个人笔记同步到看板与网页。

完整代码放学习目录；概念解释、实验结论、错误原因和代码位置写进 Obsidian，不必把所有代码重复复制一遍。
