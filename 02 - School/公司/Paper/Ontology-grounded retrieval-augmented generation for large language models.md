---
created: 2026-07-16T19:07
updated: 2026-07-17T17:11
---
# Abstract


# 重难点
## Ontology
Definition 1 An ontology $\mathcal{O} \subseteq \mathcal{S} \times \mathcal{A} \times (\mathcal{S} \cup \{\phi\})$ consists of a set of triples that relate a set of entities $\mathcal{S}$ using a set of attributes $\mathcal{A}$, where $(s,a,v) \in \mathcal{O}$ denotes that the subject entity $s$ has an attribute $a$, and the value $v := v_\mathcal{O}(s,a)$ is either: (1) Another entity $s' \in \mathcal{S}$, or (2) An unspecified domain value, denoted by $\phi$. Here, $v := v_\mathcal{O}(s,a)$ represents the value of the attribute $a$ for entity $s$, which is either another entity within the ontology or an undefined (unspecified) text or data.
### 定义1 领域本体$\mathcal{O}$ 详细解析
#### 一、先拆解核心数学表达式
$$\mathcal{O} \subseteq \mathcal{S} \times \mathcal{A} \times (\mathcal{S} \cup \{\phi\})$$
- $\mathcal{S}$：**实体集合**（领域里所有可定义的对象，比如作物、种植区）
- $\mathcal{A}$：**属性/关系集合**（比如“名称”“所属种植区域”）
- $\times$：笛卡尔积，组合三元组$(s,a,v)$
- 末尾值域：取值$v$只能是两种情况：要么是另一个实体$s' \in \mathcal{S}$，要么是特殊空标记$\phi$
- $\mathcal{O}$是这类合法三元组构成的集合，也就是**本体由规范三元组组成**

#### 二、三元组$(s,a,v)$的语义
$(s,a,v) \in \mathcal{O}$ 含义：**主体实体$s$具备属性$a$，该属性对应的取值为$v$**
$v$分两类（论文明确划分）：
1. **嵌套实体型取值**：$v=s' \in \mathcal{S}$
属性值指向本体里的另一个实体，天然形成层级嵌套关系，例：
$($大豆，种植区域，西北产区$)$，“西北产区”也是$\mathcal{S}$里定义的实体，还能继续挂自己的属性
2. **未指定字面量取值**：$v=\phi$
代表这个属性的值是普通文本、数字这类非结构化字面量，不属于本体里预定义的实体，没法继续往下嵌套层级

#### 三、函数$v_\mathcal{O}(s,a)$说明
$v:=v_\mathcal{O}(s,a)$是本体的取值映射函数：输入实体$s$、属性$a$，输出该属性对应的取值$v$，输出结果只会落在「实体」或「空标记字面量」两种范畴内。

#### 四、结合你整套OG-RAG体系的关联理解
1. **本体是全局规范模板**：后续LLM从文档抽取事实块时，实体$s$、属性$a$必须从$\mathcal{S}、\mathcal{A}$里选取，不能自定义词汇，实现“本体约束抽取”；
2. **两种取值正好对应FLATTEN算法的两类三元组**：
   - $v=s'$（实体）→ 嵌套三元组$(s,a,s')$，需要递归扁平化；
   - $v=\phi$（字面量）→ 叶子三元组$(s,a,v)$，可直接拼接路径扁平化；
3. $\phi$标记用来区分“可继续嵌套的中间实体”和“终止层级的普通文本数值”，是FLATTEN递归终止判断的依据。

#### 五、通俗举例
设$\mathcal{S}=\{大豆,西北产区\}$，$\mathcal{A}=\{作物名,种植区域\}$
- $(大豆,种植区域,西北产区)$：$v=西北产区 \in \mathcal{S}$，嵌套型三元组；
- $(大豆,作物名,\phi)$：作物名的实际值是普通字符串“Soybean”，不属于预定义实体，用$\phi$标记归类为字面量类型。

#### 六、和普通知识图谱三元组的区别
常规KG三元组允许取值直接写任意字面量；
这个本体定义做了**强约束**：所有字面量统一用$\phi$归类，只有预定义实体才能作为结构化嵌套取值，能严格统一后续扁平化、超图构建的数据格式。

