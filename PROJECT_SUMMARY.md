# Mini DeepResearch 项目说明

## 项目位置

```
/Users/macbookpro/Downloads/mini_deepresearch/
```

## 文件列表

### 核心文件

| 文件 | 说明 |
|------|------|
| `main_langchain.py` | 主程序：LangChain Agent 定义与完整研究流程 |
| `pyproject.toml` | 项目依赖与元数据（uv 管理） |
| `.env` | 环境变量（API Key，不提交到 git） |
| `.env.example` | 环境变量模板 |

### 辅助文件

| 文件 | 说明 |
|------|------|
| `test_setup.py` | 环境检查脚本，验证依赖、API 配置、文件结构 |
| `README.md` | 完整项目文档 |
| `QUICKSTART.md` | 快速上手指南（4步） |

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置 API

```bash
cp .env.example .env
# 填入阿里云百炼平台 API Key 和 Base URL
```

### 3. 验证环境

```bash
uv run test_setup.py
```

### 4. 运行程序

```bash
uv run main_langchain.py
```

## 系统架构

```
用户查询
    ↓
PlannerAgent (qwen-plus)
    ↓ 生成 10-20 个搜索词（结构化输出）
SearchAgent (DuckDuckGo + qwen-plus，并发执行)
    ↓ 每条搜索生成 300 字内摘要
WriterAgent (qwen-plus)
    ↓ 综合所有摘要，生成 1500 字以上中文报告
保存到 research_reports/
```

## 技术栈

- **框架**: LangChain (`langchain`, `langchain-openai`, `langchain-community`)
- **模型**: 阿里云通义千问 `qwen-plus`（OpenAI 兼容接口）
- **搜索**: DuckDuckGo (`duckduckgo-search`)
- **数据验证**: Pydantic v2
- **运行时**: Python 3.10+，异步并发（asyncio）
- **包管理**: uv

## 核心功能

- 智能搜索规划（10-20 个相关搜索词）
- 异步并发搜索（提高效率）
- 智能内容摘要（每条搜索 < 300 字）
- 详细报告生成（1500+ 字，中文输出）
- 自动文件保存（Markdown 格式）
- 后续问题建议

## 注意事项

1. 需要阿里云百炼平台 API Key，并设置 `OPENAI_BASE_URL`
2. 需要稳定的网络连接（DuckDuckGo 搜索）
3. 完整研究流程约需 3-5 分钟
4. 注意 API 调用次数与费用
