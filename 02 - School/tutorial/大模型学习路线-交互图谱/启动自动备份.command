#!/bin/bash
# 大模型学习路线-交互图谱 · 自动备份服务
# 双击运行：启动 / 重启后台备份服务，并打印当前状态
PLIST="$HOME/Library/LaunchAgents/local.llmatlas.autosave.plist"
LABEL="local.llmatlas.autosave"
UID_NUM=$(id -u)

echo "== 自动备份服务 =="
if [ ! -f "$PLIST" ]; then
  echo "找不到 $PLIST，自动备份没有安装。"
  echo "请把 大模型学习路线-交互图谱 文件夹发给安装者重新部署。"
  read -r -p "按回车关闭…" _
  exit 1
fi

if launchctl print "gui/$UID_NUM/$LABEL" >/dev/null 2>&1; then
  launchctl kickstart -k "gui/$UID_NUM/$LABEL"
else
  launchctl bootstrap "gui/$UID_NUM" "$PLIST"
  launchctl enable "gui/$UID_NUM/$LABEL" 2>/dev/null || true
fi

sleep 1.5
if curl -fsS --max-time 3 http://127.0.0.1:8765/ping; then
  echo
  echo "服务已就绪：回到页面看侧栏底部应显示「自动备份 · 已保存 HH:MM:SS」。"
else
  echo
  echo "启动失败，日志：$HOME/Library/Application Support/LLMAtlasAutoSave/autosave.log"
fi
read -r -p "按回车关闭…" _
