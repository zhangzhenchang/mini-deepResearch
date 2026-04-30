"""
简单示例 - 演示如何使用Mini DeepResearch
"""

import asyncio
from main_langchain import ResearchManager


async def example_1():
    """示例1: 基本使用"""
    print("=== 示例1: 基本使用 ===\n")
    manager = ResearchManager()
    await manager.run("AI在教育中的应用")


async def example_2():
    """示例2: 技术研究"""
    print("=== 示例2: 技术研究 ===\n")
    manager = ResearchManager()
    await manager.run("MCP (Model Context Protocol) 技术详解")


async def example_3():
    """示例3: 市场分析"""
    print("=== 示例3: 市场分析 ===\n")
    manager = ResearchManager()
    await manager.run("2024年全球电动汽车市场趋势")


async def main():
    """主函数 - 选择要运行的示例"""
    print("Mini DeepResearch 示例程序\n")
    print("请选择要运行的示例:")
    print("1. AI在教育中的应用")
    print("2. MCP技术详解")
    print("3. 全球电动汽车市场趋势")
    print("4. 自定义查询")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == "1":
        await example_1()
    elif choice == "2":
        await example_2()
    elif choice == "3":
        await example_3()
    elif choice == "4":
        custom_query = input("请输入您的研究主题: ").strip()
        if custom_query:
            manager = ResearchManager()
            await manager.run(custom_query)
        else:
            print("查询不能为空！")
    else:
        print("无效的选项！")


if __name__ == "__main__":
    asyncio.run(main())
