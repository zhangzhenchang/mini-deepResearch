# 从零到一快速实现 Mini DeepResearch 🔍

> 本文将带你用 **LangChain + 阿里云通义千问** 从零搭建一个具备"规划 → 搜索 → 报告"能力的 Mini DeepResearch 系统，全程代码可运行。

---

## 一、什么是 Deep Research？

OpenAI 于 2025 年初推出了 ChatGPT 的全新功能——**Deep Research（深度研究）**，这是一项革命性的 AI 代理能力，旨在帮助用户高效完成复杂的研究任务。通过自动化的信息搜集、分析和报告生成，Deep Research 能在短时间内完成原本需要数小时甚至数天的工作，极大地提升了知识工作的效率和质量。

**Deep Research** 的核心优势包括：

- 🧠 **多步骤推理与信息整合**：利用最新的 OpenAI o3 模型，从多个来源收集信息，深入分析，整合成结构化报告
- 🤖 **自动化研究流程**：用户只需提出研究主题，AI 自动规划步骤、执行搜集与分析，生成详尽报告
- 📎 **引用来源明确**：报告中包含清晰的引用来源，便于验证和进一步阅读
- 📁 **支持文件上传**：用户可上传文档或数据表格，AI 结合这些信息进行更精准的分析
- 🌍 **适用多种领域**：市场调研、政策分析、科学研究、个人决策支持，均可胜任

---

## 二、DeepSearch vs DeepResearch，傻傻分不清？🤔

很多人容易把 **DeepSearch** 和 **DeepResearch** 混为一谈。但它们解决的是完全不同的问题——**DeepSearch 是 DeepResearch 的构建模块，是后者赖以运转的核心引擎。**

### DeepSearch

DeepSearch 的核心理念是：**在搜索、阅读和推理三个环节中不断循环往复，直到找到最优答案。**

可以把它理解为一个配备了各类网络工具（搜索引擎、网页阅读器）的 LLM Agent。这个 Agent 通过分析当前的观察结果和过往操作记录，来决定下一步行动：是直接给出答案，还是继续在网络上探索。这构建了一种**状态机架构**，其中 LLM 负责控制状态间的转换。

```
[搜索] → [阅读] → [推理] → 是否满足? → 否 → [搜索] → ...
                                        ↓ 是
                                      [输出答案]
```

### DeepResearch

DeepResearch 是在 DeepSearch 的基础上，**增加了一个结构化框架，用于生成长篇研究报告**。

它的工作流程：
1. 创建报告目录（大纲）
2. 对每个章节，系统性地调用 DeepSearch 搜集对应内容
3. 从引言 → 相关工作 → 方法论 → 结论，逐章生成
4. 将所有章节整合到一个提示词中，提升报告整体连贯性

```
[大纲规划]
    ↓
[章节1: DeepSearch] → [章节2: DeepSearch] → ... → [章节N: DeepSearch]
    ↓
[整合所有章节 → 最终报告]
```

---

## 三、动手实现！Mini DeepResearch 🚀

### 3.1 目标

构建一个"研究型助手"，可以：

1. 接收一个研究主题（如"AI 对教育的影响"）
2. 自动规划应该搜索的子问题 / 关键词
3. 每个关键词在网上搜索信息并摘要
4. 把多个摘要汇总成一份**完整的研究报告**

这是一个具备「规划能力 + 工具调用 + 总结归纳」的完整 Agent 系统。

### 3.2 项目架构

整个系统由三个核心 Agent 组成，线性串联：

```
用户查询
    ↓
planner_agent（规划搜索词）
    ↓ 生成 5-10 个搜索词
search_agent（并发执行搜索）× N
    ↓ 每条搜索生成 300 字内摘要
writer_agent（综合撰写报告）
    ↓
Markdown 研究报告
```

| Agent 名 | 职责 |
|----------|------|
| `planner_agent` | 生成研究关键词和搜索策略 |
| `search_agent` | 执行网络搜索 + 总结内容 |
| `writer_agent` | 汇总所有搜索结果，编写报告 |

