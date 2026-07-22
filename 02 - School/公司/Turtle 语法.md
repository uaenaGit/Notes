---
created: 2026-07-16T09:31
updated: 2026-07-16T09:51
---
# Turtle 语法零基础完整笔记
## 一、Turtle 是什么
Turtle（Terse RDF Triple Language）是**RDF/OWL 最常用文本序列化格式**，用来写知识图谱、本体，可读性远优于XML/RDF/JSON-LD，本体工具（Protegé、OWL API）默认导出格式。
核心最小单元：**三元组 (主语 谓语 宾语)**

## 二、基础符号规则
### 1. 语句结束符 `.`
每一条完整三元组末尾必须加点，代表语句结束。
```turtle
:a rdf:type owl:Class . # 完整语句，结尾.
```

### 2. 分号 `;`：同主语，复用主语
多个谓语宾语共享同一个主语，用 `;` 分隔，不用重复写主语。
对应你代码里的类定义：
```turtle
:DomainConcept1 rdf:type owl:Class ;
                sysml:metaclass "ITEM_DEF" .
# 等价两句：
# :DomainConcept1 rdf:type owl:Class .
# :DomainConcept1 sysml:metaclass "ITEM_DEF" .
```

### 3. 逗号 `,`：同主语+同谓语，多个宾语
```turtle
:UAV rdfs:label "无人机", "Unmanned Aerial Vehicle" .
```

### 4. 注释 `#`
# 后面整行都是注释，机器忽略，用于写说明。

## 三、前缀 @prefix（最重要，简化长URI）
### 语法
`@prefix 简写别名: <完整URI基础路径> .`
示例你文中的：
```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
# owl:Class = <http://www.w3.org/2002/07/owl#Class>
```
### 特殊前缀 @base
`@base <xxx#> .`
全局基础地址，直接 `:资源名` 就能省略完整URL，文中所有`:DomainConcept1`依赖这个base。

## 四、三元组三要素类型
### 1. 主语、谓语：只能是 IRI（资源链接）
两种写法：
1. 完整尖括号 `<http://xxx#Concept>`
2. 简写前缀 `:DomainConcept1` / `owl:Class`

### 2. 宾语两种类型
#### （1）IRI资源（指向另一个本体概念）
`:A rdfs:subClassOf :B .`
#### （2）字面量 Literal（字符串、数字、日期）
用双引号包裹，可搭配xsd数据类型
```turtle
:UAV weight "5.2"^^xsd:float .
:UAV name "侦察无人机" . # 默认xsd:string
```
你代码里 `"ITEM_DEF"` 就是无类型字符串字面量。

## 五、OWL本体常用固定词汇（对应你的代码）
### 1. 本体声明
`<本体URL> rdf:type owl:Ontology .`
告诉解析器：这份文件是OWL本体。

### 2. 类 Class（领域概念）
`:概念名 rdf:type owl:Class .`
代表领域里一类事物，如无人机、传感器。

### 3. 注解属性 AnnotationProperty
`<sysml:metaclass> rdf:type owl:AnnotationProperty .`
- 仅用来打标签、备注；
- **不参与逻辑推理**，只附加外部建模信息（你案例绑定SysML元模型）；
- 区别于对象属性/数据属性（用于推理约束）。

## 六、最简完整示例（对照你给的uav本体）
```turtle
# 1. 定义前缀
@prefix : <http://example.org/uav#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@base <http://example.org/uav#> .

# 2. 声明这是一个OWL本体
<http://example.org/uav#> rdf:type owl:Ontology .

# 3. 定义注解属性
<http://omg.org/sysml/v2#metaclass> rdf:type owl:AnnotationProperty .

# 4. 定义领域类
:DomainConcept1 rdf:type owl:Class ;
                <http://omg.org/sysml/v2#metaclass> "ITEM_DEF" .
```

## 七、初学者高频易错点
1. 漏写结尾 `.` → 解析报错；
2. `;` 和 `,` 混淆：分号换谓语，逗号换宾语；
3. 字面量不加双引号；
4. 前缀末尾必须带 `#` 或 `/`，否则简写失效；
5. AnnotationProperty 不能用来做推理公理，仅标注。

## 八、快速记忆总结
1. Turtle = 主语 谓语 宾语 .
2. `;` 同主语换谓语，`,` 主谓不变换宾语；
3. `@prefix` 简化长网址，`:xxx` 靠@base生效；
4. 尖括号=完整资源地址，双引号=文本/数字值；
5. owl:Ontology标记本体，owl:Class定义业务概念，AnnotationProperty做备注标签。