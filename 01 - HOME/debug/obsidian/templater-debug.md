---
created: 2026-02-22 12:18
tags:
  - debug
  - issue
  - troubleshooting
status: 🔴 进行中
priority: ⭐⭐⭐
---

# 🐛 问题调试记录

## 📋 问题概述
**标题**: obsidian中templater的`tp.system.multi_suggester` 返回对象与属性(Properties)面板不匹配。
**发现时间**: 2026-02-22
**影响范围**: 使用该模版生成的笔记

## 🔍 问题描述
<!-- 详细描述遇到的问题，包括预期行为和实际行为 -->
**`tp.system.multi_suggester` 返回的是一个对象数组（包含 `item` 和 `value` 等属性），而不是你期望的纯字符串数组。**
当 Templater 试图将这些**对象**直接拼接到字符串 `tR` 中时，Obsidian 的属性面板（Properties）检测到数据类型不匹配（它期望的是字符串列表，却收到了对象列表），从而触发了“multitext 数据不兼容”的警告。

## 🖥️ 环境信息
| 项目   | 信息             |
| ---- | -------------- |
| 操作系统 | windows11      |
| 软件版本 | Version 1.11.7 |
| 相关依赖 | templater插件    |
| 硬件配置 | 无              |
|      |                |

## 📝 错误日志
![[Pasted image 20260222122540.png]]

## ✅ 已尝试的解决方案
| 序号 | 方案 | 结果 | 时间 |
|------|------|------|------|
| 1 | | ❌ 失败 | |
| 2 | | ❌ 失败 | |
| 3 | | ✅ 成功 | |

## 🔬 分析过程
### 假设1
- 推测原因:`tp.system.multi_suggester` 返回的是一个对象数组（包含 `item` 和 `value` 等属性），而不是你期望的纯字符串数组。当 Templater 试图将这些**对象**直接拼接到字符串 `tR` 中时，Obsidian 的属性面板（Properties）检测到数据类型不匹配（它期望的是字符串列表，却收到了对象列表），从而触发了“multitext 数据不兼容”的警告。
- 验证方法:
- 验证结果:

### 假设2
- 推测原因:
- 验证方法:
- 验证结果:

## 💡 最终解决方案
<!-- 记录最终解决问题的方法 -->
<!-- 修改前代码 -->
```
// 分类
const categories = [ 
  "数组", "字符串", "模拟", "枚举", "双指针", "滑动窗口", "栈", "数学",
  "位运算", "矩阵", "堆", "二分", "链表", "树", "图", "动态规划" 
];

const selectedCategories = await tp.system.multi_suggester(categories, categories);
if (!Array.isArray(selectedCategories)) selectedCategories = [];

// 如果用户没选任何项，设默认值 
const finalCategories = selectedCategories.length > 0 ? selectedCategories : ["待补充"];

tR += "分类: \n";
finalCategories.forEach(cat => {
  tR += `  - ${cat}\n`;
});
```

<!-- 修改后代码 -->
```
// 分类
const categories = [ 
  "数组", "字符串", "模拟", "枚举", "双指针", "滑动窗口", "栈", "数学",
  "位运算", "矩阵", "堆", "二分", "链表", "树", "图", "动态规划" 
];

// 获取用户选择 (返回的是对象数组 [{item: "数组", value: "数组"}, ...])
const selectedObjects = await tp.system.multi_suggester(categories, categories);

// 提取纯字符串数组
let finalCategories = [];
if (Array.isArray(selectedObjects)) {
    // 关键修改：映射提取 .item 属性
    finalCategories = selectedObjects.map(obj => obj.item);
}

// 如果用户没选任何项，设默认值 
if (finalCategories.length === 0) {
    finalCategories = ["待补充"];
}

// 生成 YAML 格式输出
tR += "分类:\n";
finalCategories.forEach(cat => {
    tR += `  - ${cat}\n`;
});
```
## 📚 参考资料
- [链接1]()
- [链接2]()

## 🎯 经验总结
<!-- 记录本次调试的收获和避免复现的方法 -->
- 多使用ai
- 
- 

## 📎 附件
- [x] 相关截图 ✅ 2026-02-22
- [ ] 日志文件
- [x] 代码片段 ✅ 2026-02-22

---
**最后更新**: 2026-02-22 12:18
## 解决状态
- [ ] ⬜ 未解决
- [ ] 🟠 进行中
- [ ] 🟡 部分解决
- [x] 🟢 已解决 ✅ 2026-02-22