技术选型：
- **框架**：LangChain（LCEL 语法）
- **模型**：阿里云通义千问 `qwen-plus`（OpenAI 兼容接口）
- **搜索**：DuckDuckGo（`ddgs` 包）
- **包管理**：`uv`

### 3.3 环境准备

**安装依赖**（`pyproject.toml` 已配置好）：

```bash
uv sync
```

**配置 `.env`**：

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

可以用内置的环境检查脚本验证配置是否正确：

```bash
uv run test_setup.py
```

`test_setup.py` 会依次检查 Python 版本（需 ≥ 3.10）、依赖包安装情况、API Key 和 Base URL 是否设置，以及核心文件是否存在，全部通过后方可运行主程序。

---

## 四、核心代码详解 💻

### 4.1 数据结构定义

在写 Agent 之前，先用 **Pydantic** 定义好三个数据模型，让 LLM 的输出有明确的结构约束：

```python
from pydantic import BaseModel, Field

# 单条搜索建议
class WebSearchItem(BaseModel):
    reason: str = Field(description="为什么这个搜索对查询很重要的理由")
    query: str  = Field(description="用于网络搜索的搜索词")

# 完整搜索计划：包含若干条搜索建议
class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="要执行的网络搜索列表")

# 最终报告结构
class ReportData(BaseModel):
    short_summary: str            = Field(description="研究结果的简短2-3句摘要")
    markdown_report: str          = Field(description="最终报告（Markdown格式）")
    follow_up_questions: list[str] = Field(description="建议进一步研究的主题")
```

`WebSearchItem` 包含两个字段：

| 字段 | 说明 |
|------|------|
| `reason` | 为什么搜索这个关键词（解释搜索动机） |
| `query` | 要搜索的关键词本身 |

### 4.2 LLM 初始化

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),  # 阿里云兼容接口
)
```

通过设置 `base_url`，无需改任何框架代码，直接把请求打到阿里云百炼平台。

### 4.3 Planner Agent

Planner Agent 的职责：**接收研究主题，生成一份"搜索计划（`WebSearchPlan`）"，告诉系统应该搜索哪些子问题 / 关键词及搜索理由。**

```python
planner_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是一个研究助手。根据用户的查询，生成一组网络搜索关键词来最好地回答查询。生成5到10个搜索词。"),
        ("human", "{query}"),
    ])
    | llm.with_structured_output(WebSearchPlan)  # ← 直接输出 Pydantic 对象，无需手动解析 JSON
)
```

`with_structured_output(WebSearchPlan)` 是关键：它把 Pydantic 模型的字段结构传递给 LLM，让模型按固定格式输出，**省去手动解析 JSON 的步骤**，直接返回 `WebSearchPlan` 对象。

调用时加了兜底逻辑，模型失败时自动构造5个默认搜索词：

```python
async def _plan_searches(self, query: str) -> WebSearchPlan:
    try:
        plan = await planner_chain.ainvoke({"query": query})  # 结构化输出，直接得到 WebSearchPlan
        return plan
    except Exception as e:
        return WebSearchPlan(searches=[               # 兜底：手动构造5个固定搜索词
            WebSearchItem(reason="主要搜索", query=query),
            WebSearchItem(reason="最新进展", query=f"{query} 2026 最新"),
            WebSearchItem(reason="应用案例", query=f"{query} 案例"),
            ...
        ])
