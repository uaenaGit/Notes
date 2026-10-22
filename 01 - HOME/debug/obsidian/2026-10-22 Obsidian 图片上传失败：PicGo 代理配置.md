---
title: Obsidian 图片上传失败：PicGo 代理配置
date: 2026-10-22
tags:
  - debug
  - obsidian
  - PicGo
  - 代理
status: 已解决
---

# Obsidian 图片上传失败：PicGo 代理配置

## 问题现象

在 Obsidian 中通过 **Image auto upload** 插件粘贴并上传图片时，上传失败，控制台出现：

```text
Failed request: TypeError:
Cannot read properties of undefined (reading '0')
    at PicGoUploader.uploadFileByClipboard
```

截图中的错误发生在 Image auto upload 插件处理 PicGo 上传结果时。

## 使用环境

| 项目 | 配置 |
| --- | --- |
| 笔记软件 | Obsidian |
| 图片上传插件 | Image auto upload 4.1.0 |
| 实际提供上传服务的软件 | PicGo |
| 图床 | GitHub |
| 代理软件 | FastLink |
| Obsidian 调用的上传地址 | `http://127.0.0.1:36677/upload` |
| FastLink 本地代理地址 | `http://127.0.0.1:7892` |

以上端口是本次排查时的实际配置，其他电脑或以后更改设置后可能不同。

## 排查依据

1. PicGo 日志记录到了来自 Obsidian 的请求，并开始上传剪贴板图片，说明 **Obsidian → PicGo 的本地调用已经成功**。
2. PicGo 使用 GitHub 上传器，在向 `api.github.com` 发起上传请求时失败：

   ```text
   Uploading... Current uploader is [github]
   method: PUT
   statusCode: 0
   message: socket hang up
   ```

   `socket hang up` 表示连接被中途断开；`statusCode: 0` 在这里表示没有取得有效的 HTTP 响应，不能据此认定是 GitHub 返回了某个权限错误。
3. PicGo 的上传代理为空；FastLink 正在运行，其核心进程监听本机 `127.0.0.1:7892` 端口。
4. 给 PicGo 配置 FastLink 代理后，用户重新测试，确认图片可以成功上传。

## 引发原因

### 直接原因：PicGo 上传请求没有正确通过 FastLink 代理

原先 PicGo 没有配置上传代理，到 GitHub 的上传连接出现 `socket hang up`。配置代理后上传恢复，说明本次故障与 PicGo 的代理路径有关。

**代理软件已经启动，不代表所有应用的网络请求都会自动通过它。** 是否自动使用代理，取决于代理模式、系统设置以及应用自身的网络实现。本次通过 PicGo 的“上传代理”设置明确指定了转发路径。

日志能够确认连接中断，但不能仅凭这条日志确定具体是哪一个网络环节断开了连接。

### 二次报错：Obsidian 插件没有妥善处理上传失败结果

插件处理返回结果的相关逻辑为：

```javascript
data: typeof data.result == "string" ? data.result : data.result[0]
```

PicGo 上传失败后没有提供预期的 `result` 图片链接，插件仍尝试读取 `data.result[0]`，因此出现：

```text
Cannot read properties of undefined (reading '0')
```

所以，截图里的 JavaScript 错误是上传失败后的二次报错；处理网络连接问题后，本次上传恢复。

## 解决办法

1. 打开 **PicGo → PicGo 设置 → 设置上传代理**（不同版本的菜单名称可能略有差异）。
2. 填入 FastLink 的本地 HTTP 代理地址：

   ```text
   http://127.0.0.1:7892
   ```

3. 保存设置，通过系统托盘菜单退出 PicGo，再重新打开。
4. 保持 FastLink 已连接，在 Obsidian 中重新复制并粘贴图片测试。

### 两个地址不要混淆

| 设置位置 | 地址 | 用途 |
| --- | --- | --- |
| PicGo 的上传代理 | `http://127.0.0.1:7892` | 让 PicGo 上传到 GitHub 时通过 FastLink 转发 |
| Obsidian 的 Image auto upload 上传地址 | `http://127.0.0.1:36677/upload` | 让 Obsidian 调用本机 PicGo 上传服务 |

本次保留 Obsidian 的上传地址，调整的是 PicGo 的上传代理。

## 验证结果

配置上传代理后，用户确认 **Obsidian 已能成功上传图片**，问题解决。

## 再次出现时的排查顺序

1. **先用 PicGo 自身上传图片。** 如果也失败，优先排查 PicGo、代理和图床连接；如果成功，再检查 Obsidian 插件及其上传服务地址。
2. **确认 FastLink 已连接。** 如果本地代理端口发生变化，同步更新 PicGo 的上传代理地址。
3. **查看 PicGo 日志。** 本机日志位置为 `%APPDATA%\picgo\picgo.log`。优先查看最后一次上传的实际错误，不要只根据 Obsidian 的 `reading '0'` 判断原因。
4. **按实际错误继续排查。** 连接中断或超时优先检查网络；如果收到 HTTP 401、403 等响应，再结合响应内容检查 GitHub Token、仓库权限等设置。

## 经验总结

图片上传经过 **Obsidian → 本机 PicGo → GitHub 图床**。本次故障发生在 PicGo 到 GitHub 的环节，但最终显示在 Obsidian 中。排查时应沿调用链查看上游日志，找到最先发生的错误，避免被后续的插件报错误导。