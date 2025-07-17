#!/usr/bin/env python3
"""
新闻抓取和汇总程序

这个脚本用于抓取News Minimalist网站的新闻，翻译并保存为Markdown文件。
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: python-dotenv 未安装，请手动设置环境变量")

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


sys.path.insert(0, str(project_root))
from src.enrichment_agent.tools import scrape_news_minimalist_playwright, save_to_markdown
from src.enrichment_agent.configuration import Configuration


async def run_news_task():
    """执行新闻抓取和汇总任务。"""
    
    print("开始执行新闻抓取任务...")
    
    # 创建配置
    config = Configuration()
    
    try:
        # 抓取新闻
        print("1. 抓取News Minimalist网站...")
        scraped_content = await scrape_news_minimalist_playwright(
            state=None,
            config={"configurable": {"model": config.model}}
        )
        
        if scraped_content and not scraped_content.startswith("Error"):
            print("✅ 新闻抓取成功")
            print(f"抓取内容长度: {len(scraped_content)} 字符")
            print(f"内容预览: {scraped_content[:200]}...")
        else:
            print("❌ 新闻抓取失败")
            print(f"错误信息: {scraped_content}")
            return False
        
        # 保存文件
        print("\n2. 保存到Markdown文件...")
        today = datetime.now().strftime('%Y%m%d')
        filename = f"今日新闻汇总.md"
        
        save_result = await save_to_markdown(
            content=scraped_content,
            filename=filename,
            state=None,
            config={"configurable": {"model": config.model}}
        )
        
        if "成功保存" in save_result:
            print("✅ 文件保存成功")
            print(f"保存结果: {save_result}")
        else:
            print("❌ 文件保存失败")
            print(f"错误信息: {save_result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False


async def main():
    """主函数。"""
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("请在 .env 文件中添加 DEEPSEEK_API_KEY")
        return
    
    # 运行任务
    success = await run_news_task()
    
    if success:
        print("\n✅ 新闻抓取任务完成")
    else:
        print("\n❌ 新闻抓取任务失败，请检查配置和网络连接")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 