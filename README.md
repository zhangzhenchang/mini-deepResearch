# Mini DeepResearch

基于 LangChain 的自动化研究助手，适配阿里云通义千问（Qwen）模型，可自动规划搜索、并发执行 DuckDuckGo 网络检索并生成结构化的 Markdown 研究报告。

## 功能特点

- **智能搜索规划**: 使用 qwen-plus 自动生成 10-20 个相关搜索词
- **并发搜索**: 异步并发执行多个 DuckDuckGo 网络搜索，提高效率
- **智能摘要**: 对每个搜索结果进行精炼摘要（300 字以内）
- **报告生成**: 综合所有搜索结果，生成详细的 Markdown 格式研究报告（1500 字以上）
- **自动保存**: 报告自动保存至 `research_reports/` 目录

## 系统架构

系统由三个 Agent 组成：

1. **PlannerAgent（规划 Agent）**: 接收用户查询，生成网络搜索计划
2. **SearchAgent（搜索 Agent）**: 并发执行网络搜索并对结果进行摘要
3. **WriterAgent（写作 Agent）**: 综合所有搜索摘要，撰写最终研究报告

## 环境要求

- Python >= 3.10
- 阿里云百炼平台 API Key（用于调用 qwen-plus 模型）

## 安装依赖

```bash
uv sync
```

或使用 pip：

```bash
pip install langchain langchain-openai langchain-community duckduckgo-search pydantic python-dotenv
```

## 环境配置

复制 `.env.example` 并填入你的阿里云 API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 阿里云百炼平台 API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 阿里云 OpenAI 兼容接口地址
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> API Key 申请地址：[阿里云百炼平台](https://bailian.console.aliyun.com/)

## 使用方法

### 基本使用

```bash
python main_langchain.py
```

### 自定义查询

修改 `main_langchain.py` 底部的 `test_query` 变量：

```python
test_query = "你想研究的主题"
```

### 代码调用示例

```python
import asyncio
from main import ResearchManager

async def custom_research():
    manager = ResearchManager()
    await manager.run("量子计算的最新进展")

asyncio.run(custom_research())
```

## 输出说明

程序运行后会产生两种输出：

1. **控制台输出**: 实时显示研究进度与最终报告
2. **Markdown 文件**: 自动保存在 `research_reports/` 目录下，文件名格式为 `关于<查询内容>调研报告.md`

示例控制台输出：

```
初始化已完成，欢迎使用。使用前请确认相关模型能够被顺利调用。
Starting research...
Planning searches...
Starting searching...
Search term: AI education applications
Reason for searching: ...
Searching... 1/15 completed
...
Thinking about report...

=====REPORT=====

# AI在教育中的应用研究报告
...

=====FOLLOW UP QUESTIONS=====

1. AI如何个性化学习路径？
2. 教育AI的伦理问题有哪些？

Report saved as: research_reports/关于AI在教育中的应用调研报告.md
```

## 配置选项

### 修改使用的模型

在 `main_langchain.py` 的 `ResearchManager.__init__` 中更改 `model` 参数：

```python
self.llm = ChatOpenAI(
    model="qwen-plus",  # 可改为 "qwen-max"、"qwen-turbo" 等
    ...
)
```

### 修改搜索数量

修改 `PLANNER_PROMPT` 中的数量要求：

```python
"Output between 10 and 20 terms to query for."  # 调整数字
```

### 修改报告长度

修改 `WRITER_PROMPT` 中的字数要求：

```python
"Aim for 10-20 pages of content, at least 1500 words."  # 调整长度
```

### 修改输出语言

修改 `WRITER_PROMPT` 末尾的语言要求：

```python
"最终结果请用中文输出。"  # 改为其他语言要求
```

## 项目结构

```
mini_deepresearch/
├── main_langchain.py              # 主程序（Agent 定义与研究流程）
├── .env                 # 环境变量（API Key 等，不提交到 git）
├── .env.example         # 环境变量模板
├── README.md            # 项目说明文档
└── research_reports/    # 报告输出目录（自动创建）
```

## 常见问题

**Q: 调用模型时报错 401 / Invalid API Key？**  
A: 检查 `.env` 中的 `OPENAI_API_KEY` 是否正确，以及 `OPENAI_BASE_URL` 是否指向阿里云兼容接口。

**Q: 搜索失败怎么办？**  
A: 程序会自动跳过失败的搜索并继续处理其余结果，不影响最终报告生成。

**Q: 如何加快运行速度？**  
A: 减少 `PLANNER_PROMPT` 中的搜索数量，或将模型改为 `qwen-turbo`。

**Q: 报告保存在哪里？**  
A: 保存在项目根目录下的 `research_reports/` 文件夹，文件名包含查询关键词。

## 许可证

本项目基于课程《2025大模型Agent智能体开发实战》的示例代码改编。
