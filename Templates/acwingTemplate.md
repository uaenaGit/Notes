---
created: 2026-03-06T13:17
updated: 2026-03-19T09:42
---
<%*
// ====== 基础信息 ======
const today = tp.date.now("YYYY-MM-DD HH:mm");

// ====== 用户交互输入 ======
const title = await tp.system.prompt("题目名称（如：两数之和）");
const id = await tp.system.prompt("题号（如：1）", "");

// 难度选择
const difficulty = await tp.system.suggester(
    ["简单", "中等", "困难"], 
    ["简单", "中等", "困难"]
);

// 状态选择
const status = await tp.system.suggester(
    ["Y(通过)", "N(不会)", "?(有疑问)"], 
    ["Y(通过)", "N(不会)", "?(有疑问)"]
);

// 分类选择
const categories = [
  "暴力", "数组", "字符串", "模拟", "枚举", "回溯", "双指针", "哈希", 
  "滑动窗口", "栈", "数学", "递归", "位运算", "搜索", "矩阵", "堆", 
  "并查集", "二分", "链表", "树", "图", "贪心", "动态规划"
];
const selectedCategories = await tp.system.multi_suggester(categories, categories);
const finalCategories = (selectedCategories && Array.isArray(selectedCategories) && selectedCategories.length > 0) ? selectedCategories : ["待补充"];

// 标签：写死为 "acwing"
const finalTags = ["acwing"]; 
const tagsArrayFormat = finalTags.map(t => `"${t}"`).join(", ");

// 备注和链接
const notes = await tp.system.prompt("备注（可留空）", "");
const link = await tp.system.prompt("输入题目链接", "");

// ====== 格式化数据 ======
const categoriesText = finalCategories.join(", "); 

// ====== 生成内容字符串 ======
// 【关键修改】直接使用 tR = ，不要加 let 或 const，因为 tR 是 Templater 内置变量
tR = `---
难度: ${difficulty}
情况: ${status}
日期: ${today}
分类: ${categoriesText}
tags: [${tagsArrayFormat}]
备注: ${notes}
---

> 🔗[${id} - ${title}](${link})

## 📌 题目描述
> （请在此处粘贴题目描述）

${tp.file.cursor(1)}

## 💡 解题思路 

## 💻 代码实现
> my answer

- **时间复杂度**：\$O(...)\$
- **空间复杂度**：\$O(...)\$

> to optimize

- **时间复杂度**：\$O(...)\$
- **空间复杂度**：\$O(...)\$

>✨ tips

> others' answer

- **时间复杂度**：\$O(...)\$
- **空间复杂度**：\$O(...)\$

>✨ tips

## 🔁 复盘与扩展
> 关键点：

> 易错点：

## 🔗 相关题目


> ⏱️ 本次耗时：____ 分钟
`;
_%>