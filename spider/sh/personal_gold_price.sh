#!/bin/bash
# ---------------------------------------------
# 手动执行：爬取股市黄金金价，并写入日志文件
# ---------------------------------------------

# Python 路径（改成你的虚拟环境路径）
PYTHON_PATH="/home/ubuntu/pyenv/bin/python"

# Python 脚本路径
SCRIPT_PATH="/home/ubuntu/mnt/py/lxy8220/spider/personal_gold_spider.py"

# 日志文件夹路径
LOG_DIR="/home/ubuntu/mnt/py/lxy8220/spider/log"

# 当前日期（格式：2025-10-27）
DATE=$(date +"%Y-%m-%d")

# 执行 Python 脚本并输出日志
$PYTHON_PATH $SCRIPT_PATH >> "$LOG_DIR/tanaka_gold_spider_${DATE}.log" 2>&1