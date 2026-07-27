---
created: 2026-07-27T09:43
updated: 2026-07-27T09:50
---
# Git 分支开发提交操作笔记
> 适用场景：项目主干 `main` 受保护，无直接推送权限；新建个人分支开发，提交 PR 等待评审；遵循 `fetch + rebase` 规范，生成线性干净提交历史
> 适配：Ontology Builder 项目，新手友好，规避高危操作

## 基础约定
1. 远程仓库别名：`origin`
2. 主干分支：`main`（禁止直接开发、禁止强推）
3. 分支命名规范
   - 新增功能：`feature/xxx`
   - 缺陷修复：`fix/xxx`
   - 示例：`feature/ontology-model-adjust`
4. 核心准则：**所有代码修改仅在个人分支进行，永远不在 main 分支写代码**

## 场景1：当前在 main 分支，本地已有未提交修改
不要在main直接提交，将改动迁移至新建分支
```bash
# 1.临时储藏所有本地改动
git stash

# 2.创建并切换到个人开发分支
git checkout -b feature/你的分支名

# 3.恢复储藏的代码到新分支
git stash pop

# 4.检查状态确认迁移成功
git status
```
> ⚠️ 环境文件提醒：`.env.builder`、密钥配置文件禁止提交远端
```bash
# 将本地环境文件加入忽略清单
echo ".env.builder" >> .gitignore
```
提交代码（指定文件，杜绝盲目 `git add .`）
```bash
git add src/xxx/file1.py src/xxx/file2.py
git commit -m "清晰描述本次改动内容"
```

## 场景2：新建分支后，第一次推送远程并创建PR
```bash
# 拉取远程所有分支最新信息（仅下载，不修改本地代码）
git fetch origin

# 基于远程最新主干执行变基，同步上游代码
git rebase origin/main
```
### 冲突处理（终端提示 conflict 时执行）
1. 打开冲突文件，删除 `<<<<<<< HEAD` 标记，人工合并代码
2. 保存文件，加入暂存
```bash
git add 冲突文件名.py
```
3. 继续完成rebase流程
```bash
git rebase --continue
```
> 放弃本次变基、恢复原状：`git rebase --abort`

### 推送分支
首次推送分支，无需强制推送
```bash
git push origin feature/你的分支名
```
推送完成后进入仓库网页，创建 PR/MR
- 源分支：个人feature分支
- 目标分支：`main`
- 填写改动说明，提交等待管理员评审

## 场景3：PR评审后，根据意见迭代修改（日常循环）
```bash
# 1.修改代码完成，提交变更
git add 修改的文件.py
git commit -m "根据评审意见调整xxx逻辑"

# 2.同步远程最新代码
git fetch origin

# 3.变基同步主干main
git rebase origin/main

# 【出现冲突：参照上方冲突处理流程】

# 分支已推送到远端，rebase修改提交历史，使用安全强推
git push --force-with-lease origin feature/你的分支名
```
> 注意：尽量不用 `git push -f`；`--force-with-lease` 安全性更高

## 核心命令概念笔记
1. `git fetch origin`
下载远端所有分支最新提交，**不会改动本地文件，安全性最高**
2. `git rebase origin/main`
把远端主干最新提交放在前面，本地提交拼接在后，形成线性提交历史，方便代码评审
3. `git pull = git fetch + git merge`
会生成多余合并提交，历史出现分叉，**本项目工作流不推荐使用**

## 绝对不能触碰的红线
1. ❌ 禁止在 `main` 分支编写、提交代码
2. ❌ 严禁在 `main` 分支执行任何 `push --force`
3. ❌ 多人共用同一个feature分支时，禁止rebase+强推，改用merge
4. ❌ 不要提交本地环境配置、密钥文件
5. ✅ `--force-with-lease` **仅限自己独立使用的个人分支**

## 日常开发极简命令速查表
```bash
# 写完代码提交
git add xxx.py
git commit -m "改动描述"

# 同步远端主干
git fetch origin
git rebase origin/main

# 解决冲突后推送
git push --force-with-lease origin feature/xxx
```

## Stash 储藏备用命令
```bash
git stash list      # 查看所有储藏记录
git stash pop       # 取出最近储藏，并删除储藏记录（推荐）
git stash apply     # 取出储藏内容，但保留储藏记录（备用）
```

