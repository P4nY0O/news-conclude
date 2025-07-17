# 快速开始指南

## 1. 安装依赖

```bash
# 进入项目目录
cd news-conclude-app

# 安装Python依赖
pip install -e .

# 安装额外依赖
pip install beautifulsoup4 aiohttp
```

## 2. 配置API密钥

创建 `.env` 文件：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加以下内容：
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 3. 测试功能

```bash
# 运行测试脚本
python test_news.py
```

## 4. 手动运行

```bash
# 运行新闻抓取任务
python scheduler.py
```

## 5. 设置定时任务

```bash
# 设置每天上午9点自动运行
./setup_cron.sh
```

## 6. 查看结果

抓取的新闻文件保存在 `news_outputs/` 目录中：

```bash
# 查看最新生成的新闻文件
ls -la news_outputs/

# 查看文件内容
cat news_outputs/news_summary_$(date +%Y%m%d).md
```

## 常见问题

### Q: 提示找不到模块？
A: 确保已经运行了 `pip install -e .`

### Q: API密钥错误？
A: 检查 `.env` 文件中的API密钥是否正确设置

### Q: 网络连接问题？
A: 确保可以访问 `https://www.newsminimalist.com/`

### Q: 权限问题？
A: 运行 `chmod +x setup_cron.sh` 给脚本执行权限

## 自定义配置

### 修改抓取时间
编辑 `setup_cron.sh` 中的cron表达式：
- `0 9 * * *` = 每天上午9点
- `0 14 * * *` = 每天下午2点
- `0 */6 * * *` = 每6小时一次

### 修改输出目录
编辑 `src/enrichment_agent/tools.py` 中的 `output_dir` 变量。

### 修改翻译语言
编辑 `src/enrichment_agent/tools.py` 中的翻译提示词。 