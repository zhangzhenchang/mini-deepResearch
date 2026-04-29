# Mini DeepResearch

基于OpenAI Agents SDK的研究助手系统，可以自动进行网络搜索并生成详细的研究报告。

## 功能特点

- **智能搜索规划**: 使用o4-mini模型自动生成10-20个相关搜索词
- **并发搜索**: 异步并发执行多个网络搜索，提高效率
- **智能总结**: 对每个搜索结果进行智能摘要
- **报告生成**: 综合所有搜索结果，生成详细的Markdown格式研究报告
- **自动保存**: 自动将报告保存为Markdown文件

## 系统架构

系统由三个Agent组成：

1. **PlannerAgent (规划Agent)**: 根据用户查询生成搜索计划
2. **SearchAgent (搜索Agent)**: 执行网络搜索并总结结果
3. **WriterAgent (写作Agent)**: 综合搜索结果生成最终报告

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

需要设置OpenAI API密钥：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 使用方法

### 基本使用

```bash
python main.py
```

### 自定义查询

修改`main.py`中的`test_query`变量：

```python
test_query = "你想研究的主题"
```

### 代码示例

```python
import asyncio
from main import ResearchManager

async def custom_research():
    manager = ResearchManager()
    await manager.run("量子计算的最新进展")

asyncio.run(custom_research())
```

## 输出说明

程序会生成以下输出：

1. **控制台输出**: 实时显示研究进度和最终报告
2. **Markdown文件**: 保存在`research_reports/`目录下

## 配置选项

### 修改模型

在`main.py`中可以修改使用的模型：

```python
# 规划Agent使用o4-mini
planner_agent = Agent(
    name="PlannerAgent",
    instructions=PLANNER_PROMPT,
    model="o4-mini",  # 可改为 "gpt-4.1" 等
    output_type=WebSearchPlan,
)

# 写作Agent使用o4-mini
writer_agent = Agent(
    name="WriterAgent",
    instructions=WRITER_PROMPT,
    model="o4-mini",  # 可改为 "gpt-4.1" 等
    output_type=ReportData,
)
```

### 修改报告长度

修改`WRITER_PROMPT`中的要求：

```python
WRITER_PROMPT = (
    "..."
    "Aim for 10-20 pages of content, at least 1500 words."  # 修改这里
    "最终结果请用中文输出。"
)
```

### 修改搜索数量

修改`PLANNER_PROMPT`中的要求：

```python
PLANNER_PROMPT = (
    "..."
    "Output between 10 and 20 terms to query for."  # 修改这里
)
```

## 项目结构

```
mini_deepresearch/
├── main.py              # 主程序文件
├── requirements.txt     # 依赖包列表
├── README.md           # 项目说明文档
└── research_reports/   # 报告输出目录（自动创建）
```

## 注意事项

1. 需要有效的OpenAI API密钥
2. 需要网络连接以执行网络搜索
3. o4-mini模型需要API访问权限
4. 搜索和报告生成可能需要几分钟时间

## 示例输出

运行程序后，会看到类似以下输出：

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

## 一、概述
...

=====FOLLOW UP QUESTIONS=====

1. AI如何个性化学习路径？
2. 教育AI的伦理问题有哪些？
...

Report saved as: research_reports/关于AI在教育中的应用调研报告.md
```

## 常见问题

**Q: 如何更改输出语言？**  
A: 修改`WRITER_PROMPT`中的"最终结果请用中文输出"为其他语���要求。

**Q: 搜索失败怎么办？**  
A: 程序会自动跳过失败的搜索，继续处理其他搜索结果。

**Q: 如何加快速度？**  
A: 可以减少搜索数量或使用更快的模型（如gpt-4.1-mini）。

## 许可证

本项目基于课程《2025大模型Agent智能体开发实战》的示例代码改编。
