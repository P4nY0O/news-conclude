#!/usr/bin/env python3
"""
定时新闻抓取和汇总脚本

这个脚本会定时运行新闻抓取任务，将News Minimalist的新闻翻译并保存为Markdown文件。
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


sys.path.insert(0, str(project_root))
from src.enrichment_agent.tools import scrape_news_minimalist_playwright, save_to_markdown
from src.enrichment_agent.configuration import Configuration


async def run_news_task():
    """运行新闻抓取和汇总任务。"""
    
    print(f"[{datetime.now()}] 开始执行新闻抓取任务...")
    
    try:
        # 创建配置
        config = Configuration()
        
        # 使用Playwright抓取新闻
        scraped_content = await scrape_news_minimalist_playwright(
            config={"configurable": {"model": config.model}}
        )
        
        if scraped_content.startswith("Error"):
            print(f"[{datetime.now()}] 抓取失败: {scraped_content}")
            return False
        
        # 保存到文件
        today = datetime.now().strftime('%Y%m%d')
        filename = f"今日新闻汇总_{today}.md"
        
        save_result = await save_to_markdown(
            content=scraped_content,
            filename=filename,
            state=None,
            config={"configurable": {"model": config.model}}
        )
        
        if "成功保存" in save_result:
            print(f"[{datetime.now()}] 任务执行成功: {save_result}")
            return True
        else:
            print(f"[{datetime.now()}] 保存失败: {save_result}")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] 任务执行出错: {str(e)}")
        return False


async def main():
    """主函数。"""
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    # 运行任务
    success = await run_news_task()
    
    if success:
        print(f"[{datetime.now()}] 新闻抓取任务完成")
    else:
        print(f"[{datetime.now()}] 新闻抓取任务失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 