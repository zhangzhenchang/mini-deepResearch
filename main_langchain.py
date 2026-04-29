"""
Mini DeepResearch - 基于LangChain的研究助手
使用LangChain重构，支持阿里云百炼等国内模型
"""

import asyncio
import os
import json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.tools import DuckDuckGoSearchResults

# 加载环境变量
load_dotenv()


# ==================== 数据模型定义 ====================

class WebSearchItem(BaseModel):
    """单个网络搜索项"""
    reason: str = Field(description="为什么这个搜索对查询很重要的理由")
    query: str = Field(description="用于网络搜索的搜索词")


class WebSearchPlan(BaseModel):
    """网络搜索计划"""
    searches: List[WebSearchItem] = Field(description="要执行的网络搜索列表")


class ReportData(BaseModel):
    """研究报告数据"""
    short_summary: str = Field(description="研究结果的简短2-3句摘要")
    markdown_report: str = Field(description="最终报告（Markdown格式）")
    follow_up_questions: List[str] = Field(description="建议进一步研究的主题")


# ==================== LangChain组件初始化 ====================

# 初始化LLM（支持阿里云百炼）
llm = ChatOpenAI(
    model="qwen-plus",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
)

# 初始化搜索工具
search_tool = DuckDuckGoSearchResults(max_results=5)


# ==================== Agent链定义 ====================

# 1. 规划Agent - 生成搜索计划
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个研究助手。根据用户的查询，生成一组网络搜索关键词来最好地回答查询。
    生成5到10个搜索词。

    重要：你必须只返回纯JSON格式，不要有任何其他文字说明。
    JSON格式如下：
    {{"searches": [{{"reason": "搜索理由", "query": "搜索关键词"}}, {{"reason": "搜索理由2", "query": "搜索关键词2"}}]}}
    """),
    ("user", "{query}")
])

# 不使用JsonOutputParser，改用普通解析
planner_chain = planner_prompt | llm


# 2. 搜索Agent - 执行搜索并总结
search_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个研究助手。根据给定的搜索词，总结搜索结果。
    总结必须是2-3段，少于300字。捕捉要点。简洁地写，不需要完整的句子或良好的语法。
    这将被综合报告的人使用，所以你必须捕捉本质并忽略任何冗余内容。
    不要包含除摘要本身之外的任何额外评论。"""),
    ("user", "搜索词: {query}\n\n搜索结果:\n{search_results}")
])

search_chain = search_prompt | llm


# 3. 写作Agent - 生成最终报告
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深研究员，负责为研究查询撰写连贯的报告。
    你将获得原始查询和研究助手完成的一些初步研究。

    你应该首先为报告提出一个大纲，描述报告的结构和流程。
    然后，生成报告并将其作为最终输出返回。

    最终输出应为Markdown格式，并且应该详细且冗长。目标是10-20页的内容，至少1500字。
    最终结果请用中文输出。

    重要：你必须只返回纯JSON格式，不要有任何其他文字说明。
    JSON格式如下：
    {{"short_summary": "简短摘要", "markdown_report": "完整报告", "follow_up_questions": ["问题1", "问题2"]}}
    """),
    ("user", "原始查询: {query}\n\n研究结果:\n{research_results}")
])

# 不使用JsonOutputParser，改用普通解析
writer_chain = writer_prompt | llm


# ==================== 研究管理器 ====================

class ResearchManager:
    """管理整个研究流程"""

    def __init__(self):
        self.planner = planner_chain
        self.searcher = search_chain
        self.writer = writer_chain
        self.search_tool = search_tool

    async def run(self, query: str):
        """执行完整的研究流程"""
        print(f"Starting research for: {query}")

        # 步骤1: 规划搜索
        print("\n[1/3] Planning searches...")
        try:
            response = await self.planner.ainvoke({"query": query})
            # 手动解析JSON
            content = response.content
            print(f"Raw response: {content[:200]}...")

            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                search_plan = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")

            print(f"Generated {len(search_plan['searches'])} search queries")
        except Exception as e:
            print(f"Error in planning: {e}")
            # 如果JSON解析失败，使用备用方案
            print("Using fallback: generating simple search queries...")
            search_plan = {
                "searches": [
                    {"reason": "主要搜索", "query": query},
                    {"reason": "最新进展", "query": f"{query} 2026 最新"},
                    {"reason": "应用案例", "query": f"{query} 案例"},
                    {"reason": "技术原理", "query": f"{query} 技术"},
                    {"reason": "发展趋势", "query": f"{query} 趋势"},
                ]
            }

        # 步骤2: 执行搜索并总结
        print("\n[2/3] Executing searches...")
        research_results = []

        for i, search_item in enumerate(search_plan["searches"][:5]):  # 限制为5个搜索
            search_query = search_item["query"]
            print(f"  Searching ({i+1}/5): {search_query}")

            try:
                # 执行搜索
                search_results = self.search_tool.invoke(search_query)

                # 总结搜索结果
                summary = await self.searcher.ainvoke({
                    "query": search_query,
                    "search_results": search_results
                })

                research_results.append({
                    "query": search_query,
                    "summary": summary.content
                })
            except Exception as e:
                print(f"    Error searching '{search_query}': {e}")
                continue

        # 步骤3: 生成最终报告
        print("\n[3/3] Generating final report...")
        research_text = "\n\n".join([
            f"## 搜索: {r['query']}\n{r['summary']}"
            for r in research_results
        ])

        try:
            response = await self.writer.ainvoke({
                "query": query,
                "research_results": research_text
            })

            # 手动解析JSON
            content = response.content
            print(f"Writer response length: {len(content)} chars")

            # 清理控制字符
            import re
            content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)

            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                report = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in writer response")

            # 保存报告
            self._save_report(query, report)

            print("\n" + "="*50)
            print("Research Complete!")
            print("="*50)
            print(f"\n摘要: {report['short_summary']}")
            print(f"\n后续问题:")
            for q in report.get('follow_up_questions', []):
                print(f"  - {q}")

        except Exception as e:
            print(f"Error generating report: {e}")
            # 备用方案：直接保存研究结果
            print("Saving research results as fallback...")
            fallback_report = {
                "short_summary": f"关于'{query}'的研究结果",
                "markdown_report": f"# {query}\n\n{research_text}",
                "follow_up_questions": []
            }
            self._save_report(query, fallback_report)

    def _save_report(self, query: str, report: dict):
        """保存报告到文件"""
        # 创建文件夹
        folder_name = "research_reports"
        os.makedirs(folder_name, exist_ok=True)

        # 生成文件名
        sanitized_query = query.replace(" ", "_").replace("：", "").replace("?", "").replace("？", "")
        file_name = f"{folder_name}/关于{sanitized_query}调研报告.md"

        # 写入文件
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(report["markdown_report"])

        print(f"\nReport saved to: {file_name}")


# ==================== 主程序 ====================

async def main():
    """主函数"""
    print("="*50)
    print("Mini DeepResearch - LangChain版本")
    print("="*50)

    # 创建研究管理器
    manager = ResearchManager()

    # 示例查询
    test_query = "AI在教育中的应用"

    # 执行研究
    await manager.run(test_query)


if __name__ == "__main__":
    asyncio.run(main())

