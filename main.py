"""
Mini DeepResearch - 基于OpenAI Agents SDK的研究助手
从零到一快速搭建Mini DeepResearch系统
"""

import asyncio
import os
import time
from pydantic import BaseModel
from agents import Agent, WebSearchTool, Runner
from agents.model_settings import ModelSettings


# ==================== 数据模型定义 ====================

class WebSearchItem(BaseModel):
    """单个网络搜索项"""
    reason: str
    """为什么这个搜索对查询很重要的理由"""

    query: str
    """用于网络搜索的搜索词"""


class WebSearchPlan(BaseModel):
    """网络搜索计划"""
    searches: list[WebSearchItem]
    """要执行的网络搜索列表，以最好地回答查询"""


class ReportData(BaseModel):
    """研究报告数据"""
    short_summary: str
    """研究结果的简短2-3句摘要"""

    markdown_report: str
    """最终报告（Markdown格式）"""

    follow_up_questions: list[str]
    """建议进一步研究的主题"""


# ==================== Agent定义 ====================

# 1. 规划Agent - 负责生成搜索计划
PLANNER_PROMPT = (
    "You are a helpful research assistant. Given a query, come up with a set of web searches "
    "to perform to best answer the query. Output between 10 and 20 terms to query for."
)

planner_agent = Agent(
    name="PlannerAgent",
    instructions=PLANNER_PROMPT,
    model="o4-mini",
    output_type=WebSearchPlan,
)


# 2. 搜索Agent - 负责执行网络搜索并总结结果
SEARCH_INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary "
    "itself."
)

search_agent = Agent(
    name="SearchAgent",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool()],
    model_settings=ModelSettings(tool_choice="required"),
)


# 3. 写作Agent - 负责综合搜索结果并生成最终报告
WRITER_PROMPT = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research "
    "assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 10-20 pages of content, at least 1500 words."
    "最终结果请用中文输出。"
)

writer_agent = Agent(
    name="WriterAgent",
    instructions=WRITER_PROMPT,
    model="o4-mini",
    output_type=ReportData,
)


# ==================== 研究管理器 ====================

class ResearchManager:
    """研究管理器 - 协调整个研究流程"""

    def __init__(self):
        print("初始化已完成，欢迎使用。使用前请确认相关模型能够被顺利调用。")

    async def run(self, query: str) -> None:
        """
        执行完整的研究流程

        Args:
            query: 研究查询��题
        """
        print("Starting research...")

        # 步骤1: 使用planner_agent生成搜索计划
        search_plan = await self._plan_searches(query)

        # 步骤2: 使用search_agent执行搜索
        search_results = await self._perform_searches(search_plan)

        # 步骤3: 使用writer_agent撰写最终报告
        report = await self._write_report(query, search_results)

        # 打印最终报告
        print("\n\n=====REPORT=====\n\n")
        print(report.markdown_report)
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        for i, question in enumerate(report.follow_up_questions, 1):
            print(f"{i}. {question}")

        # 保存为Markdown文件
        self.save_report_as_md(query, report.markdown_report)

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        """生成搜索计划"""
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        return result.final_output_as(WebSearchPlan)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """并发执行所有搜索"""
        print("Starting searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
        results = []

        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")

        return results

    async def _search(self, item: WebSearchItem) -> str | None:
        """执行单个搜索"""
        print(f"Search term: {item.query}\nReason for searching: {item.reason}")
        try:
            result = await Runner.run(
                search_agent,
                input=f"Search term: {item.query}\nReason for searching: {item.reason}"
            )
            return str(result.final_output)
        except Exception as e:
            print(f"Search failed: {e}")
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        """生成最终报告"""
        print("Thinking about report...")
        print(f"Original query: {query}\nSummarized search results: {len(search_results)} results")

        result = await Runner.run(
            writer_agent,
            input=f"Original query: {query}\nSummarized search results: {search_results}",
        )

        return result.final_output_as(ReportData)

    def save_report_as_md(self, query: str, markdown_content: str) -> None:
        """
        保存生成的报告为Markdown文件

        Args:
            query: 原始查询
            markdown_content: Markdown格式的报告内容
        """
        # 创建文件夹（如果不存在）
        folder_name = "research_reports"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # 使用用户的查询作为文件名
        sanitized_query = query.replace(" ", "_").replace("：", "").replace("?", "").replace("？", "")
        file_name = f"{folder_name}/关于{sanitized_query}调研报告.md"

        # 写入Markdown文件
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(markdown_content)

        print(f"\nReport saved as: {file_name}")


# ==================== 主程序 ====================

async def main():
    """主函数"""
    # 创建研究管理器
    manager = ResearchManager()

    # 示例查询
    test_query = "AI在教育中的应用"

    # 执行研究
    await manager.run(test_query)


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