```

### 4.4 Search Agent 🔍

`search_agent` 是整个系统中真正"去网上查资料"的角色。它接收一个搜索关键词，调用 DuckDuckGo 搜索，然后生成一份**简洁摘要（2-3 段，< 300 字），不带评论，只保留信息本身**。

搜索工具用的是 `ddgs`（DuckDuckGo 搜索的新包名）：

```python
from langchain_community.tools import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults(max_results=5)
```

> 💡 也可以换用**博查 API**，免费资源包提供 1000 次查询，DeepSeek 官方使用的就是这个：[bocha.cn](https://bocha.cn/)

Search Agent 的 LCEL 链定义：

```python
search_chain = (
    RunnablePassthrough.assign(                         # 保留原有字段，追加新字段
        search_results=RunnableLambda(                  # 新增 search_results 字段
            lambda x: search_tool.invoke(x["query"])   # 执行搜索（同步调用自动放入线程池）
        )
    )
    | ChatPromptTemplate.from_messages([
        ("system",
         "你是一个研究助手。根据给定的搜索词和搜索结果，生成简洁的摘要。"
         "摘要必须是2-3段，少于300字。捕捉要点，简洁地写。"
         "不要包含除摘要本身之外的任何额外评论。"),
        ("human", "搜索词: {query}\n\n搜索结果:\n{search_results}"),
    ])
    | llm
)
```

这里用到了 LCEL 的核心组件 `RunnablePassthrough.assign`：**在不丢失原有输入字段的前提下，向字典追加新字段**。链执行到 Prompt 时，输入已从 `{"query", "reason"}` 扩展为 `{"query", "reason", "search_results"}`。

模型行为要求：

| 指令含义 | 说明 |
|----------|------|
| 你是研究助手 | 模拟一个能查资料的人 |
| 给关键词后上网搜索 | 关键词来自 planner_agent |
| 写出 2-3 段简洁总结 | 每次结果必须压缩到 300 字以内 |
| 可以语法不完整 | 重点是信息密度，不是行文流畅 |
| 不要添加自己的评论 | 只提取信息，不主观判断 |

**并发执行所有搜索**（这是系统效率的关键）：

```python
async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
    inputs = [{"query": item.query, "reason": item.reason} for item in search_plan.searches]
    results = await search_chain.abatch(
        inputs,
        config={"max_concurrency": 5},  # 最多5条并发，避免触发限流
        return_exceptions=True,          # 单条失败不中断整批
    )
    summaries = [r.content for r in results if not isinstance(r, Exception)]  # 过滤失败项
    return summaries
```

`abatch` + `max_concurrency` 一行搞定并发控制，比手写 `asyncio.gather` 更简洁，且 `return_exceptions=True` 保证单条搜索失败不会中断整批任务。

Search Agent 整体流程：

```
关键词（来自 planner_agent） → search_agent →
     🔍 DuckDuckGo 搜索
     ✂️ 生成 2-3 段摘要
     📦 返回给 writer_agent 写整合报告
```

### 4.5 Writer Agent ✍️

Writer Agent 是**整个研究系统的"输出终结者"**，负责把所有搜索摘要综合成一份**完整、结构化、可阅读的长篇报告**。

任务清单：
- 收到研究主题和之前所有搜索摘要
- **先写一个大纲（outline）**
- 根据大纲写出详细的 Markdown 格式报告
- 同时生成简短总结和后续可研究的问题

```python
_WRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "你是一位资深研究员，负责为研究查询撰写连贯的报告。\n"
     "你应该首先为报告提出一个大纲，描述报告的结构和流程。"
     "然后，生成报告并将其作为最终输出返回。\n"
     "最终输出应为Markdown格式，并且应该详细且冗长。目标是10-20页的内容，至少1500字。"
     "最终结果请用中文输出。"),
    ("human", "原始查询: {query}\n\n研究结果:\n{research_results}"),
])

# 正常路径：结构化输出，直接返回 ReportData 对象
writer_chain = _WRITER_PROMPT | llm.with_structured_output(ReportData)

# 降级路径：报告过长时 JSON 会被截断，改用纯文本输出兜底
writer_chain_plain = _WRITER_PROMPT | llm
```

提示词要点：

| 行为 | 说明 |
|------|------|
| 角色设定 | 资深研究员（senior researcher） |
| 输入 | 研究主题 + 所有搜索摘要 |
| 第一步 | 写出报告结构（outline） |
| 第二步 | 写出 Markdown 报告正文 |
| 要求 | 长、详细、有逻辑（10-20页，1500+ 字） |
| 输出格式 | Markdown（`# 一级标题`, `- 列表` 等） |
| 输出语言 | 中文 |

