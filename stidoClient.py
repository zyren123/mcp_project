import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client=OpenAI(base_url="https://api.siliconflow.cn/v1")

    # methods will go here
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """使用OpenAI API处理查询并调用可用工具"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]
        
        print("可用工具:", available_tools)
        print("初始消息:", messages)
        
        # 处理结果和可能的工具调用
        final_text = []
        
        while True:
            # 调用OpenAI API
            print("调用OpenAI API...")
            response = self.client.chat.completions.create(
                model="Qwen/Qwen2.5-7B-Instruct",
                messages=messages,
                tools=available_tools,
                tool_choice="auto"
            )
            
            print("API响应:", response)
            
            # 获取模型响应
            assistant_message = response.choices[0].message
            assistant_content = assistant_message.content
            
            # 如果有文本内容，添加到最终结果
            if assistant_content:
                final_text.append(assistant_content)
                print(f"模型回复: {assistant_content}")
            
            # 检查是否有工具调用
            tool_calls = assistant_message.tool_calls
            if not tool_calls:
                # 没有工具调用，结束对话
                break
                
            # 处理每个工具调用
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                
                print(f"调用工具: {function_name}, 参数: {function_args}")
                
                # 执行工具调用
                try:
                    # 将字符串JSON转换为Python字典
                    import json
                    args_dict = json.loads(function_args)
                    
                    # 调用MCP工具
                    result = await self.session.call_tool(function_name, args_dict)
                    final_text.append(f"[调用工具 {function_name} 使用参数 {function_args}]")
                    
                    # 添加工具调用结果到消息历史
                    messages.append({
                        "role": "assistant",
                        "content": assistant_content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": function_args
                                }
                            }
                        ]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)  # 确保结果是字符串
                    })
                    
                    print(f"工具返回结果: {result}")
                except Exception as e:
                    error_msg = f"工具调用失败: {str(e)}"
                    final_text.append(error_msg)
                    print(error_msg)
                    
                    # 添加错误信息到消息历史
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: {str(e)}"
                    })
            
            # 继续对话循环，让模型处理工具调用的结果
        
        # 返回所有结果
        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())