## Ontology-mapped data
Definition 2 Ontology-mapped data $\mathcal{I} := \mathcal{D}(\mathcal{O})$ is a set of factual-blocks, where each factual-block $F$ represents a set of ontology relationships $(s,a,v) \in F$, where the value $v$ is derived as follows: If value $v_\mathcal{O}(s,a) = \phi$ then $v \in \mathcal{V}$ is extracted from the document text; otherwise $v = v_\mathcal{O}(s,a)$ is the value provided by the ontology.

### 定义2 本体映射数据 $\mathcal{I}$ 解析
#### 一、核心符号总览
1. $\mathcal{I} := \mathcal{D}(\mathcal{O})$：**本体映射后的数据**，是把原始文档$\mathcal{D}$按照本体$\mathcal{O}$的规范做结构化转换得到的结果
2. $\mathcal{I}$ 的组成：由多个**事实块 factual-block $F$** 构成，也就是前面OG-RAG预处理阶段LLM抽取出来的那一组组嵌套事实
3. 每个事实块$F$内部是多条符合本体约束的三元组$(s,a,v)$
4. $v_\mathcal{O}(s,a)$：定义1里本体自带的属性取值映射函数；$\phi$代表本体标记「此处要从文档取字面量」；$\mathcal{V}$是字面量取值集合

---
#### 二、$v$ 的两种取值规则（整段定义的核心）
##### 情况1：本体标注该位置是字面量空位：$v_\mathcal{O}(s,a)=\phi$
本体只规定了实体$s$、属性$a$，没有预先填好取值，需要**从原始文档文本里抽取真实值$v$**，抽出来的$v$属于普通字面量集合$\mathcal{V}$。
举例：本体规定`(作物,作物名称,φ)`，LLM从文档读到“作物是大豆”，就把$v$填成`大豆`。

##### 情况2：本体本身已经定义好了取值：$v_\mathcal{O}(s,a)\neq\phi$
本体预先就绑定好了属性对应的实体取值，直接沿用本体给定的值，不需要再从文档抽取。
举例：本体预先定义`(作物,所属产区,西北产区)`，“西北产区”是本体内已定义实体，直接复用这个取值。

---
#### 三、结合整套论文流程梳理作用
1. 本体$\mathcal{O}$相当于**结构化抽取模板**：只定好实体、属性框架，部分位置留$\phi$空白；
2. LLM执行OG-PREPROCESS步骤时，对照模板读文档：空白位从文档抽字面量，已定义位直接继承本体值；
3. 填充完成的一组组三元组打包成一个个事实块$F$，全部汇总就是本体映射数据$\mathcal{I}$；
4. 后续再对每个$F$执行`FLATTEN`扁平化、构建超图，完成OG-RAG的知识库搭建。

---
#### 四、通俗总结
本体先搭好知识骨架，分两种位置：
- 空白槽位（$\phi$）：去文档里找具体文字、数字填上；
- 固定槽位：直接用本体提前设定好的实体值；
把填充完整的多条关联三元组打包成事实块，所有事实块合起来，就是$\mathcal{I}$。

