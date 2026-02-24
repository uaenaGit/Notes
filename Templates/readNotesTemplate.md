<%*
// 获取当前日期
const today = tp.date.now("YYYY-MM-DD");
const now = tp.date.now("YYYY-MM-DD HH:mm");

// 书籍信息输入
const bookTitle = await tp.system.prompt("书名");
const bookAuthor = await tp.system.prompt("作者");
const bookCategory = await tp.system.suggester(
    ["文学", "历史", "哲学", "心理学", "商业", "科技", "传记", "小说", "其他"],
    ["文学", "历史", "哲学", "心理学", "商业", "科技", "传记", "小说", "其他"]
);

// 评分系统 (1-5 星)
const ratingOptions = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"];
const ratingValues = [1, 2, 3, 4, 5];
const selectedRating = await tp.system.suggester(ratingOptions, ratingValues);
const finalRating = selectedRating || 0;

// 阅读状态
const statusOptions = ["🔴 未开始", "🟡 进行中", "🟢 已完成", "⚫ 已暂停"];
const statusValues = ["unread", "reading", "completed", "paused"];
const selectedStatus = await tp.system.suggester(statusOptions, statusValues);
const finalStatus = selectedStatus || "unread";

// 开始阅读日期
const startDate = finalStatus === "completed" || finalStatus === "reading" 
    ? await tp.system.prompt("开始阅读日期 (YYYY-MM-DD)", today) 
    : "";

// 完成阅读日期
let endDate = "";
if (finalStatus === "completed") {
    endDate = await tp.system.prompt("完成阅读日期 (YYYY-MM-DD)", today);
}
_%>
---
created: <% today %>
modified: <% now %>
tags:
  - reading-notes
  - book/<% bookCategory %>
book-title: "<% bookTitle %>"
book-author: "<% bookAuthor %>"
book-category: <% bookCategory %>
book-rating: <% finalRating %>
reading-status: <% finalStatus %>
<% if (startDate) { -%>
start-date: <% startDate %>
<% } -%>
<% if (endDate) { -%>
end-date: <% endDate %>
<% } -%>
aliases: [<% bookTitle %>]
---

# 📖 <% bookTitle %>

## 📋 书籍信息
| 项目 | 信息 |
|------|------|
| **作者** | <% bookAuthor %> |
| **分类** | <% bookCategory %> |
| **评分** | <% ratingOptions[finalRating - 1] || "暂未评分" %> (<% finalRating %>/5) |
| **状态** | <% statusOptions[statusValues.indexOf(finalStatus)] %> |
| **开始阅读** | <% startDate || "未开始" %> |
| **完成阅读** | <% endDate || "未完成" %> |

## 🎯 核心观点
### 主要论点
- 

### 关键概念
- 

### 重要框架/模型
- 

## 💡 精彩摘录
> 引用内容
> 
> —— 第 X 页

> 引用内容
> 
> —— 第 X 页

## 🧠 个人思考
### 启发与收获
- 

### 质疑与反思
- 

### 与其他知识的联系
- 

## 📝 实践应用
### 可执行的行动项
- [ ] 
- [ ] 

### 生活/工作中的应用场景
- 

## 🔗 相关链接
- [[相关笔记]]
- [外部资源链接]()

## 📊 阅读统计
- **总页数**: 
- **阅读天数**: 
- **每日平均页数**: 

---
**最后更新**: <% now %>
**阅读进度**: <% finalStatus === "completed" ? "✅ 已完成" : finalStatus === "reading" ? "🔄 进行中" : "⏳ 未开始" %>