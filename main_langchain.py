"""
Mini DeepResearch - 基于LangChain LCEL的研究助手
使用LCEL (LangChain Expression Language) 语法重构
"""

import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()


# ==================== 数据模型定义 ====================

class WebSearchItem(BaseModel):
    reason: str = Field(description="为什么这个搜索对查询很重要的理由")
    query: str = Field(description="用于网络搜索的搜索词")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="要执行的网络搜索列表")


class ReportData(BaseModel):
    short_summary: str = Field(description="研究结果的简短2-3句摘要")
    markdown_report: str = Field(description="最终报告（Markdown格式）")
    follow_up_questions: list[str] = Field(description="建议进一步研究的主题")


# ==================== LCEL 原子链 ====================

llm = ChatOpenAI(
    model="qwen-plus",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

search_tool = DuckDuckGoSearchResults(max_results=5)

planner_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是一个研究助手。根据用户的查询，生成一组网络搜索关键词来最好地回答查询。生成5到10个搜索词。"),
        ("human", "{query}"),
    ])
    | llm.with_structured_output(WebSearchPlan)
)

search_chain = (
    RunnablePassthrough.assign(
        search_results=RunnableLambda(lambda x: search_tool.invoke(x["query"]))
    )
    | ChatPromptTemplate.from_messages([
        ("system",
         "你是一个研究助手。根据给定的搜索词和搜索结果，生成简洁的摘要。"
         "摘要必须是2-3段，少于300字。捕捉要点，简洁地写。"
         "这将被综合报告的人使用，请捕捉本质并忽略任何冗余内容。"
         "不要包含除摘要本身之外的任何额外评论。"),
        ("human", "搜索词: {query}\n\n搜索结果:\n{search_results}"),
    ])
    | llm
)

_WRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "你是一位资深研究员，负责为研究查询撰写连贯的报告。"
     "你将获得原始查询和研究助手完成的一些初步研究。\n"
     "你应该首先为报告提出一个大纲，描述报告的结构和流程。"
     "然后，生成报告并将其作为最终输出返回。\n"
     "最终输出应为Markdown格式，并且应该详细且冗长。目标是10-20页的内容，至少1500字。"
     "最终结果请用中文输出。"),
    ("human", "原始查询: {query}\n\n研究结果:\n{research_results}"),
])

# 结构化输出链（正常路径）
writer_chain = _WRITER_PROMPT | llm.with_structured_output(ReportData)

# 纯文本链（降级路径：报告过长导致 JSON 截断时使用）
writer_chain_plain = _WRITER_PROMPT | llm


# ==================== 研究管理器 ====================

class ResearchManager:

    def __init__(self):
        print("初始化已完成，欢迎使用。使用前请确认相关模型能够被顺利调用。")

    async def run(self, query: str) -> None:
        print(f"Starting research for: {query}")

        search_plan    = await self._plan_searches(query)         # WebSearchPlan: 包含5-10个搜索词
        search_results = await self._perform_searches(search_plan) # list[str]: 每条搜索的摘要文本
        report         = await self._write_report(query, search_results) # ReportData: 最终结构化报告

        print("\n\n=====REPORT=====\n\n")
        print(report.markdown_report)   # Markdown 格式正文
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        for i, question in enumerate(report.follow_up_questions, 1):
            print(f"{i}. {question}")

        self._save_report(query, report.markdown_report)

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        print("\n[1/3] Planning searches...")
        try:
            plan = await planner_chain.ainvoke({"query": query})  # 结构化输出，直接得到 WebSearchPlan
            print(f"  Generated {len(plan.searches)} queries")
            return plan
        except Exception as e:
            print(f"  Planning failed ({e}), using fallback queries...")
            return WebSearchPlan(searches=[               # 兜底：手动构造5个固定搜索词
                WebSearchItem(reason="主要搜索", query=query),
                WebSearchItem(reason="最新进展", query=f"{query} 2026 最新"),
                WebSearchItem(reason="应用案例", query=f"{query} 案例"),
                WebSearchItem(reason="技术原理", query=f"{query} 技术"),
                WebSearchItem(reason="发展趋势", query=f"{query} 趋势"),
            ])

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        print("\n[2/3] Executing searches...")
        inputs = [{"query": item.query, "reason": item.reason} for item in search_plan.searches]  # search_chain 所需的入参格式
        results = await search_chain.abatch(
            inputs,
            config={"max_concurrency": 5},  # 最多5条并发，避免触发限流
            return_exceptions=True,          # 单条失败不中断整批
        )
        summaries = [r.content for r in results if not isinstance(r, Exception)]  # 过滤失败项，取摘要文本
        print(f"  {len(summaries)}/{len(inputs)} searches completed")
        return summaries

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        print("\n[3/3] Generating final report...")
        payload = {
            "query": query,
            "research_results": "\n\n---\n\n".join(search_results),  # 用分隔线拼接各条摘要
        }
        try:
            return await writer_chain.ainvoke(payload)
        except Exception as e:
            # 报告过长时 JSON 会被截断导致解析失败，降级为纯文本输出
            print(f"  Structured output failed ({type(e).__name__}), falling back to plain text...")
            response = await writer_chain_plain.ainvoke(payload)
            return ReportData(
                short_summary=f"关于「{query}」的研究报告",
                markdown_report=response.content,
                follow_up_questions=[],
            )

    def _save_report(self, query: str, markdown_content: str) -> None:
        folder_name = "research_reports"
        os.makedirs(folder_name, exist_ok=True)
        sanitized_query = query.replace(" ", "_").replace("：", "").replace("?", "").replace("？", "")  # 清理文件名非法字符
        file_name = f"{folder_name}/关于{sanitized_query}调研报告.md"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"\nReport saved to: {file_name}")


# ==================== 主程序 ====================

async def main():
    print("=" * 50)
    print("Mini DeepResearch - LangChain LCEL版本")
    print("=" * 50)

    manager = ResearchManager()
    await manager.run("AI在教育中的应用")


if __name__ == "__main__":
    asyncio.run(main())
