<%*
// ====== 基础信息 ======
const today = tp.date.now("YYYY-MM-DD HH:mm");

// ====== 用户交互输入 ======
const title = await tp.system.prompt("题目名称（如：两数之和）");
const id = await tp.system.prompt("题号（如：1）", "");
const difficulty = await tp.system.suggester(["easy", "medium", "hard"], ["easy", "medium", "hard"]);
const status = await tp.system.suggester(["Y(通过)", "N(不会)", "?(有疑问)"], ["Y(通过)", "N(不会)", "?(有疑问)"]);

// 分类
const categories = ["数组", "字符串", "模拟", "枚举", "双指针", "滑动窗口", "栈", "数学", "位运算", "矩阵", "堆", "二分", "链表", "树", "图", "动态规划"];
const selectedCategories = await tp.system.multi_suggester(categories, categories);
const finalCategories = (selectedCategories && Array.isArray(selectedCategories) && selectedCategories.length > 0) ? selectedCategories : ["待补充"];

// 标签
const tags = ["每日一题", "面试经典150 题", "hot100", "leetcode", "acwing"];
const selectedTags = await tp.system.multi_suggester(tags, tags);
const finalTags = (selectedTags && Array.isArray(selectedTags) && selectedTags.length > 0) ? selectedTags : [];

// 备注和链接
const notes = await tp.system.prompt("备注（可留空）", "");
const link = await tp.system.prompt("输入题目链接", "");

// ====== 格式化数据 ======
// 1. 分类：为了匹配截图的"字符串，模拟"样式，我们生成一个逗号分隔的字符串
//    如果你希望分类也能像标签一样有胶囊按钮，请改用下面的 categoriesArray 格式
const categoriesText = finalCategories.join(", "); 

// 2. 标签：必须是标准数组格式 ["A", "B"] 才能显示为胶囊
const tagsArrayFormat = finalTags.map(t => `"${t}"`).join(", ");

// ====== 生成 YAML Frontmatter ======
// 关键点：
// - 使用 'tags' 键名：Obsidian 原生支持，自动渲染为胶囊，无警告
// - 使用 'categories' 键名：Obsidian 将其视为列表，界面显示为逗号分隔，无警告
// - 其他字段使用英文键名以保证最大兼容性，你可以在 Obsidian 属性面板中手动修改它们的显示名称（别名）

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

- **时间复杂度**：\`O(...)\`
- **空间复杂度**：\`O(...)\`

> to optimize

- **时间复杂度**：\`O(...)\`
- **空间复杂度**：\`O(...)\`

> tips

> others' answer

- **时间复杂度**：\`O(...)\`
- **空间复杂度**：\`O(...)\`

> tips

## 🔁 复盘与扩展
> 关键点：

> 易错点：

## 🔗 相关题目

> ⏱️ 本次耗时：______ 分钟
`;
_%>