#!/bin/bash
# ---------------------------------------------
# 清理日志
# ---------------------------------------------

# 日志文件夹路径
LOG_DIR="/home/ubuntu/mnt/py/lxy8220/spider/log"

# 保存天数
KEEP_DAYS=7

echo "🧹 开始清理日志目录：$LOG_DIR"
echo "⏳ 保留最近 $KEEP_DAYS 天的日志文件..."

if [! - d "$LOG_DIR"]; then
  echo "⚠️ 日志目录不存在：$LOG_DIR"
  exit 1
fi

# 删除7天以前的日志文件
find "$LOG_DIR" -type f -name "*/log" -mtime +$KEEP_DAYS -exec rm -f {} /;

echo "✅ 日志清理完成。"