# 快速开始指南

## 第一步：安装依赖

```bash
uv sync
```

或使用 pip：

```bash
pip install langchain langchain-openai langchain-community duckduckgo-search pydantic python-dotenv
```

## 第二步：配置 API

```bash
cp .env.example .env
```

编辑 `.env`，填入阿里云百炼平台的 API Key 和接口地址：

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> API Key 申请地址：[阿里云百炼平台](https://bailian.console.aliyun.com/)

## 第三步：验证环境

```bash
uv run test_setup.py
```

所有检查通过后会显示：

```
✓ 所有检查通过！可以开始使用。
```

## 第四步：运行程序

```bash
uv run main_langchain.py
```

默认研究主题为 "AI在教育中的应用"，修改 `main_langchain.py` 底部的 `test_query` 即可更换主题：

```python
test_query = "你的研究主题"
```

## 预期输出

程序运行时会依次显示：

1. 初始化信息
2. 搜索规划 — 生成 10-20 个搜索词
3. 搜索进度 — 显示每条搜索的完成情况
4. 报告生成 — 综合所有结果
5. 最终报告 — 控制台完整输出（中文 Markdown）
6. 后续问题 — 建议进一步研究的方向
7. 文件保存 — 报告保存在 `research_reports/` 目录

## 在代码中调用

```python
import asyncio
from main import ResearchManager

async def my_research():
    manager = ResearchManager()
    await manager.run("你想研究的主题")

asyncio.run(my_research())
```

## 常见问题

**Q: 安装依赖失败？**  
尝试使用国内镜像：
```bash
pip install langchain langchain-openai langchain-community duckduckgo-search pydantic python-dotenv \
    -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q: 报错 401 / Invalid API Key？**  
检查 `.env` 中的 `OPENAI_API_KEY` 是否正确，`OPENAI_BASE_URL` 是否为阿里云兼容接口地址。

**Q: 搜索失败？**  
部分搜索失败不影响整体运行，程序会自动跳过并继续处理其余结果。

**Q: 如何更换模型？**  
修改 `main_langchain.py` 中 `ResearchManager.__init__` 的 `model` 参数，如改为 `"qwen-max"` 或 `"qwen-turbo"`。
