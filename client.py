from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="/Users/mac/.local/bin/uv",
    args=["run", "server.py"],
    # command="python",  # Executable
    # args=["server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)


# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def run():
    print("正在连接到MCP服务器...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()
            print("成功连接到服务器！")

            # List available tools
            tools = await session.list_tools()
            print(f"可用工具: {tools}")

            # List available resources
            resources = await session.list_resources()
            print(f"可用资源: {resources}")

            # Call a tool
            a = 5
            b = 3
            result = await session.call_tool("add", arguments={"a": a, "b": b})
            print(f"{a} + {b} = {result}")

            # Get a resource
            name = "用户"
            resource_path = f"greeting://{name}"
            try:
                content, mime_type = await session.read_resource(resource_path)
                print(f"个性化问候: {content}")
            except Exception as e:
                print(f"获取资源失败: {e}")

            print("客户端演示完成！")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())