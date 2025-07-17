# News Minimalist 新闻抓取和汇总系统

这是一个基于LangGraph的自动化新闻抓取和汇总系统，专门用于从 [News Minimalist](https://www.newsminimalist.com/) 网站抓取新闻，翻译成中文并保存为Markdown文件。

## 功能特性

- 🔍 **自动抓取**: 定时从News Minimalist网站抓取最新新闻
- 🌐 **智能翻译**: 使用AI模型将英文新闻翻译成中文
- 📝 **结构化输出**: 生成格式化的Markdown文档
- ⏰ **定时任务**: 支持crontab定时执行
- 📊 **日志记录**: 完整的执行日志和错误追踪

## 安装和配置

### 1. 安装依赖

```bash
# 进入项目目录
cd news-conclude-app

# 安装Python依赖
pip install -e .
```

### 2. 配置环境变量

创建 `.env` 文件并添加API密钥：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加以下内容：
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 3. 设置定时任务

```bash
# 给脚本执行权限
chmod +x setup_cron.sh

# 运行设置脚本
./setup_cron.sh
```

这将设置每天上午9点自动运行新闻抓取任务。

## 使用方法

### 手动运行

```bash
# 直接运行新闻抓取任务
python scheduler.py
```

### 查看输出

抓取的新闻文件保存在 `news_outputs/` 目录中，文件名格式为：
- `news_summary_YYYYMMDD.md` (例如: `news_summary_20241201.md`)

### 查看日志

```bash
# 查看定时任务日志
tail -f news_outputs/cron.log
```

## 项目结构

```
news-conclude-app/
├── src/enrichment_agent/
│   ├── tools.py              # 工具函数（包含新闻抓取工具）
│   ├── news_graph.py         # 新闻抓取专用图
│   └── ...
├── scheduler.py              # 定时任务脚本
├── setup_cron.sh            # 定时任务设置脚本
├── news_outputs/            # 输出目录
│   ├── news_summary_*.md    # 生成的新闻文件
│   └── cron.log             # 定时任务日志
└── NEWS_README.md           # 本文件
```

## 自定义配置

### 修改抓取时间

编辑 `setup_cron.sh` 文件中的cron表达式：

```bash
# 当前设置：每天上午9点
CRON_JOB="0 9 * * * cd $SCRIPT_DIR && $PYTHON_PATH $PYTHON_SCRIPT >> $SCRIPT_DIR/news_outputs/cron.log 2>&1"

# 例如：每天下午2点
CRON_JOB="0 14 * * * cd $SCRIPT_DIR && $PYTHON_PATH $PYTHON_SCRIPT >> $SCRIPT_DIR/news_outputs/cron.log 2>&1"
```

### 修改输出格式

编辑 `src/enrichment_agent/tools.py` 中的 `scrape_news_minimalist` 函数来调整翻译和汇总的格式。

### 修改抓取网站

编辑 `src/enrichment_agent/tools.py` 中的URL：

```python
url = "https://www.newsminimalist.com/"  # 修改为其他网站
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 确保在 `.env` 文件中正确设置了API密钥
   - 检查API密钥是否有效且有足够的配额

2. **网络连接问题**
   - 检查网络连接是否正常
   - 确保可以访问目标网站

3. **权限问题**
   - 确保脚本有执行权限：`chmod +x setup_cron.sh`
   - 确保有写入 `news_outputs/` 目录的权限

4. **依赖问题**
   - 重新安装依赖：`pip install -e .`
   - 检查Python版本（需要3.9+）

### 查看详细日志

```bash
# 查看完整的crontab日志
cat news_outputs/cron.log

# 查看系统cron日志
sudo tail -f /var/log/cron
```

## 开发

### 添加新功能

1. 在 `src/enrichment_agent/tools.py` 中添加新的工具函数
2. 在 `src/enrichment_agent/news_graph.py` 中修改图结构
3. 更新 `scheduler.py` 中的逻辑

### 测试

```bash
# 运行测试
python -m pytest tests/

# 手动测试新闻抓取
python scheduler.py
```

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！ 