<%*
// 1. 获取日期
const today = tp.date.now("YYYY-MM-DD");
const now = tp.date.now("YYYY-MM-DD HH:mm");

// 2. 交互式输入
const bookTitle = await tp.system.prompt("📖 书名");
const bookAuthor = await tp.system.prompt("✍️ 作者");
const bookPublisher = await tp.system.prompt("🏢 出版社", "");

const bookCategory = await tp.system.suggester(
    ["文学", "历史", "哲学", "商业", "科技", "心理", "其他"],
    ["文学", "历史", "哲学", "商业", "科技", "心理", "其他"]
);

const rating = await tp.system.suggester(
    ["⭐⭐⭐⭐⭐ (5)", "⭐⭐⭐⭐ (4)", "⭐⭐⭐ (3)", "⭐⭐ (2)", "⭐ (1)", "暂不评分"],
    [5, 4, 3, 2, 1, 0]
);

const status = await tp.system.suggester(
    ["🔴 想读", "🟡 在读", "🟢 读完", "⚫ 弃读"],
    ["want-to-read", "reading", "completed", "abandoned"]
);

// 3. 处理日期逻辑
let startDate = "";
let endDate = "";
if (status === "reading" || status === "completed") {
    startDate = await tp.system.prompt("📅 开始阅读日期", today);
}
if (status === "completed") {
    endDate = await tp.system.prompt("📅 完成阅读日期", today);
}
_%>
---
created: <% today %>
modified: <% now %>
tags:
  - 读书笔记
  - 书籍/<% bookCategory %>
  - 状态/<% status %>
book:
  title: "<% bookTitle %>"
  author: "<% bookAuthor %>"
  publisher: "<% bookPublisher %>"
  category: "<% bookCategory %>"
  rating: <% rating %>
  status: "<% status %>"
  start-date: "<% startDate %>"
  end-date: "<% endDate %>"
aliases: ["<% bookTitle %>", "<% bookTitle %> (<% bookAuthor %>)"]
---

# 📖 <% bookTitle %>

> **作者**: <% bookAuthor %>  
> **出版社**: <% bookPublisher %>  
> **评分**: <% rating > 0 ? "⭐".repeat(rating) : "暂未评分" %>  
> **状态**: <% status === "completed" ? "🟢 读完" : status === "reading" ? "🟡 在读" : "🔴 想读" %>  
> **阅读时间**: <% startDate %> <% endDate ? `→ ${endDate}` : "" %>

---

## 🎯 一句话总结


## 📋 核心观点
1. 
2. 
3. 

## 💡 精彩摘录
> 

## 🧠 个人思考
- 

## 📝 行动清单
- [ ] *