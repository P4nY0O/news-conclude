#!/bin/bash

# 设置定时任务脚本
# 这个脚本会设置每天定时运行新闻抓取任务

echo "设置定时新闻抓取任务..."

# 获取当前脚本的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/scheduler.py"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: 找不到 scheduler.py 文件"
    exit 1
fi

# 获取Python解释器路径
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "错误: 找不到 python3"
    exit 1
fi

# 创建临时crontab文件
TEMP_CRON=$(mktemp)

# 导出当前crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# 添加新的定时任务（每3小时运行一次）
# 格式: 分钟 小时 日 月 星期 命令
CRON_JOB="0 */3 * * * cd $SCRIPT_DIR && $PYTHON_PATH $PYTHON_SCRIPT > /dev/null 2>&1"

# 检查是否已经存在相同的任务
if grep -q "$PYTHON_SCRIPT" "$TEMP_CRON"; then
    echo "定时任务已存在，跳过添加"
else
    echo "$CRON_JOB" >> "$TEMP_CRON"
    echo "已添加定时任务: 每3小时运行一次新闻抓取"
fi

# 安装新的crontab
crontab "$TEMP_CRON"

# 清理临时文件
rm "$TEMP_CRON"

echo "定时任务设置完成！"
echo "任务将每3小时自动运行一次（0:00, 3:00, 6:00, 9:00, 12:00, 15:00, 18:00, 21:00）"
echo ""
echo "查看当前crontab:"
crontab -l 