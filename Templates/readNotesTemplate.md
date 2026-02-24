<%*
// ====== 基础信息 ======
const today = tp.date.now("YYYY-MM-DD");
const now = tp.date.now("YYYY-MM-DD HH:mm");

// ====== 用户交互输入 ======
const bookTitle = await tp.system.prompt("📖 书名");
const bookAuthor = await tp.system.prompt("✍️ 作者");
const bookPublisher = await tp.system.prompt("🏢 出版社", "");

// 分类
const categories = ["文学", "历史", "哲学", "商业", "科技", "心理", "教育", "艺术", "科学", "其他"];
const bookCategory = await tp.system.suggester(categories, categories);
const finalCategory = bookCategory || "其他";

// 评分 (1-5)
const rating = await tp.system.suggester(
    ["⭐⭐⭐⭐⭐ (5)", "⭐⭐⭐⭐ (4)", "⭐⭐⭐ (3)", "⭐⭐ (2)", "⭐ (1)", "暂不评分"],
    [5, 4, 3, 2, 1, 0]
);
const finalRating = rating || 0;

// 阅读状态
const status = await tp.system.suggester(
    ["🔴 想读", "🟡 在读", "🟢 读完", "⚫ 弃读"],
    ["want-to-read", "reading", "completed", "abandoned"]
);
const finalStatus = status || "want-to-read";

// 日期信息
let startDate = "";
let endDate = "";
if (finalStatus === "reading" || finalStatus === "completed") {
    startDate = await tp.system.prompt("📅 开始阅读日期", today);
}
if (finalStatus === "completed") {
    endDate = await tp.system.prompt("📅 完成阅读日期", today);
}

// 标签
const tags = ["读书笔记", "待整理", "已复盘", "推荐"];
const selectedTags = await tp.system.multi_suggester(tags, tags);
const finalTags = (selectedTags && Array.isArray(selectedTags) && selectedTags.length > 0) ? selectedTags : ["读书笔记"];

// ====== 格式化数据 ======
// 标签：必须是标准数组格式 ["A", "B"] 才能显示为胶囊
const tagsArrayFormat = finalTags.map(t => `"${t}"`).join(", ");

// ====== 生成 YAML Frontmatter ======
tR = `---
created: ${today}
modified: ${now}
书名: ${bookTitle}
作者: ${bookAuthor}
出版社: ${bookPublisher}
分类: ${finalCategory}
评分: ${finalRating}
状态: ${finalStatus}
开始日期: ${startDate}
完成日期: ${endDate}
tags: [${tagsArrayFormat}]
aliases: ["${bookTitle}", "${bookTitle} (${bookAuthor})"]
---

# 📖 ${bookTitle}

> **作者**: ${bookAuthor}  
> **出版社**: ${bookPublisher}  
> **评分**: ${finalRating > 0 ? "⭐".repeat(finalRating) : "暂未评分"}  
> **状态**: ${finalStatus === "completed" ? "🟢 读完" : finalStatus === "reading" ? "🟡 在读" : finalStatus === "want-to-read" ? "🔴 想读" : "⚫ 弃读"}  
> **阅读时间**: ${startDate} ${endDate ? \`→ \${endDate}\` : ""}

---

## 🎯 一句话总结
<!-- 用一句话概括这本书的核心内容 -->


---

## 📋 核心内容

### 主要观点
1. 
2. 
3. 

### 关键概念
| 概念 | 解释 |
|------|------|
| | |
| | |

### 知识框架
\`\`\`
<!-- 用文字或 ASCII 图描述书中的知识框架 -->

\`\`\`

---

## 💡 精彩摘录

> 
> — 第 X 页

> 
> — 第 X 页

> 
> — 第 X 页

---

## 🧠 个人思考

### 启发与收获
- 
- 
- 

### 质疑与反思
- 
- 

### 与其他知识的联系
- 关联笔记：[[ ]]
- 关联笔记：[[ ]]

---

## 📝 实践应用

### 行动清单
- [ ] 
- [ ] 
- [ ] 

### 应用场景
| 场景 | 如何应用 |
|------|---------|
| 工作 | |
| 生活 | |
| 学习 | |

---

## 🔗 相关资源

### 内部链接
- [[ ]]

### 外部链接
- []()
- []()

### 类似书籍
- [[ ]]
- [[ ]]

---

## 📊 阅读记录

| 日期 | 进度 | 备注 |
|------|------|------|
| ${today} | 0% | 开始阅读 |
| | | |

---

*最后更新: ${now}*
\`;
_%>