> ⚠️ **实践中的坑**：`with_structured_output` 要求模型把整篇报告包裹进 JSON 字符串输出。报告很长时，输出会超出 token 上限被截断，Pydantic 拿到残缺 JSON 就抛 `ValidationError`。

解决方案——双链路 + 自动降级：

```python
async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
    payload = {
        "query": query,
        "research_results": "\n\n---\n\n".join(search_results),  # 用分隔线拼接各条摘要
    }
    try:
        return await writer_chain.ainvoke(payload)            # 正常路径：结构化输出
    except Exception as e:
        # 报告过长时 JSON 截断，降级为纯文本输出
        print(f"  Structured output failed ({type(e).__name__}), falling back to plain text...")
        response = await writer_chain_plain.ainvoke(payload)
        return ReportData(
            short_summary=f"关于「{query}」的研究报告",
            markdown_report=response.content,               # 内容完整，不丢失
            follow_up_questions=[],
        )
```

### 4.6 ResearchManager 主类

三个 Agent 由 `ResearchManager` 串联编排：

```python
class ResearchManager:

    def __init__(self):
        print("初始化已完成，欢迎使用。使用前请确认相关模型能够被顺利调用。")

    async def run(self, query: str) -> None:
        search_plan    = await self._plan_searches(query)          # WebSearchPlan: 5-10个搜索词
        search_results = await self._perform_searches(search_plan)  # list[str]: 每条搜索的摘要
        report         = await self._write_report(query, search_results)  # ReportData: 最终报告

        print(report.markdown_report)
        self._save_report(query, report.markdown_report)
```

报告自动保存到 `research_reports/` 目录，文件名由查询主题生成：

```python
def _save_report(self, query: str, markdown_content: str) -> None:
    sanitized_query = query.replace(" ", "_").replace("？", "")  # 清理文件名非法字符
    file_name = f"research_reports/关于{sanitized_query}调研报告.md"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(markdown_content)
```

---

## 五、运行效果 🎬

```bash
uv run main_langchain.py
```

```
==================================================
Mini DeepResearch - LangChain LCEL版本
==================================================
初始化已完成，欢迎使用。

[1/3] Planning searches...
  Generated 7 queries

[2/3] Executing searches...
  7/7 searches completed

[3/3] Generating final report...

=====REPORT=====

# AI在教育中的应用研究报告
## 一、概述
...（1500字以上详细报告）

=====FOLLOW UP QUESTIONS=====

1. AI如何实现个性化学习路径？
2. 教育AI的数据隐私问题如何解决？
...

Report saved to: research_reports/关于AI在教育中的应用调研报告.md
```

---

## 六、项目结构总览 📁

```
mini_deepresearch/
├── main_langchain.py    # 主程序：三个 Agent + ResearchManager
├── test_setup.py        # 环境检查：依赖、API、文件结构一键验证
├── pyproject.toml       # 项目依赖（uv 管理）
├── .env                 # API Key 配置（不提交到 git）
├── .env.example         # 配置模板
├── README.md            # 项目文档
├── QUICKSTART.md        # 4步快速上手指南
└── research_reports/    # 报告输出目录（自动创建）
```

---

## 七、总结 🎯

本文从概念到代码，完整实现了一个 Mini DeepResearch 系统：

| 模块 | 技术方案 |
|------|---------|
| 规划 | `planner_chain` + `with_structured_output` |
| 搜索 | `DuckDuckGoSearchResults` + `abatch` 并发 |
| 写报告 | `writer_chain` + 自动降级兜底 |
| 数据流 | LCEL `RunnablePassthrough.assign` |

整个系统不到 180 行代码，核心思路清晰：

> **规划 → 并发搜索 → 结构化报告**

这套架构也很容易扩展：换成博查 API 提升搜索质量、接入更强的 `qwen-max` 提升报告深度、或者在 `_plan_searches` 里增加迭代式规划来逼近真正的 DeepSearch。

感兴趣的同学可以直接克隆运行，配置好阿里云 API Key 后 `uv run main_langchain.py` 即可体验。

---

> 💬 如果有问题或建议，欢迎在评论区交流！
