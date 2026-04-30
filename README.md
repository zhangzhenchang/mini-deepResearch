# Mini DeepResearch

基于 **LangChain LCEL** 的自动化研究助手，适配阿里云通义千问（Qwen）模型，可自动规划搜索、并发执行 DuckDuckGo 网络检索并生成结构化的 Markdown 研究报告。

## 功能特点

- **智能搜索规划**: 使用 `qwen-plus` 自动生成 5-10 个相关搜索词
- **并发搜索**: 通过 `abatch` 异步并发执行多个 DuckDuckGo 搜索，提高效率
- **智能摘要**: 对每个搜索结果进行精炼摘要（300 字以内）
- **报告生成**: 综合所有摘要，生成详细的 Markdown 格式研究报告（1500 字以上）
- **自动保存**: 报告自动保存至 `research_reports/` 目录
- **降级兜底**: 报告过长时自动切换纯文本输出，防止 JSON 截断报错

## 系统架构

系统由三条 LCEL 链组成，线性串联：

```
用户查询
    ↓
planner_chain（生成 5-10 个搜索词）
    ↓
search_chain × N（并发执行，每条生成摘要）
    ↓
writer_chain（综合所有摘要，撰写最终报告）
    ↓
Markdown 研究报告（自动保存）
```

| Agent           | 职责                                             |
| --------------- | ------------------------------------------------ |
| `planner_chain` | 接收用户查询，输出结构化搜索计划 `WebSearchPlan` |
| `search_chain`  | 执行 DuckDuckGo 搜索，生成 300 字内摘要          |
| `writer_chain`  | 综合所有摘要，撰写 1500 字以上 Markdown 报告     |

## 环境要求

- Python >= 3.10
- 阿里云百炼平台 API Key（用于调用 `qwen-plus` 模型）

## 安装依赖

```bash
uv sync
```

或使用 pip：

```bash
pip install langchain langchain-openai langchain-community ddgs pydantic python-dotenv
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

## 验证环境

```bash
uv run test_setup.py
```

全部通过后即可运行主程序。

## 使用方法

### 基本使用

```bash
uv run main_langchain.py
```

### 自定义查询

修改 `main_langchain.py` 底部的 `test_query` 变量：

```python
test_query = "你想研究的主题"
```

### 代码调用示例

```python
import asyncio
from main_langchain import ResearchManager

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
==================================================
Mini DeepResearch - LangChain LCEL版本
==================================================
初始化已完成，欢迎使用。使用前请确认相关模型能够被顺利调用。
Starting research for: AI在教育中的应用

[1/3] Planning searches...
  Generated 7 queries

[2/3] Executing searches...
  7/7 searches completed

[3/3] Generating final report...

=====REPORT=====

# AI在教育中的应用研究报告
...

=====FOLLOW UP QUESTIONS=====

1. AI如何个性化学习路径？
2. 教育AI的伦理问题有哪些？

Report saved to: research_reports/关于AI在教育中的应用调研报告.md
```

## 配置选项

### 修改使用的模型

在 `main_langchain.py` 中更改模块级 `llm` 的 `model` 参数：

```python
llm = ChatOpenAI(
    model="qwen-plus",  # 可改为 "qwen-max"、"qwen-turbo" 等
    ...
)
```

### 修改搜索数量

修改 `planner_chain` 的系统提示中的数量要求：

```python
("system", "...生成5到10个搜索词。")  # 调整数字
```

### 修改报告长度

修改 `_WRITER_PROMPT` 的系统提示中的字数要求：

```python
("system", "...目标是10-20页的内容，至少1500字。")  # 调整长度
```

### 修改输出语言

修改 `_WRITER_PROMPT` 末尾的语言要求：

```python
("system", "...最终结果请用中文输出。")  # 改为其他语言要求
```

## 项目结构

```
mini_deepresearch/
├── main_langchain.py    # 主程序（LCEL 链定义与研究流程）
├── test_setup.py        # 环境检查脚本
├── pyproject.toml       # 项目依赖（uv 管理）
├── .env                 # 环境变量（不提交到 git）
├── .env.example         # 环境变量模板
├── README.md            # 项目说明文档
├── QUICKSTART.md        # 快速上手指南
└── research_reports/    # 报告输出目录（自动创建）
```

## 常见问题

**Q: 调用模型时报错 401 / Invalid API Key？**  
A: 检查 `.env` 中的 `OPENAI_API_KEY` 是否正确，以及 `OPENAI_BASE_URL` 是否指向阿里云兼容接口。

**Q: 搜索失败怎么办？**  
A: 程序会自动跳过失败的搜索并继续处理其余结果，不影响最终报告生成。

**Q: 报告生成时报 JSON 解析错误？**  
A: 报告内容过长时会触发 JSON 截断，程序已内置降级逻辑，会自动切换为纯文本输出，报告内容不会丢失。

**Q: 如何加快运行速度？**  
A: 减少 `planner_chain` 提示词中的搜索数量，或将模型改为 `qwen-turbo`。

**Q: 报告保存在哪里？**  
A: 保存在项目根目录下的 `research_reports/` 文件夹，文件名包含查询关键词。
