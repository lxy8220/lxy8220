#!/bin/bash
# ---------------------------------------------
# 手动执行：爬取田中贵金属金价，并写入日志文件
# ---------------------------------------------

# Python 路径（改成你的虚拟环境路径）
PYTHON_PATH="/home/ubuntu/pyenv/bin/python"

# Python 脚本路径
SCRIPT_PATH="/home/ubuntu/mnt/py/lxy8220/spider/tanaka_gold_price.py"

# 日志文件夹路径
LOG_DIR="/home/ubuntu/mnt/py/lxy8220/spider/log"

# 当前日期（格式：2025-10-27）
DATE=$(date +"%Y-%m-%d")

# 创建日志文件名
LOG_FILE="${LOG_DIR}/tanaka_gold_price_${DATE}.log"

# 当前时间（小时和分钟）
HOUR=$(date +%H)
MINUTE=$(date +%M)

if [[ ("$HOUR" == "09" && "$MINUTE" == "30") || ("$HOUR" == "14" && "$MINUTE" == "00") ]]; then
  # 执行 Python 脚本并输出日志
  $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1
fi


