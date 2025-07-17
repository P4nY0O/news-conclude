"""Define a news scraping and summarization agent.

This module creates a specialized graph for scraping news from News Minimalist
and translating/summarizing the content into Chinese markdown files.
"""

import json
from typing import Any, Dict, List, Literal, Optional, cast
from datetime import datetime

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from enrichment_agent import prompts
from enrichment_agent.configuration import Configuration
from enrichment_agent.state import InputState, OutputState, State
from enrichment_agent.tools import scrape_news_minimalist, save_to_markdown
from enrichment_agent.utils import init_model


class NewsState(BaseModel):
    """State for news scraping and summarization."""
    
    messages: List[BaseMessage] = Field(default_factory=list)
    scraped_content: Optional[str] = None
    translated_summary: Optional[str] = None
    saved_file: Optional[str] = None
    error: Optional[str] = None


async def scrape_news(
    state: NewsState, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    """抓取News Minimalist网站的新闻内容。"""
    
    try:
        # 调用专门的新闻抓取工具
        scraped_content = await scrape_news_minimalist(state=state, config=config or {})
        
        return {
            "scraped_content": scraped_content,
            "messages": state.messages + [
                HumanMessage(content="请抓取News Minimalist网站的最新新闻"),
                AIMessage(content=f"已成功抓取新闻内容：\n{scraped_content[:200]}...")
            ]
        }
    except Exception as e:
        return {
            "error": f"抓取新闻时出错: {str(e)}",
            "messages": state.messages + [
                HumanMessage(content="请抓取News Minimalist网站的最新新闻"),
                AIMessage(content=f"抓取失败: {str(e)}")
            ]
        }


async def translate_and_summarize(
    state: NewsState, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    """翻译和汇总抓取的新闻内容。"""
    
    if not state.scraped_content:
        return {
            "error": "没有可翻译的内容",
            "messages": state.messages + [
                AIMessage(content="错误：没有抓取到新闻内容")
            ]
        }
    
    try:
        # 构建翻译和汇总提示
        translation_prompt = f"""
        请将以下从News Minimalist网站抓取的英文新闻内容翻译成中文，并进行汇总整理。
        
        要求：
        1. 准确翻译所有重要信息
        2. 保持新闻的客观性和准确性
        3. 按重要性排序
        4. 添加日期标记：{datetime.now().strftime('%Y年%m月%d日')}
        5. 使用Markdown格式输出
        6. 添加标题：今日新闻汇总
        
        原始内容：
        {state.scraped_content}
        """
        
        raw_model = init_model(config)
        result = await raw_model.ainvoke(translation_prompt)
        translated_summary = str(result.content)
        
        return {
            "translated_summary": translated_summary,
            "messages": state.messages + [
                AIMessage(content=f"翻译和汇总完成：\n{translated_summary[:200]}...")
            ]
        }
    except Exception as e:
        return {
            "error": f"翻译和汇总时出错: {str(e)}",
            "messages": state.messages + [
                AIMessage(content=f"翻译失败: {str(e)}")
            ]
        }


async def save_summary(
    state: NewsState, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    """保存汇总的新闻内容到Markdown文件。"""
    
    if not state.translated_summary:
        return {
            "error": "没有可保存的内容",
            "messages": state.messages + [
                AIMessage(content="错误：没有翻译后的内容可保存")
            ]
        }
    
    try:
        # 生成文件名
        today = datetime.now().strftime('%Y%m%d')
        filename = f"news_summary_{today}.md"
        
        # 保存到文件
        save_result = await save_to_markdown(
            content=state.translated_summary,
            filename=filename,
            state=state,
            config=config or {}
        )
        
        return {
            "saved_file": save_result,
            "messages": state.messages + [
                AIMessage(content=f"保存完成: {save_result}")
            ]
        }
    except Exception as e:
        return {
            "error": f"保存文件时出错: {str(e)}",
            "messages": state.messages + [
                AIMessage(content=f"保存失败: {str(e)}")
            ]
        }


def create_news_graph() -> Any:  # type: ignore
    """创建新闻抓取和汇总的图。"""
    
    # 创建图
    workflow = StateGraph(NewsState)
    
    # 添加节点
    workflow.add_node("scrape_news", scrape_news)
    workflow.add_node("translate_and_summarize", translate_and_summarize)
    workflow.add_node("save_summary", save_summary)
    
    # 设置入口点
    workflow.set_entry_point("scrape_news")
    
    # 添加边
    workflow.add_edge("scrape_news", "translate_and_summarize")
    workflow.add_edge("translate_and_summarize", "save_summary")
    workflow.add_edge("save_summary", "__end__")
    
    return workflow.compile()


# 创建图实例
news_graph = create_news_graph() 