## Flattening a factual block
Algorithm 1 Flattening a factual block
**Require:** Factual block $F$, Concatenation $\oplus$.
**Ensure:** A set of flattened factual-blocks $\overline{F} \leftarrow$
$\text{FLATTEN}(F)$ flattens any nested information present in $F$.
1: **procedure** $\text{FLATTEN}(F)$
2: $\quad \overline{F} \leftarrow \{\}$
3: $\quad \overline{F}_0 \leftarrow \{ (s \oplus a, v) : (s,a,v) \in F, v \in \mathcal{V}, (s',a',s) \notin F \}$. $\triangleright$ can be directly flattened
4: $\quad \overline{F} \leftarrow \overline{F} \cup \{ \overline{F}_0 \}$.
5: $\quad$ **for** $(s,a,s') \in F \setminus \overline{F}_0$ **do**
6: $\quad\quad$ **if** $s' \in \mathcal{S}$ **then**
7: $\quad\quad\quad F_{s'} \leftarrow \overline{F}_0 \cup \{ (s \oplus a \oplus s' \oplus a', v') : (s',a',v') \in F \}$.
8: $\quad\quad\quad \overline{F} \leftarrow \overline{F} \cup \text{FLATTEN}(F_{s'})$.
9: $\quad\quad$ **end if**
10: $\quad$ **end for**
11: $\quad$ **return** $\overline{F}$
12: **end procedure**

### 算法逐行拆解：FLATTEN 事实块扁平化递归算法
#### 一、先明确基础符号定义（先搞懂术语才能读懂）
| 符号 | 含义 |
| ---- | ---- |
| $F$ | **嵌套事实块集合**，元素格式分两类：<br>1. 叶子事实：$(s,a,v)$，属性$a$把主体$s$绑定到字面量值$v$（无更深嵌套）<br>2. 嵌套事实：$(s,a,s')$，属性$a$把主体$s$绑定到另一个子主体$s'$（$s'$还能继续挂属性，产生嵌套） |
| $\oplus$ | **路径拼接/字符串拼接算子**，把多级主体、属性拼接成一条扁平化的长路径 |
| $\mathcal{V}$ | 字面量值集合（普通数值、字符串，不是可继续嵌套的主体） |
| $\mathcal{S}$ | 主体集合（可以继续挂载属性、产生更深嵌套的节点） |
| $\overline{F}$ | 最终输出：**完全扁平化后的事实集合**，所有嵌套都被展开，只剩「长路径→字面量值」的结构 |
| $F\setminus \overline{F}_0$ | 总集合减去可直接扁平化的叶子事实，剩下全是嵌套型事实$(s,a,s')$ |

**算法核心目标**：把多层级嵌套的主体-属性结构，递归拆成一条条无嵌套的扁平化路径，消除层级关系。

---
#### 二、逐行代码解析
##### 1-2行：初始化
```
procedure FLATTEN(F)
    $\overline{F} \leftarrow \{\}$
```
定义递归函数，先初始化空集合，用来存放最终扁平化结果。

##### 3行：提取**可直接扁平化的叶子事实**
$$\overline{F}_0 \leftarrow \{(s \oplus a,v): (s,a,v) \in F,v \in \mathcal{V},(s',a',s) \notin F\}$$
筛选条件同时满足3点：
1. 事实格式是叶子结构 $(s,a,v)$，终点$v$是普通字面量；
2. $s$ 不存在「别的主体$s'$通过某个属性$a'$指向它」，也就是$s$本身不是中间嵌套子节点；
3. 直接把主体$s$和属性$a$拼接成路径$s\oplus a$，映射到值$v$。

注释含义：这类叶子事实没有上层嵌套，可以直接扁平化处理。

##### 4行：把这批叶子结果加入总结果
$$\overline{F} \leftarrow \overline{F} \cup \{\overline{F}_0\}$$
把第一层能直接展开的叶子事实，先并入最终集合。

##### 5行：遍历剩下的**嵌套型事实**
```
for (s,a,s') ∈ F\F̄₀ do
```
排除已经处理完的叶子$\overline{F}_0$，只遍历剩下的嵌套条目：$(s,a,s')$，也就是$s$通过属性$a$指向子主体$s'$，$s'$还能继续挂属性。

##### 6行：判断子节点是否可继续嵌套
```
if s' ∈ S then
```
如果$s'$属于主体集合（还能继续挂载属性、存在更深层级），就需要递归展开。

##### 7行：构造子递归的输入集合$F_{s'}$
$$F_{s'} \leftarrow \overline{F}_0 \cup \{(s \oplus a \oplus s' \oplus a',v'): (s',a',v') \in F\}$$
1. 带上本轮已经处理好的叶子集合$\overline{F}_0$；
2. 把上层路径$s\oplus a$、子主体$s'$、子属性$a'$全部拼接，形成完整长路径，绑定子节点的叶子值$v'$；
> 本质：把上层的路径前缀，拼接到子节点所有属性前面，消除层级。

##### 8行：递归扁平化子结构，结果并入总集合
$$\overline{F} \leftarrow \overline{F} \cup \text{FLATTEN}(F_{s'})$$
对子集合$F_{s'}$再次调用FLATTEN，把子层级全部展开，展开后的结果合并进全局扁平化集合。

##### 9-11行：结束分支、循环，返回结果
- 内层`if`结束、遍历完所有嵌套事实；
- 把完全去嵌套的$\overline{F}$返回。

---
#### 三、举极简例子直观理解
##### 原始嵌套结构
1. 顶层：$(公司,部门,研发部)$ → $(s=公司,a=部门,s'=研发部)$（嵌套型）
2. 子节点：$(研发部,人数,50)$ → $(s=研发部,a=人数,v=50)$（叶子字面量）

##### 算法执行过程
1. $\overline{F}_0$初始为空：`研发部`被`公司.部门`指向，不满足「无上层指向」，不能直接扁平化；
2. 进入循环处理嵌套事实$(公司,部门,研发部)$，`研发部∈S`可继续嵌套；
3. 构造$F_{研发部}$：拼接路径 `公司⊕部门⊕研发部⊕人数`，绑定值`50`；
4. 递归调用FLATTEN，把子层级展开；
5. 最终扁平化结果：$\{(公司.部门.研发部.人数,\ 50)\}$，**彻底消除两层嵌套**。

---
#### 四、算法设计要点总结
1. **分两类处理事实**：无上层依赖的叶子直接扁平化；带嵌套指向的节点走递归；
2. **路径前缀继承**：每往下递归一层，就把上层所有主体、属性拼进路径前缀，层级被抹平；
3. **递归终止条件**：当子节点最终指向字面量$\mathcal{V}$，不再有可嵌套的主体，递归结束；
4. 最终输出：所有嵌套结构全部变成「一条完整拼接路径 → 字面量值」的扁平键值对。

#### 五、容易混淆的细节提醒
- 第3行`(s',a',s) ∉ F`：是过滤**被上层节点引用的中间节点**，这类节点不能直接扁平化，必须跟着上层路径一起拼接；
- 第7行每次拼接都会带上$\overline{F}_0$：保证每轮递归都不会丢失上一轮已经处理好的叶子数据；
- $F\setminus\overline{F}_0$：只处理嵌套条目，避免重复处理已经扁平化的叶子事实。


## Hypergraph
Definition 3 A hypergraph $\mathcal{H}(\mathcal{I}) := (\mathcal{N}, \mathcal{E})$ consists of hypernodes $\mathcal{N}$ and hyperedges $\mathcal{E}$, such that each hyperedge $e \in \mathcal{E}$ is an arbitrary set of hypernodes. Defining $\mathcal{P}(X)$ as the power set of $X$ and $\bigoplus X$ as the set that is formed by concatenating the strings within each element of the set $X$, we have the hyperedges $\mathcal{E} \subseteq \mathcal{P}(\mathcal{N})$ and the hypernodes $\mathcal{N} \subseteq \big[\bigoplus\mathcal{P}(\mathcal{S} \times \mathcal{A})\big] \times \mathcal{V}$, where $\times$ is the cartesian product.
### 定义3 超图$\mathcal{H}(\mathcal{I})$完整解析
#### 一、先拆解基础概念：普通图 vs 超图
普通图：一条边**只能连接2个顶点**；
**超图**：一条**超边（hyperedge）**可以一次性连接**任意数量（≥1）的超节点（hypernode）**，超边就是超节点构成的子集，这是超图最核心特征。

公式开头：$\mathcal{H}(\mathcal{I}) := (\mathcal{N},\mathcal{E})$
- $\mathcal{N}$：全体**超节点**集合
- $\mathcal{E}$：全体**超边**集合
约束：$\forall e\in\mathcal{E}$，超边$e$本身就是一堆超节点组成的集合。

---
#### 二、逐个解释文中数学符号
1. $\mathcal{P}(X)$：集合$X$的**幂集**，也就是$X$所有子集构成的集合
   例：$X=\{a,b\}$，$\mathcal{P}(X)=\{\emptyset,\{a\},\{b\},\{a,b\}\}$
2. $\mathcal{E}\subseteq\mathcal{P}(\mathcal{N})$：所有超边都是超节点集合的子集，和定义完全对应——每条超边都是若干超节点组成的子集
3. $\bigoplus X$：文中专门定义的**字符串拼接算子**：
   集合$X$里的每一个元素本身是一组字符串，把单个元素内的所有字符串按顺序拼接，处理完所有元素得到新集合，就是$\bigoplus X$
4. $\times$：**笛卡尔积**，两个集合元素两两配对组合
5. $\mathcal{S}$：主体集合、$\mathcal{A}$：属性集合、$\mathcal{V}$：字面量取值集合（和你之前FLATTEN算法的符号体系完全一致）

---
#### 三、超节点约束：$\mathcal{N}\subseteq \big[\bigoplus\mathcal{P}(\mathcal{S}\times\mathcal{A})\big]\times\mathcal{V}$，分层拆解
##### 第1层：$\mathcal{S}\times\mathcal{A}$
主体、属性做笛卡尔积，得到所有「(主体,属性)」二元组，对应知识里的一条条属性关联。

##### 第2层：$\mathcal{P}(\mathcal{S}\times\mathcal{A})$
对上面所有二元组取幂集，代表可以任意挑选多组「主体-属性」组合，形成不同的路径组。

##### 第3层：$\bigoplus\mathcal{P}(\mathcal{S}\times\mathcal{A})$
把幂集里每一个子集内的「主体-属性」按顺序**字符串拼接**，生成一条条完整长路径（就是FLATTEN算法扁平化后的路径）。

##### 第4层：$\big[\bigoplus\mathcal{P}(\mathcal{S}\times\mathcal{A})\big]\times\mathcal{V}$
把拼接好的路径，和字面量取值$\mathcal{V}$做笛卡尔积，最终形式就是 **(扁平化长路径, 取值)**，正好对应FLATTEN扁平化输出的键值对结构。

##### 整体约束含义
所有超节点$\mathcal{N}$，都只能是「扁平化路径+取值」这种键值结构，**超节点就是扁平化后的事实条目**。

---
#### 四、把整段定义翻译成通俗逻辑
1. 基于原始知识输入$\mathcal{I}$构建超图$\mathcal{H}$，结构=(超节点集合$\mathcal{N}$，超边集合$\mathcal{E}$)
2. 超边没有连接数量限制，任意挑选一批超节点就能组成一条超边；
3. 超边必须是超节点集合的子集；
4. 超节点来源：
   - 先把原始所有(主体,属性)组合做子集枚举
   - 子集内的内容拼接成长路径（FLATTEN扁平化操作）
   - 路径再绑定具体字面量值，得到一条事实键值对，这就是一个超节点；
   - 所有超节点都不能超出这种结构。

#### 五、和你前面FLATTEN算法的关联
- FLATTEN负责把嵌套事实**扁平化**，生成「长路径-取值」的键值；
- 这条定义就是把**扁平化后的每一条事实键值，作为超图的一个超节点**；
- 再把存在关联的一批事实节点打包成一条超边，用超图结构建模扁平化后的知识集合。

#### 六、举极简例子辅助理解
设：$\mathcal{S}=\{公司\},\mathcal{A}=\{部门,人数\},\mathcal{V}=\{50\}$
1. $\mathcal{S}\times\mathcal{A}=\{(公司,部门),(公司,人数)\}$
2. $\mathcal{P}(\mathcal{S}\times\mathcal{A})$枚举所有子集，取出子集$\{(公司,部门),(公司,人数)\}$
3. $\bigoplus$拼接得到路径：`公司部门人数`
4. 和$\mathcal{V}$笛卡尔积：(`公司部门人数`,50)，这一个键值对就是**一个超节点**；
如果同时有(`公司地址`,`北京`)这个节点，把两个节点打包成集合，就构成一条超边。

## OG-RAG

Algorithm 2 OG-RAG
**Require:** Query $Q$, Domain-specific Ontology $\mathcal{O}$,
    Documents $\mathcal{D}$, Sentence embedding function
    $Z$, LLM $\mathcal{M}_0$, Maximum length $L$
**Ensure:** Retrieved context $\mathcal{C}_\mathcal{H}(Q)$ is grounded in
    the ontology and relevant to the query

1: **procedure** $\text{OG-PREPROCESS}(\mathcal{O}, \mathcal{D}, \mathcal{M}_0)$
2: $\quad \mathcal{I} \leftarrow \text{LLM } \mathcal{M}_0(\text{Mapping Prompt}, \mathcal{D}, \mathcal{O})$
3: $\quad \mathcal{H}(\mathcal{I}) \leftarrow \text{Hypergraph with edges } \bigcup_{F\in\mathcal{I}} \text{FLATTEN}(F).$
4: **end procedure**
5: **procedure** $\text{OG-RETRIEVE}(Q, \mathcal{H}(\mathcal{I}), Z, k, L)$
6: $\quad \mathcal{N}, \mathcal{E} \leftarrow \text{nodes, edges of hypergraph } \mathcal{H}(\mathcal{I}).$
7: $\quad \mathcal{N}_S(Q) \leftarrow \text{topk}_{(s,a,v)\in\mathcal{N}}\langle Z(s \oplus a), Z(Q)\rangle.$
8: $\quad \mathcal{N}_V(Q) \leftarrow \text{topk}_{(s,a,v)\in\mathcal{N}}\langle Z(v), Z(Q)\rangle.$
9: $\quad \mathcal{N}(Q) \leftarrow \mathcal{N}_S(Q) \cup \mathcal{N}_V(Q).$
10:$\quad \mathcal{C}_\mathcal{H}(Q) \leftarrow \{\}$
11:$\quad$ **while** $(|\mathcal{N}(Q)| > 0) \lor (|\mathcal{C}_\mathcal{H}(Q)| < L)$ **do**
12:$\quad\quad \mathcal{C}_\mathcal{H}(Q) \leftarrow \mathcal{C}_\mathcal{H}(Q) \cup \arg\max_{e\in\mathcal{E}} |\{n \in \mathcal{N}(Q) : n \in e\}|$
13:$\quad$ **end while**
14:$\quad$ **return** $\mathcal{C}_\mathcal{H}(Q)$
15: **end procedure**

### Algorithm 2 OG-RAG 算法完整解析
#### 一、先明确输入输出
##### Require（输入）
- $Q$：用户查询问题
- $\mathcal{O}$：领域本体（Ontology，定义实体、属性、层级规范）
- $\mathcal{D}$：原始待检索文档集
- $Z(\cdot)$：句子/文本向量化嵌入函数，把文本转为向量算相似度
- $\mathcal{M}_0$：基础大语言模型LLM
- $L$：最终检索上下文最大长度上限

##### Ensure（输出目标）
检索得到上下文$\mathcal{C}_\mathcal{H}(Q)$，**两条约束**：
1. 内容严格贴合本体$\mathcal{O}$的知识规范
2. 和用户查询$Q$语义高度相关

整体算法分两大阶段：**OG-PREPROCESS（离线预处理建超图）** + **OG-RETRIEVE（在线查询检索上下文）**

---
#### 二、第一阶段：OG-PREPROCESS 离线预处理（行1-4）
##### 行2：抽取结构化事实集合$\mathcal{I}$
$$\mathcal{I} \leftarrow \text{LLM } \mathcal{M}_0(\text{Mapping Prompt}, \mathcal{D}, \mathcal{O})$$
给大模型传入「本体映射提示词」、原始文档$\mathcal{D}$、领域本体$\mathcal{O}$，让LLM从文档里抽取**符合本体规范的嵌套事实块**，全部汇总成事实集合$\mathcal{I}$。

##### 行3：构建知识超图$\mathcal{H}(\mathcal{I})$
$$\mathcal{H}(\mathcal{I}) \leftarrow \text{Hypergraph with edges } \bigcup_{F\in\mathcal{I}} \text{FLATTEN}(F)$$
1. 遍历$\mathcal{I}$里每一条嵌套事实$F$，调用你之前学的**FLATTEN扁平化算法**，把嵌套事实展开成「路径-取值」形式的超节点；
2. 把同一实体关联的扁平化超节点打包成超边；
3. 所有事实处理完成，最终建成完整知识超图$\mathcal{H}(\mathcal{I})$（超节点=扁平化事实，超边=事实关联关系）。

> 这一步把非结构化文档 → 本体约束结构化事实 → FLATTEN扁平化 → 超图知识网络，是整套OG-RAG的核心底座。

---
#### 三、第二阶段：OG-RETRIEVE 在线检索（行5-15）
##### 行6：拆分超图要素
$$\mathcal{N},\mathcal{E} \leftarrow \text{nodes, edges of hypergraph } \mathcal{H}(\mathcal{I})$$
取出超图全部超节点集合$\mathcal{N}$、全部超边集合$\mathcal{E}$。

##### 行7-9：两轮筛选初筛候选节点$\mathcal{N}(Q)$
###### 行7：按**事实路径**语义召回
$$\mathcal{N}_S(Q) \leftarrow \text{top}k_{(s,a,v)\in\mathcal{N}}\big\langle \mathbf{Z}(s\oplus a),\mathbf{Z}(Q) \big\rangle$$
- $s\oplus a$：FLATTEN拼接出的属性长路径；
- $\langle\cdot,\cdot\rangle$：向量余弦相似度；
- 对所有超节点的路径做向量相似度计算，取相似度最高的前$k$个节点，得到$\mathcal{N}_S(Q)$。

**向量相似度的计算方式**
检索阶段采用**余弦相似度**完成向量间相似度打分，计算公式：
$$
\cos(\boldsymbol{x},\boldsymbol{y})=\frac{\boldsymbol{x}\cdot\boldsymbol{y}}{\Vert\boldsymbol{x}\Vert_2\cdot\Vert\boldsymbol{y}\Vert_2}=\frac{\sum_{i=1}^d x_i y_i}{\sqrt{\sum_{i=1}^d x_i^2}\cdot\sqrt{\sum_{i=1}^d y_i^2}}
$$
- $\boldsymbol{x}\cdot\boldsymbol{y}$：两个向量的**点积**，把向量对应维度的数值相乘后再全部累加求和
- $\Vert\boldsymbol{x}\Vert_2、\Vert\boldsymbol{y}\Vert_2$：分别为两个向量的**L2范数（向量模长）**
- $d$：嵌入向量的维度，常用BGE、BERT类模型输出维度多为384维、768维
- 数值取值范围为$[-1,1]$，**数值越接近1，代表两段文本语义相似度越高**；夹角为90°时相似度为0，向量方向完全相反时相似度为-1

OG-RAG算法里两处相似度计算逻辑完全一致，仅输入编码的文本不同：
1. 按事实路径召回：把扁平化拼接后的属性长路径文本编码为向量$\boldsymbol{x}$，用户查询语句编码为向量$\boldsymbol{y}$，计算二者余弦相似度，筛选相似度最高的前$k$个节点
2. 按事实取值召回：把超节点里的事实取值文本编码为向量$\boldsymbol{x}$，用户查询语句编码为向量$\boldsymbol{y}$，同样通过余弦相似度排序取前$k$个节点

**文本编码为向量（嵌入函数$\boldsymbol{Z(\cdot)}$的实现流程）**
统一使用**预训练句嵌入模型**（如BGE、E5、Sentence-BERT）完成文本转向量，完整处理步骤如下：
1. **文本预处理与分词**
对待编码文本（属性路径文本/事实取值文本/用户查询文本）做基础清洗，统一格式后调用模型自带分词器，将文本拆分为子词token，转换为数字ID序列，按模型要求补充首尾标记、做长度截断或空白补全。
2. **语义特征计算**
对每个token查表生成初始词向量，叠加位置编码区分词语先后顺序，再送入Transformer多层注意力网络，结合上下文语义计算每个token的深层特征向量。
3. **整句向量聚合**
主流采用**均值池化**：把所有token输出的特征向量逐维度求平均值，整合得到整段文本的单一向量；部分方案也可直接取开头`[CLS]`标记对应的向量作为句向量。
4. **L2归一化**
对聚合后的向量做模长归一化处理，归一化后计算余弦相似度可直接简化为向量点积，大幅提升检索计算效率。

实操注意要点：
- 属性路径、事实取值、用户查询**必须使用完全相同的嵌入模型、相同预处理规则**编码，保证所有向量处于同一个向量空间，相似度计算才有意义
- 工程落地时分批处理：离线阶段提前把所有超节点的路径、取值文本批量编码存入向量库，在线检索时仅对用户查询实时编码，再批量匹配相似度筛选候选节点

**三、可直接参考的极简代码示例**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

# 加载嵌入模型，对应算法里的Z(·)
embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
# 待编码的两类文本
path_text = "Crop has growing zone CropGrowingZone with name"
query_text = "大豆的种植区域是什么"

# 文本转向量，开启归一化
vec_x = embed_model.encode(path_text, normalize_embeddings=True)
vec_y = embed_model.encode(query_text, normalize_embeddings=True)
# 归一化后直接点积即可得到余弦相似度
cos_sim = np.dot(vec_x, vec_y)
```

###### 行8：按**事实取值**语义召回
$$\mathcal{N}_V(Q) \leftarrow \text{top}k_{(s,a,v)\in\mathcal{N}}\big\langle \mathbf{Z}(v),\mathbf{Z}(Q) \big\rangle$$
再对超节点里的具体取值$v$做向量相似度，取前$k$个节点得到$\mathcal{N}_V(Q)$。

###### 行9：合并两路候选
$$\mathcal{N}(Q) \leftarrow \mathcal{N}_S(Q) \cup \mathcal{N}_V(Q)$$
把「路径相关」「取值相关」两类候选节点去重合并，得到初始待选节点池。

##### 行10：初始化最终上下文集合
$$\mathcal{C}_\mathcal{H}(Q) \leftarrow \{\}$$

##### 行11-13：贪心扩充上下文（核心排序逻辑）
循环终止条件二选一满足就停止：
1. 候选节点池$\mathcal{N}(Q)$被选空；
2. 上下文长度达到上限$L$

每一轮贪心选择规则（行12）：
$$\mathcal{C}_\mathcal{H}(Q) \leftarrow \mathcal{C}_\mathcal{H}(Q) \cup \arg\max_{e\in\mathcal{E}} \big|\{n\in\mathcal{N}(Q):n\in e\}\big|$$
翻译：
遍历所有超边$e$，统计**这条超边包含多少个当前候选池里的节点**，优先挑选「命中候选节点数量最多」的超边，把这条超边绑定的所有事实节点加入上下文；
本质：利用超边的关联聚合特性，优先把**成组关联的相关事实批量召回**，避免零散召回孤立事实，保证知识的完整性。

##### 行14：输出最终上下文
返回组装完成、符合本体约束的检索上下文$\mathcal{C}_\mathcal{H}(Q)$，送入LLM做问答生成。

---
#### 四、算法设计亮点（对比普通RAG）
1. **本体强约束**：事实抽取全程受领域本体$\mathcal{O}$规范，不会抽取脱离领域的无效知识；
2. **嵌套事实扁平化**：靠FLATTEN算法统一所有层级事实的表达格式，方便向量计算；
3. **双向相似度召回**：同时匹配「属性路径语义」+「属性取值语义」，召回更全面；
4. **超图贪心组召回**：不是单个句子独立排序，而是优先召回关联性最强的一整组事实，解决普通RAG碎片化检索的问题；
5. **长度可控**：循环终止受最大长度$L$限制，适配LLM上下文窗口。

#### 五、全流程链路串联
原始文档$\mathcal{D}$+本体$\mathcal{O}$
→ LLM抽取结构化嵌套事实$\mathcal{I}$
→ FLATTEN扁平化所有事实
→ 构建事实关联超图$\mathcal{H}(\mathcal{I})$
→ 用户查询$Q$双向向量初筛候选节点
→ 按超边关联度贪心批量选关联事实
→ 输出合规、成体系的检索上下文




