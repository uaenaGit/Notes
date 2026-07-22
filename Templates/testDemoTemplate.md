---
created: 2026-02-23T20:45
updated: 2026-04-20T18:21
---
<%*
// ====== 1. 基础交互输入 ======
// 弹出输入框获取基础信息
const tripTitle = await tp.system.prompt("📍 旅行目的地（如：日本·东京）");
if (!tripTitle) { new Notice("未输入目的地，已取消"); return; } // 增加一个取消判断

const dateStart = await tp.system.prompt("📅 开始日期 (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD"));
const dateEnd = await tp.system.prompt("🏁 结束日期 (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD"));
const companions = await tp.system.prompt("👥 同行人（逗号分隔）", "");
const budgetTotal = await tp.system.prompt("💰 总预算", "");

// 状态选择
const statusOptions = ["规划中 ✈️", "进行中 🔥", "已完成 ✅", "已取消 ❌"];
const status = await tp.system.suggester(statusOptions, statusOptions);

// 标签选择
const tagOptions = ["国内", "国外", "特种兵", "休闲游", "美食之旅", "独自旅行"];
const selectedTags = await tp.system.multi_suggester(tagOptions, tagOptions);

// 处理标签格式：如果用户没选，selectedTags 可能是 undefined，需要处理
let tagsStr = "";
if (selectedTags && selectedTags.length > 0) {
    tagsStr = selectedTags.map(t => `"travel/${t.replace(/ /g, '_')}"`).join(", ");
}

// ====== 2. 生成 YAML Frontmatter ======
// 注意：这里最后面千万不要加分号
tR = `---
title: ${tripTitle}
date: ${dateStart} ~ ${dateEnd}
companions: ${companions}
budget_total: ${budgetTotal}
status: "${status}"
tags: [${tagsStr}, "travel/trip"]
aliases: ["${tripTitle} 游记"]
cover: 
---

# ✈️ ${tripTitle} 旅行笔记

> **时间**：${dateStart} 至 ${dateEnd}
> **同行人**：${companions}
> **状态**：${status}

---

## 📅 详细日程

### Day 1: ${dateStart}
- **上午**：
- **下午**：
- **晚上**：

### Day 2: 
- **上午**：
- **下午**：
- **晚上**：

*(按需复制 Day)*

---

## 🏨 住宿记录

| 酒店/民宿名称 | 区域/位置 | 费用 (元/晚) | 评分 (1-5) | 评价与备注 |
| :--- | :--- | :--- | :--- | :--- |
| **示例：新宿华盛顿酒店** | 新宿 | 800 | ⭐⭐⭐⭐ | 离地铁近，房间虽小但干净。 |
|  |  |  |  |  |
|  |  |  |  |  |

---

## 🍜 美食探店

| 餐厅名称 | 推荐菜品 | 人均消费 | 评分 (1-5) | 评价与避雷 |
| :--- | :--- | :--- | :--- | :--- |
| **示例：一兰拉面** | 原味拉面 | 100 | ⭐⭐⭐ | 味道一般，主要是吃个氛围，排队太久。 |
|  |  |  |  |  |
|  |  |  |  |  |

---

## 🎒 物品清单 (Checklist)
- [ ] 证件 (护照/身份证)
	- [ ] 护照
	- [ ] 身份证
- [ ] 电子设备 (充电器/转换插头)
	- [ ] 电脑
	- [ ] ipad
	- [ ] 手机
	- [ ] 充电器
- [ ] 衣物
	- [ ] 短袖
	- [ ] 薄外套
	- [ ] 冲锋衣
	- [ ] 羽绒服
	- [ ] 短裤
	- [ ] 长裤
- [ ] 洗漱用品
	- [ ] 牙膏牙刷
	- [ ] 毛巾
	- [ ] 拖鞋
	- [ ] 洗面奶
	- [ ] 洗衣液
	- [ ] 洗发露
	- [ ] 沐浴露
- [ ] 日常用品
	- [ ] 防晒霜
	- [ ] 雨伞
	- [ ] 墨镜
	- [ ] 卫生用品
- [ ] 药品
	- [ ] 创口贴
- [ ] 书本
	- [ ] 宋词三百首


`
_%>