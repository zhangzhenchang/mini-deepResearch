"""
测试脚本 - 验证环境配置是否正确
"""

import sys
import os


def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("  需要Python 3.8或更高版本")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    required_packages = {
        "agents": "openai-agents-sdk",
        "pydantic": "pydantic",
        "asyncio": "asyncio (内置)"
    }

    all_installed = True
    for module, package in required_packages.items():
        try:
            if module == "asyncio":
                import asyncio
            elif module == "agents":
                import agents
            elif module == "pydantic":
                import pydantic
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            all_installed = False

    return all_installed


def check_api_key():
    """检查API密钥"""
    print("\n检查API密钥...")
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ OPENAI_API_KEY 已设置: {masked_key}")
        return True
    else:
        print("✗ OPENAI_API_KEY 未设置")
        print("  请设置环境变量: export OPENAI_API_KEY='your-key'")
        return False


def check_file_structure():
    """检查文件结构"""
    print("\n检查文件结构...")
    required_files = ["main.py", "requirements.txt", "README.md"]

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
        print("✓ ��有检查通过！可以开始使用。")
        print("\n运行示例:")
        print("  python main.py")
        print("  python example.py")
    else:
        print("✗ 部分检查失败，请根据上述提示修复问题。")
        print("\n安装依赖:")
        print("  pip install -r requirements.txt")
        print("\n设置API密钥:")
        print("  export OPENAI_API_KEY='your-key'")
    print("=" * 50)


if __name__ == "__main__":
    main()
