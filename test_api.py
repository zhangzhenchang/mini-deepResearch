"""测试阿里云百炼API连接"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

print("Testing API connection...")
print(f"API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"API Base: {os.getenv('OPENAI_BASE_URL')}")

try:
    llm = ChatOpenAI(
        model="qwen-plus",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )

    response = llm.invoke("你好，请用一句话介绍你自己")
    print(f"\nSuccess! Response: {response.content}")

except Exception as e:
    print(f"\nError: {e}")
    print(f"\nError type: {type(e).__name__}")
