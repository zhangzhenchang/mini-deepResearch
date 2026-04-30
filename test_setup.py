"""
测试脚本 - 验证环境配置是否正确
"""

import sys
import os


def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("  需要Python 3.10或更高版本")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    required_packages = {
        "langchain": "langchain",
        "langchain_openai": "langchain-openai",
        "langchain_community": "langchain-community",
        "duckduckgo_search": "ddgs",
        "pydantic": "pydantic",
        "dotenv": "python-dotenv",
        "asyncio": "asyncio (内置)"
    }

    all_installed = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            all_installed = False

    return all_installed


def check_api_key():
    """检查API密钥及接口地址"""
    print("\n检查API配置...")
    from dotenv import load_dotenv
    load_dotenv()

    passed = True

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ OPENAI_API_KEY 已设置: {masked_key}")
    else:
        print("✗ OPENAI_API_KEY 未设置")
        print("  请在 .env 文件中设置: OPENAI_API_KEY=sk-xxxxxxxx")
        passed = False

    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        print(f"✓ OPENAI_BASE_URL 已设置: {base_url}")
    else:
        print("✗ OPENAI_BASE_URL 未设置")
        print("  请在 .env 文件中设置: OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1")
        passed = False

    return passed


def check_file_structure():
    """检查文件结构"""
    print("\n检查文件结构...")
    required_files = ["main_langchain.py", ".env", "README.md"]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 不存在")
            all_exist = False

    return all_exist


def main():
    """主测试函数"""
    print("=" * 50)
    print("Mini DeepResearch 环境检查")
    print("=" * 50)

    results = []
    results.append(("Python版本", check_python_version()))
    results.append(("依赖包", check_dependencies()))
    results.append(("API密钥", check_api_key()))
    results.append(("文件结构", check_file_structure()))

    print("\n" + "=" * 50)
    print("检查结果汇总")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有检查通过！可以开始使用。")
        print("\n运行示例:")
        print("  uv run main_langchain.py")
    else:
        print("✗ 部分检查失败，请根据上述提示修复问题。")
        print("\n安装依赖:")
        print("  uv sync")
        print("\n配置API:")
        print("  cp .env.example .env  # 然后填入阿里云 API Key 和 Base URL")
    print("=" * 50)


if __name__ == "__main__":
    main()
