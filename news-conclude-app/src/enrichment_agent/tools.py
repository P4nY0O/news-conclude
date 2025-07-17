"""Tools for data enrichment.

This module contains functions that are directly exposed to the LLM as tools.
These tools can be used for tasks such as web searching and scraping.
Users can edit and extend these tools as needed.
"""

import json
from typing import Any, Optional, cast
from datetime import datetime
import os

import aiohttp
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from bs4 import BeautifulSoup

from enrichment_agent.configuration import Configuration
from enrichment_agent.state import State
from enrichment_agent.utils import init_model


async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Query a search engine.

    This function queries the web to fetch comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events. Provide as much context in the query as needed to ensure high recall.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)


_INFO_PROMPT = """You are doing web research on behalf of a user. You are trying to find out this information:

<info>
{info}
</info>

You just scraped the following website: {url}

Based on the website content below, jot down some notes about the website.

<Website content>
{content}
</Website content>"""


async def scrape_website(
    url: str,
    *,
    state: Annotated[State, InjectedState],
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    """Scrape and summarize content from a given URL.

    Returns:
        str: A summary of the scraped content, tailored to the extraction schema.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()

    p = _INFO_PROMPT.format(
        info=json.dumps(state.extraction_schema, indent=2),
        url=url,
        content=content[:40_000],
    )
    raw_model = init_model(config)
    result = await raw_model.ainvoke(p)
    return str(result.content)


async def scrape_news_minimalist(
    *,
    state: Any,
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    """专门抓取News Minimalist网站的最新新闻并翻译汇总。
    
    Returns:
        str: 抓取到的新闻内容的中文翻译和汇总
    """
    url = "https://www.newsminimalist.com/"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return f"Error: Failed to fetch {url}, status code: {response.status}"
                
                content = await response.text()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # 提取新闻内容（根据网站结构调整选择器）
        news_items = []
        
        # 尝试不同的选择器来找到新闻内容
        selectors = [
            'article',  # 文章标签
            '.post',    # 文章类
            '.news-item', # 新闻项类
            '.entry',   # 条目类
            'h1, h2, h3', # 标题
            '.content', # 内容类
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:  # 移除数量限制
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:  # 过滤太短的内容
                        news_items.append(text)
                break
        
        if not news_items:
            # 如果上面的选择器都没找到，尝试获取所有文本
            news_items = [soup.get_text(strip=True)[:5000]]
        
        # 构建翻译和汇总提示
        translation_prompt = f"""
        请将以下从News Minimalist网站抓取的英文新闻内容翻译成中文，并进行汇总整理。
        要求：
        1. 准确翻译所有重要信息
        2. 保持新闻的客观性和准确性
        3. 按重要性排序
        4. 添加日期标记：{datetime.now().strftime('%Y年%m月%d日')}
        5. 输出所有重要新闻，不要限制数量
        6. 使用Markdown格式，包含标题、来源、摘要等
        
        原始内容：
        {chr(10).join(news_items)}  # 输出所有抓取的新闻
        """
        
        raw_model = init_model(config)
        result = await raw_model.ainvoke(translation_prompt)
        
        return str(result.content)
        
    except Exception as e:
        return f"Error scraping News Minimalist: {str(e)}"


async def save_to_markdown(
    content: str,
    filename: str = "",
    *,
    state: Any,
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    """将汇总的新闻内容保存到Markdown文件。
    
    Args:
        content: 要保存的内容
        filename: 文件名，如果不提供则使用默认格式
    
    Returns:
        str: 保存结果信息
    """
    if not filename:
        today = datetime.now().strftime('%Y%m%d')
        filename = f"news_summary_{today}.md"
    
    # 确保输出目录存在
    output_dir = os.path.expanduser("~/Desktop")
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"成功保存到文件: {filepath}"
    except Exception as e:
        return f"保存文件时出错: {str(e)}"

# 新增：Playwright抓取工具
import asyncio
from typing import Optional

async def scrape_news_minimalist_playwright(
    *,
    state: Optional[State] = None,
    config: Optional[RunnableConfig] = None,
) -> str:
    """使用Playwright模拟浏览器抓取News Minimalist首页内容并提取新闻文本。"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return "Error: playwright未安装，请先运行 pip install playwright && playwright install"

    url = "https://www.newsminimalist.com/"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            page = await browser.new_page()
            # 设置更长的超时时间和更宽松的等待条件
            await page.goto(url, timeout=120000, wait_until='domcontentloaded')
            # 等待页面基本加载完成
            try:
                await page.wait_for_load_state('networkidle', timeout=60000)
            except:
                # 如果网络空闲等待失败，至少等待DOM加载
                await page.wait_for_load_state('domcontentloaded', timeout=30000)
            # 尝试提取主要内容
            # 先抓取所有文章标签
            articles = await page.query_selector_all('article')
            news_items = []
            for article in articles:  # 移除数量限制
                text = await article.inner_text()
                if text and len(text) > 20:
                    news_items.append(text.strip())
            # 如果没抓到，退而求其次抓body文本
            if not news_items:
                body = await page.query_selector('body')
                if body:
                    news_items = [(await body.inner_text())[:10000]]  # 增加到10000字符
            await browser.close()
        if not news_items:
            return "Error: 未能提取到新闻内容"
        # 构建翻译和汇总提示
        translation_prompt = f"""
        请将以下从News Minimalist网站抓取的英文新闻内容翻译成中文，并进行汇总整理。
        要求：
        1. 准确翻译所有重要信息
        2. 保持新闻的客观性和准确性
        3. 按重要性排序,每条新闻注明时间
        4. 添加日期标记：{datetime.now().strftime('%Y年%m月%d日')}
        5. 输出所有重要新闻，不要限制数量
        6. 使用Markdown格式，包含标题、来源、摘要等,开头不要加```markdown
        
        原始内容：
        {chr(10).join(news_items)}  # 输出所有抓取的新闻
        """
        raw_model = init_model(config)
        result = await raw_model.ainvoke(translation_prompt)
        return str(result.content)
    except Exception as e:
        return f"Error scraping News Minimalist with Playwright: {str(e)}"
