# server.py
from mcp.server.fastmcp import FastMCP
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(base_url="https://api.siliconflow.cn/v1")

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def compare(a: int, b: int) -> int:
    """Compare two numbers,return True if a>b,otherwise return False"""
    return a>b

# 添加对话重写工具
@mcp.tool()
def rewrite(chat_history: str, last_user_content: str) -> str:
    """
    使用OpenAI API重写对话内容
    
    参数:
    - chat_history: 对话历史
    - last_user_content: 用户最后一条消息内容
    
    返回:
    - 重写后的内容
    """
    # 构建提示词
    system_prompt = """
    你是一个对话改写机器人，负责对给定的用户（学生或家长）和老师的对话进行总结改写，给出当前消息的改写，要求改写后的当前消息具有完整的语义信息，你必须遵循如下指令:
    1. 你需要纠正当前消息中的错别字、同音字、形近字以及字序错误问题;
    2. 当前消息可能会用几条邻近的消息来描述同一个问题，你需要结合邻近的几条消息与当前消息总结成一句语义完整的语句;
    3. 当前消息可能是对上文消息的答复，你需要综合上文消息和当前消息答复，将当前消息改写成一句语义完整的话；
    4. 若当前消息只是简单的'好的','收到','谢谢'等回复类消息，则不需要进行改写
    5. 若当前消息与上文消息没有关系，或已经是一句完整表达一个问题的话，不需要进行改写，直接输出当前消息
    6. 若当前消息没有说完整，且和历史的消息没有关系，禁止猜测当前消息的意图，不需要进行改写
    7. 输出中禁止杜撰与对话内容无关的信息，也禁止猜测对话消息的意图
    8. 请注意你只需要对当前消息进行改写
    """
    
    user_prompt = f"""
    下面是一段用户（学生或家长）和老师的对话：
    <对话内容>
    {chat_history}
    </对话内容>
    当前消息为：{last_user_content}
    请输出改写后的文本。
    """
    
    try:
        # 使用OpenAI API调用模型
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",  # 使用千问模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
        )
        
        # 获取生成的内容
        result = response.choices[0].message.content
        return result
    except Exception as e:
        return f"重写失败: {str(e)}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
