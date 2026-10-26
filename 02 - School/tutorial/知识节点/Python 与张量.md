---
title: "Python 与张量"
kind: "概念"
status: "未开始"
atlas_id: "py"
tags: ["大模型学习", "知识节点"]
---
# Python 与张量

## 学习范围

形状、广播、索引、设备与 dtype。已有 Python 基础，可边写边查。

## 验收标准

能预测矩阵运算的输出形状，并定位维度错误。

## 资料

[资料入口](https://numpy.org/doc/stable/user/absolute_beginners.html)

## 我的理解

先回答：张量的 shape、dtype、device 分别描述什么？

- shape：待自己解释并举例。
- dtype：待自己解释并举例。
- device：待自己解释并举例。

不要一次填满所有内容，学到哪里写到哪里。

## 代码与实验

先预测，再运行以下代码，把实际输出和原因补在后面：

```python
import torch

x = torch.arange(6, dtype=torch.float32).reshape(2, 3)
bias = torch.tensor([10.0, 20.0, 30.0])
print(x.shape, x.dtype, x.device)
print(x + bias)
print(x @ torch.ones(3, 2))
```

我的预测：

实际输出：

广播为什么成立：

矩阵乘法为什么得到这个形状：

## 问题与排错

记录现象 → 原因 → 定位过程 → 解决方式。

## 关联笔记

- [[按需补数学]]
- [[PyTorch 训练闭环]]
- [[NumPy 线性回归]]

## 学习记录

- 日期：
- 本次完成：
- 下次行动：

## 迁移前卡片原文

## Python 与张量
**概念** · 现在开始

形状、广播、索引、设备与 dtype。已有 Python 基础，可边写边查。

**验收：** 能预测矩阵运算的输出形状，并定位维度错误。

[资料入口](https://numpy.org/doc/stable/user/absolute_beginners.html)
