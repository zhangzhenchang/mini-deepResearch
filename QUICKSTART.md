# 快速开始指南

## 第一步：安装依赖

```bash
cd /Users/macbookpro/Downloads/mini_deepresearch
pip install -r requirements.txt
```

## 第二步：配置API密钥

### 方法1：环境变量（推荐）

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

### 方法2：使用.env文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# OPENAI_API_KEY=your-openai-api-key-here
```

## 第三步：验证环境

```bash
python test_setup.py
```

如果所有检查都通过，你会看到：
```
✓ 所有检查通过！可以开始使用。
```

## 第四步：运行程序

### 方式1：运行默认示例

```bash
python main.py
```

这将研究主题："AI在教育中的应用"

### 方式2：运行交互式示例

```bash
python example.py
```

然后选择预设的示例或输入自定义查询。

### 方式3：在代码中使用

```python
import asyncio
from main import ResearchManager

async def my_research():
    manager = ResearchManager()
    await manager.run("你想研究的主题")

asyncio.run(my_research())
```

## 预期输出

程序运行时会显示：

1. **初始化信息**
2. **搜索规划** - 生成10-20个搜索词
3. **搜索进度** - 显示每个搜索的完成情况
4. **报告生成** - 综合所有结果
5. **最终报告** - 在控制台显示完整报告
6. **后续问题** - 建议进一步研究的主题
7. **文件保存** - 报告保存在 `research_reports/` 目录

## 常见问题

### Q1: 安装依赖失败

```bash
# 尝试升级pip
pip install --upgrade pip

# 或使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: API密钥错误

确保你的API密钥有效且有权限访问o4-mini模型。

### Q3: 搜索失败

- 检查网络连接
- 确认API配额充足
- 部分搜索失败不影响整体运行

### Q4: 修改研究主题

编辑 `main.py` 文件的最后部分：

```python
async def main():
    manager = ResearchManager()
    test_query = "你的研究主题"  # 修改这里
    await manager.run(test_query)
```

## 下一步

- 查看 `README.md` 了解详细配置选项
- 查看 `example.py` 学习更多使用方式
- 修改 Agent 的 prompt 来定制行为
- 调整模型参数优化性能

## 获取帮助

如果遇到问题：

1. 运行 `python test_setup.py` 检查环境
2. 查看 `README.md` 中的常见问题
3. 检查 OpenAI API 状态
4. 确认模型访问权限

祝使用愉快！
